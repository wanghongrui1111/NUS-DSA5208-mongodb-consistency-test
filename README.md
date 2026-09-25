# NUS DSA5208 MongoDB Consistency Test

Docker-based MongoDB replica-set laboratory for the final v5 consistency matrix. The harness records command routing, session state, seed convergence, fault lifecycle, and oplog evidence before deriving each verdict.

## Final experiment design

Every applicable scenario × consistency model executes this 24-cell matrix:

```text
ReadConcern      {local, majority}
× WriteConcern   {w:1, majority}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
× causal session {off, on}
= 24 cells
```

Every cell first writes a setup-only `seed` with `w:majority`, then directly verifies that mongo1, mongo2, and mongo3 all hold the same exact `seed write_id`. Action 1 begins only after that convergence check passes.

Models:

- RYW — `W1 → R1`
- MR — `R1 → R2`
- WFR — `R1 → W1`; the successor primary's immediate post-ACK oplog branch is evidence.
- MW — `W1 → W2`; the successor primary's immediate post-ACK oplog branch is evidence.

## Final scenarios

| Scenario | Fault choreography | Models |
|---|---|---|
| `baseline` | healthy replica set | all four |
| `between-delay` | Action 1 → mongo3 `tc netem` (`100ms ±20ms`, `3%` loss) → Action 2 → clear | all four |
| `between-partition-mongo12-vs-mongo3-client` | seed convergence → mongo1→mongo3 and mongo2→mongo3 P_old 60s delay → Action 1 → `{mongo1,mongo2}` / `{mongo3,client}` partition → Action 2 → heal | all four |
| `between-partition-mongo1-vs-mongo23-client` | seed convergence → mongo1→mongo2,mongo3 P_old 60s delay → Action 1 → `{mongo1}` / `{mongo2,mongo3,client}` partition → Action 2 → heal | all four |
| `between-stop-mongo3` | Action 1 → stop mongo3 → Action 2 → restart | all four |
| `recover-delay` | mongo3 delay → Action 1 → clear → Action 2 | all four |
| `recover-partition-mongo12-vs-mongo3-client` | plain partition before Action 1 → heal → Action 2 | all four |
| `recover-partition-mongo1-vs-mongo23-client` | plain partition before Action 1 → heal → Action 2 | all four |
| `recover-stop-mongo3` | stop mongo3 before Action 1 → restart → Action 2 | all four |

The two **between-partition** scenarios retain P_old pre-delay. The two **recover-partition** scenarios deliberately use plain Docker network partitions without P_old delay.

Faults are Docker-native: directional delay uses `tc` in network-namespace sidecars; partitions use Docker network detach/private-network moves; node failure uses Docker stop/start. Every cell clears its fault before the next cell; P_old cells also verify qdisc removal and mongo1 primary restoration.

## Run

Prerequisites: Docker Desktop with `docker compose`, Python 3, and the repository virtual environment.

```bash
# From netlab-v5/
PYTHONPATH=. ../.venv/bin/python -m pytest tests -q

# One selected cell per scenario/model; optional smoke only.
./run-parallel.sh v5-smoke rc=local,wc=1,preference=primary,causal=off

# Final full matrix: no --only filter.
./run-parallel.sh v5-full-<run-id>
```

`run-parallel.sh` runs RYW, MR, WFR, and MW in four isolated Compose projects. A full run emits 36 `results.json` files and 864 checked cells. The launcher invokes `check_results.py` for each model when collection completes.

## Result bundle

[`result/`](result/) contains the final validated full-run handoff:

- `REPORT.md` — per-scenario/model 24-cell verdict tables.
- `INCONCLUSIVE_ANALYSIS.md` — all final-run inconclusive cells, classified by immediate evidence failure.
- `V4_TO_V5_WFR_POLD_CHANGE.md` — why four v4 WFR P_old violations are v5 inconclusive.
- `artifacts/` — copied raw `results.json`, `run.json`, and delay evidence for the 864-cell run.
- `results-summary.json` and `MANIFEST.json` — aggregate counts and SHA-256 inventory.

## Layout

```text
├── compose.yaml                 # MongoDB 7.0 nodes and tc namespace sidecars
├── compose.client.yaml          # in-network collector
├── netlabv5/
│   ├── matrix.py                # 24-cell configuration space
│   ├── client.py                # seed, workload, routing, and oplog capture
│   ├── host.py                  # lifecycle, barriers, tc, partitions, cleanup
│   └── judge.py                 # evidence-based verdicts
├── probes/                      # test-only stale-precondition probes
├── tests/
├── result/                      # final full-run result handoff
└── run-parallel.sh              # four-stack smoke/full runner
```
