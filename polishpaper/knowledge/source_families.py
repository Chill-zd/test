"""Optional provenance correction; never changes approval or source scope."""
import copy
import hashlib
import json
import re
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(root):
    path = Path(root) / 'source_family_corrections.json'
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    payload = {k: v for k, v in value.items() if k != 'payload_sha256'}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if value.get('payload_sha256') != digest or value.get('schema') != 'source-family-corrections-1':
        raise ValueError('Source-family correction hash/schema mismatch')
    if sha(Path(root) / 'lexicon.yaml') != value['lexicon_sha256']:
        raise ValueError('Source-family correction lexicon changed')
    for proof in value['proofs']:
        if sha(proof['path']) != proof['sha256'] or proof['verbatim_quote'] not in Path(proof['path']).read_text():
            raise ValueError('Source-family proof changed or quote missing')
    return {**value, 'active_pointer_sha256': sha(path)}


def family(paper_id, aliases):
    return aliases.get(re.sub(r'v\d+$', '', paper_id), re.sub(r'v\d+$', '', paper_id))


def apply(root, entries):
    correction = load(root)
    if correction is None:
        return entries, None
    out = []
    for entry in entries:
        item = copy.deepcopy(entry)
        families = sorted({family(s.split(':', 1)[0], correction['aliases']) for s in item.get('sources', [])})
        item['source_family_correction'] = {
            'registered_work_family_count': len(families), 'registered_work_families': families,
            'meets_shared_threshold': len(families) >= 3,
            'legacy_scope': item.get('scope'),
            'legacy_independent_paper_count': item.get('source_enrichment', {}).get('independent_paper_count', item.get('independent_paper_count')),
            'approval_scope_expanded': False,
        }
        out.append(item)
    return out, {'active_pointer_sha256': correction['active_pointer_sha256'], 'payload_sha256': correction['payload_sha256']}


def assert_fresh(evidence, root):
    current = load(root)
    expected = evidence.get('source_family_correction')
    actual = None if current is None else {k: current[k] for k in ('active_pointer_sha256', 'payload_sha256')}
    if expected != actual:
        raise ValueError('Cached evidence source-family correction changed')
