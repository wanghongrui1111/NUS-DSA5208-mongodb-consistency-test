# MongoDB Consistency Experiments: Key Mechanisms and Interpretation Boundaries

> **Purpose**: Explain the mechanisms actually tested by this project's MongoDB client-centric consistency experiments, how faults create observable differences, and which phenomena must not be mischaracterized as violations of MongoDB's documented guarantees.
>
> **Scope**: RYW, MR, MW, and WFR experiments on a three-node replica set (`mongo1`, `mongo2`, and `mongo3`), and netlab-v5's simplified configuration space.
>
> **Companion materials**: [Environment and Configuration Guide](ENVIRONMENT-SETUP-EN.md), [MongoDB documentation on causal consistency](https://www.mongodb.com/docs/manual/core/causal-consistency-read-write-concerns/).

---

## 1. First Distinguish Three Levels

### 1.1 Client-centric consistency is not global linearizability

The four properties in these experiments constrain the observational/causal ordering of successive operations by the **same client (or within the same session)**. They do not require every client to observe the same global state in real time.

| Property | Constrained operation relation | Semantics the client should obtain |
|---|---|---|
| RYW (read-your-writes) | $W_1 \rightarrow R_1$ | A read after one's own write must not regress to a version preceding that write |
| MR (monotonic reads) | $R_1 \rightarrow R_2$ | A later read must not observe an older version than an earlier read |
| MW (monotonic writes) | $W_1 \rightarrow W_2$ | The later write must occur on a history branch that follows the earlier write |
| WFR (writes-follow-reads) | $R_1 \rightarrow W_2$ | The later write must build on the state previously read, or on a successor of that state |

Here, “successor” refers to **historical/causal order**, not merely to final document field values that happen to look the same.

### 1.2 MongoDB's mechanism-level guarantees differ from the experiment harness's verdicts

A `violated` result means that the harness has found an operation relation or oplog branch witness showing that the tested relation did not hold.

This is **not automatically equivalent to** “MongoDB violated a documented guarantee.” Each cell must also be checked individually to determine:

1. whether the same explicit, causally consistent session was used;
2. whether the read concern / write concern combination satisfies the documented guarantee matrix;
3. whether the reads and writes actually succeeded and whether sufficient evidence can be obtained from the faulted side; and
4. whether the cell deliberately tests a weak configuration (in which case a stale read or unavailability is often expected).

The three verdict states must therefore remain strictly distinct:

- `holds`: the currently available raw evidence supports that the relation holds;
- `violated`: the currently available raw evidence provides a witness that the relation was broken;
- `inconclusive`: a timeout, error, unacknowledged write, unavailable auditable oplog, or similar condition means the result **must not be counted as `holds`**.

### 1.3 A correct document value does not imply a correct causal history

The current MW/WFR successor operation often uses a blind `$set` to isolate the database's history mechanism. For example, writing `v=8` directly on the new primary can leave the final document with the expected value even when the new primary never contained `v=7` from the old primary.

```text
Old branch: C0 → seed(v=7) → R1
New branch: C0 → successor($set v=8)
```

The final `$set v=8` can “look correct,” but the successor's prior state is `C0`, not `C1=v=7`. This remains the kind of history gap relevant to WFR/MW. To demonstrate business-level consequences, add a separate read-dependent control workload such as CAS, revision tracking, or inventory decrement; do not overstate the current blind-write experiment as having proved that business data must be incorrect.

---

## 2. Four Kinds of State That Determine Replica-Set Behavior

### 2.1 Node-local applied state (local state)

`readConcern: "local"` reads data already applied locally by a particular node. This state can include writes not yet incorporated into the majority history and can therefore expose writes that will later be rolled back.

A typical experiment stops both secondaries and then performs a `w:1` write of `v=2` on the old primary.

```text
Old primary local      → v=2
Old primary majority   → v=0
Old primary later loses primary status and rejoins → v=2 is rolled back
```

**Testing implication**: the freshness of `local` state does not imply durability or continued inclusion in the authoritative history after failover.

### 2.2 A node's local majority snapshot

`readConcern: "majority"` returns only the majority-committed snapshot that the node considers safe. It does not expose a rollback branch that has not entered the majority history, but different nodes need not install the same latest snapshot simultaneously.

For example, after `mongo1 + mongo2` have acknowledged a `w:"majority"` write while `mongo3` still has apply delay:

```text
mongo1 majority → version 1
mongo2 majority → version 1
mongo3 majority → version 0
```

**Testing implication**: acknowledgement of a majority write does not mean that every secondary can already read that write; an ordinary majority read from a secondary also does not promise immediate convergence to the globally latest majority write.

### 2.3 The replica set's global majority commit point

The global majority commit point indicates that a particular oplog entry has been durably acknowledged by a majority of voting nodes. It determines when a write can be considered part of the majority history, but it does not by itself imply that every member has applied the write, nor can it replace a client's causal dependency.

The following formulation must be avoided:

```text
w:majority succeeds ⇒ every node has the latest value
```

The correct formulation is:

```text
w:majority succeeds ⇒ the write has received sufficient majority acknowledgement; a lagging secondary's visible snapshot may still be older.
```

### 2.4 Divergent histories, elections, and rollback

When the old primary is isolated from the remaining majority, it may temporarily retain writes that exist only on its own branch. After `mongo2,mongo3` elect a new primary, writes absent from the old primary's branch may ultimately be rolled back.

This is the core of the MW/WFR tests: not that “an additional update necessarily occurs during the partition,” but that the client first observes or writes on the old branch and then sends a subsequent operation to the new branch, which is still at the earlier state.

---

## 3. The Respective Roles of RC, WC, Read Preference, and Causal Sessions

### 3.1 Read concern (RC) controls what a read is allowed to observe

The project's unified simplified configuration space going forward is:

```text
RC ∈ {local, majority}
```

- `local`: reads the locally applied state of an eligible node, offering low latency but potentially exposing content that has not been majority committed;
- `majority`: reads only that node's majority-committed snapshot, avoiding rollback branches but potentially waiting or returning an older safe snapshot.

### 3.2 Write concern (WC) controls the acknowledgement threshold for a successful write

The simplified configuration space going forward is:

```text
WC ∈ {w:1, majority}
```

- `w:1`: the primary can ACK once it has accepted/written the operation; after a failure, the write may be absent from the new majority history;
- `w:"majority"`: requires majority acknowledgement, providing stronger assurance that the write has entered the majority history, but not guaranteeing immediate readability from every node.

### 3.3 Read preference determines which replica actually executes a read

For each cell, v5 actually supplies one of:

```text
{primary, primaryPreferred, secondaryPreferred}
```

Read preference does not change the semantics of RC/WC, but it determines whether a read can reach a lagging or isolated secondary:

- `primary`: reads ordinarily go to the current primary;
- `primaryPreferred`: prefers the primary and considers other eligible nodes only when the primary is unreachable;
- `secondaryPreferred`: prefers a secondary and is a key configuration for exposing replication lag and stale-read paths.

Reporting only RC/WC is therefore insufficient; under the same RC/WC combination, different read preferences can produce entirely different behavior.

### 3.4 A causal session carries dependencies across operations

For acknowledged writes, the experiment's two **operations under test** use the same explicit `ClientSession`. When `causal_consistency=True`, the driver maintains the session's `clusterTime` / `operationTime`; a subsequent read carries a lower bound analogous to `afterClusterTime`, and the server cannot return a result from a snapshot earlier than that dependency.

Intuitively, this behaves like a logical-time dependency rather than a Lamport clock manually implemented by the application:

```text
W1 / R1 produces or observes time T
→ the session remembers T
→ subsequent R2 / W2 must be at least causally compatible with T
```

Important boundaries:

- **Using the same session does not automatically imply causal consistency**. With `causal=off`, the session object may still be reused, but the driver is not required to maintain the causal read lower bound described above;
- `w:0` provides no acknowledged write, so this project does not establish a session for it and does not generate `w:0 + causal=on` cells;
- the setup seed for MR/WFR is performed outside the session to construct the initial state and must not be described as though “all database operations occur in the same session.”

### 3.5 Minimal reference matrix for the four documented guarantees

For a causally consistent session, the MongoDB documentation gives the following commonly used core combinations:

| RC | WC | RYW | MR | MW | WFR |
|---|---|---:|---:|---:|---:|
| `majority` | `majority` | ✅ | ✅ | ✅ | ✅ |
| `majority` | `w:1` | — | ✅ | — | ✅ |
| `local` | `majority` | — | — | ✅ | — |
| `local` | `w:1` | — | — | — | — |

Here, “—” does not mean that the experiment must fail; it means that the property is not documented as guaranteed. `available` also cannot be used for a causally consistent session; it belongs to the historical v4 full matrix, not v5's simplified configuration space.

---

## 4. Actual Execution Sequences for the Four Consistency Properties in These Experiments

### 4.1 RYW: a read after a write must not be routed to an older replica

```text
W1 (normally on the primary) → R1 (possibly routed to a secondary by read preference)
```

The risky path created by a fault or delay is:

```text
W1 has been ACKed by the primary
→ the target secondary has not yet replicated W1
→ R1 is sent to the target secondary
→ the pre-write version is returned
```

- With `causal=on`, the session imposes a time lower bound on the subsequent read; if the target node cannot satisfy it, the correct behavior is ordinarily to wait, time out, or become unavailable rather than return a stale value that violates the dependency;
- with `causal=off` or weak concerns, a stale read is an observable and expected candidate outcome.

### 4.2 MR: a later read must not be older than an earlier read

```text
R1 (from a newer node) → R2 (from a more lagged node)
```

MR does not require the client to perform a write. The experiment first creates a newer seed; R1 reaches a node containing that seed, and R2 is then routed to a node that does not contain it.

```text
R1 sees v=1
R2 sees v=0
```

This constitutes an MR witness. If R2 times out or the target cannot be read, the result can only be recorded as `inconclusive`, not as evidence that MR holds.

### 4.3 MW: the new primary must not accept a later write detached from the earlier write's history

Semantic sequence:

```text
W1 on P_old → partition / failover → W2 on P_new
```

The key mechanism is preventing `W1` from being replicated to the new majority before detach. v4 first applies a long directional delay from **`mongo1 → mongo2,mongo3` before Action 1**; W1 is permitted only after the qdisc has been verified as active. It then detaches `mongo1`, allows `mongo2,mongo3` to form a new majority and elect a primary, and finally writes W2 on P_new.

If P_new's oplog contains W2 but not W1 when W2 succeeds, W2 belongs to a branch that does not contain W1, providing an MW history witness.

### 4.4 WFR: after reading state from the old primary, a later write must not land on an earlier branch

WFR has **three semantic actions** and must not be misread as only “a read followed by a write”:

```text
S (source seed write) → R1 → W2 (successor write)
```

The current artifact names are:

| Semantics | Record name | Execution location |
|---|---|---|
| source seed | `seed` | `mongo1` / P_old |
| read | `read1` | `mongo1` / P_old |
| successor write | `write1` | `mongo2` / P_new |

Complete choreography:

```text
Pre-enable netem delay from mongo1 → mongo2,mongo3
→ write S to P_old
→ R1 on P_old confirms that this run's S was read
→ detach mongo1
→ mongo2,mongo3 elect P_new
→ W2 succeeds on P_new
→ immediately capture P_new's local.oplog.rs before heal
```

If the oplog shows:

```text
P_new contains W2
P_new does not contain S
```

then the state preceding W2 was neither the state read by R1 nor one of its successors. No additional synchronization or write between R1 and W2 is needed; **the absence of synchronization is precisely what leaves P_new at `C0`, thereby creating the WFR break.**

---

## 5. How Fault Injection Corresponds to Mechanism Assumptions

### 5.1 Delay / packet loss: creating replication lag, not physical isolation

The target parameters for delay going forward are:

```text
target=mongo3; delay=100 ms; jitter=20 ms; loss=3%
```

The implementation now configures the qdisc directly with `tc netem` in the target network namespace and reads the qdisc back as evidence. This avoids unstable Pumba container enumeration when client containers are short-lived.

This fault is suitable for testing when a secondary's local or majority snapshot lags as replication/network performance degrades and whether a causal read waits.

### 5.2 Endpoint / client partition: forcing Action 2 onto the stale side

The historical v3 endpoint-partition procedure for RYW/MR is:

1. initialize `v=0` with `w:3`;
2. detach `mongo3` into a private network;
3. execute Action 1 on the `mongo1,mongo2` majority;
4. move the client through a barrier into the private network and direct-connect Action 2 to `mongo3`;
5. restore the endpoint after each cell.

This is not the only way to simulate “ordinary automatic driver routing.” Instead, it deliberately forces a single-node stale path to test whether RC/WC/session semantics preserve the relation on that path or correctly make the operation unavailable.

### 5.3 P_old / P_new partition: creating a history branch, not merely reading a stale value

The v4 partition for MW/WFR does not isolate `mongo3` by itself; it separates the old primary `mongo1` from the new majority `mongo2,mongo3`. The most important design invariant is:

```text
delay_active_before_detach == true
```

If the delay is installed only after the predecessor action, seed/W1 may already have replicated to the new majority. P_new would then no longer be stale, and the experiment could not demonstrate a branch gap.

### 5.4 Node shutdown: distinguishing “one fewer node” from “primary replacement/history divergence”

The design that shuts down `mongo3` after Action 1 observes how RC/WC, read preference, and causal sessions behave with one fewer replica. It differs from a P_old/P_new partition:

- if the remaining nodes can still form a majority, majority semantics may remain satisfiable;
- if the majority is lost, operations may wait or fail;
- merely shutting down a secondary does not necessarily create divergent histories or rollback.

Node-shutdown results must therefore not be conflated with MW/WFR branch witnesses from an old-primary partition.

### 5.5 Fault-before-action + recovery-before-action2: testing whether dependencies are correctly satisfied after recovery

A recovery experiment has the following structure: the fault is already present **before** Action 1, and Action 2 runs only after recovery. It does not test “whether a stale value can be read during continuous isolation”; it tests whether a client's subsequent operation observes a state satisfying the preceding dependency after network recovery, replication catch-up, and election stabilization.

For every fault type, the experiment must record fault installation/recovery times, qdisc or network-state readback, primary changes, and the start/end times of Action 1/2. Without this event evidence, a result cannot be attributed to the intended fault window.

---

## 6. Evidence Chain That the Experimental Implementation Must Preserve

Each cell should retain at least the following raw evidence rather than storing only the final V/I/H verdict:

1. **Configuration**: RC, WC, causal toggle, read preference, and URI/direct-connect mode;
2. **operation record**: unique `comment`, request id, actual serving node, start/end times, reply or exception, and session times;
3. **fault events**: install, verify, detach/attach, heal, qdisc readback, and election state;
4. **history evidence**: for MW/WFR, `local.oplog.rs` captured from the successor-serving primary before heal;
5. **derived checker output**: the explicit decision rule used and the raw operation / oplog tags it cites.

The oplog capture must not be delayed in particular: if heal occurs first, the old primary's branch may resynchronize or be rolled back, leaving it impossible to audit whether P_new contained the predecessor history when W2 was ACKed.

---

## 7. Historical v3/v4 Results Must Not Be Mixed with the New v5 Workflow

- **v3 RYW/MR**: the historical full matrix comes from endpoint-isolated `mongo3`; its exact source snapshot should be reviewed together with the results.
- **v4 MW/WFR**: uses P_old/P_new choreography, pre-delay, and a fault-window oplog snapshot; this mechanism is more reliable than the earlier design that applied delay only after an action.
- **v5**: unifies future experiments around the simplified matrix:

```text
RC {local, majority}
× WC {w:1, majority}
× causal {off, on}
× ReadPreference {primary, primaryPreferred, secondaryPreferred}
```

This yields 24 cells per fault scenario. v5 results may be interpreted only from the corresponding run's raw artifacts and smoke/full-run verification status; the fact that “v4 was run previously” cannot substitute for v5 execution evidence.

---

## 8. Conclusion Templates Suitable for Direct Use in a Report

### Acceptable wording

> In `<run-id>`, under the `<RC, WC, causal, RP>` configuration, Action 2 was actually served by `<node>`; the raw record shows `<observed version / error>`. For MW/WFR, the pre-heal oplog snapshot shows that the successor tag is present while the predecessor tag is absent. This run therefore provides a `<model>` history-gap witness as defined by the harness.

### Wording that cannot be used directly

> This phenomenon proves that MongoDB does not support causal consistency.

Such a statement is not justified unless the cell has been shown, item by item, to satisfy the documented session/RC/WC prerequisites and incorrect routing, fault-window assumptions, and checker assumptions have been ruled out.

### Correct wording for `inconclusive`

> The operation on the isolated side did not produce, within the timeout, a successful result or history evidence suitable for evaluation. The cell is therefore `inconclusive`; it neither demonstrates that the guarantee holds nor constitutes a violation.

---

## 9. Pre-Experiment Checklist

- [ ] The current primary and expected P_old/P_new roles have been verified;
- [ ] the target RC/WC/causal/RP combination has been explicitly written to the run metadata;
- [ ] the two operations under test that require causal semantics reuse the same explicit session;
- [ ] `w:0` is excluded from causal-session tests;
- [ ] the delay/partition is installed at the correct time and has a state readback;
- [ ] when required, the predecessor has definitively not replicated to the new majority before detach;
- [ ] the actual serving node for Action 2 can be identified from the raw record;
- [ ] MW/WFR captures the successor oplog before heal;
- [ ] the run generates raw `results.json` before the checker derives verdicts;
- [ ] the full run for the same configuration space is interpreted or started only after the smoke test passes.

---

## 10. One-Sentence Overview

Rather than merely comparing “whether a new or old value was read,” this project controls **replica-local state, majority history, read routing, session causal time, the fault window, and the failover branch** to determine whether a single client's subsequent operation still occurs on a successor history of the state that the client previously wrote or observed.
