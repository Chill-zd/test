"""Opt-in adjacent sentence evidence; all interpretations remain pending human review."""
import json
import hashlib
import re
from pathlib import Path
from .writing_routes import sha, check_source, generator_inputs


def verify(item):
    route = item['route']
    binding = route['source']
    if sha(binding['path']) != binding['sha256']:
        raise ValueError('Adjacent-transfer source changed')
    candidate = json.loads(Path(binding['path']).read_text())
    units = check_source(candidate, binding['unit_ids'])
    unit = units[item['unit_id']]
    # Match against the physical raw paragraph as well as its prose projection.
    raw = candidate['units'][item['unit_id']].get('raw_text', unit['text'])
    quote = item['literal_contiguous_text']
    if raw.count(quote) != 1 or unit['text'].count(quote) != 1:
        raise ValueError('Adjacent sentences are not a contiguous physical source span')
    if re.search(r'\$|\\(?:begin|end|section|bibliography|item|\[|\])|\n\s*\n|(?<!\\)%', quote):
        raise ValueError('Adjacent example crosses an insertion or non-prose boundary')
    span_id=hashlib.sha256((candidate['basis']['paper_id']+'|'+item['unit_id']+'|'+quote).encode()).hexdigest()
    if item.get('source_span_id') and item['source_span_id'] != span_id:
        raise ValueError('Physical span identity changed')
    if len(item['sentences']) not in (2, 3) or ' '.join(item['sentences']) != quote:
        raise ValueError('Adjacent sentence reconstruction differs')
    expected = item.get('neighbor_context')
    if expected is not None:
        text = unit['text']
        a = text.index(quote)
        if expected['before'] != text[:a] or expected['after'] != text[a+len(quote):]:
            raise ValueError('Adjacent context changed')
    return candidate, units, generator_inputs(route)


def build(route_catalog, output):
    """Conservatively retain a diverse small menu from vetted route source bindings."""
    data = json.loads(Path(route_catalog).read_text())
    result = []
    seen = set()
    for section, routes in data['sections'].items():
        for route in routes:
            binding = route['source']
            candidate = json.loads(Path(binding['path']).read_text())
            units = check_source(candidate, binding['unit_ids'])
            paper = candidate['basis']['paper_id']
            if (paper, section) in seen:
                continue
            for uid, unit in units.items():
                # Whitespace is preserved: only ordinary single-space boundaries qualify.
                sentences = re.split(r'(?<=[.!?]) (?=[A-Z])', unit['text'])
                for left, right in zip(sentences, sentences[1:]):
                    quote = left + ' ' + right
                    if not (40 <= len(left) <= 600 and 40 <= len(right) <= 600):
                        continue
                    item = dict(id=f'adjacent-{len(result)+1:02d}', section_type=section,
                        unit_id=uid, route=route, sentences=[left,right], literal_contiguous_text=quote,
                        reader_task={'en':'Assess the source paragraph’s stated task and how the second sentence develops the first.', 'zh':route['when']},
                        old_to_new=route['coherence']['old_to_new'],
                        omit_if=route['omit_if'], semantic_status='pending_human',
                        transfer_guard='Transfer only an applicable information relationship; supply all objects, conditions and claims from the target manuscript. This paragraph-level interpretation is not a verified sentence-level semantic judgment.')
                    try:
                        verify(item)
                    except ValueError:
                        continue
                    result.append(item)
                    seen.add((paper, section))
                    break
                if (paper,section) in seen:
                    break
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps({'schema':'adjacent-transfers-1','items':result},ensure_ascii=False,indent=2)+'\n')
    return result


def select(card, root, exclusions=None, max_items=3):
    path = Path(root) / 'adjacent_transfers.json'
    audit = {'status':'absent','selected':[],'withheld':[]}
    if not path.exists():
        return [], audit
    data=json.loads(path.read_text())
    if data.get('schema') != 'adjacent-transfers-1':
        raise ValueError('Unknown adjacent transfer schema')
    spec_binding=data.get('editorial_specification')
    if spec_binding:
        if sha(spec_binding['path']) != spec_binding['sha256']:
            raise ValueError('Editorial specification changed')
        spec=json.loads(Path(spec_binding['path']).read_text())
        if data['items'] != spec['items']:
            raise ValueError('Catalog differs from editorial specification')
    audit.update(status='active',catalog={'path':str(path.resolve()),'sha256':sha(path)})
    items=[]
    requested=set(card.get('adjacent_transfer_ids',[]))
    if not requested:
        audit['selection_policy']='Explicit reader-task ID selection required; section membership does not establish relevance.'
        return [], audit
    for entry in data['items']:
        if entry['section_type'] != card['section_type'] or (requested and entry['id'] not in requested):
            continue
        candidate, units, lineage=verify(entry)
        if exclusions is None or lineage is None or not exclusions.allow('writing_routes',lineage,entry['id']+':generator') or not exclusions.allow('writing_routes',candidate,entry['id']):
            audit['withheld'].append(entry['id'])
            continue
        if len(items)>=max_items:
            continue
        items.append({'evidence_id':'adjacent_transfer:'+entry['id'],'source_tag':'synthesized_guidance','adjacent_transfer':entry,'source_examples':units,'conditions':[entry['transfer_guard']],'provenance':{'source':entry['route']['source'],'generator_inputs':lineage,'semantic_status':'pending_human'}})
        audit['selected'].append(entry['id'])
    return items,audit


def build_curated(specification, output):
    """Reproduce the reviewed editorial selection without discovery-order IDs."""
    spec=json.loads(Path(specification).read_text())
    if spec.get('schema') != 'adjacent-editorial-spec-1':
        raise ValueError('Unknown editorial specification')
    result=[]
    spans=set()
    ids=set()
    for item in spec['items']:
        verify(item)
        binding=item['route']['source']
        identity=(binding['path'],item['unit_id'],item['literal_contiguous_text'])
        if identity in spans or item['id'] in ids:
            raise ValueError('Duplicate curated ID or physical span')
        spans.add(identity)
        ids.add(item['id'])
        result.append(item)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps({'schema':'adjacent-transfers-1','interpretation_status':spec['interpretation_status'],'editorial_specification':{'path':str(Path(specification).resolve()),'sha256':sha(specification)},'items':result},ensure_ascii=False,indent=2)+'\n')
    return result
