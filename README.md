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

## 已实现实验（不含结果）

下表只整理当前 harness 已实现并可执行的实验设计；不陈述任何 cell 的运行结果或一致性结论。

| 场景 | 故障与时序 | 覆盖模型 | 要检验的路径 |
|---|---|---|---|
| `baseline` | 无故障，健康三节点副本集 | RYW、MR、MW、WFR | 各 concern、read preference 与 causal session 组合的健康基线 |
| `partition-ryw-mr` | 在两次被测操作之间隔离 `{mongo1,mongo2}` 与 `{mongo3,labclient}` | RYW、MR | client 被移入可能落后的 `mongo3` 一侧后的读路径 |
| `stop-mongo3` | Action 1 后停止 `mongo3`，Action 2 前维持停止状态 | RYW、MR、MW、WFR | 少一个 secondary 时的路由、确认与 session 依赖行为 |
| `recover-delay` | Action 1 前对 `mongo3` 注入 `100ms ±20ms` 延迟和 `3%` 丢包；Action 2 前恢复 | RYW、MR、MW、WFR | 复制落后恢复后，后续操作是否满足前序依赖 |
| `recover-partition-mongo12-vs-mongo3-client` | Action 1 前隔离 `{mongo1,mongo2}` 与 `{mongo3,labclient}`；Action 2 前恢复 | RYW、MR、MW、WFR | 多数派侧与落后副本/client 侧重新连通后的行为 |
| `recover-partition-mongo1` | Action 1 前隔离 `mongo1`；Action 2 前恢复 | RYW、MR、MW、WFR | 单节点 primary-candidate 隔离和恢复 |
| `recover-partition-mongo2` | Action 1 前隔离 `mongo2`；Action 2 前恢复 | RYW、MR、MW、WFR | 单个 secondary 隔离和恢复 |
| `recover-partition-mongo3` | Action 1 前隔离 `mongo3`；Action 2 前恢复 | RYW、MR、MW、WFR | 被 `secondaryPreferred` 优先选择的 secondary 隔离和恢复 |
| `recover-partition-client` | Action 1 前隔离 `labclient`；Action 2 前恢复 | RYW、MR、MW、WFR | client 与整个 replica set 失联后恢复 |

所有适用的场景/模型组合都在同一 24-cell 配置矩阵下执行。对于包含故障的场景，host runner 使用 barrier 在规定时点安装或恢复故障，并将故障事件、操作记录和必要的 oplog snapshot 写入 artifact；这些 artifact 是后续独立分析的输入，不是本 README 的结果部分。

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
