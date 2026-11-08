"""Read-only reconciliation of saved E003 V004 profiles with the local manifest.

This checks profile-to-manifest metadata only. It does not open ZIP archives or
recompute decompressed content hashes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    manifest_path = root / "data/manifests/openrca.json"
    profiles_dir = (
        root
        / "experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V004"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected: dict[str, dict] = {}
    for archive in manifest["archives"]:
        for entry in archive["entries"]:
            path = entry.get("path", "")
            if "/telemetry/" in path and path.lower().endswith(".csv"):
                if path in expected:
                    raise ValueError(f"duplicate telemetry path in manifest: {path}")
                expected[path] = entry

    profile_files = sorted(profiles_dir.glob("file-*.json"))
    profiles: dict[str, dict] = {}
    errors: list[str] = []
    for path in profile_files:
        profile = json.loads(path.read_text(encoding="utf-8"))
        source_path = profile.get("path")
        if not source_path:
            errors.append(f"{path.name}: missing source path")
            continue
        if source_path in profiles:
            errors.append(f"duplicate profile source path: {source_path}")
        profiles[source_path] = profile

    missing = sorted(expected.keys() - profiles.keys())
    extra = sorted(profiles.keys() - expected.keys())
    errors.extend(f"missing profile: {path}" for path in missing)
    errors.extend(f"unexpected profile: {path}" for path in extra)

    checked = 0
    for source_path in sorted(expected.keys() & profiles.keys()):
        expected_entry = expected[source_path]
        profile = profiles[source_path]
        checked += 1
        if profile.get("expanded_bytes") != expected_entry.get("size"):
            errors.append(f"{source_path}: expanded byte count differs")
        if profile.get("compressed_bytes") != expected_entry.get("compressed_size"):
            errors.append(f"{source_path}: compressed byte count differs")
        if profile.get("header") != expected_entry.get("header"):
            errors.append(f"{source_path}: header differs")
        if profile.get("decision") != "QUALIFIED":
            errors.append(f"{source_path}: decision is {profile.get('decision')!r}")
        if profile.get("crc_eof_verified") is not True:
            errors.append(f"{source_path}: CRC/EOF marker is not true")
        if profile.get("row_conservation") is not True:
            errors.append(f"{source_path}: row conservation marker is not true")
        rows_seen = profile.get("counts", {}).get("rows_seen")
        if not isinstance(rows_seen, int) or rows_seen < 0:
            errors.append(f"{source_path}: invalid rows_seen")
        digest = profile.get("decompressed_sha256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{source_path}: invalid decompressed SHA-256 field")

    report = {
        "audit": "E003 V004 saved-profile to manifest metadata reconciliation",
        "manifest_telemetry_csv_count": len(expected),
        "profile_file_count": len(profile_files),
        "matched_paths_checked": checked,
        "missing_profiles": len(missing),
        "unexpected_profiles": len(extra),
        "errors": errors,
        "result": "PASS_METADATA_RECONCILIATION" if not errors else "FAIL",
        "scope_limit": (
            "Saved JSON profile fields were compared to saved manifest metadata. "
            "Raw ZIPs were not opened; CRC, decompressed SHA-256, and row counts "
            "were not independently recomputed from source bytes."
        ),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
