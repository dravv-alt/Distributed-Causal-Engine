"""Evaluator-only annotations and explicit query associations; never inference features."""
from datetime import datetime,timezone,timedelta
import re
from ..representation_v2.timestamps import epoch_ns

LOCAL=timezone(timedelta(hours=8))
MONTHS={name.lower():n for n,name in enumerate(('January','February','March','April','May','June','July','August','September','October','November','December'),1)}


def parse_query_window(instruction):
    dates=re.findall(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(\d{4})',instruction,re.I)
    times=re.findall(r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b',instruction)
    if len(dates)!=1 or len(times)!=2:
        return None
    month,day,year=dates[0]
    try:
        values=[]
        for h,m,s in times:
            dt=datetime(int(year),MONTHS[month.lower()],int(day),int(h),int(m),int(s or 0),tzinfo=LOCAL)
            values.append(int(dt.timestamp())*10**9)
        return tuple(values) if values[0]<values[1] else None
    except ValueError:
        return None


def associations(queries,labels):
    result=[]
    for q in queries:
        scoring=q['raw']['scoring_points']
        # These patterns are from official main/evaluate.py; semantics are evaluator-owned.
        components=re.findall(r'The (?:\d+-th|only) predicted root cause component is ([^\n]+)',scoring)
        reasons=re.findall(r'The (?:\d+-th|only) predicted root cause reason is ([^\n]+)',scoring)
        times=re.findall(r'The (?:\d+-th|only) root cause occurrence time is within 1 minutes \(i.e., <=1min\) of ([^\n]+)',scoring)
        n=max(len(components),len(reasons),len(times))
        window=parse_query_window(q['raw']['instruction'])
        matched=[]
        errors=[]
        if not n or any(len(v) not in (0,n) for v in (components,reasons,times)):
            errors.append('unsupported scoring point structure')
        else:
            for i in range(n):
                candidates=[]
                for label in labels:
                    if label['scenario']!=q['scenario']:
                        continue
                    raw=label['raw']
                    if components and raw['component']!=components[i]:
                        continue
                    if reasons and raw['reason']!=reasons[i]:
                        continue
                    if times and raw['datetime']!=times[i]:
                        continue
                    if window and not window[0]<=label['fault_ns']<window[1]:
                        continue
                    candidates.append(label['incident_id'])
                if len(candidates)==1:
                    matched.extend(candidates)
                else:
                    errors.append('nonunique or absent label match')
        result.append({'query_id':q['query_id'],'scenario':q['scenario'],'status':'QUALIFIED' if not errors else 'UNKNOWN',
            'incident_ids':sorted(set(matched)),'source_window_ns':window,'errors':errors,
            'association_evidence':'exact official scoring-field elements + explicit instruction window where parseable; no positional join'})
    return result
