import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "experiments" / "E011_domain_rule_source_support" / "results"
errors = []
for run_dir in sorted(RUNS.glob("E011-R*")):
    manifest_path = run_dir / "artifact-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = run_dir / item["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"] or path.stat().st_size != item["bytes"]:
            errors.append(f"{run_dir.name}/{item['path']}")
    print(f"{run_dir.name}: {len(manifest['files'])} artifacts; {'FAIL' if errors else 'PASS'}")
print("mismatches:", errors)
if errors:
    raise SystemExit(1)
