# NUS DSA5208 MongoDB Consistency Test

A Docker-based MongoDB replica-set laboratory for observing client-centric consistency behavior under controlled faults. The harness collects raw command, session, and oplog evidence before deriving a per-cell result; Docker state alone never determines a consistency verdict.

## Configuration matrix

Every applicable scenario exercises the 24-cell matrix:

```text
ReadConcern     {local, majority}
× WriteConcern  {w:1, majority}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
× causal session {off, on}
= 24 cells per experiment
```

Read preference is an explicit experimental dimension. `secondaryPreferred` is the key path for observing a lagging secondary; `primaryPreferred` falls back away from the primary only when necessary; `primary` normally routes reads to the elected primary.

## Scenarios and models

Models: RYW (read-your-writes), MR (monotonic reads), MW (monotonic writes), and WFR (writes-follow-reads).

1. `baseline` — healthy three-node replica set; all four models.
2. `partition-ryw-mr` — partition `{mongo1,mongo2}` from `{mongo3,labclient}` between actions; RYW and MR.
3. `stop-mongo3` — stop `mongo3` between actions; all four models.
4. `recover-delay` — install delay/loss before action 1, recover before action 2.
5. `recover-partition-mongo12-vs-mongo3-client` — recover a two-group partition before action 2.
6. `recover-partition-mongo1`, `recover-partition-mongo2`, `recover-partition-mongo3`, and `recover-partition-client` — recover the named isolated endpoint before action 2.

Each scenario begins from a healthy reset. Cleanup restores stopped nodes, network endpoints, and delay rules even when a collector fails.

## Quick start

Prerequisites: Docker Desktop with `docker compose`, plus Python 3 on the host for orchestration and result checking.

```bash
# From this repository root
export NETLAB_STACK=netlab-v5

# Build the in-network PyMongo client image
 docker build -t netlab-v5-client:latest client-image

# Run the unit tests inside that image
 docker run --rm -v "$PWD":/work -w /work -e PYTHONPATH=/work \
   netlab-v5-client:latest pytest tests -q

# Smoke: three preferences × one RC/WC/causal combination for every scenario
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario all \
  --run-id v5-smoke-<YYYYMMDD-HHMMSS> \
  --only rc=majority,wc=majority,causal=on
python3 check_results.py artifacts-v5/v5-smoke-<YYYYMMDD-HHMMSS>

# Full matrix
PYTHONPATH=. python3 -m netlabv5.host --scenario all --run-id v5-full-<YYYYMMDD-HHMMSS>
python3 check_results.py artifacts-v5/v5-full-<YYYYMMDD-HHMMSS>
```

`--only` is a comma-separated filter. For example:

```bash
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario baseline --experiment ryw \
  --only rc=majority,wc=majority,preference=secondaryPreferred,causal=on
```

Generated evidence is written below `artifacts-v5/<run-id>/` and is ignored by Git.

## Repository layout

```text
├── compose.yaml                 # Three MongoDB 7.0 members and tc helper
├── compose.client.yaml          # In-network labclient configuration
├── client-image/Dockerfile      # Python 3.11 + pinned PyMongo client
├── netlabv5/
│   ├── matrix.py                # 24-cell RC × WC × preference × causal space
│   ├── client.py                # Workload, command monitoring, session evidence
│   ├── host.py                  # Compose lifecycle, barriers, faults, cleanup
│   └── judge.py                 # Evidence-based per-model check
├── tests/                       # Unit tests
├── docs/
│   ├── ENVIRONMENT-SETUP-ZH.md
│   └── CONSISTENCY-MECHANISMS-ZH.md
└── check_results.py             # Artifact integrity and derived-result checker
```

See [环境与配置指南](docs/ENVIRONMENT-SETUP-ZH.md) for the runtime topology and [MongoDB 一致性机制与判读边界](docs/CONSISTENCY-MECHANISMS-ZH.md) for the meaning and limitations of RC, WC, read preference, causal sessions, failover, and oplog evidence.
