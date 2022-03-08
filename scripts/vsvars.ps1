[CmdletBinding()]
param(
    [ScriptBlock]$ScriptBlock
)

# Based on https://github.com/microsoft/vswhere/wiki/Start-Developer-Command-Prompt
$init = {
    Write-Host -ForegroundColor Cyan "Launching nested prompt with Visual Studio activated. Type 'exit' to return."
    $vswhere = (gcm -ea 0 vswhere).Source ?? "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    $installationPath = & $vswhere -prerelease -latest -property installationPath
    if ($installationPath -and (test-path "$installationPath\Common7\Tools\vsdevcmd.bat")) {
      & "${env:COMSPEC}" /s /c "`"$installationPath\Common7\Tools\vsdevcmd.bat`" -no_logo -arch=amd64 && set" | foreach-object {
        $name, $value = $_ -split '=', 2
        set-content env:\"$name" $value
      }
    }
}
if ($ScriptBlock -ne $null) {
    $cmd = [ScriptBlock]::Create(
        $init.ToString() + "`n" + $ScriptBlock.ToString()
    )
    & (Get-Process -Id $pid).Path $cmd
} else {
    & (Get-Process -Id $pid).Path -NoExit $init
}

