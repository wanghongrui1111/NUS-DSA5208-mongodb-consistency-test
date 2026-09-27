# Inconclusive (`I`) analysis

This analysis was generated automatically from the final 36 result sets and covers all **223** I cells. I means that the precise witness required by the checker is missing; it does not indicate H.

## Overall causes

| cause | cells | meaning |
|---|---:|---|
| `operation_error:_OperationCancelled` | 85 | PyMongo cancelled the operation during server selection, connection-pool reconstruction, or a socket operation; no comparable witness is available. |
| `operation_error:NotPrimaryError` | 48 | After the partition, the node is no longer the writable primary; this is an availability/election outcome. |
| `operation_error:WriteConcernError` | 39 | The write may have been persisted locally, but the requested write concern was not satisfied; under the P_old delay, it cannot serve as a confirmed predecessor. |
| `operation_error:ExecutionTimeout` | 30 | The server did not complete the operation within maxTimeMS; no comparable witness is available. |
| `operation_error:AutoReconnect` | 14 | After network detach/private-network isolation, the driver's existing topology/DNS path cannot connect to a candidate member; the predecessor or successor operation did not complete, so H/V cannot be determined. |
| `operation_error:NetworkTimeout` | 4 | The connection or socket received no response within the configured timeout; this indicates that the observation path is unavailable. |
| `oplog_evidence_insufficient` | 3 | The WFR/MW successor branch cannot simultaneously prove the required relation between the predecessor and successor. |

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
