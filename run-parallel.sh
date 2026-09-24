#!/usr/bin/env bash
set -euo pipefail

# One isolated Compose stack per model: faults, resets, networks, volumes, and
# artifacts cannot interfere across RYW/MR/WFR/MW.
run_id="${1:?run id required}"
only="${2:-rc=majority,wc=majority,preference=primaryPreferred,causal=on}"

mkdir -p artifacts-v5/logs
printf '%s\n' ryw mr wfr mw | xargs -n1 -P4 -I{} bash -c '
  model="$1"
  args=(--scenario all --run-id "'$run_id'-${model}" --experiment "$model" --only "'$only'")
  NETLAB_STACK="v5-${model}" PYTHONPATH=netlab-v5 .venv/bin/python -m netlabv5.host "${args[@]}" \
    >"artifacts-v5/logs/'$run_id'-${model}.log" 2>&1
' _ {}

python3 netlab-v5/check_results.py artifacts-v5/"$run_id"-ryw
python3 netlab-v5/check_results.py artifacts-v5/"$run_id"-mr
python3 netlab-v5/check_results.py artifacts-v5/"$run_id"-wfr
python3 netlab-v5/check_results.py artifacts-v5/"$run_id"-mw
