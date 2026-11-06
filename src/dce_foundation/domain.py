"""Dataset-independent values. Unknown semantics are None, not inferred defaults."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode()).hexdigest()


class Relation(str, Enum):
    CALLS = "CALLS"
    OBSERVED_ON = "OBSERVED_ON"
    HAS_OBSERVATION = "HAS_OBSERVATION"
    IN_TRACE = "IN_TRACE"
    PARENT_SPAN = "PARENT_SPAN"
    SUPPORTED_BY = "SUPPORTED_BY"
    CONTAINS = "CONTAINS"
    LABELS = "LABELS"
    AFFECTS = "AFFECTS"


RELATION_CATEGORY = {
    "CALLS": "observed_structural", "OBSERVED_ON": "evidence",
    "HAS_OBSERVATION": "evidence", "IN_TRACE": "structural",
    "PARENT_SPAN": "observed_structural", "SUPPORTED_BY": "evidence",
    "CONTAINS": "structural", "LABELS": "evaluation_label",
    "AFFECTS": "labelled_event",
}
# Temporal / possible-causal / established-causal edges are deliberately absent.


@dataclass(frozen=True)
class EventTime:
    epoch_ns: int
    utc: str
    source_value: str
    source_field: str
    source_unit: str
    precision_ns: int
    timezone: str = "UTC epoch; source datetime labels interpreted UTC+08:00"


@dataclass(frozen=True)
class Provenance:
    source: str
    path: str
    row: int
    attributes: dict[str, Any]
    quality: tuple[str, ...] = ()


@dataclass(frozen=True)
class Entity:
    id: str
    source_id: str
    environment: str
    kind: str = "UNKNOWN"
    observed: bool = True


@dataclass(frozen=True)
class MetricObservation:
    id: str
    time: EventTime
    entity_id: str
    name: str
    value: float | None
    unit: str | None
    provenance: Provenance
    kind: str = "metric"


@dataclass(frozen=True)
class LogEvent:
    id: str
    time: EventTime
    entity_id: str
    message: str | None
    severity: str | None
    provenance: Provenance
    kind: str = "log"


@dataclass(frozen=True)
class TraceSpan:
    id: str
    time: EventTime
    entity_id: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    duration_raw: str | None
    duration_unit: str | None
    end_time: EventTime | None
    status: str | None
    provenance: Provenance
    kind: str = "span"


@dataclass(frozen=True)
class Dependency:
    id: str
    source_entity: str
    target_entity: str
    relation: str
    evidence_ids: tuple[str, ...]
    time: EventTime
    category: str = "observed_structural"


@dataclass(frozen=True)
class FaultEvent:
    id: str
    time: EventTime
    entity_id: str
    reason: str | None
    provenance: Provenance
    end_time: EventTime | None = None
    epistemic_status: str = "source_label_not_inferred"


@dataclass(frozen=True)
class GroundTruth:
    incident_id: str
    events: tuple[FaultEvent, ...]
    queries: tuple[dict[str, str], ...] = ()
    source: str = "external_evaluation_labels"


@dataclass
class Incident:
    id: str
    environment: str
    start_ns: int
    end_ns: int
    entities: dict[str, Entity] = field(default_factory=dict)
    observations: list[Any] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    ground_truth: GroundTruth | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def operational_dict(self) -> dict:
        result = asdict(self)
        result.pop("ground_truth")
        return result

    def to_dict(self) -> dict:
        return asdict(self)
