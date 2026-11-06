#!/usr/bin/env bash
# Reproduces the R0 synthetic baseline. All datasets share ONE environment (env-seed 11); only noise/faults differ.
set -euo pipefail
export PYTHONWARNINGS=ignore
R=${1:-runs}; mkdir -p "$R"
dce simulate --out $R/train          --seed 11 --env-seed 11 --duration 40000
dce simulate --out $R/heldout_seed   --seed 12 --env-seed 11 --duration 30000
dce simulate --out $R/heldout_sparse --seed 21 --env-seed 11 --duration 100000 --mean-gap 2500 --p-concurrent 0
dce simulate --out $R/heldout_load   --seed 13 --env-seed 11 --duration 30000 --load-scale 1.5
dce simulate --out $R/missing        --seed 15 --env-seed 11 --duration 30000 --missing-rate 0.03
dce simulate --out $R/faultfree      --seed 14 --env-seed 11 --duration 30000 --no-faults
dce train --data $R/train --out $R/bundle --seed 0
dce eval --bundle $R/bundle --data $R/train \
  --heldout $R/heldout_sparse $R/heldout_seed $R/heldout_load $R/missing \
  --faultfree $R/faultfree --out $R/report.json
