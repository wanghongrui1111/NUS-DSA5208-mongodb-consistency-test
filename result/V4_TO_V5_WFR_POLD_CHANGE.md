# Why four v4 WFR violations are v5 inconclusive

The change is a stricter P_old predecessor contract, not evidence that a guarantee began holding. v4 used the converged setup `seed` as WFR's predecessor. v5 seeds only to establish an identical baseline, then writes a unique `source` after the P_old delay is installed; `R1` must read that source and the source must be acknowledged before WFR can be judged.

For all four changed cells (`RC=local`, `WC=majority`, `RP=primaryPreferred|secondaryPreferred`, causal off/on), v5 records `source.ok=false` with `WriteConcernError`. `R1` can still observe the locally applied source, and successor `W1` succeeds on mongo2, but the source never satisfied `w:majority` while the pre-delay held the majority side stale. v5 therefore has no acknowledged predecessor witness and correctly labels the cell I.

In v4 the seed was successful and served as the predecessor, so a successor oplog branch lacking its tag became V. The v5 source rule prevents treating a setup write as the delayed P_old predecessor and prevents upgrading a failed-majority source write to a WFR violation.
