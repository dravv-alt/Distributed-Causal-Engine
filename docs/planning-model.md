# Planning model

Initial product output is a recommendation, not an executed infrastructure change.
A plan references candidate root sets, evidence IDs and a versioned runbook. Each action declares prerequisites,
expected observations, affected resources, verification interval, rollback reference and approval requirement.

Uncertain diagnosis or missing prerequisite evidence must produce a review-needed/no-plan result.
Do not present a fixed restart template as an optimized recovery plan. Planning experiments need outcome definitions,
a baseline and controlled execution environment before any efficacy claim.

The delivered R0 package contains no recovery planner. Reserve src/planning for later implementation.
