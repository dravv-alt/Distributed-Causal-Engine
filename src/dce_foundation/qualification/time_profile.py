"""Constant-memory complete timestamp census, with exact Decimal event time."""
from collections import Counter
from decimal import Decimal, InvalidOperation
from ..representation_v2.timestamps import FACTORS


class FullTimeProfile:
    def __init__(self,start,end,allowance=3600):
        self.start,self.end = start,end
        self.lower = {u:Decimal(start-allowance*10**9)/f for u,f in FACTORS.items()}
        self.upper = {u:Decimal(end+allowance*10**9)/f for u,f in FACTORS.items()}
        self.epoch_lower = {u:Decimal(946684800*10**9)/f for u,f in FACTORS.items()}
        self.epoch_upper = {u:Decimal(4133980800*10**9)/f for u,f in FACTORS.items()}
        self.counts = Counter()
        self.date_units = Counter()
        self.epoch_units = Counter()
        self.minimum,self.maximum,self.previous = None,None,None

    def observe(self,text):
        self.counts['rows_seen'] += 1
        try:
            value = Decimal(text)
            if not value.is_finite():
                raise ValueError('nonfinite timestamp')
            units = [u for u in FACTORS if self.epoch_lower[u] <= value < self.epoch_upper[u]]
            date_units = [u for u in FACTORS if self.lower[u] <= value < self.upper[u]]
            self.date_units.update(date_units)
            self.epoch_units.update(units)
            if len(units) != 1:
                self.counts['ambiguous_rows' if units else 'invalid_rows'] += 1
                return 'ambiguous' if units else 'invalid',None,None
            unit = units[0]
            exact = value*FACTORS[unit]
            if exact != exact.to_integral_value():
                raise ValueError('subnanosecond precision')
            ns = int(exact)
            self.minimum = ns if self.minimum is None else min(self.minimum,ns)
            self.maximum = ns if self.maximum is None else max(self.maximum,ns)
            if self.previous is not None and ns < self.previous:
                self.counts['out_of_order'] += 1
            self.previous = ns
            state = 'in_window' if self.start <= ns < self.end else 'out_of_window'
            self.counts[state] += 1
            return state,ns,unit
        except (ValueError,InvalidOperation,TypeError):
            self.counts['malformed_rows'] += 1
            return 'malformed',None,None

    def report(self):
        supported = [u for u,c in self.date_units.items() if c]
        observed = [u for u,c in self.epoch_units.items() if c]
        unit = supported[0] if len(supported)==1 and observed==supported else None
        return {'counts':dict(self.counts),'candidate_date_support':dict(self.date_units),
                'candidate_epoch_support':dict(self.epoch_units),'selected_scale':unit,
                'decision':'QUALIFIED' if unit else 'AMBIGUOUS_OR_INVALID',
                'min_timestamp_ns':self.minimum,'max_timestamp_ns':self.maximum,
                'source_day_ns':[self.start,self.end],
                'selection_evidence':'entire-file unique candidate + directory date + neighbour ordering; no magnitude-only selection',
                'row_conservation':self.counts['rows_seen']==sum(self.counts[x] for x in ('in_window','out_of_window','ambiguous_rows','invalid_rows','malformed_rows'))}
