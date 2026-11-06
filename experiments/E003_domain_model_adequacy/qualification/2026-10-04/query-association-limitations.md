# Query association findings — not an RCA score

The V002 evaluator-only association artifact contains 335 query rows: 333 uniquely matched, two explicitly UNKNOWN. No positional join was used. This count is available before the full telemetry census finishes and must not be mistaken for incident observability or RCA accuracy.

## Market/cloudbed-1 query row 30

The instruction describes two failures on March 20, 2022, 08:30–09:00. Both scoring elements specify only the same reason, `container network latency`. The current independent matching procedure requires each element to identify a unique label and cannot distinguish repeated reason-only elements. It retains UNKNOWN instead of assigning labels by position.

A future evaluator qualification can examine unique joint/multiset association for repeated elements. That would be a new documented procedure with fixtures, not a silent change to this run's criterion.

## Market/cloudbed-1 query row 68

The instruction crosses midnight: March 21, 2022, 23:30 to March 22, 2022, 00:00. The current conservative query-window parser supports a single explicit date and reports no window here. Component/reason matching without that constraint is not unique, so association remains UNKNOWN.

A separately reviewed parser revision can support explicit cross-date bounds. This limitation belongs to the adapter, not evidence that the source incident is invalid.

## Consequence

Unrestricted official-query scoring is not qualified by V002. Annotation-window representation and coverage remain auditable independently. Neither query is discarded from the denominator. Source instructions and scoring points stay evaluation-only and never enter projected inference data.
