# MongoDB 一致性实验：关键机制与判读边界

> **用途**：说明本项目测试 MongoDB client-centric consistency 时真正被测的机制、故障如何构造出可观察差异，以及哪些现象不能被误写成 MongoDB 违反官方保证。
>
> **范围**：三节点 replica set（`mongo1`、`mongo2`、`mongo3`）上的 RYW、MR、MW、WFR 实验，以及 netlab-v5 的简化配置空间。
>
> **配套材料**：[环境与配置指南](ENVIRONMENT-SETUP-ZH.md)、[MongoDB 官方 causal consistency 文档](https://www.mongodb.com/docs/manual/core/causal-consistency-read-write-concerns/)。

---

## 1. 先分清三个层次

### 1.1 客户端一致性不是全局线性一致性

本实验的四个模型约束的是**同一客户端（或同一会话）前后操作的观察/因果顺序**，而不是要求所有客户端实时看到同一个全局状态。

| 模型 | 约束的操作关系 | 客户端应得到的语义 |
|---|---|---|
| RYW（read-your-writes） | $W_1 \rightarrow R_1$ | 自己写后再读，不能倒退到写前版本 |
| MR（monotonic reads） | $R_1 \rightarrow R_2$ | 后一次读不能比前一次读到更旧的版本 |
| MW（monotonic writes） | $W_1 \rightarrow W_2$ | 后写必须在前写之后的历史分支上发生 |
| WFR（writes-follow-reads） | $R_1 \rightarrow W_2$ | 后写必须建立在先前读到状态或其后继状态上 |

这里的“后继”是**历史/因果顺序**，不只是最终 document 的字段值看起来一样。

### 1.2 MongoDB 的机制保证与实验 harness 判定不同

实验结果中的 `violated` 意味着：harness 已找到一条操作关系或 oplog branch witness，显示被测关系没有成立。

这**不自动等价于**“MongoDB 违反官方保证”。还必须逐格检查：

1. 使用的是不是同一显式、causally consistent session；
2. read concern / write concern 是否满足官方保证矩阵；
3. 读写是否实际成功、是否可从故障侧获得足够证据；
4. 此 cell 是否是特意测试弱配置（此时出现旧读或不可用常是预期行为）。

因此三个判定状态应严格区分：

- `holds`：当前原始证据支持关系成立；
- `violated`：当前原始证据提供关系断裂 witness；
- `inconclusive`：超时、错误、未确认写、没有可审计 oplog 等，**不能算作 holds**。

### 1.3 文档值正确不等于因果历史正确

当前 MW/WFR 的 successor 常采用 blind `$set`，以便隔离数据库历史机制。例如在新主上直接写入 `v=8`，即使新主没有旧主上的 `v=7`，最终文档也可能恰好为预期值。

```text
旧分支：C0 → seed(v=7) → R1
新分支：C0 → successor($set v=8)
```

最终 `$set v=8` 可以“看起来正确”，但 successor 的前态是 `C0` 而非 `C1=v=7`。这仍是 WFR/MW 所关心的 history gap。若要展示业务后果，应另加 CAS、revision、库存扣减等 read-dependent 控制 workload；不要把当前 blind-write 实验夸大为已证明业务数据必错。

---

## 2. Replica set 中决定现象的四类状态

### 2.1 节点本地已应用状态（local state）

`readConcern: "local"` 读取的是某个节点已经应用的本地数据。它可以包含尚未进入多数派历史的写，因此可能暴露未来被 rollback 的写。

典型实验：停止两个 secondary 后，在旧 primary 做 `w:1` 写入 `v=2`。

```text
旧 primary local     → v=2
旧 primary majority  → v=0
旧 primary 随后失去主地位并回归 → v=2 被 rollback
```

**测试含义**：`local` 的新鲜度不等于持久性，也不等于 failover 后仍在权威历史中。

### 2.2 节点 local majority snapshot

`readConcern: "majority"` 只返回该节点认为已安全的 majority-committed snapshot。它不会暴露未进入 majority history 的 rollback branch，但不同节点不必同时安装到同一最新 snapshot。

例如 `mongo1 + mongo2` 已确认 `w:"majority"` 写、`mongo3` 仍有 apply delay 时：

```text
mongo1 majority → version 1
mongo2 majority → version 1
mongo3 majority → version 0
```

**测试含义**：多数派写 ACK 不意味着每个 secondary 已经能读到该写；普通 secondary majority read 也不承诺立即追到全局最新 majority write。

### 2.3 replica set 全局 majority commit point

global majority commit point 表示某个 oplog entry 已被多数投票节点持久确认。它决定某次写何时可被视为进入 majority history，但不能直接推出所有成员已经应用、也不能替代客户端因果依赖。

必须避免写成：

```text
w:majority 成功 ⇒ 所有节点都有最新值
```

正确表述是：

```text
w:majority 成功 ⇒ 该写已得到足够多数确认；落后 secondary 的可见快照仍可能较旧。
```

### 2.4 分叉历史、选主与 rollback

当旧 primary 与其余多数派隔离时，旧 primary 可暂时保有仅存在于自己分支的写。`mongo2,mongo3` 选出新 primary 后，旧分支缺失的写最终可能 rollback。

这正是 MW/WFR 测试的核心：不是“分区期间一定发生了额外更新”，而是 client 先在旧分支观察/写入，再把后续操作送到尚停留在旧前态的新分支。

---

## 3. RC、WC、read preference 与 causal session 各自负责什么

### 3.1 Read concern（RC）控制读允许看到什么

本项目后续统一的简化空间为：

```text
RC ∈ {local, majority}
```

- `local`：可读节点本地已应用状态，低延迟但可见未多数派提交内容；
- `majority`：只读该节点的 majority-committed snapshot，避免读取可 rollback 分支，但可能等待或返回较旧的安全 snapshot。

### 3.2 Write concern（WC）控制写成功的确认门槛

后续简化空间为：

```text
WC ∈ {w:1, majority}
```

- `w:1`：primary 已接受/写入即可 ACK；故障后有可能不在新多数派历史中；
- `w:"majority"`：需要多数派确认，写进入 majority history 的强度更高，但不保证每个节点即时可读。

### 3.3 Read preference 决定读实际在哪个副本执行

后续 v5 对每个 cell 真正传入：

```text
{primary, primaryPreferred, secondaryPreferred}
```

它不改变 RC/WC 的语义，却决定是否有机会命中落后或隔离的 secondary：

- `primary`：读通常落在当前主；
- `primaryPreferred`：优先主，主不可达时才转向其他可选节点；
- `secondaryPreferred`：优先 secondary，是暴露复制延迟和 stale-read path 的关键配置。

因此不能只报 RC/WC；同一个 RC/WC 下读偏好不同，现象可能完全不同。

### 3.4 causal session 是跨操作携带依赖的机制

对于可确认写，实验的两项**被测操作**使用同一个显式 `ClientSession`。当 `causal_consistency=True` 时，driver 维护 session 的 `clusterTime` / `operationTime`，后续 read 会带上类似 `afterClusterTime` 的下界：服务器不能在早于该依赖的快照上返回结果。

直觉上它相当于逻辑时间依赖，而不是应用程序手写 Lamport clock：

```text
W1 / R1 产生或观察到时间 T
→ session 记住 T
→ 后续 R2 / W2 至少要与 T 因果兼容
```

重要边界：

- **同一个 session ≠ 自动 causal consistency**。`causal=off` 仍可复用 session object，但不要求 driver 维护上述因果读下界；
- `w:0` 无 acknowledged write，本项目不为其建立 session，也不生成 `w:0 + causal=on` cell；
- MR/WFR 的 setup seed 是构造初始状态的 session 外操作，不能描述成“所有数据库操作都在同一 session 内”。

### 3.5 官方四保证矩阵的最小对照

在 causally consistent session 下，MongoDB 文档给出的常用核心组合为：

| RC | WC | RYW | MR | MW | WFR |
|---|---|---:|---:|---:|---:|
| `majority` | `majority` | ✅ | ✅ | ✅ | ✅ |
| `majority` | `w:1` | — | ✅ | — | ✅ |
| `local` | `majority` | — | — | ✅ | — |
| `local` | `w:1` | — | — | — | — |

这里的 “—” 不是实验一定失败，而是官方不承诺该项保证。`available` 也不能用于 causally consistent session；它属于历史 v4 的大矩阵，不属于 v5 的简化空间。

---

## 4. 四种 consistency model 在本实验中的真实时序

### 4.1 RYW：写后不能被路由到更旧副本

```text
W1（通常在 primary） → R1（可能经 read preference 到 secondary）
```

故障/延迟制造的风险路径：

```text
W1 已被 primary ACK
→ target secondary 尚未复制 W1
→ R1 被送到 target secondary
→ 返回写前版本
```

- `causal=on` 时，session 对后续 read 施加时间下界；若目标节点不能满足，正确现象通常是等待、超时或不可用，而不是返回违反依赖的旧值；
- `causal=off` 或弱 concern 下，旧读是可观察且预期的候选结果。

### 4.2 MR：后读不能比先读更旧

```text
R1（较新节点） → R2（较落后节点）
```

MR 不需要 client 自己写。实验首先构造一个较新 seed；R1 命中含 seed 的节点，R2 再被路由到不含 seed 的节点。

```text
R1 sees v=1
R2 sees v=0
```

这才是 MR witness。若 R2 超时或 target 不可读，只能记为 `inconclusive`，不能记为 MR 成立。

### 4.3 MW：新主不能接受脱离前写历史的后写

语义时序：

```text
W1 on P_old → partition / failover → W2 on P_new
```

机制关键在于让 `W1` 不能在 detach 前抢先复制到新多数派。v4 的做法是在 **Action 1 前**，先对 `mongo1 → mongo2,mongo3` 加定向长延迟；确认 qdisc 生效后才允许 W1。然后 detach `mongo1`，让 `mongo2,mongo3` 形成新多数派并选主，最后在 P_new 写 W2。

若 P_new 在 W2 成功时的 oplog 有 W2、却没有 W1，则 W2 属于一个不含 W1 的 branch，构成 MW history witness。

### 4.4 WFR：读到旧主状态后，后写不能落到更早分支

WFR 有 **三个语义 action**，不能误读为只有 “read 后 write”：

```text
S（source seed write） → R1 → W2（successor write）
```

当前 artifact 名称是：

| 语义 | 记录名 | 执行位置 |
|---|---|---|
| source seed | `seed` | `mongo1` / P_old |
| read | `read1` | `mongo1` / P_old |
| successor write | `write1` | `mongo2` / P_new |

完整 choreography：

```text
预先启用 mongo1 → mongo2,mongo3 的 netem delay
→ S 写到 P_old
→ R1 在 P_old 确认读到本轮 S
→ detach mongo1
→ mongo2,mongo3 选出 P_new
→ W2 在 P_new 成功
→ 在 heal 前立即抓取 P_new 的 local.oplog.rs
```

若 oplog 显示：

```text
P_new contains W2
P_new does not contain S
```

则 W2 执行的前态不是 R1 所读的状态或其后继。这里不需要 R1 与 W2 之间发生额外同步或写入；**“没有同步”恰恰使 P_new 仍停留在 `C0`，从而形成 WFR 断裂。**

---

## 5. 故障注入如何对应机制假设

### 5.1 延迟 / 丢包：制造复制落后，不等于物理隔离

后续 delay 的目标参数为：

```text
target=mongo3; delay=100 ms; jitter=20 ms; loss=3%
```

实现改为直接在目标网络 namespace 中用 `tc netem` 设置 qdisc，并读回 qdisc 作为证据；这避免短生命周期 client 容器下 Pumba 容器枚举不稳定的问题。

它适合测试：复制/网络变慢时 secondary 的 local 或 majority snapshot 何时落后、causal read 是否等待。

### 5.2 endpoint / client partition：强制 Action 2 落到 stale side

RYW/MR 的历史 v3 endpoint partition 做法是：

1. 先以 `w:3` 初始化 `v=0`；
2. 将 `mongo3` detach 到私有网络；
3. Action 1 在 `mongo1,mongo2` 多数派执行；
4. client 通过 barrier 进入私有网络，Action 2 direct-connect 到 `mongo3`；
5. 每格恢复 endpoint。

这不是模拟“普通 driver 自动选路”的唯一形式，而是有意强制制造单节点 stale path，检验 RC/WC/session 能否在该路径下维持关系或正确地变为不可用。

### 5.3 P_old / P_new partition：制造历史分支，不只是读到旧值

MW/WFR 的 v4 分区不是把 `mongo3` 单独隔离，而是把旧主 `mongo1` 与新多数派 `mongo2,mongo3` 分开。最重要的设计不变量是：

```text
delay_active_before_detach == true
```

如果延迟在 predecessor action 后才安装，seed/W1 可能已经复制到新多数派；这时 P_new 实际不再 stale，实验就无法证明 branch gap。

### 5.4 node shutdown：区分“少一个节点”与“换主/分叉”

在 Action 1 后关闭 `mongo3` 的设计用于观察少一个 replica 时 RC/WC、read preference、causal session 的行为。它与 P_old/P_new 分区不同：

- 若 remaining nodes 仍能形成多数派，majority 语义可能仍可满足；
- 若失去多数派，操作可能等待/失败；
- 单纯关闭 secondary 不必产生分叉历史或 rollback。

因此 node shutdown 的结果不能直接与 old-primary partition 的 MW/WFR branch witness 混写。

### 5.5 fault-before-action + recovery-before-action2：测试恢复后依赖是否被正确满足

恢复实验的结构是：故障在 Action 1 **前**已经存在；恢复后再执行 Action 2。它测试的不是“持续隔离时能否读旧值”，而是网络恢复、复制追赶和选主稳定后，客户端后续操作是否看到满足前序依赖的状态。

所有故障类型均须记录：故障安装/恢复时间、qdisc 或网络状态回读、primary 变化、Action 1/2 的开始结束时间。没有这些事件证据，就不能将结果归因于预期故障窗口。

---

## 6. 实验实现中必须保持的证据链

每个 cell 应保留至少以下原始证据，而不是只保存最终 V/I/H：

1. **配置**：RC、WC、causal 开关、read preference、URI/direct-connect 模式；
2. **operation record**：唯一 `comment`、request id、实际服务节点、开始/结束时间、回复或异常、session 时间；
3. **故障事件**：install、verify、detach/attach、heal、qdisc 回读、选主状态；
4. **历史证据**：对于 MW/WFR，在 heal 前从 successor serving primary 捕获 `local.oplog.rs`；
5. **派生 checker 输出**：明确采用的判断规则和其引用的原始 operation / oplog tag。

尤其是 oplog 捕获时机不可后移：若先 heal 再抓取，旧主分支可能重新同步/rollback，P_new 在 W2 ACK 时到底是否含 predecessor history 就不再可审计。

---

## 7. v3/v4 历史结果与 v5 新流程不能混用

- **v3 RYW/MR**：历史完整矩阵来自 endpoint-isolated `mongo3`；其精确源码快照应随结果一同审查。
- **v4 MW/WFR**：使用 P_old/P_new choreography、pre-delay、fault-window oplog snapshot；该机制比早期“action 后再 delay”设计更可靠。
- **v5**：统一后续实验的简化矩阵：

```text
RC {local, majority}
× WC {w:1, majority}
× causal {off, on}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
```

即每个故障场景 24 个 cell。v5 结果只能根据相应 run 的原始 artifact 和 smoke/full-run 验证状态解读，不能用“v4 曾跑过”替代 v5 的执行证据。

---

## 8. 写报告时可直接采用的结论模板

### 可以写

> 在 `<run-id>` 中，`<RC, WC, causal, RP>` 配置下，Action 2 实际由 `<node>` 服务；原始 record 显示 `<observed version / error>`。对于 MW/WFR，heal 前 oplog snapshot 显示 successor tag 存在而 predecessor tag 不存在。因此该运行提供了 harness 所定义的 `<model>` history-gap witness。

### 不能直接写

> 该现象证明 MongoDB 不支持 causal consistency。

除非已经逐项证明该 cell 满足官方 session/RC/WC 前提，并排除错误的路由、故障窗口或 checker 假设。

### 对 `inconclusive` 的正确写法

> 隔离侧操作未能在超时内取得可用于判断的成功结果/历史证据，因此该 cell 为 `inconclusive`；它既不证明保证成立，也不构成 violation。

---

## 9. 实验前检查清单

- [ ] 当前 primary 与预期 P_old/P_new 角色已验证；
- [ ] 目标 RC/WC/causal/RP 的组合已显式写入运行 metadata；
- [ ] 需要 causal 的两项被测操作复用同一个显式 session；
- [ ] `w:0` 不进入 causal session 测试；
- [ ] delay/partition 在正确时点安装，并有状态回读；
- [ ] 必要时 predecessor 在 detach 前确实未复制到新多数派；
- [ ] Action 2 的实际服务节点可从原始 record 识别；
- [ ] MW/WFR 在 heal 前抓取 successor oplog；
- [ ] run 先生成原始 `results.json`，再由 checker 派生判定；
- [ ] smoke 通过后才解释或启动同配置空间的 full run。

---

## 10. 一句话总览

本项目不是简单比较“读到新值还是旧值”，而是在控制 **副本本地状态、majority history、read routing、session 因果时间、故障窗口与 failover branch** 后，判断单一客户端的后续操作是否仍发生在它先前写入或观察到状态的后继历史上。
