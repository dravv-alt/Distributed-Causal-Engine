"""Feature schema contract. Order, names and units are part of the model contract."""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA_VERSION = "dce.features.v1"
FEATURES = ("latency_ms", "error_rate", "request_rate", "cpu_util")
UNITS = ("ms", "ratio", "req/s", "ratio")
FEATURE_INDEX = {f: i for i, f in enumerate(FEATURES)}


class SchemaMismatch(ValueError):
    pass


@dataclass(frozen=True)
class FeatureSchema:
    version: str = SCHEMA_VERSION
    features: tuple = FEATURES
    units: tuple = UNITS

    def to_dict(self) -> dict:
        return {"version": self.version, "features": list(self.features), "units": list(self.units)}

    def check_compatible(self, other: "FeatureSchema") -> None:
        if (self.version, self.features, self.units) != (other.version, other.features, other.units):
            raise SchemaMismatch(
                f"feature schema mismatch: {self.version}/{self.features}/{self.units} "
                f"vs {other.version}/{other.features}/{other.units}"
            )
