# MongoDB 一致性实验：环境与配置指南

本文记录本仓库 `netlab-v5` 的可复现运行配置。实验 client 必须位于 Docker 网络内；host 进程只负责 Compose 生命周期、barrier、故障注入和结果检查。

## 1. 前置条件

- Docker Desktop，且 `docker info` 与 `docker compose version` 能成功返回；
- Docker 镜像：`mongo:7.0`、`python:3.11-slim`、`ghcr.io/alexei-led/pumba-alpine-nettools:latest`；
- host Python 3：`netlabv5.host` 和 `check_results.py` 只依赖标准库；
- Docker 当前用户必须能启动容器、创建网络和命名 volume。

MongoDB 固定为 `mongo:7.0`，避免 `latest` 造成的版本漂移。实验 client image 内固定安装 `pymongo==4.18.1` 与 `pytest>=7,<9`。

## 2. Docker 拓扑

`compose.yaml` 运行三个有数据、可投票的 replica-set member：

```text
mongo1  priority=2  → 正常情况下优先成为 PRIMARY
mongo2  priority=1  → 故障/切换时可成为 PRIMARY
mongo3  priority=0  → 可复制、可投票，但不会成为 PRIMARY
```

所有节点使用：

```text
mongod --replSet rs0 --bind_ip_all --oplogSize 128
```

Compose project 名由 `NETLAB_STACK` 控制，默认是 `netlab-v5`。因此网络和 volume 的名称都是 stack-scoped：

```text
${NETLAB_STACK}-network
${NETLAB_STACK}-mongo1-data
${NETLAB_STACK}-mongo2-data
${NETLAB_STACK}-mongo3-data
```

`tc-injector` 使用 `NET_ADMIN` 和 `network_mode: service:mongo1`；它仅用于受控的网络实验，不能视为生产部署的权限模板。延迟测试实际在 `mongo3` 的 network namespace 设置 `tc netem delay 100ms 20ms loss 3%`，并回读 qdisc 保存证据。

## 3. Client 配置

`compose.client.yaml` 将本仓库挂载到 `/work`，并在同一个 Compose 网络中运行：

```yaml
working_dir: /work
PYTHONPATH: /work
volumes:
  - ./:/work
```

Collector 的 replica-set URI 是：

```text
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/netlabv5?replicaSet=rs0
```

不要将 host 的 `localhost` URI 替换为此 URI；这会改变 client 的网络位置与故障可达性。

## 4. 配置矩阵

`netlabv5/matrix.py` 为每个适用模型/场景生成：

```text
RC {local, majority}
× WC {w:1, majority}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
× causal {off, on}
= 24 cells
```

Read preference 是新加入且必须报告的维度：

- `primary`：读通常服务于当前 primary；
- `primaryPreferred`：优先 primary，primary 不可达时才退回其他可选节点；
- `secondaryPreferred`：优先 secondary，是观察 replication lag 与 stale-read path 的关键配置。

同一 RC/WC 下，三种 read preference 可能让 Action 2 命中不同节点，因此不能只汇报 RC/WC。

## 5. 启动和运行

从仓库根目录运行：

```bash
export NETLAB_STACK=netlab-v5

docker build -t netlab-v5-client:latest client-image

docker run --rm -v "$PWD":/work -w /work -e PYTHONPATH=/work \
  netlab-v5-client:latest pytest tests -q
```

正常实验不需手工初始化 replica set。`netlabv5.host` 会启动容器、等待 ping、必要时执行 `rs.initiate`、等待 primary，并用 majority write concern 清空 `netlabv5` database。

```bash
# Smoke：保留三种 read preference，每个适用 experiment 为 3 cells
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario all --run-id v5-smoke-<YYYYMMDD-HHMMSS> \
  --only rc=majority,wc=majority,causal=on
python3 check_results.py artifacts-v5/v5-smoke-<YYYYMMDD-HHMMSS>

# Full：每个适用 experiment 24 cells
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario all --run-id v5-full-<YYYYMMDD-HHMMSS>
python3 check_results.py artifacts-v5/v5-full-<YYYYMMDD-HHMMSS>
```

`--only` 是逗号分隔的 `key=value` 过滤器；例如只执行 secondary-preferred 的 RYW baseline cell：

```bash
PYTHONPATH=. python3 -m netlabv5.host \
  --scenario baseline --experiment ryw \
  --only rc=majority,wc=majority,preference=secondaryPreferred,causal=on
```

## 6. 证据与清理

每个 run 的原始证据位于：

```text
artifacts-v5/<run-id>/<scenario>/<experiment>/results.json
artifacts-v5/<run-id>/<scenario>/run.json
```

`results.json` 包含操作/command/oplog 证据；`check_results.py` 从这些证据派生检查结果。不要手改 artifact 后宣称为实验结论。

保留数据的停止方式：

```bash
NETLAB_STACK=netlab-v5 docker compose -f compose.yaml down
```

删除本实验的所有 MongoDB volume：

```bash
NETLAB_STACK=netlab-v5 docker compose -f compose.yaml down -v --remove-orphans
```

后者不可恢复；`artifacts-v5/` 不会自动删除，并且已被 `.gitignore` 排除。
