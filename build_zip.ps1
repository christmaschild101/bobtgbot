# Packages Bob for JustRunMy.App Zip deployment.
# Usage:  powershell -ExecutionPolicy Bypass -File build_zip.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dist = Join-Path $root "dist"
$zip  = Join-Path $dist "bob-justrunmy.zip"

$files = @(
    "bob.py",
    "requirements.txt",
    "JUSTRUNMY.md",
    "bot\__init__.py",
    "bot\config.py",
    "bot\storage.py",
    "bot\handlers.py"
)

foreach ($f in $files) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $f))) {
        throw "Missing file: $f"
    }
}

New-Item -ItemType Directory -Force -Path $dist | Out-Null
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }

# Build a staging dir so the zip root holds bob.py/bot/... directly.
$stage = Join-Path $dist ".stage"
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
foreach ($f in $files) {
    $src = Join-Path $root $f
    $dst = Join-Path $stage $f
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item -LiteralPath $src -Destination $dst
}

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force
Remove-Item -LiteralPath $stage -Recurse -Force

Write-Output "Created: $zip"