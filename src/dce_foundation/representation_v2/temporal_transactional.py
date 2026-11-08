"""Additive event-time accumulator with transactional input validation.

The original ``temporal.EventTimeWindowAccumulator`` remains unchanged for
historical experiments. This candidate parses and validates before mutating
event-ID, accepted/rejected, or watermark state.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .temporal import EventTimeWindowAccumulator, TimedSample


class TransactionalEventTimeWindowAccumulator(EventTimeWindowAccumulator):
    """Leave accumulator state unchanged when a sample fails value validation."""

    def ingest(self, sample: TimedSample) -> None:
        if sample.event_id in self._seen_ids:
            self._rejected.append(
                {"event_id": sample.event_id, "reason": "duplicate_event_id"}
            )
            return

        # Out-of-window and late samples are terminal, explicit rejections.
        # They differ from invalid numeric input, which raises and can be fixed.
        if not self.start_ns <= sample.event_ns < self.end_ns:
            self._seen_ids.add(sample.event_id)
            self._rejected.append(
                {"event_id": sample.event_id, "reason": "out_of_window"}
            )
            return
        if (
            self._max_seen_ns is not None
            and sample.event_ns < self._max_seen_ns - self.allowed_lateness_ns
        ):
            self._seen_ids.add(sample.event_id)
            self._rejected.append(
                {"event_id": sample.event_id, "reason": "beyond_allowed_lateness"}
            )
            return

        # Decimal parsing has no side effects; mutate state only after it passes.
        if sample.value is not None:
            try:
                value = Decimal(sample.value)
                if not value.is_finite() or value < 0:
                    raise ValueError("counter value must be finite and nonnegative")
            except InvalidOperation as exc:
                raise ValueError("counter value is not numeric") from exc

        self._seen_ids.add(sample.event_id)
        self._accepted.append(sample)
        self._max_seen_ns = (
            sample.event_ns
            if self._max_seen_ns is None
            else max(self._max_seen_ns, sample.event_ns)
        )
