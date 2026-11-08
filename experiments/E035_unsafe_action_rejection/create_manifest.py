import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
included = [
    "README.md", "hypothesis.md", "protocol.md", "configuration.json", "run.py",
    "generate.py", "evaluate.py", "audit.py", "run.md", "decision.md",
    "fixtures/proposals.json", "evaluator/labels.json",
    "results/E035-R001/predictions.json", "results/E035-R001/metrics.json",
    "results/E035-R001/independent-audit.json",
]
entries = []
for rel in included:
    data = (root / rel).read_bytes()
    entries.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
manifest = {"experiment": "E035", "run": "E035-R001", "files": entries,
            "scope": "synthetic offline validator; no action execution"}
(root / "results" / "E035-R001" / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"hashed_files": len(entries), "manifest": str(root / "results" / "E035-R001" / "artifact-manifest.json")}))
