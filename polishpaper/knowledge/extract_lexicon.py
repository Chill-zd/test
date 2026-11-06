from __future__ import annotations
from .verify import verify_batch

def extract(client,paper_id,section_type,units,raw_dir):
    return _extract(client,'lexicon','gpt',paper_id,section_type,units,raw_dir)

def _extract(client,kind,provider,paper_id,section_type,units,raw_dir):
    import json,shutil
    from pathlib import Path
    from ..llm.host_bridge import PendingHostCall
    root=Path(raw_dir);root.mkdir(parents=True,exist_ok=True)
    stem=f'{paper_id}_{section_type}_{kind}';raw=root/f'{stem}.raw.json';verified=root/f'{stem}.verified.json';dropped=root/f'{stem}.dropped.json'
    if verified.exists():
        cached=json.loads(verified.read_text())
        if not cached[0].get('admission_status','verified').startswith('diagnostic'):return cached[0]['items']
    prompt=Path(__file__).parents[1]/'prompts'/f"{kind[:-1] if kind.endswith('s') else kind}_extract.md"
    instruction=prompt.read_text()
    from ..corpus.parser import strip_comments,CONCEPTS
    packet={'paper_id':paper_id,'section_type':section_type,'projection_policy':'Only comment-free author prose is supplied; physical raw source is retained separately for source verification.','units':[{'unit_id':u['unit_id'],'text':u.get('prose_text',strip_comments(u['text'])),'prose_sha256':u.get('prose_sha256'),'raw_source_sha256':u['sha256'],'file':u['file'],'line_start':u['line_start'],'line_end':u['line_end'],'offset_start':u.get('offset_start'),'offset_end':u.get('offset_end')} for u in units]}
    if kind=='lexicon':packet['allowed_concept_seed']=CONCEPTS
    messages=[{'role':'system','content':instruction},{'role':'user','content':json.dumps(packet,ensure_ascii=False)}]
    attempts=root/'_attempts'/stem;attempts.mkdir(parents=True,exist_ok=True)
    if raw.exists() and not list(attempts.iterdir()):
        legacy=attempts/'legacy';legacy.mkdir();shutil.copyfile(raw,legacy/'response.raw.txt')
        (legacy/'metadata.json').write_text(json.dumps({'status':'legacy_raw_preserved','provider_finish_reason':'not captured by earlier implementation; cannot reconstruct'},indent=2))
    prior=sorted(p for p in attempts.iterdir() if p.name.isdigit())
    attempt=None
    if prior:
        latest=prior[-1];audit=json.loads((latest/'request.json').read_text())
        if audit.get('status')=='pending_host' and audit['messages']==messages:attempt=latest
    if attempt is None:
        attempt=attempts/f'{len(prior)+1:03d}';attempt.mkdir()
    audit={'kind':kind,'paper_id':paper_id,'section_type':section_type,'provider':provider,'messages':messages,'status':'reserved'}
    (attempt/'request.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    try:
        raw_text=client.complete(provider=provider,messages=messages,task_id=stem,purpose=kind,extract=True,response_format={'type':'json_object'})
    except PendingHostCall:
        audit['status']='pending_host';(attempt/'request.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));raise
    except Exception as exc:
        audit.update(status='failed',error_type=type(exc).__name__);(attempt/'request.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));raise
    (attempt/'response.raw.txt').write_text(raw_text)
    (attempt/'metadata.json').write_text(json.dumps(getattr(client,'last_response_metadata',{}),ensure_ascii=False,indent=2))
    if not raw.exists():
        with raw.open('x') as stream:stream.write(raw_text)
    try:
        response=json.loads(raw_text)
        if not isinstance(response,dict):raise ValueError('extraction must be JSON object')
    except (json.JSONDecodeError,ValueError) as exc:
        audit.update(status='invalid_json',error_type=type(exc).__name__);(attempt/'request.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));raise
    good,bad=verify_batch(response.get('items',[]),units,kind)
    result=[{'kind':kind,'items':good,'attempt_audit':str(attempt),'admission_status':'verified','input_projection':'comment-free prose; raw physical source remains authoritative for coordinates/hash'}]
    verified.write_text(json.dumps(result,ensure_ascii=False,indent=2));dropped.write_text(json.dumps(bad,ensure_ascii=False,indent=2))
    (attempt/'verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(attempt/'dropped.json').write_text(json.dumps(bad,ensure_ascii=False,indent=2))
    audit.update(status='verified',verified=len(good),dropped=len(bad));(attempt/'request.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    rejected=root.parent/'_dropped';rejected.mkdir(exist_ok=True);(rejected/dropped.name).write_text(json.dumps(bad,ensure_ascii=False,indent=2))
    if len(bad)>.2*max(1,len(good)+len(bad)):print(f'warning: {stem}: >20% dropped')
    return good
