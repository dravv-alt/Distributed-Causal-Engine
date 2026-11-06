<#!
.SYNOPSIS
Runs the frozen E001-R001 reproduction of the delivered R0 synthetic baseline.

.DESCRIPTION
This is intentionally an explicit PowerShell equivalent of
dce-r0/dce/scripts/reproduce_r0_baseline.sh.  It writes only below the supplied
run directory and does not modify the delivered R0 source or prior baseline
report.  Invoke it from the repository root.
#>
[CmdletBinding()]
param(
    [string]$RunDirectory = "experiments/E001/results/E001-R001"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = Join-Path $repoRoot "dce-r0/dce"
$out = Join-Path $repoRoot $RunDirectory

New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $sourceRoot
try {
    $env:PYTHONPATH = "src"
    $env:PYTHONWARNINGS = "ignore"

    python -m dce.cli simulate --out $out/train --seed 11 --env-seed 11 --duration 40000
    python -m dce.cli simulate --out $out/heldout_seed --seed 12 --env-seed 11 --duration 30000
    python -m dce.cli simulate --out $out/heldout_sparse --seed 21 --env-seed 11 --duration 100000 --mean-gap 2500 --p-concurrent 0
    python -m dce.cli simulate --out $out/heldout_load --seed 13 --env-seed 11 --duration 30000 --load-scale 1.5
    python -m dce.cli simulate --out $out/missing --seed 15 --env-seed 11 --duration 30000 --missing-rate 0.03
    python -m dce.cli simulate --out $out/faultfree --seed 14 --env-seed 11 --duration 30000 --no-faults
    python -m dce.cli train --data $out/train --out $out/bundle --seed 0
    python -m dce.cli eval --bundle $out/bundle --data $out/train --heldout $out/heldout_sparse $out/heldout_seed $out/heldout_load $out/missing --faultfree $out/faultfree --out $out/report.json
}
finally {
    Pop-Location
}
