"""All-file header audit and bounded profiling; no archive extraction."""
from collections import Counter
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
from pathlib import Path, PurePosixPath
import zipfile
from .telemetry.openrca import HEADERS, LABEL_HEADERS, SCENARIOS, OpenRCAAdapter
from .event_time import normalize_time


def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(4*1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def inspect_dataset(root, profile_rows=256):
    root=Path(root)
    archives=[]
    schemas={}
    labels={}
    label_issues=[]
    for path in sorted(root.glob("*.zip")):
        entries=[]
        with zipfile.ZipFile(path) as z:
            for info in sorted(z.infolist(),key=lambda i:i.filename):
                if info.is_dir(): continue
                item={"path":info.filename,"size":info.file_size,"compressed_size":info.compress_size,"zip_crc32":f"{info.CRC:08x}"}
                if info.filename.endswith(".csv"):
                    with z.open(info) as f:
                        reader=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig",newline=""))
                        headers=reader.fieldnames
                        rows=[]
                        for row in reader:
                            rows.append(row)
                            if len(rows)>=profile_rows and PurePosixPath(info.filename).name not in LABEL_HEADERS: break
                        name=PurePosixPath(info.filename).name
                        key=info.filename.split("/")[0]+":"+name+":"+",".join(headers or [])
                        schema=schemas.setdefault(key,{"fields":headers,"paths":[],"profiled_rows":0,"missing":Counter(),"duplicate_profile_rows":0,"cardinality":{},"row_shape_errors":0})
                        schema["paths"].append(info.filename)
                        schema["profiled_rows"]+=len(rows)
                        schema["row_shape_errors"]+=sum(None in r or any(v is None for v in r.values()) for r in rows)
                        for r in rows:
                            schema["missing"].update(k for k,v in r.items() if v in (None,""))
                        schema["duplicate_profile_rows"]+=len(rows)-len({tuple(sorted(r.items(),key=lambda x:str(x[0]))) for r in rows})
                        for h in headers or []:
                            schema["cardinality"][h]=max(schema["cardinality"].get(h,0),len({r.get(h) for r in rows}))
                        item["header"]=headers
                        item["profiled_rows"]=len(rows)
                        if name in LABEL_HEADERS:
                            labels[info.filename]={"rows":len(rows),"fields":headers}
                            if name=="record.csv":
                                for line,r in enumerate(rows,2):
                                    try:
                                        t=normalize_time(r["timestamp"],"timestamp","s")
                                        dt=datetime.strptime(r["datetime"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                                        if int(dt.timestamp())*10**9!=t.epoch_ns:
                                            label_issues.append({"path":info.filename,"row":line,"error":"datetime/epoch disagreement"})
                                    except (ValueError,KeyError) as e:
                                        label_issues.append({"path":info.filename,"row":line,"error":str(e)})
                entries.append(item)
        archives.append({"path":path.as_posix(),"bytes":path.stat().st_size,"sha256":file_hash(path),"entries":entries})
    for schema in schemas.values(): schema["missing"]=dict(sorted(schema["missing"].items()))
    unsupported=[]
    for archive in archives:
        for entry in archive["entries"]:
            if not entry["path"].endswith(".csv"): continue
            system=entry["path"].split("/")[0]
            name=PurePosixPath(entry["path"]).name
            expected=LABEL_HEADERS.get(name) or set(HEADERS.get(system,{}).get(name,()))
            if set(entry["header"] or [])!=set(expected): unsupported.append(entry["path"])
    return {"dataset":"OpenRCA","source":"https://github.com/microsoft/OpenRCA",
            "local_source_path":root.resolve().as_posix(),"source_version":"UNKNOWN",
            "telemetry_license_provenance":"UNKNOWN; repository licence does not independently verify downloaded telemetry rights",
            "schema_version":"openrca-inspected-v1","processing_version":"dce-foundation-0.1.0",
            "raw_policy":"read-only originals in place; reference manifest",
            "archive_integrity":"archive SHA256 recorded; CSV prefixes read; full decompression CRC test NOT performed",
            "profile_rows_per_telemetry_file":profile_rows,"profile_scope":"prefix per file; cardinality = max distinct in a single profiled file, NOT full population",
            "archives":archives,"schemas":schemas,"label_counts":labels,"label_timestamp_issues":label_issues,
            "unsupported_headers":unsupported}
