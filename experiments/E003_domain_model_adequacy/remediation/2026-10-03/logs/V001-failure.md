# V001 retained engineering failure

V001 stopped on its first telemetry file because the coverage query expected `observations.resource_id`, absent from the newly created SQLite schema. No adequacy result or decision was produced. Its source snapshot, preflight, dataset hashes, partial database and stdout/stderr remain unchanged under results/V001 and logs/V001-*.log.

Fix: add the resource foreign identity column and populate it from canonical observations. Added a cross-system disk-pipeline integration fixture covering conservation, duplicate retention, graph output and repeated hashes. This repairs implementation to the existing protocol; selection and gates are unchanged. New execution directory: V002. The configuration's V001 field records the initial intended validation; each actual execution is identified by its directory and summary.
