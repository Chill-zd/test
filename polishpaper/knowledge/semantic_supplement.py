"""Opt-in exact-packet semantic supplements; immutable historical review survives.

No caller currently enables this module in ordinary retrieval. Offline reports
separate literal coverage from genuinely reviewed source-context scope.
"""
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

SCHEMA='semantic-supplement-1'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def binding(path): return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def read_bound(value):
    if sha(value['path'])!=value['sha256']: raise ValueError('Supplement source changed: '+value['path'])
    return json.loads(Path(value['path']).read_text())
def check_bindings(value):
    if isinstance(value,dict):
        if set(('path','sha256'))<=value.keys() and isinstance(value['path'],str):
            if sha(value['path'])!=value['sha256']:raise ValueError('Supplement nested source changed')
        for v in value.values(): check_bindings(v)
    elif isinstance(value,list):
        for v in value: check_bindings(v)

def family(paper):
    p=re.sub(r'v\d+$','',paper)
    if p in {'arxiv_2205.14202','arxiv_2602.05591','2205.14202+2602.05591'}:return '2205.14202+2602.05591'
    return p

def prepare(schema_packet,context_packet,legacy_overlay,audit,output):
    paths=dict(schema_packet=schema_packet,context_packet=context_packet,legacy_overlay=legacy_overlay,audit=audit,audit_manifest=Path(audit).parent/'manifest.json')
    sources={k:binding(v) for k,v in paths.items()}
    schema=read_bound(sources['schema_packet']);contexts=read_bound(sources['context_packet'])
    ids=[x['id'] for x in schema['items']]+[x['id'] for x in contexts['items']]
    if len(ids)!=28 or len(set(ids))!=28 or sum(i.startswith('schema:') for i in ids)!=8:raise ValueError('Expected exact eight-schema and twenty-context packet')
    check_bindings(schema)
    value={'schema':SCHEMA,'sources':sources,'scope_ids':ids,'reviewer':None,'reviewed_at':None,'declaration':None,'synthetic_fixture':False,'decisions':{i:{'decision':None,'notes':''} for i in ids}}
    p=Path(output)
    if p.exists():raise ValueError('Immutable intake already exists')
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return value

def validate(path,require_complete=False):
    v=json.loads(Path(path).read_text())
    if v.get('schema')!=SCHEMA:raise ValueError('Unknown supplement')
    sources={k:read_bound(b) for k,b in v['sources'].items()}
    expected=[x['id'] for x in sources['schema_packet']['items']]+[x['id'] for x in sources['context_packet']['items']]
    if len(expected)!=28 or len(set(expected))!=28 or v['scope_ids']!=expected or set(v['decisions'])!=set(expected):raise ValueError('Supplement scope differs from exact packet')
    check_bindings(sources['schema_packet'])
    for source,expected_hash in sources['audit_manifest']['inputs'].items():
        if sha(source)!=expected_hash:raise ValueError('Context audit source changed')
    for d in v['decisions'].values():
        if d.get('decision') not in {None,'approve','reject','needs_revision','not_applicable'} or not isinstance(d.get('notes'),str):raise ValueError('Invalid supplied decision')
    if require_complete and (not all(v.get(k) for k in ['reviewer','reviewed_at','declaration']) or any(d['decision'] is None for d in v['decisions'].values())):raise ValueError('Explicit complete human declaration required')
    return v,sources

def recount(path):
    v,s=validate(path)
    # Legacy approval covers reviewed example bindings only, never all registered
    # or newly discovered literal occurrences. Original notes remain untouched.
    reviewed={};withheld=set()
    for entry in s['legacy_overlay']['lexicon_entries']:
        phrase=entry['phrase']
        if entry['decision']['decision']=='approve':reviewed.setdefault(phrase,set()).update(family(e['paper_id']) for e in entry.get('example_bindings',[]))
        else:withheld.add(phrase)
    before={k:sorted(x) for k,x in reviewed.items()}
    for item in s['context_packet']['items']:
        if v['decisions'][item['id']]['decision']=='approve':
            for context in item['new_contexts']:
                if context['eligible_prose']:reviewed.setdefault(item['phrase'],set()).add(family(context['family']))
    eligible=sorted(k for k,x in reviewed.items() if len(x)>=3 and k not in withheld)
    return {'supplement_sha256':sha(path),'source_hashes':v['sources'],'reviewed_legacy_families':before,'reviewed_plus_approved_context_families':{k:sorted(x) for k,x in reviewed.items()},'historical_withheld_phrases':sorted(withheld),'eligible_shared_phrases':eligible,'eligible_shared_count':len(eligible),'threshold_15_met':len(eligible)>=15,'approved_schema_ids':[i for i,d in v['decisions'].items() if i.startswith('schema:') and d['decision']=='approve'],'production_enabled':False}

def atomic(path,bytes_):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        with os.fdopen(fd,'wb') as f:f.write(bytes_);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def activate(path,knowledge_dir,*,enabled=False):
    if not enabled:raise ValueError('Semantic supplement activation defaults off')
    v,_=validate(path,require_complete=True)
    if v.get('synthetic_fixture'):raise ValueError('Synthetic decisions cannot activate')
    pointer=Path(knowledge_dir)/'semantic_supplement_active.json'
    payload=json.dumps({'schema':'semantic-supplement-active-1','supplement':binding(path)},sort_keys=True).encode()
    if pointer.exists() and pointer.read_bytes()==payload:return {'status':'already_active'}
    receipt=Path(str(path)+'.activation.json')
    if receipt.exists():raise ValueError('Existing activation receipt; refusing unrelated pointer overwrite')
    before=pointer.read_bytes() if pointer.exists() else None
    record={'pointer':str(pointer.resolve()),'before_hex':None if before is None else before.hex(),'after_sha256':hashlib.sha256(payload).hexdigest()}
    # Receipt precedes pointer so previous state survives an interrupted activation.
    receipt.write_text(json.dumps(record,indent=2)+'\n');atomic(pointer,payload)
    return {'status':'activated','receipt':str(receipt)}

def rollback(receipt):
    record=json.loads(Path(receipt).read_text());pointer=Path(record['pointer'])
    if not pointer.exists() or sha(pointer)!=record['after_sha256']:raise ValueError('Pointer changed; rollback refuses unrelated work')
    if record['before_hex'] is None:pointer.unlink()
    else:atomic(pointer,bytes.fromhex(record['before_hex']))

def load(knowledge_dir):
    pointer=Path(knowledge_dir)/'semantic_supplement_active.json'
    if not pointer.exists():return None
    p=json.loads(pointer.read_text())
    if p['schema']!='semantic-supplement-active-1':raise ValueError('Unknown supplement pointer')
    read_bound(p['supplement']);value,_=validate(p['supplement']['path'],require_complete=True)
    if value.get('synthetic_fixture'):raise ValueError('Synthetic active supplement')
    return {'pointer_sha256':sha(pointer),'supplement_sha256':p['supplement']['sha256'],'value':value}

def assert_fresh(snapshot,knowledge_dir):
    current=load(knowledge_dir)
    expected=None if current is None else {k:current[k] for k in ['pointer_sha256','supplement_sha256']}
    if snapshot!=expected:raise ValueError('Cached evidence semantic supplement changed')

def select(card,knowledge_dir,exclusions=None,*,max_contexts=None):
    """Select real reviewed schema and relevant exact contexts before lane limits.

    Returns ordinary evidence objects; does not emit unrelated decisions. Source
    filters operate on the source object, not the supplement's multi-paper packet.
    """
    active=load(knowledge_dir)
    if active is None:return {'snapshot':None,'items':[],'schema':None,'selected_ids':[]}
    value=active['value'];sources={k:read_bound(b) for k,b in value['sources'].items()}
    snapshot={k:active[k] for k in ('pointer_sha256','supplement_sha256')}
    schema=None;selected=[]
    target='schema:'+card['section_type']
    for entry in sources['schema_packet']['items']:
        if entry['id']!=target or value['decisions'][entry['id']]['decision']!='approve':continue
        candidate=read_bound(entry['candidate'])
        # A schema has a single actual owning source. Global review bindings must
        # not contaminate the exclusion identity with unrelated review papers.
        source={'paper_id':candidate['basis']['paper_id'],'source_files':candidate['bindings'].get('original_source_files',[])}
        if exclusions and not exclusions.allow('schema',source,entry['id']):continue
        moves=[]
        for move in candidate['moves']:
            moves.append({'id':move['id'],'move':move['move'],'source_quotes':[{'text':e['text'],'source':{k:e['source'][k] for k in ('unit_id','file','sha256','line_start','line_end') if k in e['source']}} for e in move.get('evidence',[])]})
        section=candidate['source_section_observation'] or {}
        schema={'schema':'approved-source-specific-schema-1','section_type':candidate['section_type'],'review_status':'approved','human_approval':True,'schema_approval':{'id':entry['id'],'supplement_sha256':snapshot['supplement_sha256']},'source':source,'basis':candidate['basis'],'section_task':section.get('section_task'),'moves':moves,'interpretation_omissions':candidate.get('interpretation_omissions'),'related_work_route_summary':(candidate.get('pending_related_correction') or {}).get('new_sonnet_proposal',{}).get('route_summary_zh'),'conditions':['One reviewed source-specific route; choose and adapt only where the target section has the same task. It is not a compulsory paragraph sequence.','Approval covers this exact projection. Synthesized alternative routes retain their own status.','Preserve supplied scientific meaning; source observations do not certify scientific truth.']}
        selected.append(entry['id'])
    terms={}
    for row in sources['audit']['original_rows']:terms.setdefault(row['phrase'],set()).add(row['term'].casefold())
    concepts={c.casefold() for c in card.get('concepts',[])}
    withheld={e['phrase'] for e in sources['legacy_overlay']['lexicon_entries'] if e['decision']['decision']!='approve'}
    items=[]
    for entry in sources['context_packet']['items']:
        if value['decisions'][entry['id']]['decision']!='approve' or entry['phrase'] in withheld:continue
        if not concepts.intersection(terms.get(entry['phrase'],set())):continue
        for context in entry['new_contexts']:
            if not context['eligible_prose']:continue
            if sha(context['source_file'])!=context['source_file_sha256']:raise ValueError('Approved lexical source changed')
            if exclusions and not exclusions.allow('lexicon',context,entry['id']):continue
            items.append({'evidence_id':entry['id'],'source_tag':'coauthor_text','text':entry['phrase']+'\nExact reviewed source context:\n'+context['quote'],'conditions':['Approved only for the quoted source context; apply only when the target has the same object, conditions and rhetorical function.','Source-specific terminology and rhetorical context only; this is not a reusable stylistic template or evidence of individual authorship. Use the separately vetted writing-route catalog for imitative patterns.','Original notes and conditions from other occurrences do not transfer to this context.','Historical needs_revision decisions remain withheld.'],'provenance':{'schema':'approved-phrase-context-1','evidence_role':'source_specific_terminology_not_style_template','review_status':'approved','review_item_id':entry['id'],'supplement_sha256':snapshot['supplement_sha256'],'phrase':entry['phrase'],'source_context':context}})
    # Selection and exclusions happen before this deterministic lane limit.
    if max_contexts is not None:items=items[:max_contexts]
    selected.extend(item['evidence_id'] for item in items)
    return {'snapshot':snapshot,'items':items,'schema':schema,'selected_ids':selected}

def literal_metrics(knowledge_dir,exclusions=None):
    """Actual canonical registrations, separately from reviewed applicability.

    Family exclusions are applied to contexts before computing eligible scopes;
    this metric never turns source-literal frequency into stylistic permission.
    """
    active=load(knowledge_dir)
    if active is None:return None
    supplement=json.loads((Path(knowledge_dir)/'semantic_supplement_active.json').read_text())['supplement']
    path=Path(supplement['path']).parent/'canonical_literal_shared_registry.json'
    if not path.exists():return None
    registry=json.loads(path.read_text());audit=read_bound(registry['audit']);read_bound(registry['approval_supplement'])
    expected={x['phrase']:x for x in audit['results'] if x['prose_family_count']>=3}
    if len(registry['entries'])!=len(expected) or {x['phrase'] for x in registry['entries']}!=set(expected):raise ValueError('Canonical literal registry scope changed')
    for entry in registry['entries']:
        original=expected[entry['phrase']]
        if entry['source_contexts']!=original['contexts'] or entry['independent_work_families']!=original['prose_families']:raise ValueError('Canonical literal registry source scope changed')
    if registry['approval_supplement']['sha256']!=active['supplement_sha256']:raise ValueError('Literal registry references another approval supplement')
    eligible=[];rows=[]
    for entry in registry['entries']:
        families=set();unit_ids=[]
        for context in entry['source_contexts']:
            if not context['eligible_prose']:continue
            if exclusions and not exclusions.allow('lexicon',context,'literal:'+entry['phrase']+':'+context['unit_id']):continue
            families.add(family(context['family']));unit_ids.append(context['unit_id'])
        if len(families)>=3:eligible.append(entry['phrase'])
        rows.append({'phrase':entry['phrase'],'eligible_family_count':len(families),'eligible_families':sorted(families),'eligible_source_units':sorted(set(unit_ids)),'eligible_scope':'shared' if len(families)>=3 else 'source_specific'})
    reviewed=recount(supplement['path'])
    return {'registry':binding(path),'literal_registered_shared_count':len(registry['entries']),'eligible_literal_shared_count':len(eligible),'eligible_literal_shared_phrases':eligible,'literal_gate_15_met':len(eligible)>=15,'eligible_source_scopes':rows,'reviewed_applicable_shared_count_full_scope':reviewed['eligible_shared_count'],'reviewed_applicability_is_additional_level1_gate':False,'extraction_item_rate':{'scope':'twelve exact adopted legacy lexical/pattern/schema batches','raw':164,'retained':163,'dropped':1,'ratio':1/164,'full_final_knowledge_rate_established':False},'level1_fully_passed':False,'remaining_limit':'Full final knowledge denominator scope is not established; frequency and reviewed applicability are distinct.'}
