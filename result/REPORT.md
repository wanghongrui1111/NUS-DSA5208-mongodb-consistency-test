# MongoDB v5 full experiment report

## 1. 范围与完整性

本文件记录最终 v5 全量运行 `v5-dual-pold-full-20260925-r2`。四个 model 使用彼此隔离的 Compose stack；每个 scenario-model 有 24 cells：`RC {local, majority} × WC {w:1, majority} × RP {primary, primaryPreferred, secondaryPreferred} × causal {off,on}`。

程序化核验：36 个 `results.json`、864 个唯一 checked cells；每 cell 的三节点 exact seed ID 收敛。P_old cell 另含 qdisc install/remove evidence。总计 H=574，V=67，I=223。

## 2. 判定口径与限制

H=holds，V=violated，I=inconclusive。RYW/MR 比较操作返回值；WFR/MW 使用 Action2 successor ACK 后、heal 前捕获的实际 serving primary `local.oplog.rs` branch。I 表示缺少 required witness，不等于 H。`majority` read concern 提供 rollback-safe snapshot，并不单独承诺 freshness。

图例：每格依次列 `primary`、`primaryPreferred`、`secondaryPreferred`。

## baseline

**故障流程：** 无故障。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=21，V=3，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

## between-delay

**故障流程：** Action 1 后，在 mongo3 安装 100 ms delay、20 ms jitter、3% loss；Action 2 后清除规则。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

## between-partition-mongo12-vs-mongo3-client

**故障流程：** P_old：seed 收敛后，对 mongo1→mongo3 与 mongo2→mongo3 安装 60 s directional delay；Action 1 后分区 `{mongo1,mongo2}` 与 `{mongo3,labclient}`；Action 2 后 heal。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=0，V=12，I=12。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=3，V=9，I=12。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=0，V=0，I=24。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=0，V=0，I=24。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

## between-partition-mongo1-vs-mongo23-client

**故障流程：** P_old：seed 收敛后，对 mongo1→mongo2,mongo3 安装 60 s directional delay；Action 1 后分区 `{mongo1}` 与 `{mongo2,mongo3,labclient}`；Action 2 后 heal。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=0，V=12，I=12。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=6，V=12，I=6。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=0，V=6，I=18。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=0，V=12，I=12。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:V<br>primaryPreferred:V<br>secondaryPreferred:V | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

## between-stop-mongo3

**故障流程：** Action 1 后停止 mongo3，Action 2 后恢复。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

## recover-delay

**故障流程：** Action 1 前在 mongo3 安装 100 ms delay、20 ms jitter、3% loss；Action 2 前清除规则。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

## recover-partition-mongo12-vs-mongo3-client

**故障流程：** 普通 partition recovery：Action 1 前分区 `{mongo1,mongo2}` 与 `{mongo3,labclient}`；Action 2 前 heal；不包含 P_old pre-delay。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=0，V=0，I=24。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=1，V=0，I=23。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=5，V=0，I=19。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=0，V=0，I=24。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |
| majority | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I | primary:I<br>primaryPreferred:I<br>secondaryPreferred:I |

## recover-partition-mongo1-vs-mongo23-client

**故障流程：** 普通 partition recovery：Action 1 前分区 `{mongo1}` 与 `{mongo2,mongo3,labclient}`；Action 2 前 heal；不包含 P_old pre-delay。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=22，V=1，I=1。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:V |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=19，V=0，I=5。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:H<br>secondaryPreferred:I | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=20，V=0，I=4。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=21，V=0，I=3。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:I<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:I |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

## recover-stop-mongo3

**故障流程：** Action 1 前停止 mongo3；Action 2 前恢复。

### RYW — `W1 → R1`

来源：`v5-dual-pold-full-20260925-r2-ryw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MR — `R1 → R2`

来源：`v5-dual-pold-full-20260925-r2-mr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### WFR — `R1 → W1`

来源：`v5-dual-pold-full-20260925-r2-wfr`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

### MW — `W1 → W2`

来源：`v5-dual-pold-full-20260925-r2-mw`；24 cells；H=24，V=0，I=0。

**causal=off**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |

**causal=on**

| RC \ WC | w:1 | majority |
|---|---|---|
| local | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
| majority | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H | primary:H<br>primaryPreferred:H<br>secondaryPreferred:H |
