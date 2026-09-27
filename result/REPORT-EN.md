# MongoDB v5 full experiment report

## 1. Scope and completeness

This document records the final complete v5 run `v5-dual-pold-full-20260925-r2`. The four models use mutually isolated Compose stacks; each scenario-model has 24 cells: `RC {local, majority} × WC {w:1, majority} × RP {primary, primaryPreferred, secondaryPreferred} × causal {off,on}`.

Programmatic verification: 36 `results.json` files and 864 unique checked cells; the exact seed IDs of all three nodes converge for every cell. P_old cells additionally include qdisc install/remove evidence. Totals: H=574, V=67, I=223.

## 2. Judgment criteria and limitations

H=holds, V=violated, I=inconclusive. RYW/MR compare operation return values; WFR/MW use the actual serving primary `local.oplog.rs` branch captured after the Action2 successor ACK and before heal. I indicates that the required witness is missing; it does not mean H. `majority` read concern provides a rollback-safe snapshot but does not, by itself, guarantee freshness.

Legend: each cell lists `primary`, `primaryPreferred`, and `secondaryPreferred`, in that order.

## baseline

**Fault sequence:** No fault.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=21, V=3, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=24, V=0, I=0.

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

**Fault sequence:** After Action 1, install 100 ms delay, 20 ms jitter, and 3% loss on mongo3; remove the rule after Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=24, V=0, I=0.

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

**Fault sequence:** P_old: after seed convergence, install a 60 s directional delay on mongo1→mongo3 and mongo2→mongo3; after Action 1, partition `{mongo1,mongo2}` from `{mongo3,labclient}`; heal after Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=0, V=12, I=12.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=3, V=9, I=12.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=0, V=0, I=24.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=0, V=0, I=24.

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

**Fault sequence:** P_old: after seed convergence, install a 60 s directional delay on mongo1→mongo2,mongo3; after Action 1, partition `{mongo1}` from `{mongo2,mongo3,labclient}`; heal after Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=0, V=12, I=12.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=6, V=12, I=6.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=0, V=6, I=18.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=0, V=12, I=12.

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

**Fault sequence:** Stop mongo3 after Action 1 and restore it after Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=24, V=0, I=0.

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

**Fault sequence:** Before Action 1, install 100 ms delay, 20 ms jitter, and 3% loss on mongo3; remove the rule before Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=24, V=0, I=0.

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

**Fault sequence:** Standard partition recovery: before Action 1, partition `{mongo1,mongo2}` from `{mongo3,labclient}`; heal before Action 2; does not include the P_old pre-delay.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=0, V=0, I=24.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=1, V=0, I=23.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=5, V=0, I=19.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=0, V=0, I=24.

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

**Fault sequence:** Standard partition recovery: before Action 1, partition `{mongo1}` from `{mongo2,mongo3,labclient}`; heal before Action 2; does not include the P_old pre-delay.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=22, V=1, I=1.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=19, V=0, I=5.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=20, V=0, I=4.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=21, V=0, I=3.

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

**Fault sequence:** Stop mongo3 before Action 1; restore it before Action 2.

### RYW — `W1 → R1`

Source: `v5-dual-pold-full-20260925-r2-ryw`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-wfr`; 24 cells; H=24, V=0, I=0.

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

Source: `v5-dual-pold-full-20260925-r2-mw`; 24 cells; H=24, V=0, I=0.

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
