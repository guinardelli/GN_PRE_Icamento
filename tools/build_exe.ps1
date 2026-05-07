$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DistPath = Join-Path $ProjectRoot "dist\release_$Timestamp"
$SpecPath = Join-Path $ProjectRoot "packaging\GN_PRE_Icamento.spec"

Push-Location $ProjectRoot
try {
    python -m PyInstaller --noconfirm --clean --distpath $DistPath $SpecPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    $ExePath = Join-Path $DistPath "GN_PRE_Icamento\GN_PRE_Icamento.exe"
    & $ExePath --smoke-test
    if ($LASTEXITCODE -ne 0) {
        throw "Executable smoke test failed with exit code $LASTEXITCODE."
    }

    $ZipPath = Join-Path $ProjectRoot "dist\GN_PRE_Icamento_1.0.0_windows.zip"
    Compress-Archive `
        -Path (Join-Path $DistPath "GN_PRE_Icamento") `
        -DestinationPath $ZipPath `
        -Force

    Write-Host "Executable ready: $ExePath"
    Write-Host "Distribution ZIP ready: $ZipPath"
}
finally {
    Pop-Location
}
