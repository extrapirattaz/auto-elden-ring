param([string]$Python = "py")
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Cannot create the Python environment." }
}
& .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw "Cannot install build dependencies." }
& .\.venv\Scripts\python.exe scripts\build_release.py
if ($LASTEXITCODE -ne 0) { throw "Release build or verification failed." }
