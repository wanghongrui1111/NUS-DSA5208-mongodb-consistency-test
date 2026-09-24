# netlab v5

A compact MongoDB session-guarantee lab. Every scenario uses the same eight-cell matrix:

`RC {local, majority} × WC {w:1, majority} × causal {off, on}`.

The collector writes raw operation/command/oplog evidence to `results.json`, then derives the per-cell `check` from that evidence. Docker orchestration never assigns a consistency outcome.

## Ordered scenarios

1. `baseline`: no fault; all RYW, MR, WFR, MW cells.
2. `partition-ryw-mr`: partition `{mongo1,mongo2}` from `{mongo3,labclient}` between actions; RYW and MR only.
3. `stop-mongo3`: stop `mongo3` after action 1 and run action 2; all four models.
4. Recovery scenarios: install the fault before action 1, recover it after action 1, then run action 2. They cover `delay`, `{mongo1,mongo2}` vs `{mongo3,client}`, and single-node/client partitions.

A scenario resets data while healthy. It restores a stopped node, netem process, and network endpoints in `finally` cleanup.

## Commands

```bash
# Unit tests
PYTHONPATH=netlab-v5 .venv/bin/python -m pytest netlab-v5/tests -q

# One-cell smoke for every scenario
PYTHONPATH=netlab-v5 .venv/bin/python -m netlabv5.host --scenario all --run-id v5-smoke \
  --only rc=majority,wc=majority,causal=on

# Full ordered suite (8 cells per selected experiment)
PYTHONPATH=netlab-v5 .venv/bin/python -m netlabv5.host --scenario all --run-id v5-full
python3 netlab-v5/check_results.py artifacts-v5/v5-full
```

## Scope and limitations

The replica set runs as three Docker containers on one host. Partitions are Docker endpoint moves; delay is Pumba netem on `mongo3`. These are reproducible traffic and membership faults, not physical-failure claims.
