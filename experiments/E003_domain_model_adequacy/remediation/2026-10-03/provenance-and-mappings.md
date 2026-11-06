# Source-to-canonical and reconstruction contract

All 18 existing OpenRCA telemetry header families are checked against inspected v1 headers. New header fields yield unsupported dispositions. Every logical source record has `(source_key, source_row)` in SQLite `dispositions`, exact source fields, an outcome and error. The source catalog maps opaque keys back to original archive paths and headers. Original ZIP bytes remain the byte-format reconstruction oracle.

| Source | Mapping |
|---|---|
| timestamp/startTime | Decimal epoch candidate supported by source-local date and neighbouring records; selected unit/evidence retained |
| cmdb_id/service/tc/serviceName | exact scoped Resource; unknown kind unless explicitly supported |
| kpi_name/name + value | one named metric; original numeric string |
| rr/sr/cnt/mrt/count/avg_time/num/succee_num/succee_rate | separate observations; all original field meanings remain unverified |
| log value | exact source message; unknown severity |
| trace_id/traceId + span_id/id + parent_id/parent_span/pid | exact span identity and unresolved/resolved parent state |
| duration/elapsedTime | raw numeric duration; unit unknown, end time absent |
| status_code/success | raw token; meaning unknown |
| dsName, type, callType, operation_name, itemid, bomc_id | exact provenance attributes; not inferred dependencies/units |
| Workbook Type/Host/Name | source-backed kind where recognized and RUNS_ON from explicit Host/Name pairs |
| Workbook From (containers) | documented candidates only; no alias or deployment assertion without reviewed interpretation |
| record.csv + query.csv | evaluator-only storage; no operational graph input |

Observation IDs hash source key and record number, with metric-name disambiguation for wide rows. Operational dependency IDs reference exact parent/child observation IDs or workbook cells. Canonical-to-source reconstruction joins observations to dispositions on source key/row. Rejected/ambiguous/out_of_window/unsupported records remain in dispositions with raw fields. Duplicate rows remain distinct observations; fingerprints count duplicate occurrences without deleting them.

No field is silently dropped from accepted/rejected source records. Missing structured meaning is reported as semantic insufficiency rather than raw-data loss. CSV quoting, byte layout and whitespace conventions are preserved by the raw archives, not reserialized canonical values.

Disk SQLite is an experiment artifact store for bounded batches. A whole-corpus import, restart recovery, complete incident retrieval and production database behavior have not been qualified by this amendment. Prefix measurements never establish whole-file counts or absence of telemetry around an incident.
