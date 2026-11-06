"""Human-only decisions and their incrementally searchable original/comment pairs."""
from __future__ import annotations
import json,sqlite3
from pathlib import Path

def record(task_dir,decisions_path,db_path):
    import yaml
    task=Path(task_dir);decisions=yaml.safe_load(Path(decisions_path).read_text()) or {}
    if not isinstance(decisions,dict):raise ValueError('decisions must map change IDs to accept/reject records')
    draft=json.loads((task/'draft.json').read_text());card=json.loads((task/'taskcard.json').read_text())
    evidence=json.loads((task/'evidence.json').read_text()) if (task/'evidence.json').exists() else {'items':[]}
    evidence_map={e['evidence_id']:e for e in evidence['items']}
    path=Path(db_path);path.parent.mkdir(parents=True,exist_ok=True);count=0
    known={c['change_id'] for c in draft['changes']}
    if set(decisions)-known:raise ValueError('unknown change IDs in decisions')
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS feedback(task_id TEXT,change_id TEXT,decision TEXT,original TEXT,new TEXT,evidence TEXT,section_type TEXT,concepts TEXT,note TEXT,PRIMARY KEY(task_id,change_id))')
        for c in draft['changes']:
            d=decisions.get(c['change_id'])
            if d is None or (isinstance(d,dict) and d.get('decision') is None):continue
            if not isinstance(d,dict) or d.get('decision') not in ('accept','reject'):raise ValueError('decision must be accept or reject')
            db.execute('INSERT OR REPLACE INTO feedback VALUES(?,?,?,?,?,?,?,?,?)',(task.name,c['change_id'],d['decision'],c['original_sentence'],c['revised_sentence'],json.dumps([evidence_map[s] for s in c['sources']]),card['section_type'],json.dumps(card['concepts']),d.get('note','')));count+=1
    return count

def index_objects(db_path):
    if not Path(db_path).exists():return []
    with sqlite3.connect(db_path) as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE name='feedback'").fetchone()
        rows=db.execute('SELECT task_id,change_id,decision,original,new,evidence,section_type,concepts,note FROM feedback').fetchall() if exists else []
    from .reviewed_feedback import database_objects
    return [{'kind':'feedback','id':f'feedback:{t}:{c}','text':f'Original: {o}\nCandidate: {n}\nDecision: {d}\nUser comment: {note}','section_type':st,'concepts':json.loads(cs),'source_tag':'real_annotation','conditions':['Human decision on this exact change; contextual evidence, not a universal rule'],'provenance':{'task_id':t,'change_id':c,'decision':d,'original':o,'candidate':n,'comment':note,'sources':json.loads(e)}} for t,c,d,o,n,e,st,cs,note in rows]+database_objects(db_path)

def update_index(db_path,directory,embedder):
    from ..index.search import upsert,retrieve
    directory=Path(directory)
    feedback=index_objects(db_path);upsert(feedback,directory,embedder)
    for obj in feedback:
        hits=retrieve(directory,embedder,obj['text'],obj['section_type'],obj['concepts'],[obj['kind']],len(feedback))
        if obj['id'] not in {h['id'] for h in hits}:raise RuntimeError('feedback self-retrieval failed')
    return len(feedback)

def raw_objects(directory):
    """Preserve imported human/teacher attribution; never infer a resolution."""
    import yaml
    objects=[]
    for path in sorted(Path(directory).glob('*.yaml')):
        data=yaml.safe_load(path.read_text());rows=data if isinstance(data,list) else [data]
        for i,row in enumerate(rows):
            if not isinstance(row,dict):raise ValueError(f'{path}: raw feedback must be an object')
            original=row.get('original_text',row.get('original'))
            if not isinstance(original,str) or not isinstance(row.get('comment'),str):raise ValueError(f'{path}: raw feedback requires original_text/comment')
            tag=row.get('source_tag','real_annotation')
            if tag not in ('real_annotation','teacher_note'):raise ValueError('raw feedback attribution must be real_annotation or teacher_note')
            objects.append({'kind':'feedback','id':f'feedback_raw:{path.name}:{i}','text':original+'\n'+row['comment'],'source_tag':tag,'section_type':row.get('section_type','unknown'),'concepts':row.get('concepts',[]),'conditions':row.get('conditions',[]),'provenance':{'file':str(path),'record_index':i,'record':row}})
            if isinstance(row.get('teacher_note'),str) and row['teacher_note'].strip():objects.append({**objects[-1],'id':f'teacher_note:{path.name}:{i}','text':original+'\n'+row['teacher_note'],'source_tag':'teacher_note'})
    return objects
