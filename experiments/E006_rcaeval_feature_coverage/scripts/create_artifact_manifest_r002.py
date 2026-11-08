"""Create a SHA-256 manifest for the local E006-R002 run and its inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments/E006_rcaeval_feature_coverage"
RUN = EXPERIMENT / "results/E006-R002"
OUTPUT = RUN / "artifact-manifest-r002.json"

PATHS = [
    "experiments/E006_rcaeval_feature_coverage/protocol-amendment-r002.md",
    "experiments/E006_rcaeval_feature_coverage/configuration-r002.json",
    "experiments/E006_rcaeval_feature_coverage/scripts/run_local_corpus_r002.py",
    "experiments/E006_rcaeval_feature_coverage/scripts/audit_local_corpus_r002.py",
    "experiments/E006_rcaeval_feature_coverage/scripts/create_artifact_manifest_r002.py",
    "experiments/E006_rcaeval_feature_coverage/results/E006-R002/run.md",
    "experiments/E006_rcaeval_feature_coverage/results/E006-R002/decision.md",
    "experiments/E006_rcaeval_feature_coverage/results/E006-R002/feature-scan.json",
    "experiments/E006_rcaeval_feature_coverage/results/E006-R002/source-manifest-r002.json",
    "experiments/E006_rcaeval_feature_coverage/results/E006-R002/independent-audit-r002.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    entries = []
    for relative in PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
    payload = {
        "record": "E006-R002 artifact manifest",
        "generated_by": "scripts/create_artifact_manifest_r002.py",
        "manifest_self_hash": "omitted; self-referential hash is undefined",
        "files": entries,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(entries)} fingerprints")


if __name__ == "__main__":
    main()
