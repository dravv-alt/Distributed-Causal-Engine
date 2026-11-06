# E001 protocol

Status: Draft; not executed under E001.

## Question

Can the delivered R0 baseline be reproduced from a pinned source snapshot, and what do its comparisons actually establish?

## Hypothesis

Pinned source, dependencies, configuration and seeds reproduce the delivered metrics within a tolerance chosen before execution. Reproduction alone does not demonstrate hybrid superiority.

## Independent variables

Reported method variants; sparse/concurrent faults; workload scaling; missingness; controlled seed.

## Dependent variables

Incident precision/recall, event coverage, root ranking, detection delay, false-alert exposure and paired gain; preregister exact definitions.

## Controls

Fixed environment seed/service mapping, feature schema, chronological split/embargo and training seed. Audit shared reasoning in method variants before interpreting ablations.

## Dataset/version

Pending: pin each manifest and telemetry checksum; do not identify data by folder name alone.

## Code version

Pending: Git commit plus dirty status and source-tree checksum/archive. Current R0 delivery is untracked and not represented by the repository HEAD.

## Configuration

configuration.yaml is protocol metadata; it is not consumed by the current R0 CLI. Record resolved CLI arguments/configuration per run.

## Random seeds

Proposed: environment 11; training dataset 11; held-out dense 12, sparse 21, load 13, missing 15, fault-free 14; model 0.

## Hardware

Pending execution: CPU model/core count, RAM, OS, architecture, accelerators, dependency/thread settings.

## Results

Pending. No experiment execution or new benchmark results.

## Failure cases

Pending collection. Record crashes, mismatches, unavailable inputs and weak/negative results.

## Interpretation

Pending evidence review; distinguish observations from hypotheses and scope limitations.

## Decision

Pending. Do not promote a model or claim an improvement from a draft.

## Next experiment

E002 reserved for onset/timing provenance; freeze its protocol only after E001 review.

## Freeze and amendments

Protocol commit: pending. Owner/reviewer: pending. Freeze date: pending.
Choose numerical tolerances and analysis before executing. Append dated amendments after freeze; changed hypotheses receive new IDs.
