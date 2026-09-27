# MongoDB Consistency Experiments: Environment and Configuration Guide

This document describes the reproducible runtime configuration for the `netlab-v5` repository. Experiment clients must run inside the Docker network; host processes are responsible only for the Compose lifecycle, barriers, fault injection, and result validation.

## 1. Prerequisites

- Docker Desktop, with both `docker info` and `docker compose version` completing successfully;
- Docker images: `mongo:7.0`, `python:3.11-slim`, and `ghcr.io/alexei-led/pumba-alpine-nettools:latest`;
- Python 3 on the host: `netlabv5.host` and `check_results.py` depend only on the standard library;
- The current Docker user must be able to start containers and create networks and named volumes.

MongoDB is pinned to `mongo:7.0` to avoid version drift caused by `latest`. The experiment client image pins `pymongo==4.18.1` and installs `pytest>=7,<9`.

## 2. Docker Topology

`compose.yaml` runs three data-bearing, voting replica-set members:

```text
mongo1  priority=2  → preferred as PRIMARY under normal conditions
mongo2  priority=1  → can become PRIMARY during failures or failovers
mongo3  priority=0  → can replicate and vote, but cannot become PRIMARY
```

All nodes use:

```text
mongod --replSet rs0 --bind_ip_all --oplogSize 128
```

The Compose project name is controlled by `NETLAB_STACK` and defaults to `netlab-v5`. Network and volume names are therefore stack-scoped:

```text
${NETLAB_STACK}-network
${NETLAB_STACK}-mongo1-data
${NETLAB_STACK}-mongo2-data
${NETLAB_STACK}-mongo3-data
```

`tc-injector` uses `NET_ADMIN` and `network_mode: service:mongo1`; it is intended only for controlled network experiments and must not be treated as a permissions template for production deployments. The latency test applies `tc netem delay 100ms 20ms loss 3%` in the `mongo3` network namespace, then reads back the qdisc configuration and saves it as evidence.

## 3. Client Configuration

`compose.client.yaml` mounts this repository at `/work` and runs on the same Compose network:

```yaml
working_dir: /work
PYTHONPATH: /work
volumes:
  - ./:/work
```

The collector's replica-set URI is:

```text
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/netlabv5?replicaSet=rs0
```

Do not replace this URI with a host `localhost` URI; doing so changes the client's network location and its exposure to injected faults.

## 4. Configuration Matrix

`netlabv5/matrix.py` generates the following matrix for each applicable model/scenario:

```text
RC {local, majority}
× WC {w:1, majority}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
× causal {off, on}
= 24 cells
```

Read preference is a newly added dimension and must be included in reports:

- `primary`: reads are normally served by the current primary;
- `primaryPreferred`: prefers the primary and falls back to another eligible node only when the primary is unavailable;
- `secondaryPreferred`: prefers a secondary and is the key configuration for observing replication lag and stale-read paths.

For the same RC/WC settings, the three read preferences may cause Action 2 to reach different nodes. Reporting only RC/WC is therefore insufficient.

## 5. Starting and Running the Experiments

Run the following from the repository root:

```bash
export NETLAB_STACK=netlab-v5

docker build -t netlab-v5-client:latest client-image

docker run --rm -v "$PWD":/work -w /work -e PYTHONPATH=/work \
  netlab-v5-client:latest pytest tests -q
```

Normal experiment runs do not require manual replica-set initialization. `netlabv5.host` starts the containers, waits for ping responses, runs `rs.initiate` if necessary, waits for a primary, and clears the `netlabv5` database using majority write concern.

```bash
# Smoke: retain all three read preferences, producing 3 cells per applicable experiment
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario all --run-id v5-smoke-<YYYYMMDD-HHMMSS> \
  --only rc=majority,wc=majority,causal=on
python3 check_results.py artifacts-v5/v5-smoke-<YYYYMMDD-HHMMSS>

# Full: 24 cells per applicable experiment
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario all --run-id v5-full-<YYYYMMDD-HHMMSS>
python3 check_results.py artifacts-v5/v5-full-<YYYYMMDD-HHMMSS>
```

`--only` accepts comma-separated `key=value` filters. For example, to run only the secondary-preferred RYW baseline cell:

```bash
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario baseline --experiment ryw \
  --only rc=majority,wc=majority,preference=secondaryPreferred,causal=on
```

## 6. Evidence and Cleanup

The raw evidence for each run is stored at:

```text
artifacts-v5/<run-id>/<scenario>/<experiment>/results.json
artifacts-v5/<run-id>/<scenario>/run.json
```

`results.json` contains operation, command, and oplog evidence; `check_results.py` derives validation results from this evidence. Do not manually edit an artifact and present it as an experimental result.

To stop the environment while preserving its data:

```bash
NETLAB_STACK=netlab-v5 docker compose -f compose.yaml down
```

To delete all MongoDB volumes for this experiment:

```bash
NETLAB_STACK=netlab-v5 docker compose -f compose.yaml down -v --remove-orphans
```

The latter operation is irreversible. `artifacts-v5/` is not deleted automatically and is excluded by `.gitignore`.
