param([string]$Python = "py")
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Creation de l'environnement Python impossible." }
}
& .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw "Installation des dependances impossible." }
& .\.venv\Scripts\python.exe scripts\build_release.py
if ($LASTEXITCODE -ne 0) { throw "Construction ou verification de la release impossible." }
