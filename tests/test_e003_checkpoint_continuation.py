import json
import sqlite3
import zlib
import pytest
from dce_foundation.qualification.compact import SCHEMA
from dce_foundation.qualification.continuation_run import inherit_blocks
from dce_foundation.domain import canonical_json
from dce_foundation.inspection import file_hash


@pytest.mark.parametrize('bad_count', [False, True])
def test_completed_blocks_only_and_parent_untouched(tmp_path, bad_count):
    old = tmp_path/'old'
    old.mkdir()
    parent = old/'context.sqlite'
    db = sqlite3.connect(parent)
    db.executescript(SCHEMA)
    for i in range(1,78):
        p = {'source_key':str(i),'path':f'file{i}','scenario':'Bank','decision':'QUALIFIED',
             'crc_eof_verified':True,'row_conservation':True,'decompressed_sha256':'fixture',
             'selection_counts':{'mapped':(2 if bad_count else 1) if i==1 else 0}}
        (old/f'file-{i:03d}.json').write_text(json.dumps(p))
        db.execute('INSERT INTO sources VALUES (?,?,?,?,?)',(str(i),'Bank',p['path'],'QUALIFIED',canonical_json(p)))
    body=zlib.compress(b'[[1,2,"mapped",null,{"value":"1"}]]')
    for key in ('1','incomplete'):
        db.execute('INSERT INTO blocks(source_key,environment,signal,min_ns,max_ns,records,payload) VALUES (?,?,?,?,?,?,?)',
                   (key,'Bank','metric',1,1,1,body))
    db.commit()
    db.close()
    before=file_hash(parent)
    output=tmp_path/'new'
    output.mkdir()
    new=sqlite3.connect(output/'context.sqlite')
    new.executescript(SCHEMA)
    if bad_count:
        with pytest.raises(ValueError, match='conservation'):
            inherit_blocks(old,new,output)
    else:
        assert len(inherit_blocks(old,new,output))==77
        assert new.execute('SELECT source_key,payload FROM blocks').fetchall()==[('1',body)]
        assert len(list(output.glob('file-*.json')))==77
    new.close()
    assert file_hash(parent)==before
