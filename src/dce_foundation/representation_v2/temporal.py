"""Small event-time window accumulator used by the XP004 experiment.

This module is experimental and is not wired into the delivered R0 package or
the production application. It uses explicit event-time ordering, a bounded
out-of-order allowance, separate presence/value masks, and a documented
counter-reset rule. Unknown source metric semantics must not be passed here as
if they were verified counters.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class TimedSample:
    event_id: str
    series_id: str
    event_ns: int
    value: str | None


class EventTimeWindowAccumulator:
    """Accumulate explicitly declared synthetic counter samples by event time."""

    def __init__(self, start_ns: int, end_ns: int, window_ns: int, allowed_lateness_ns: int):
        if start_ns >= end_ns or window_ns <= 0 or allowed_lateness_ns < 0:
            raise ValueError("invalid temporal bounds")
        if (end_ns - start_ns) % window_ns:
            raise ValueError("window width must divide the interval")
        self.start_ns = start_ns
        self.end_ns = end_ns
        self.window_ns = window_ns
        self.allowed_lateness_ns = allowed_lateness_ns
        self._max_seen_ns: int | None = None
        self._seen_ids: set[str] = set()
        self._accepted: list[TimedSample] = []
        self._rejected: list[dict[str, str]] = []

    def ingest(self, sample: TimedSample) -> None:
        if sample.event_id in self._seen_ids:
            self._rejected.append({"event_id": sample.event_id, "reason": "duplicate_event_id"})
            return
        self._seen_ids.add(sample.event_id)
        if not self.start_ns <= sample.event_ns < self.end_ns:
            self._rejected.append({"event_id": sample.event_id, "reason": "out_of_window"})
            return
        if self._max_seen_ns is not None and sample.event_ns < self._max_seen_ns - self.allowed_lateness_ns:
            self._rejected.append({"event_id": sample.event_id, "reason": "beyond_allowed_lateness"})
            return
        if sample.value is not None:
            try:
                value = Decimal(sample.value)
                if not value.is_finite() or value < 0:
                    raise ValueError("counter value must be finite and nonnegative")
            except InvalidOperation as exc:
                raise ValueError("counter value is not numeric") from exc
        self._accepted.append(sample)
        self._max_seen_ns = sample.event_ns if self._max_seen_ns is None else max(self._max_seen_ns, sample.event_ns)

    @property
    def accepted(self) -> tuple[TimedSample, ...]:
        return tuple(self._accepted)

    @property
    def rejected(self) -> tuple[dict[str, str], ...]:
        return tuple(self._rejected)

    def result(self) -> dict:
        windows: dict[str, dict] = {}
        previous: dict[str, Decimal] = {}
        for sample in sorted(self._accepted, key=lambda x: (x.event_ns, x.series_id, x.event_id)):
            index = (sample.event_ns - self.start_ns) // self.window_ns
            start = self.start_ns + index * self.window_ns
            key = str(start)
            feature = windows.setdefault(key, {
                "start_ns": start, "end_ns": start + self.window_ns,
                "observation_mask": 0, "value_mask": 0, "sample_count": 0,
                "valid_value_count": 0, "missing_value_count": 0,
                "counter_delta_count": 0, "counter_delta_total": "0", "reset_count": 0,
            })
            feature["observation_mask"] = 1
            feature["sample_count"] += 1
            if sample.value is None:
                feature["missing_value_count"] += 1
                continue
            value = Decimal(sample.value)
            feature["value_mask"] = 1
            feature["valid_value_count"] += 1
            prior = previous.get(sample.series_id)
            if prior is None:
                previous[sample.series_id] = value
                continue
            if value < prior:
                delta = value
                feature["reset_count"] += 1
            else:
                delta = value - prior
            previous[sample.series_id] = value
            feature["counter_delta_count"] += 1
            feature["counter_delta_total"] = str(Decimal(feature["counter_delta_total"]) + delta)

        # Emit empty windows too, so the observation mask distinguishes no rows
        # from a row with an explicitly missing value.
        window_count = (self.end_ns - self.start_ns) // self.window_ns
        for index in range(window_count):
            start = self.start_ns + index * self.window_ns
            windows.setdefault(str(start), {
                "start_ns": start, "end_ns": start + self.window_ns,
                "observation_mask": 0, "value_mask": 0, "sample_count": 0,
                "valid_value_count": 0, "missing_value_count": 0,
                "counter_delta_count": 0, "counter_delta_total": "0", "reset_count": 0,
            })
        return {"windows": [windows[key] for key in sorted(windows, key=int)],
                "accepted_ids": sorted(sample.event_id for sample in self._accepted),
                "rejected": list(self._rejected)}
