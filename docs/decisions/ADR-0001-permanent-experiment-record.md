# ADR-0001: Permanent experiment record

Date: 2026-10-02
Status: accepted for repository scaffolding, per user request

Context: notebooks and delivered R0 artifacts need a common scientific record before substantial new code.
Decision: use the current repository root as DCE; retain existing artifacts; reserve the requested modules;
allocate E001/E002 with explicit draft/reserved status; use Git history and artifact manifests for provenance.
Root PRD.md links to the complete docs/PRD.md to avoid competing specifications.

Consequences: new experiments must follow EXPERIMENT_INDEX.md. IDs are permanent; frozen records receive append-only amendments.
The new src directories are placeholders, not replacements for dce-r0/dce/src/dce.
Branch protection and immutable artifact-storage enforcement remain deployment tasks.
