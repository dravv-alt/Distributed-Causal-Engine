"""Verify and record the pinned environment required before a future E002 rerun."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path


PACKAGES = {
    "numpy": "1.26.4", "scipy": "1.15.1", "scikit-learn": "1.6.1",
    "networkx": "3.4.2", "joblib": "1.4.2", "threadpoolctl": "3.5.0", "pytest": "9.0.2",
}
THREAD_VARS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
EXPECTED_LOCK_SHA256 = "694071fa9d6850d9cab412f1c135879427f5846a166eec7fc7d6e411f1309320"
EXPECTED_PYTHON = (3, 12, 6)


def memory_gib() -> float | None:
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MemoryStatus(); status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return round(status.ullTotalPhys / 1024**3, 2)
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--lock", default="requirements-e002-lock.txt")
    parser.add_argument("--installation-method", required=True)
    parser.add_argument("--expected-executable", required=True)
    args = parser.parse_args()
    lock = Path(args.lock)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        import numpy  # noqa: F401
        import scipy  # noqa: F401
        import sklearn  # noqa: F401
        import networkx  # noqa: F401
    installed = {name: importlib.metadata.version(name) for name in PACKAGES}
    matches = {name: installed[name] == version for name, version in PACKAGES.items()}
    lock_hash = hashlib.sha256(lock.read_bytes()).hexdigest()
    thread_settings = {name: os.environ.get(name) for name in THREAD_VARS}
    expected_executable = Path(args.expected_executable).resolve()
    checks = {
        "python_version": tuple(sys.version_info[:3]) == EXPECTED_PYTHON,
        "active_interpreter": Path(sys.executable).resolve() == expected_executable,
        "lock_hash": lock_hash == EXPECTED_LOCK_SHA256,
        "packages": all(matches.values()),
        "thread_settings": all(value is None for value in thread_settings.values()),
        "runtime_warnings": not caught,
    }
    report = {
        "schema_version": "dce.e002.environment.v1",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "qualified": all(checks.values()),
        "checks": checks,
        "requirements_lock": {"path": str(lock).replace("\\", "/"), "sha256": lock_hash, "expected_sha256": EXPECTED_LOCK_SHA256},
        "python": {"executable": sys.executable, "expected_executable": str(expected_executable), "version": sys.version.replace("\n", " "), "prefix": sys.prefix},
        "packages": {name: {"expected": PACKAGES[name], "installed": installed[name], "matches": matches[name]} for name in PACKAGES},
        "hardware": {"platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor() or None,
                     "logical_cpu_count": os.cpu_count(), "physical_memory_gib": memory_gib()},
        "thread_settings": thread_settings,
        "runtime_warnings": [str(item.message) for item in caught],
        "installation_method": args.installation_method,
        "scope": "Qualification for E002-R002 only. This does not alter or qualify E002-R001."
    }
    target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"qualified": report["qualified"], "output": str(target)}, indent=2))
    return 0 if report["qualified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
