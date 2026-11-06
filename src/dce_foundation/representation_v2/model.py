"""Source-independent canonical values. UNKNOWN is deliberate, not a default guess."""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
from ..domain import canonical_json, digest


class ResourceKind(str, Enum):
    SERVICE = "SERVICE"
    POD = "POD"
    CONTAINER = "CONTAINER"
    HOST = "HOST"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    QUEUE = "QUEUE"
    APPLICATION = "APPLICATION"
    UNKNOWN = "UNKNOWN"


class Relation(str, Enum):
    CALLS = "CALLS"
    DEPENDS_ON = "DEPENDS_ON"
    RUNS_ON = "RUNS_ON"
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    HOSTS = "HOSTS"


@dataclass(frozen=True)
class SourceRef:
    source: str
    source_key: str
    row: int
    attributes: dict[str, Any]
    interpretation: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Resource:
    resource_id: str
    resource_kind: ResourceKind
    canonical_name: str
    source_name: str
    environment: str
    provenance: SourceRef
    namespace: str | None = None
    aliases: tuple[str, ...] = ()


def resource(environment, name, provenance, kind=ResourceKind.UNKNOWN, aliases=()):
    if not name or name != name.strip():
        raise ValueError("missing or whitespace identity")
    return Resource("resource:" + digest([environment, name]), kind, name, name,
                    environment, provenance, aliases=tuple(aliases))


@dataclass(frozen=True)
class MetricSemantics:
    metric_name: str
    source_metric_name: str
    source: str
    unit: str = "UNKNOWN"
    temporality: str = "UNKNOWN"
    aggregation: str = "UNKNOWN"
    kind: str = "UNKNOWN"
    description: str = "Source meaning unverified"
    provenance: SourceRef | None = None


class MetricRegistry:
    def __init__(self):
        self.entries = {}

    def register(self, entry):
        if entry.provenance is None:
            raise ValueError("semantic declarations require source evidence")
        key = (entry.source, entry.source_metric_name)
        if key in self.entries and self.entries[key] != entry:
            raise ValueError("conflicting semantics")
        self.entries[key] = entry

    def lookup(self, source, name):
        return self.entries.get((source, name), MetricSemantics(name, name, source))


@dataclass(frozen=True)
class Observation:
    object_id: str
    signal: str
    event_ns: int
    resource_id: str
    provenance: SourceRef
    metric: MetricSemantics | None = None
    value: str | None = None
    message: str | None = None
    severity: str = "UNKNOWN"
    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    service: str | None = None
    duration_raw: str | None = None
    duration_unit: str = "UNKNOWN"
    end_ns: int | None = None
    status_raw: str | None = None
    status_meaning: str = "UNKNOWN"
    quality: tuple[str, ...] = ()


@dataclass(frozen=True)
class Dependency:
    dependency_id: str
    source: str
    target: str
    relation_type: Relation
    evidence: tuple[str, ...]
    provenance: SourceRef
    epistemic_status: str = "OBSERVED"
    event_ns: int | None = None
    validity: str = "UNKNOWN"


@dataclass(frozen=True)
class QueryWindow:
    start_ns: int
    query_ns: int
    modalities: tuple[str, ...] = ("metric", "log", "span")
    future_information_policy: str = "exclude_event_time_after_query"

    def __post_init__(self):
        if self.start_ns > self.query_ns:
            raise ValueError("window starts after query")


@dataclass(frozen=True)
class FaultEvent:
    fault_id: str
    timestamp_ns: int
    target: str
    fault_type: str | None
    provenance: SourceRef
    end_ns: int | None = None


@dataclass(frozen=True)
class GroundTruth:
    incident_id: str
    root_cause: str
    injection_ns: int
    fault_type: str | None
    provenance: SourceRef
    root_cause_indicator: str | None = None


@dataclass(frozen=True)
class Incident:
    incident_id: str
    query_window: QueryWindow | None
    associated_faults: tuple[str, ...]
    association_rule: str = "UNKNOWN; evaluator owns query association"


def serialized(value):
    return canonical_json(asdict(value))
