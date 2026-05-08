$ErrorActionPreference = "Stop"

Write-Host "Tkinter is now the official UI. Delegating to tools\build_exe.ps1..."
& (Join-Path $PSScriptRoot "build_exe.ps1")
