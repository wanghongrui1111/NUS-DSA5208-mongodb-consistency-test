# Inconclusive (`I`) analysis

本分析从最终 36 份结果自动生成，覆盖全部 **223** 个 I。I 是缺少 checker 所需的精确 witness，不表示 H。

## Overall causes

| cause | cells | meaning |
|---|---:|---|
| `operation_error:_OperationCancelled` | 85 | PyMongo 在 server selection、连接池重建或 socket operation 期间取消操作；没有可比较 witness。 |
| `operation_error:NotPrimaryError` | 48 | 分区后的节点不再是 writable primary；这是 availability/election outcome。 |
| `operation_error:WriteConcernError` | 39 | 写已可能局部落盘，但没有满足请求的 write concern；在 P_old delay 下不能作为已确认 predecessor。 |
| `operation_error:ExecutionTimeout` | 30 | 服务器在 maxTimeMS 内未完成操作；没有可比较 witness。 |
| `operation_error:AutoReconnect` | 14 | 网络 detach/private-network 后，driver 的现有 topology/DNS path 无法连接候选 member；前驱或后继操作未完成，不能判 H/V。 |
| `operation_error:NetworkTimeout` | 4 | 连接或 socket 在配置 timeout 内没有得到回复；表示观察路径不可用。 |
| `oplog_evidence_insufficient` | 3 | WFR/MW 的 successor branch 不能同时证明 predecessor 与 successor 的 required relation。 |

## Scenario/model breakdown

### `between-partition-mongo12-vs-mongo3-client` — RYW: 12 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:ExecutionTimeout` | 12 | `rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo12-vs-mongo3-client` — MR: 12 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:ExecutionTimeout` | 12 | `rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo12-vs-mongo3-client` — WFR: 24 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:NotPrimaryError` | 24 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo12-vs-mongo3-client` — MW: 24 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:NotPrimaryError` | 24 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo1-vs-mongo23-client` — RYW: 12 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:WriteConcernError` | 12 | `rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo1-vs-mongo23-client` — MR: 6 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:ExecutionTimeout` | 3 | `rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on` |
| `operation_error:WriteConcernError` | 3 | `rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo1-vs-mongo23-client` — WFR: 18 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:WriteConcernError` | 12 | `rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
| `oplog_evidence_insufficient` | 3 | `rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off` |
| `operation_error:ExecutionTimeout` | 3 | `rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on` |
### `between-partition-mongo1-vs-mongo23-client` — MW: 12 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:WriteConcernError` | 12 | `rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `recover-partition-mongo12-vs-mongo3-client` — RYW: 24 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 24 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `recover-partition-mongo12-vs-mongo3-client` — MR: 23 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 16 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on` |
| `operation_error:NetworkTimeout` | 4 | `rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off` |
| `operation_error:AutoReconnect` | 3 | `rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `recover-partition-mongo12-vs-mongo3-client` — WFR: 19 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 16 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on` |
| `operation_error:AutoReconnect` | 3 | `rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off` |
### `recover-partition-mongo12-vs-mongo3-client` — MW: 24 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 24 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=1|pref=primary|causal=on`<br>`rc=local|wc=1|pref=primaryPreferred|causal=off`<br>`rc=local|wc=1|pref=primaryPreferred|causal=on`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=primary|causal=on`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=primary|causal=off`<br>`rc=majority|wc=1|pref=primary|causal=on`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=primary|causal=off`<br>`rc=majority|wc=majority|pref=primary|causal=on`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=primaryPreferred|causal=on`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `recover-partition-mongo1-vs-mongo23-client` — RYW: 1 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 1 | `rc=local|wc=1|pref=primary|causal=off` |
### `recover-partition-mongo1-vs-mongo23-client` — MR: 5 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 1 | `rc=local|wc=1|pref=primary|causal=off` |
| `operation_error:AutoReconnect` | 4 | `rc=local|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=local|wc=1|pref=secondaryPreferred|causal=on`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off` |
### `recover-partition-mongo1-vs-mongo23-client` — WFR: 4 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 1 | `rc=local|wc=1|pref=primary|causal=off` |
| `operation_error:AutoReconnect` | 3 | `rc=majority|wc=1|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=off`<br>`rc=majority|wc=majority|pref=secondaryPreferred|causal=on` |
### `recover-partition-mongo1-vs-mongo23-client` — MW: 3 I cells

| immediate checker reason | count | configurations |
|---|---:|---|
| `operation_error:_OperationCancelled` | 2 | `rc=local|wc=1|pref=primary|causal=off`<br>`rc=local|wc=majority|pref=secondaryPreferred|causal=on` |
| `operation_error:AutoReconnect` | 1 | `rc=local|wc=majority|pref=secondaryPreferred|causal=off` |
