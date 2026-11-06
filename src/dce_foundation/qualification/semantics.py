"""Metric qualification inventory; UNKNOWN is accepted without fabricated evidence."""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class MetricQualification:
    metric_name: str
    source: str
    scenario: str
    unit: str = "UNKNOWN"
    temporality: str = "UNKNOWN"
    aggregation: str = "UNKNOWN"
    kind: str = "UNKNOWN"
    evidence_source: str | None = None
    confidence: float = 0.0
    status: str = "UNKNOWN"

    def __post_init__(self):
        assertions = any(v != "UNKNOWN" for v in (self.unit,self.temporality,self.aggregation,self.kind))
        if assertions and (not self.evidence_source or self.status != "QUALIFIED"):
            raise ValueError("asserted semantics require explicit qualified evidence")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence outside [0,1]")
        if self.status == "UNKNOWN" and (self.confidence != 0 or self.evidence_source):
            raise ValueError("UNKNOWN must not claim evidential confidence")


def inventory_entry(scenario,source,name,count):
    return {**asdict(MetricQualification(name,source,scenario)),"source_observations":count,
            "feature_eligibility":"no unit-dependent transforms while semantics UNKNOWN"}
