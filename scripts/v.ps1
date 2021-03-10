[CmdletBinding()]
param(
    [Switch]$Activate,
    [Switch]$Create,
    [Switch]$Temp,
    [ScriptBlock]$ScriptBlock
)

if (($Activate -and $Create) -or ($Activate -and $Temp) -or ($Create -and $Temp)) {
    throw "Only one of activate, create, and temp is allowed"
}
if ($ScriptBlock -and ($Activate -or $Create -or $Temp)) {
    throw "Cannot have flags and a scriptblock"
}

if ($Temp) {
    $Name = Join-Path $env:TEMP (New-Guid)
    virtualenv $Name
    & (Get-Process -Id $pid).Path -NoExit {
        param($name)
        Write-Host -ForegroundColor Cyan "Launching nested prompt in virtual environment. Type 'exit' to return."
        Write-Host -ForegroundColor Cyan "This is a temporary environment and will be deleted on exit."
        & (Join-Path $name "Scripts" "activate.ps1")
        Register-EngineEvent PowerShell.Exiting { Remove-Item -Recurse $name } | Out-Null
    } -args $name
}

$ve_exists = (Test-Path -PathType Leaf ./.venv/pyvenv.cfg)

if ($Create) {
    if ($ve_exists) {
        Write-Error ".venv exists - cannot create it"
        return
    }
    virtualenv .venv
}

if ($Activate) {
    if (!$ve_exists) {
        Write-Error ".venv does not exist"
        return
    }
    . .venv/Scripts/Activate.ps1
}

if ($ScriptBlock) {
    if (!$ve_exists) {
        Write-Error ".venv does not exist"
        & $ScriptBlock
        return
    }

    # Save the environment, activate the virtualenv, and run the script block
    $oldpath = $env:PATH
    $oldvenv = $env:VIRTUAL_ENV
    try {
        $env:PATH = (Resolve-Path .venv/Scripts).Path + ';' + $env:PATH
        $env:VIRTUAL_ENV = (Resolve-Path .venv).Path
        & $ScriptBlock
    }
    finally {
        $env:PATH = $oldpath
        $env:VIRTUAL_ENV = $oldenv
    }
}
