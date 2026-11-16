param([string]$OpenSCAD = 'C:\Program Files\OpenSCAD\openscad.exe')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot 'tools\python\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { $pythonPath = 'python' }
& $pythonPath (Join-Path $PSScriptRoot 'export.py') --openscad $OpenSCAD
if ($LASTEXITCODE -ne 0) { throw 'Eksport STL nie powiodl sie.' }
