$ErrorActionPreference = 'Stop'

$slangDir = 'H:\Gamedev\HDG\vendor\tools\slang'
$exe = Join-Path $slangDir 'slangc.exe'

if (-not (Test-Path $exe)) {
    Write-Error "slangc.exe not found at: $exe"
    exit 1
}

& $exe @args

exit $LASTEXITCODE