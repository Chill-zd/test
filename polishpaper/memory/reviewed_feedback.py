"""Source-bound human-reviewed advisor cases, distinct from revision decisions.

Confirmation concerns the displayed feedback case. It never means acceptance of
a manuscript revision, proof verification, or independent authentication of Clint.
"""
from copy import deepcopy
import hashlib,json,sqlite3
import re
from pathlib import Path


def load(path):return json.loads(Path(path).read_text())
def binding(path):
    path=Path(path).resolve();return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def checked(item):
    path=Path(item['path'])
    if not path.is_file() or binding(path)['sha256']!=item['sha256']:raise ValueError('Reviewed feedback source changed: '+str(path))
    return path
def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def _source_binding(case):
    result={'case_id':case['id'],'source_sha256':case['source_sha256'],'page':case['page'],
        'image_sha256':case['image_sha256'],'full_page_image_sha256':case['full_page_image_sha256']}
    if case.get('additional_target_sources'):
        result['additional_target_sources']=[{'source_sha256':case['source_sha256'],'page':s['page'],'image_sha256':s['image_sha256']} for s in case['additional_target_sources']]
    if case.get('resolution'):
        r=case['resolution'];result['later_version_binding']={k:r[k] for k in ('source_sha256','page','image_sha256')}
    return result


def _source_files(case,documents):
    values=[{'path':case['source_path'],'sha256':case['source_sha256']},
            {'path':case['image_path'],'sha256':case['image_sha256']},
            {'path':case['full_page_image_path'],'sha256':case['full_page_image_sha256']}]
    values += [{'path':s['image_path'],'sha256':s['image_sha256']} for s in case.get('additional_target_sources',[])]
    if case.get('resolution'):
        r=case['resolution'];values += [{'path':documents[r['source_sha256']]['path'],'sha256':r['source_sha256']},
            {'path':r['image_path'],'sha256':r['image_sha256']}]
    for value in values:checked(value)
    return values


def prepare(intake_dir,candidates_path,output_dir):
    """Freeze eligible records without updating the live database/index/pointer."""
    intake=Path(intake_dir).resolve();candidates_path=Path(candidates_path).resolve()
    declared=load(intake/'intake_manifest.json');validation=load(intake/'validation.json')
    if validation.get('passed') is not True:raise ValueError('Human intake has not passed source validation')
    inputs=[binding(intake/'intake_manifest.json'),binding(candidates_path)]
    for name,item in declared['files'].items():
        path=(intake/name).resolve()
        if not path.is_relative_to(intake):raise ValueError('Intake file escapes its source root')
        value={'path':str(path),'sha256':item['sha256']};checked(value);inputs.append(value)
    projection=load(intake/'feedback_only_projection.json');snapshot=load(intake/'current_review_data.snapshot.json')['feedback']
    if snapshot['fingerprint']!=projection['feedback_fingerprint']:raise ValueError('Feedback review snapshot mismatch')
    candidates=load(candidates_path);originals={c['id']:c for c in candidates['cases']}
    displayed={c['id']:c for c in snapshot['cases']};decisions=projection['feedback_decisions']
    if set(originals)!=set(displayed) or set(decisions)!=set(originals) or set(projection['feedback_source_bindings'])!=set(originals):raise ValueError('Reviewed feedback cases do not match exact original inventory')
    docs={d['source_sha256']:d for d in candidates['source_documents']};records=[];objects=[]
    for cid,case in originals.items():
        human=deepcopy(decisions[cid]);view=displayed[cid]
        if human['decision'] not in ('confirm','revise','unsure'):raise ValueError('Unknown source-case review decision')
        if projection['feedback_source_bindings'][cid]!=_source_binding(case):raise ValueError('Reviewed PDF/page/crop binding differs: '+cid)
        compared=('source_sha256','page','image_sha256','full_page_image_sha256','handwritten_literal',
            'scope','eligible_for_general_language_learning','section_type','printed_target','interpretation','conditions','counterconditions')
        if any(view[k]!=case[k] for k in compared):raise ValueError('Displayed/source feedback differs: '+cid)
        files=_source_files(case,docs)
        language=case['scope']=='language_exposition' and case['eligible_for_general_language_learning'] is True
        kind=('feedback' if human['decision']=='confirm' else 'user_guidance') if language else 'science_question'
        if human['decision']=='unsure' or (kind=='user_guidance' and not human.get('notes','').strip()):kind=None
        record={'case_id':cid,'review_decision':human['decision'],'scope':case['scope'],'index_kind':kind,
            'original_candidate':case,'displayed_case':view,'literal_human_fields':human,'source_bindings':files,
            'comment_author':case['comment_author'],'user_note_author':'user','manuscript_revision_decision':None,
            'source_verification':'Original PDF/page/crop visually checked and human reviewed; no TeX source verification.',
            'scientific_truth':'unverified','resolution_acceptance':None}
        records.append(record)
        if kind is None:continue
        text='Source target: '+human['target']+'\nAdvisor handwritten comment (Clint, user-attributed): '+human['transcription']
        if kind=='feedback':text+='\nDisplayed machine interpretation, source-case confirmed by human: '+view['interpretation']
        if human.get('notes'):text+='\nLiteral user guidance (author=user): '+human['notes']
        if kind=='feedback':text+='\nApplicability: '+human['conditions']+'\nCounterconditions: '+view['counterconditions']
        if kind=='science_question':text+='\nSeparate scientific question; no general language rule, automatic edit, or language penalty.'
        conditions=['Single source-bound feedback observation; apply only after matching the current reader task and supplied scientific meaning.',
            'Advisor handwriting and literal user guidance have distinct authors; no manuscript accept/reject decision or accepted later revision is inferred.']
        if kind=='feedback':conditions += [human['conditions'],view['counterconditions']]
        if kind=='user_guidance':conditions += ['Original case remains revise; only the literal user note is guidance. No corrected machine interpretation has been approved.']
        if kind=='science_question':conditions += ['Inherited scientific uncertainty is separate from language assessment and cannot alone lower a language verdict.']
        provenance={'schema':'reviewed-advisor-feedback-1','case_id':cid,'observation_identity':cid,
            'review_decision':human['decision'],'scope':case['scope'],'comment_author':case['comment_author'],
            'advisor_original_handwriting':case['handwritten_literal'],'human_transcription':human['transcription'],
            'literal_user_note':human.get('notes',''),'user_note_author':'user','literal_review_fields':human,
            'interpretation_author':'original_machine_candidate' if kind=='feedback' else None,
            'interpretation_status':'source_case_confirmed' if kind=='feedback' else 'not_admitted_as_language_interpretation',
            'source_bindings':files,'source_locator':case['source_locator'],'page':case['page'],
            'source_verification':record['source_verification'],'tex_source_verified':False,
            'manuscript_revision_decision':None,'later_variant':deepcopy(case.get('resolution')),
            'later_variant_acceptance':None,'scientific_truth':'unverified'}
        objects.append({'kind':kind,'id':'feedback_review:'+cid,'text':text,'section_type':case['section_type'],
            'concepts':[],'source_tag':'user_request' if kind=='user_guidance' else 'real_annotation',
            'conditions':conditions,'provenance':provenance})
    home=Path(output_dir).resolve();home.mkdir(parents=True,exist_ok=False)
    write(home/'records.json',records);write(home/'objects.json',objects)
    manifest={'schema':'reviewed-feedback-admission-1','status':'prepared_from_original_human_review',
        'inputs':inputs,'records':binding(home/'records.json'),'objects':binding(home/'objects.json'),
        'source_review_binding':declared['binding'],'counts':{k:sum(o['kind']==k for o in objects) for k in ('feedback','user_guidance','science_question')},
        'case_count':len(records),'review_counts':{d:sum(r['review_decision']==d for r in records) for d in ('confirm','revise','unsure')},
        'manuscript_decisions_created':0,'api_calls':0,'active_write':False}
    write(home/'manifest.json',manifest);return home/'manifest.json'


def verify(manifest_path):
    manifest=load(manifest_path)
    if manifest.get('schema')!='reviewed-feedback-admission-1':raise ValueError('Invalid reviewed feedback admission')
    for item in manifest['inputs']+[manifest['records'],manifest['objects']]:checked(item)
    for record in load(checked(manifest['records'])):
        for item in record['source_bindings']:checked(item)
    return manifest


def index_objects(manifest_path):
    manifest=verify(manifest_path);objects=load(checked(manifest['objects']))
    return [{**o,'provenance':{**o['provenance'],'admission_manifest':binding(manifest_path),'admission_objects':manifest['objects']}} for o in objects]


def admit(manifest_path,db_path):
    """Idempotent reviewed-case import; never writes legacy accept/reject rows."""
    objects=index_objects(manifest_path);manifest_hash=binding(manifest_path)['sha256']
    path=Path(db_path);path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS reviewed_feedback(case_id TEXT PRIMARY KEY, manifest_hash TEXT NOT NULL,payload TEXT NOT NULL)')
        for obj in objects:
            old=db.execute('SELECT manifest_hash,payload FROM reviewed_feedback WHERE case_id=?',(obj['id'],)).fetchone()
            payload=json.dumps(obj,ensure_ascii=False)
            if old and old!=(manifest_hash,payload):raise ValueError('Different reviewed case already exists; explicit versioned correction is required')
            db.execute('INSERT OR IGNORE INTO reviewed_feedback VALUES(?,?,?)',(obj['id'],manifest_hash,payload))
    return len(objects)


def database_objects(db_path):
    if not Path(db_path).exists():return []
    with sqlite3.connect(db_path) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='reviewed_feedback'").fetchone():return []
        return [json.loads(r[0]) for r in db.execute('SELECT payload FROM reviewed_feedback ORDER BY case_id')]


def assert_object_fresh(obj,cache=None):
    provenance=obj.get('provenance',{})
    if provenance.get('schema')!='reviewed-advisor-feedback-1':return
    cache={} if cache is None else cache
    for name in ('admission_manifest','admission_objects'):
        item=provenance[name];key=(item['path'],item['sha256'])
        if key not in cache:cache[key]=load(checked(item))
    manifest=cache[(provenance['admission_manifest']['path'],provenance['admission_manifest']['sha256'])]
    if manifest['objects']!=provenance['admission_objects']:raise ValueError('Reviewed feedback object envelope differs')
    originals=cache[(provenance['admission_objects']['path'],provenance['admission_objects']['sha256'])]
    original=next((o for o in originals if o['id']==obj['id']),None)
    actual=deepcopy(obj);actual.pop('score',None)
    for key in ('admission_manifest','admission_objects'):actual['provenance'].pop(key,None)
    if actual!=original:raise ValueError('Indexed feedback differs from exact reviewed source object')
    for item in manifest['inputs']+[manifest['records']]+provenance['source_bindings']:
        key=(item['path'],item['sha256'])
        if key not in cache:checked(item);cache[key]=True


def activate(manifest_path,knowledge_dir):
    manifest=verify(manifest_path);path=Path(knowledge_dir)/'feedback_review_active.json'
    if path.exists():raise ValueError('Reviewed feedback pointer already exists; preserve it before explicit replacement')
    path.parent.mkdir(parents=True,exist_ok=True)
    pointer={'schema':'reviewed-feedback-active-1','manifest':binding(manifest_path),'counts':manifest['counts']}
    write(path,pointer);return pointer


def active(knowledge_dir):
    path=Path(knowledge_dir)/'feedback_review_active.json'
    if not path.exists():return None
    pointer=load(path)
    if pointer.get('schema')!='reviewed-feedback-active-1':raise ValueError('Invalid feedback review pointer')
    manifest=load(checked(pointer['manifest']))
    if manifest.get('schema')!='reviewed-feedback-admission-1' or pointer.get('counts')!=manifest['counts']:
        raise ValueError('Feedback pointer differs from exact admission manifest')
    return {**pointer,'pointer':binding(path)}


def feedback_context(card):
    """Route advisor genres without changing the ordinary ten-type source taxonomy."""
    from ..corpus.parser import SECTION_TYPES
    domain=card['section_type'];targets=card.get('target_units',[])
    abstract=bool(targets) and all(u.get('env_kind')=='abstract' for u in targets)
    context=card.get('task_context',{})
    explicit=context.get('document_genre')=='response_letter' or card.get('document_genre')=='response_letter'
    request=card.get('user_request','')
    pattern=r'\b(?:polish|revise|edit|rewrite|improve|draft|write)\s+(?:(?:the|this|my|a|our)\s+)?(?:rebuttal|response\s+(?:letter|to\s+(?:the\s+)?reviewers?))\b'
    chinese=r'(?:润色|修改|改写|撰写|写)(?:这份|这个|这封|我的|一封|一下)?\s*(?:rebuttal|回复信|审稿回复|回复审稿人|对审稿人的回复|答复审稿人)'
    def positive(pattern):
        for match in re.finditer(pattern,request,re.I):
            prefix=request[max(0,match.start()-32):match.start()]
            if not re.search(r"(?:do\s+not|don't|never|not|no\s+need\s+to|不要|无需|不必|别)\s*$",prefix,re.I):return True
        return False
    response=explicit or positive(pattern) or positive(chinese)
    if abstract and response:raise ValueError('Conflicting abstract source and explicit response-letter task genre')
    genre='abstract' if abstract else 'response_letter' if response else 'manuscript'
    selected=genre if genre!='manuscript' else domain if domain in SECTION_TYPES else 'unknown'
    return {'section_type':selected,'document_genre':genre,'domain_section_type':domain,
        'basis':'actual target env_kind=abstract' if abstract else 'explicit response-letter task context/request' if response else 'ordinary source section type',
        'domain_taxonomy_changed':False}


def assert_evidence_fresh(evidence,knowledge_dir):
    current=active(knowledge_dir);previous=evidence.get('feedback_review')
    if current!=previous:raise ValueError('Reviewed feedback activation changed; prepare evidence again')
    cache={}
    for obj in [e.get('provenance',{}) for e in evidence.get('items',[])]+evidence.get('inherited_scientific_questions',[]):
        if obj.get('provenance',{}).get('schema')=='reviewed-advisor-feedback-1':assert_object_fresh(obj,cache)
