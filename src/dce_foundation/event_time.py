from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from .domain import EventTime


def normalize_time(value: str, field: str, unit: str) -> EventTime:
    factors = {"s": 1_000_000_000, "ms": 1_000_000}
    if unit not in factors:
        raise ValueError(f"unsupported epoch unit: {unit}")
    try:
        number = Decimal(value)
        if not number.is_finite():
            raise ValueError("nonfinite timestamp")
        exact = number * factors[unit]
        if exact != exact.to_integral_value():
            raise ValueError("timestamp precision exceeds nanoseconds")
        ns = int(exact)
        seconds, remainder = divmod(ns, 1_000_000_000)
        dt = datetime.fromtimestamp(seconds, timezone.utc)
        if not 2000 <= dt.year <= 2100:
            raise ValueError("timestamp outside supported experiment range 2000..2100")
    except (InvalidOperation, OverflowError, OSError) as exc:
        raise ValueError(f"invalid timestamp: {value!r}") from exc
    # Integer timestamps declare source granularity, not clock accuracy.
    precision = max(1, int(Decimal(factors[unit]) * Decimal(10) ** min(0, number.as_tuple().exponent)))
    utc = dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{remainder:09d}Z"
    return EventTime(ns, utc, value, field, unit, precision)
