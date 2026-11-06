"""Compressed blocks conserve source values, outcomes and query evidence."""
import json
import sqlite3
import zlib
from dce_foundation.domain import canonical_json,digest
from dce_foundation.qualification.compact import SCHEMA,BlockWriter,block_rows,projected_context_rows
from dce_foundation.qualification.projection import query_projection


def test_block_storage_fidelity_time_bounds_and_projection(tmp_path):
    db=sqlite3.connect(tmp_path/'context.sqlite')
    db.executescript(SCHEMA)
    writer=BlockWriter(db)
    db.execute('INSERT INTO sources VALUES (?,?,?,?,?)',('key','env','metric.csv','QUALIFIED','{}'))
    original=[]
    for i in range(2500):
        raw={'timestamp':str(i),'cmdb_id':'server','kpi_name':'metric','value':'0.00000000000000001','extra':'preserved'}
        oid='row:'+digest(['key',i+2])
        original.append((oid,i,'metric','env',raw))
        writer.execute('INSERT INTO context',(oid,'key',i+2,i,'env','metric','server','mapped',None,zlib.compress(canonical_json(raw).encode())))
    writer.commit()
    assert db.execute('SELECT sum(records) FROM blocks').fetchone()[0]==2500
    assert db.execute('SELECT count(*) FROM blocks').fetchone()[0]==3
    recovered=list(projected_context_rows(db,'env',100,200))
    assert recovered==original[100:201]
    assert query_projection(recovered,100,200)==query_projection(original,100,200)
    assert recovered[0][4]['extra']=='preserved'
    db.close()


def test_unqualified_source_and_rejected_rows_are_never_inference(tmp_path):
    db=sqlite3.connect(tmp_path/'context.sqlite')
    db.executescript(SCHEMA)
    db.execute('INSERT INTO sources VALUES (?,?,?,?,?)',('key','env','source','AMBIGUOUS_OR_INVALID','{}'))
    writer=BlockWriter(db)
    writer.execute('INSERT INTO context',('row','key',2,10,'env','metric','r','mapped',None,zlib.compress(b'{"cmdb_id":"r","kpi_name":"m","value":"1"}')))
    writer.commit()
    assert list(projected_context_rows(db,'env',0,20))==[]
    audit=list(block_rows(db,'env',0,20,True))
    assert audit[0][5]=='source_unqualified'
    db.close()
