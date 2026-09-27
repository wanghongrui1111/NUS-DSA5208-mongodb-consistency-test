# Why Four v4 WFR Violations Are Inconclusive in v5

The change reflects a stricter P_old predecessor contract, not evidence that a guarantee began to hold. v4 used the converged setup `seed` as WFR's predecessor. In v5, seeds establish only an identical baseline. v5 then writes a unique `source` after the P_old delay is installed; `R1` must read that source, and the source must be acknowledged before WFR can be evaluated.

For all four changed cells (`RC=local`, `WC=majority`, `RP=primaryPreferred|secondaryPreferred`, causal off/on), v5 records `source.ok=false` with `WriteConcernError`. `R1` can still observe the locally applied source, and the successor `W1` succeeds on mongo2, but the source never satisfied `w:majority` while the pre-delay kept the majority side stale. Therefore, v5 has no acknowledged predecessor witness and correctly labels the cell I.

In v4, the seed succeeded and served as the predecessor, so a successor oplog branch lacking its tag became V. The v5 source rule prevents a setup write from being treated as the delayed P_old predecessor and prevents a failed-majority source write from being classified as a WFR violation.
