"""Write-ahead, replayable host-dispatch requests. No auth token access."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from .ledger import BudgetExceeded

class PendingHostCall(RuntimeError):pass

def canonical(payload):return json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS host_requests(request_hash TEXT PRIMARY KEY,call_id INTEGER UNIQUE NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,response TEXT,receipt TEXT)')

def request(ledger,payload,scope,scope_task_id,cap):
    serialized=canonical(payload);digest=hashlib.sha256(serialized.encode()).hexdigest();folder=ledger.path.parent/'host_requests';folder.mkdir(parents=True,exist_ok=True);path=folder/(digest+'.json')
    with ledger._connect() as db:
        initialize(db);db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT call_id,payload,status,response FROM host_requests WHERE request_hash=?',(digest,)).fetchone()
        if row:
            if row[1]!=serialized:raise ValueError('host request hash collision')
            call_id,_,status,response=row
        else:
            count=db.execute('SELECT count(*) FROM calls WHERE scope=? AND task_id=?',(scope,scope_task_id)).fetchone()[0]
            if count>=cap:db.execute('ROLLBACK');raise BudgetExceeded(f'{scope} host-dispatch budget exhausted ({count}/{cap})')
            cur=db.execute('INSERT INTO calls(scope,task_id,provider,purpose,status,created,model,detail) VALUES(?,?,?,?,?,?,?,?)',(scope,scope_task_id,payload['provider'],payload['purpose'],'pending_host',datetime.now(timezone.utc).isoformat(),payload['model'],'codex_host reservation; dispatch provenance pending'))
            call_id=cur.lastrowid;status='pending';response=None
            db.execute('INSERT INTO host_requests(request_hash,call_id,payload,status) VALUES(?,?,?,?)',(digest,call_id,serialized,status))
        db.execute('COMMIT')
    artifact={'request_hash':digest,'call_id':call_id,'accounting_unit':'host_dispatches','request':payload,'response_import':'polishpaper llm respond REQUEST --response FILE --model MODEL --receipt FILE','provenance_limit':'Response import requires an operator-supplied actual host-tool dispatch receipt. The importer does not cryptographically verify model identity.'}
    if not path.exists():
        try:
            with path.open('x') as stream:stream.write(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
        except FileExistsError:pass
    else:
        existing=json.loads(path.read_text())
        if existing.get('request_hash')!=digest or canonical(existing.get('request'))!=serialized:raise ValueError('immutable host request artifact changed')
    if status=='completed':return response
    raise PendingHostCall('Host response pending: '+str(path))

def pending(ledger):
    with ledger._connect() as db:
        initialize(db);rows=db.execute("SELECT request_hash,call_id,payload,status FROM host_requests WHERE status!='completed' ORDER BY call_id").fetchall()
    return [{'request_hash':h,'call_id':i,'task_id':json.loads(p)['task_id'],'purpose':json.loads(p)['purpose'],'requested_model':json.loads(p)['model'],'status':s,'path':str(ledger.path.parent/'host_requests'/(h+'.json'))} for h,i,p,s in rows]

def respond(ledger,request_path,response_path,model,receipt_path):
    artifact=json.loads(Path(request_path).read_text());payload=artifact['request'];digest=hashlib.sha256(canonical(payload).encode()).hexdigest()
    if digest!=artifact['request_hash']:raise ValueError('host request hash changed')
    if model!=payload['model']:raise ValueError('response model does not match requested model')
    raw=Path(response_path).read_text();receipt=json.loads(Path(receipt_path).read_text())
    if not raw.strip():raise ValueError('empty host response')
    for key in ('dispatch_tool','requested_model','agent_id','dispatched_at'):
        if not isinstance(receipt.get(key),str) or not receipt[key]:raise ValueError('host receipt requires '+key)
    if receipt['requested_model']!=model or receipt['dispatch_tool']!='collaboration.spawn_agent':raise ValueError('receipt must identify actual requested host-agent dispatch')
    receipt={**receipt,'import_attestation':'operator-supplied actual host-tool receipt; identity not cryptographically verified','response_sha256':hashlib.sha256(raw.encode()).hexdigest()}
    with ledger._connect() as db:
        initialize(db);db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT call_id,payload,status,response,receipt FROM host_requests WHERE request_hash=?',(digest,)).fetchone()
        if not row or row[1]!=canonical(payload):db.execute('ROLLBACK');raise ValueError('unknown or mismatched reserved host request')
        if row[2]=='completed':
            db.execute('ROLLBACK')
            if row[3]!=raw:raise ValueError('completed host response cannot be replaced')
            return {'status':'already_imported','call_id':row[0]}
        db.execute('UPDATE host_requests SET status=?,response=?,receipt=? WHERE request_hash=?',('completed',raw,canonical(receipt),digest))
        db.execute('UPDATE calls SET status=?,detail=? WHERE id=?',('completed','codex_host response; operator-supplied dispatch receipt; '+digest,row[0]));db.execute('COMMIT')
    response_artifact=Path(request_path).with_suffix('.response.json');response_artifact.write_text(json.dumps({'request_hash':digest,'raw_response':raw,'receipt':receipt},ensure_ascii=False,indent=2)+'\n')
    return {'status':'imported','call_id':row[0],'request_hash':digest}
