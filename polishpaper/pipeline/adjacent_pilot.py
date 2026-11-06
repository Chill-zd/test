"""Freshness checks for explicitly opted-in experimental adjacent source cards."""
from pathlib import Path
from ..knowledge.writing_routes import sha
from ..knowledge.adjacent_transfers import verify


def assert_fresh(evidence):
    audit=evidence.get('adjacent_transfers',{})
    binding=audit.get('catalog')
    if binding and (not Path(binding['path']).is_file() or sha(binding['path']) != binding['sha256']):
        raise ValueError('Adjacent transfer pilot catalog changed; prepare evidence again')
    for item in evidence.get('items',[]):
        if item.get('evidence_id','').startswith('adjacent_transfer:'):
            verify(item['adjacent_transfer'])


def writer_projection(evidence):
    """Only experimental adjacent items are projected; original audit remains intact."""
    import copy
    import hashlib
    import json
    if not any(i.get('evidence_id','').startswith('adjacent_transfer:') for i in evidence.get('items',[])):
        return evidence
    result=copy.deepcopy(evidence)
    projected=[]
    for item in result['items']:
        if not item.get('evidence_id','').startswith('adjacent_transfer:'):
            projected.append(item);continue
        entry=item['adjacent_transfer']
        candidate, _, lineage=verify(entry)
        if not lineage or not lineage.get('paper_ids'):
            raise ValueError('Adjacent transfer generator identity missing')
        projected.append({'evidence_id':item['evidence_id'],'source_tag':item['source_tag'],
            'literal_adjacent_sentences':entry['literal_contiguous_text'],
            'reader_task':entry['reader_task'],'relationship':entry['old_to_new'],
            'omit_if':entry['omit_if'],'transfer_guard':entry['transfer_guard'],
            'conditions':item['conditions'],'semantic_status':entry['semantic_status'],
            'source_locator':{'unit_id':entry['unit_id'],'paper_id':candidate['basis']['paper_id']},
            'generator_identity':{'paper_ids':lineage['paper_ids']},
            'full_item_sha256':hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
    result['items']=projected
    result['adjacent_transfers']={'status':'projected_writer_only','selected':evidence.get('adjacent_transfers',{}).get('selected',[]),
        'policy':'Optional pending editorial interpretation; omit if inapplicable. Full hash-bound materials remain in evidence.json and reviewer evidence.'}
    return result
