"""Candidate-scale evidence uses source dates, precision and neighbours."""
from collections import Counter
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation

FACTORS = {"s": 10**9, "ms": 10**6, "us": 10**3, "ns": 1}


def epoch_ns(value, unit):
    try:
        x = Decimal(value) * FACTORS[unit]
        if not x.is_finite() or x != x.to_integral_value():
            raise ValueError("invalid or subnanosecond timestamp")
        ns = int(x)
        year = datetime.fromtimestamp(ns // 10**9, timezone.utc).year
        if not 2000 <= year <= 2100:
            raise ValueError("outside supported epoch range")
        return ns
    except (InvalidOperation, OverflowError, OSError, KeyError) as exc:
        raise ValueError("invalid timestamp") from exc


def day_bounds(date):
    dt = datetime.strptime(date, "%Y_%m_%d").replace(tzinfo=timezone(timedelta(hours=8)))
    start = int(dt.timestamp()) * 10**9
    return start, start + 86400 * 10**9


def profile(values, start, end, allowance_seconds=3600, minimum_support=0.99):
    counts = Counter()
    matches = []
    examples = []
    for value in values:
        units = []
        for unit in FACTORS:
            try:
                ns = epoch_ns(value, unit)
                if start - allowance_seconds * 10**9 <= ns < end + allowance_seconds * 10**9:
                    units.append(unit)
                    counts[unit] += 1
            except ValueError:
                pass
        matches.append(units)
        if len(examples) < 8:
            examples.append({"source_value": value, "candidate_units": units})
    supported = [u for u in FACTORS if counts[u]]
    selected = supported[0] if len(supported) == 1 and counts[supported[0]] / max(1, len(values)) >= minimum_support else None
    status = "validated_sample" if selected else ("ambiguous" if supported else "invalid")
    ns_values = []
    if selected:
        for v in values:
            try:
                ns_values.append(epoch_ns(v, selected))
            except ValueError:
                pass
    deltas = Counter(b - a for a, b in zip(ns_values, ns_values[1:]))
    return {"status": status, "selected_unit": selected, "rows": len(values),
            "candidate_support": dict(counts), "support_fraction": counts[selected] / len(values) if selected else None,
            "confidence_basis": "unique scale + source-local date; bounded sample, not whole-file certainty",
            "expected_window_ns": [start, end], "boundary_allowance_seconds": allowance_seconds,
            "sample_examples": examples, "out_of_order_transitions": sum(v for k,v in deltas.items() if k < 0),
            "neighbour_delta_ns_examples": dict(list(sorted(deltas.items()))[:12])}


def classify(value, interpretation, start, end):
    unit = interpretation["selected_unit"]
    if unit is None:
        return interpretation["status"], None
    try:
        ns = epoch_ns(value, unit)
    except ValueError:
        for other in FACTORS:
            try:
                if other != unit and start <= epoch_ns(value, other) < end:
                    return "ambiguous", None
            except ValueError:
                pass
        return "rejected", None
    # A later row with another plausible scale invalidates mapping, not the frozen profile.
    if not start <= ns < end:
        other = []
        for u in FACTORS:
            try:
                if u != unit and start <= epoch_ns(value, u) < end:
                    other.append(u)
            except ValueError:
                pass
        return ("ambiguous" if other else "out_of_window"), None
    return "mapped", ns
