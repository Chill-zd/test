from __future__ import annotations
import json,sqlite3
from pathlib import Path
import numpy as np

class SearchResults(list):
    def __init__(self,items=(),no_domain_evidence=False):super().__init__(items);self.no_domain_evidence=no_domain_evidence

def build(objects,directory,embedder):
    p=Path(directory);p.mkdir(parents=True,exist_ok=True)
    fingerprint=getattr(embedder,"fingerprint",None)
    vectors=embedder.encode([o["text"] for o in objects]) if objects else np.empty((0,0),dtype=np.float32)
    np.save(p/"vectors.npy",vectors)
    if fingerprint:(p/"embedding.json").write_text(json.dumps({"fingerprint":fingerprint,"dimensions":vectors.shape[1] if len(vectors) else 0}))
    with sqlite3.connect(p/"meta.sqlite") as db:
        db.execute("DROP TABLE IF EXISTS objects")
        db.execute("CREATE TABLE objects(rowid INTEGER PRIMARY KEY,kind TEXT,id TEXT,section_type TEXT,concepts TEXT,payload TEXT)")
        db.execute("CREATE INDEX IF NOT EXISTS ix_object_kind_section ON objects(kind,section_type)")
        db.executemany("INSERT INTO objects(rowid,kind,id,section_type,concepts,payload) VALUES(?,?,?,?,?,?)",[(i,o["kind"],o["id"],o.get("section_type","unknown"),json.dumps(o.get("concepts",[])),json.dumps(o,ensure_ascii=False)) for i,o in enumerate(objects)])

def retrieve(directory,embedder,query_text,section_type,concepts,kinds,top_k,*,exclude=None):
    p=Path(directory)
    if not (p/"vectors.npy").exists() or not kinds:return SearchResults(no_domain_evidence=True)
    check_fingerprint(p,embedder)
    v=np.load(p/"vectors.npy")
    if len(v)==0:return SearchResults(no_domain_evidence=True)
    marks=",".join("?" for _ in kinds)
    with sqlite3.connect(p/"meta.sqlite") as db:
        sql=f"SELECT rowid,concepts,payload FROM objects WHERE kind IN ({marks}) AND section_type IN (?, 'unknown')"
        params=[*kinds,section_type]
        if concepts:
            concept_marks=",".join("?" for _ in concepts)
            matched=db.execute(sql+f" AND EXISTS (SELECT 1 FROM json_each(objects.concepts) WHERE value IN ({concept_marks}))",params+list(concepts)).fetchall()
            if exclude is not None:matched=[row for row in matched if not exclude(json.loads(row[2]))]
            if not matched:
                matched=db.execute(sql,params).fetchall()
                if exclude is not None:matched=[row for row in matched if not exclude(json.loads(row[2]))]
        else:matched=db.execute(sql,params).fetchall()
        if not concepts and exclude is not None:matched=[row for row in matched if not exclude(json.loads(row[2]))]
    if not matched:return SearchResults(no_domain_evidence=True)
    q=np.asarray(embedder.encode([query_text])[0],dtype=np.float32);qn=np.linalg.norm(q)
    scored=[]
    for row in matched:
        vec=v[row[0]];den=float(np.linalg.norm(vec)*qn)
        scored.append((float(np.dot(vec,q)/den) if den else 0.0,json.loads(row[2])))
    scored.sort(key=lambda x:x[0],reverse=True)
    selected=[{"score":score,**obj} for score,obj in scored[:top_k]]
    from ..memory.reviewed_feedback import assert_object_fresh
    cache={}
    for obj in selected:assert_object_fresh(obj,cache)
    return SearchResults(selected,no_domain_evidence=False)

def upsert(objects,directory,embedder):
    """Embed only new/changed objects; retain unaffected rows and vectors."""
    p=Path(directory)
    if not (p/'meta.sqlite').exists():return build(objects,p,embedder)
    check_fingerprint(p,embedder)
    with sqlite3.connect(p/'meta.sqlite') as db:old=[json.loads(r[0]) for r in db.execute('SELECT payload FROM objects ORDER BY rowid')]
    vectors=np.load(p/'vectors.npy');by_id={o['id']:i for i,o in enumerate(old)}
    changed=[o for o in objects if o['id'] not in by_id or old[by_id[o['id']]]['text']!=o['text']]
    new_vectors=embedder.encode([o['text'] for o in changed]) if changed else []
    encoded={o['id']:v for o,v in zip(changed,new_vectors)}
    for o in objects:
        if o['id'] in by_id:old[by_id[o['id']]]=o
        else:by_id[o['id']]=len(old);old.append(o)
    result=[]
    for o in old:
        i=by_id[o['id']];result.append(encoded[o['id']] if o['id'] in encoded else vectors[i])
    class Cached:
        def encode(self,texts):return np.asarray(result,dtype=np.float32)
    build(old,p,Cached())


def check_fingerprint(directory,embedder):
    p=Path(directory)/'embedding.json';fingerprint=getattr(embedder,'fingerprint',None)
    if p.exists() and fingerprint and json.loads(p.read_text())['fingerprint']!=fingerprint:raise ValueError('embedding configuration changed; rebuild index')
