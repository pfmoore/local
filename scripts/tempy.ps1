$dir = Join-Path $env:TEMP (New-Guid)
New-Item -ItemType Directory -Path $dir | Out-Null
$env = (Join-Path $dir .venv)
virtualenv $env
& (Get-Process -Id $pid).Path -NoExit {
    param($dir)
    Write-Host -ForegroundColor Cyan "Launching nested prompt in virtual environment. Type 'exit' to return."
    Write-Host -ForegroundColor Cyan "This is a temporary environment and will be deleted on exit."
    $orig = $PWD
    cd $dir
    & (Join-Path $dir ".venv" "Scripts" "activate.ps1")
    Register-EngineEvent PowerShell.Exiting { cd $orig; Remove-Item -Recurse $dir } | Out-Null
} -args $dir
