"""Optional synthesized alternatives, bound to source-specific candidate evidence."""
import hashlib
import json
import re
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def physical(value):
    path=Path(value.get('file_path',value.get('path',value.get('file',''))))
    if not path.is_absolute() or sha(path)!=value.get('file_sha256',value.get('sha256')):
        raise ValueError('Writing source physical file changed')
    raw=path.read_text()
    lines=raw.splitlines(keepends=True)
    start,end=value['line_start'],value['line_end']
    if not 1 <= start <= end <= len(lines):
        raise ValueError('Invalid source line bounds')
    if 'offset_start' in value:
        a,b=value['offset_start'],value['offset_end']
        if not 0 <= a < b <= len(raw):raise ValueError('Invalid source offsets')
        text=raw[a:b]
        if raw.count('\n',0,a)+1!=start or raw.count('\n',0,b-1)+1!=end:
            raise ValueError('Source offsets and lines disagree')
    else:text=''.join(lines[start-1:end])
    if text!=value.get('raw_text',value['text']):
        raise ValueError('Source text differs from exact physical span')
    return text


def check_source(candidate, unit_ids):
    basis=candidate['basis']
    authors=basis.get('authors',[])
    if not any('chin pang ho' in a.casefold().replace('-', ' ') for a in authors):
        raise ValueError('Writing route requires Chin Pang Ho byline')
    byline=physical(basis['byline'])
    normalized=re.sub(r'[^a-z ]',' ',byline.casefold())
    normalized=' '.join(normalized.split())
    if not re.search(r'chin\s+pang\s+ho',normalized):
        raise ValueError('Physical source byline does not identify Chin Pang Ho')
    pool=candidate['units']
    if not unit_ids or any(uid not in pool for uid in unit_ids):
        raise ValueError('Writing route requires exact source unit IDs')
    for uid in unit_ids:
        unit=pool[uid]
        if unit['paper_id']!=basis['paper_id'] or unit['authors']!=authors:
            raise ValueError('Source paragraph identity differs from byline')
        physical(unit)
    from ..corpus.parser import strip_comments
    allowed=('id','unit_id','paper_id','title','authors','file','file_path','file_sha256','line_start','line_end','offset_start','offset_end')
    return {uid:{**{k:v for k,v in pool[uid].items() if k in allowed},'text':strip_comments(pool[uid].get('raw_text',pool[uid]['text']))} for uid in unit_ids}


def generator_inputs(route):
    provenance=route.get('generator_provenance')
    if not provenance and isinstance(route.get('basis'),dict):
        provenance=route['basis'].get('consultation')
    if not provenance:return None
    request=provenance.get('request',{})
    if not request.get('path') or sha(request['path'])!=request.get('sha256'):
        raise ValueError('Route generation request changed')
    data=json.loads(Path(request['path']).read_text())
    pool_binding=provenance.get('source_pool')
    title_ids={}
    if pool_binding:
        if sha(pool_binding['path'])!=pool_binding['sha256']:raise ValueError('Route generator source pool changed')
        pool=json.loads(Path(pool_binding['path']).read_text())
        for source in pool['sources']:
            title_ids.setdefault(source['title'],set()).add(source['paper_id'])
    ids=set()
    if data.get('source_paper_id'):ids.add(data['source_paper_id'])
    for example in data.get('examples',[]):
        if example.get('paper_id'):ids.add(example['paper_id'])
        elif example.get('paper') in title_ids:ids.update(title_ids[example['paper']])
        else:raise ValueError('Unknown paper lineage in route generator request')
    declared=provenance.get('input_paper_ids',provenance.get('generator_input_paper_ids'))
    if not ids or declared is None or ids!=set(declared):
        raise ValueError('Route generator family closure differs from actual request')
    return {'paper_ids':sorted(ids)}


def select(card, root, exclusions=None, max_items=4):
    path = Path(root) / 'writing_routes.json'
    audit = {'status': 'absent', 'selected': [], 'withheld': []}
    if not path.exists():
        return [], audit
    data = json.loads(path.read_text())
    if data.get('schema') != 'mdp-writing-routes-1':
        raise ValueError('Unknown writing routes schema')
    audit.update(status='active', catalog={'path': str(path.resolve()), 'sha256': sha(path)})
    items = []
    seen = set()
    routes=data['sections'].get(card['section_type'], [])
    requested=set(card.get('writing_route_ids', []))
    query=' '.join([card.get('user_request','')]+card.get('concepts',[])+[u.get('prose_text',u.get('text','')) for u in card.get('target_units',[])])
    cues={'definition':'定义','notation':'符号','objective':'目标','assumption':'假设','complexity':'复杂度','error':'误差','algorithm':'算法','update':'更新','convergence':'收敛','comparison':'比较','experiment':'实验','motivation':'动机','contribution':'贡献','limitation':'局限','transition':'衔接'}
    def tokens(text):
        text=text.casefold()
        found=set(re.findall(r'[a-z]{4,}',text))
        for en,zh in cues.items():
            if en in text or zh in text:found.add(en)
        return found
    words=tokens(query)
    def score(route):
        fit=' '.join(str(route.get(k,'')) for k in ('title','subfunction','when')).casefold()
        return len(words & tokens(fit))
    routes=sorted(routes,key=lambda r:(-score(r),hashlib.sha256((query+'|'+r['id']).encode()).hexdigest()))
    audit['menu']=[]
    audit['tie_policy']='Equal lexical scores use a deterministic request-dependent ordering, not semantic confidence; compact menu permits explicit route-ID selection.'
    for route in routes:
        if requested and route['id'] not in requested:continue
        rid = route['id']
        if rid in seen:
            raise ValueError('Duplicate writing route ID')
        seen.add(rid)
        binding = route['source']
        source = Path(binding['path'])
        if not source.is_absolute() or sha(source) != binding['sha256']:
            raise ValueError('Writing route source changed or lacks absolute binding')
        candidate = json.loads(source.read_text())
        lineage=generator_inputs(route)
        if exclusions and lineage is None:
            audit['withheld'].append(rid)
            continue
        if exclusions and not exclusions.allow('writing_routes',lineage,rid+':generator'):
            audit['withheld'].append(rid)
            continue
        # A wrapper ID or handbook path must never certify candidate lineage.
        if exclusions and not exclusions.allow('writing_routes', candidate, rid):
            audit['withheld'].append(rid)
            continue
        selected_units = check_source(candidate, binding.get('unit_ids', []))
        audit['menu'].append({k:route[k] for k in ('id','title','subfunction','when','omit_if') if k in route})
        if len(items)>=max_items:
            audit.setdefault('not_delivered',[]).append({'id':rid,'reason':'bounded_contextual_menu'})
            continue
        for key in ('when', 'sequence', 'phrases', 'omit_if', 'basis', 'coherence'):
            if key not in route:
                raise ValueError('Incomplete writing route: ' + key)
        if not all(route['coherence'].get(k) for k in ('old_to_new','next_handoff')):
            raise ValueError('Route lacks old-to-new or next-handoff guidance')
        unit_ids = binding.get('unit_ids', [])
        selected_units = check_source(candidate, unit_ids)
        for phrase in route['phrases']:
            if isinstance(phrase, dict) and phrase.get('literal') and not any(phrase['literal'] in u['text'] for u in selected_units.values()):
                raise ValueError('Claimed literal phrase is absent from selected source paragraphs')
        for anchor in route.get('anchors', []):
            text=anchor['text'] if isinstance(anchor,dict) else anchor
            if isinstance(anchor,dict) and anchor.get('unit_id') and anchor['unit_id'] not in selected_units:
                raise ValueError('Route anchor cites an undelivered source unit')
            if not text or not any(text in u['text'] for u in selected_units.values()):
                raise ValueError('Route anchor absent from selected source paragraph')
        item = {'evidence_id': 'writing_route:' + rid, 'source_tag': 'synthesized_guidance',
                'text': 'Optional contextual alternative; choose, adapt, or omit after inspecting the supplied passage.',
                'conditions': ['Authored adaptations are synthesized; source_examples are literal source context. Choose by paragraph purpose and reader knowledge, inspect neighboring referents and old-to-new information, then choose, adapt or omit. No forced order, phrase quota or scientific transfer.'],
                'provenance': {'source': binding, 'paper_id': candidate['basis']['paper_id'], 'generator_inputs':lineage, 'semantic_status': 'approved_corrected_scope' if route.get('human_approval') is True else 'pending_human'},
                'writing_route': route, 'source_examples': selected_units,
                'source_restrictions': {k: candidate[k] for k in ('restrictions', 'review_status', 'schema_approval', 'human_approval', 'projection_policy', 'interpretation_omissions', 'pending_related_correction') if k in candidate},
                'source_policy': 'Expert-synthesized generalization; bound candidate is checked on disk. Only explicitly selected complete source units are examples; missing examples establish no quotation.'}
        items.append(item)
        audit['selected'].append(rid)
    audit['selection_policy']='Explicit requested IDs or lexical purpose ranking before bounded complete examples; contextual fit remains writer judgment, all alternatives may be omitted.'
    return items, audit


def assert_fresh(evidence, root):
    recorded = evidence.get('writing_routes', {})
    if recorded.get('status') != 'active':
        if (Path(root) / 'writing_routes.json').exists() and evidence.get('mode') != 'bare':
            raise ValueError('Writing routes added; prepare evidence again')
        return
    binding = recorded['catalog']
    if sha(binding['path']) != binding['sha256']:
        raise ValueError('Writing routes catalog changed; prepare evidence again')
    for item in evidence.get('items', []):
        if item['evidence_id'].startswith('writing_route:'):
            source = item['provenance']['source']
            generator_inputs(item['writing_route'])
            check_source(json.loads(Path(source['path']).read_text()), source.get('unit_ids', []))
            if sha(source['path']) != source['sha256']:
                raise ValueError('Writing route source changed; prepare evidence again')


def assert_references(changes, evidence):
    delivered = {e['evidence_id'] for e in evidence.get('items', [])}
    for change in changes:
        for ref in change.get('sources', []):
            if isinstance(ref, str) and ref.startswith('writing_route:') and ref not in delivered:
                raise ValueError('Undelivered writing route reference: ' + ref)


def verified_legacy_examples(value, root):
    """Templates require physical Ho byline and literal example, not wrapper attribution."""
    from ..corpus.parser import strip_comments
    examples=value.get('examples',[])
    if not examples and value.get('phrase'):
        examples=[]
        for source_id in value.get('sources',[]):
            if not isinstance(source_id,str):return False
            parts=source_id.split(':')
            if len(parts)<2:return False
            examples.append({'text':value['phrase'],'source':{'paper_id':parts[0],'file':parts[1]}})
    if not examples:return False
    for example in examples:
        source=example.get('source',{})
        paper=source.get('paper_id')
        relative=source.get('file')
        if not paper or not relative:return False
        corpus=(Path(root).parent/'corpus'/'raw').resolve()
        path=(corpus/paper/relative).resolve()
        if not path.is_relative_to(corpus) or not path.is_file():return False
        raw=path.read_text();clean=strip_comments(raw)
        author=clean.find('\\author')
        if author<0 or not re.search(r'Chin[\s~-]+Pang[\s~-]+Ho',clean[author:author+2500],re.I):return False
        if not example.get('text') or example['text'] not in clean:return False
    return True


def unresolved_slots(original, revised, evidence):
    """Only declared prose placeholders copied newly from delivered adaptations."""
    def prose_occurrences(text, token=None):
        math_spans=[m.span() for m in re.finditer(r'(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]',text)]
        pattern=re.escape(token) if token else r'(?<!\\)\[[A-Za-z][A-Za-z -]{2,}\]'
        found=[]
        for match in re.finditer(pattern,text):
            if any(a<=match.start()<b for a,b in math_spans):continue
            if re.search(r'\\[A-Za-z]+(?:\[[^]]*\])*\s*$',text[:match.start()]):continue
            found.append(match[0])
        return found
    slots=set()
    for item in evidence.get('items',[]):
        for phrase in item.get('writing_route',{}).get('phrases',[]):
            if isinstance(phrase,dict):slots.update(prose_occurrences(phrase.get('adaptation','')))
    return sorted(slot for slot in slots if len(prose_occurrences(revised,slot))>len(prose_occurrences(original,slot)))
