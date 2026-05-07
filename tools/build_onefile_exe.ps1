$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DistPath = Join-Path $ProjectRoot "dist\onefile_$Timestamp"
$SpecPath = Join-Path $ProjectRoot "packaging\GN_PRE_Icamento_onefile.spec"
$FinalExePath = Join-Path $ProjectRoot "dist\GN_PRE_Icamento_1.0.0_windows_onefile.exe"

Push-Location $ProjectRoot
try {
    python -m PyInstaller --noconfirm --clean --distpath $DistPath $SpecPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    $ExePath = Join-Path $DistPath "GN_PRE_Icamento.exe"
    & $ExePath --smoke-test
    if ($LASTEXITCODE -ne 0) {
        throw "Executable smoke test failed with exit code $LASTEXITCODE."
    }

    Copy-Item -LiteralPath $ExePath -Destination $FinalExePath -Force

    Write-Host "One-file executable ready: $FinalExePath"
}
finally {
    Pop-Location
}
