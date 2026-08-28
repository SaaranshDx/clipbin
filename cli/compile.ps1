[CmdletBinding()]
param(
    [string]$Python = "py"
)

$ErrorActionPreference = "Stop"
$cliDirectory = $PSScriptRoot
$projectDirectory = Split-Path -Parent $cliDirectory
$distDirectory = Join-Path $cliDirectory "dist"
$workDirectory = Join-Path $cliDirectory "build"

Push-Location $projectDirectory
try {
    & $Python -m pip install --upgrade pyinstaller requests cryptography
    if ($LASTEXITCODE -ne 0) { throw "Could not install build dependencies." }

    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Tests failed; build cancelled." }

    & $Python -m PyInstaller `
        --clean `
        --onefile `
        --name clipbin `
        --distpath $distDirectory `
        --workpath $workDirectory `
        --specpath $cliDirectory `
        (Join-Path $cliDirectory "main.py")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }

    Write-Host "Built executable: $(Join-Path $distDirectory 'clipbin.exe')"
}
finally {
    Pop-Location
}
