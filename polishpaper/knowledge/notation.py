"""Source-bound notation suggestions. No replacement, theorem checking or admission."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re

USER_RULES = [
    'Preserve the manuscript\'s explicitly defined symbols and scientific meaning; never globally rename from a reference list.',
    r'Use \bm{...}, not \mathbf{...}, for new bold mathematical notation within authorized scope.',
    r'Use \citep{...} for new or revised citations within authorized scope.',
    'A project-specific explicit semantic mapping overrides a reference preference; collisions or unknown new objects are scientific questions, not silent repairs.',
]

def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _comment_free(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)

def _normal(text):
    return re.sub(r'\s+', '', text.replace(r'\mathbf', r'\bm'))

def _math_symbols(text):
    """Conservative decorated/Greek inventory, not a TeX expansion or semantic parser."""
    text = _comment_free(text)
    spans = re.findall(r'\$\$(.*?)\$\$|(?<!\\)\$(.*?)(?<!\\)\$|\\\[(.*?)\\\]|\\\((.*?)\\\)|\\begin\{(?:equation\*?|align\*?|gather\*?)\}(.*?)\\end\{(?:equation\*?|align\*?|gather\*?)\}', text, re.S)
    math = '\n'.join(next((v for v in row if v), '') for row in spans)
    found = re.findall(r'\\(?:bm|mathbf|mathcal|mathbb|mathfrak)\s*\{[^{}]+\}|\\(?:alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega)\b', math)
    return sorted(set(found))

def assert_notation_fresh(plan):
    """Check the exact catalogue and physical source identities frozen in a plan."""
    if plan.get('status') != 'ready':
        return
    if _hash(plan['catalog_path']) != plan['catalog_sha256']:
        raise ValueError('Notation catalogue changed after preparation')
    for source in plan.get('source_bindings', []):
        if _hash(source['source_path']) != source['source_sha256']:
            raise ValueError('Notation source changed after preparation: ' + source['id'])
        if source.get('origin_archive') and _hash(source['origin_archive']) != source['origin_archive_sha256']:
            raise ValueError('Notation original archive changed after preparation: ' + source['id'])

def build_notation_plan(text, catalog_path=None, *, overrides=None, enabled=True, source_filter=None):
    """Return explicit rules plus optional source suggestions; do not alter text.

    overrides maps catalogue semantic entry IDs to exact project LaTeX. Missing
    or disabled catalogues retain explicit user rules. Unknown override IDs are
    disclosed, never guessed. Sources must be fresh before any plan is ready.
    """
    plan = {'schema': 'notation-plan-1', 'status': 'disabled' if not enabled else 'unavailable',
            'explicit_user_rules': list(USER_RULES), 'writer_guidance': list(USER_RULES),
            'policy': 'existing_defined_notation_then_explicit_project_mapping_then_primary_then_verified_Clint_fallback',
            'matched_entries': [], 'explicit_overrides': copy.deepcopy(overrides or {}),
            'scientific_questions': [], 'source_bindings': [],
            'baseline_symbols': _math_symbols(text), 'catalog_sha256': None,
            'limitations': ['Literal matching cannot establish object identity, notation adequacy, index consistency, tensor shape, first-use definitions or scientific correctness. Unknown-symbol detection covers decorated and Greek symbols only; ordinary letters, macros and expansions need contextual review.'],
            'human_approval': False, 'automatic_renaming': False}
    if not enabled:
        return plan
    path = Path(catalog_path) if catalog_path else Path(__file__).resolve().parents[2] / 'data/knowledge/notation.json'
    if not path.exists():
        plan['scientific_questions'].append({'kind': 'notation_catalog_unavailable', 'question': 'No activated source notation catalogue is available; retain manuscript notation.'})
        return plan
    data = json.loads(path.read_text())
    if data.get('schema') != 'source-bound-notation-catalog-1':
        raise ValueError('Unsupported notation catalogue schema')
    plan.update(status='ready', catalog_path=str(path.resolve()), catalog_sha256=_hash(path))
    ids = {e['id'] for e in data['entries']}
    for key in plan['explicit_overrides']:
        if key not in ids:
            plan['scientific_questions'].append({'kind': 'unbound_override', 'object_id': key, 'question': 'Explicit project mapping is retained, but its semantic object is absent from the catalogue; clarify its definition rather than infer a match.'})
    source_ids = set()
    # Search only mathematical spans; single-letter entries must be tokens.
    math_spans = re.findall(r'\$\$(.*?)\$\$|(?<!\\)\$(.*?)(?<!\\)\$|\\\[(.*?)\\\]|\\\((.*?)\\\)|\\begin\{(?:equation\*?|align\*?|gather\*?)\}(.*?)\\end\{(?:equation\*?|align\*?|gather\*?)\}', _comment_free(text), re.S)
    plain = _normal(' | '.join(next((v for v in row if v), '') for row in math_spans))
    def lexical_match(value):
        value = _normal(value)
        if re.fullmatch(r'[A-Za-z]', value):
            return bool(re.search(r'(?<![A-Za-z])' + re.escape(value) + r'(?![A-Za-z])', plain))
        return value in plain

    for entry in data['entries']:
        if source_filter is not None and not source_filter(entry,[dict(id=r['source_id'],**data['sources'][r['source_id']]) for r in entry['source_refs']]):
            continue
        variants = [entry['preferred_latex'], *entry.get('original_latex', []), *entry.get('match_aliases', [])]
        if any(lexical_match(v) for v in variants if v) or entry['id'] in plan['explicit_overrides']:
            item = copy.deepcopy(entry)
            if entry['id'] in plan['explicit_overrides']:
                value = plan['explicit_overrides'][entry['id']]
                if not isinstance(value, str) or not value.strip():
                    raise ValueError('Notation overrides must map semantic IDs to nonempty LaTeX strings')
                item['project_latex'] = value
            item['match_status'] = 'potential_lexical_match_not_semantic_identity'
            item['instruction'] = 'Reference identity only: preserve an existing manuscript definition; use this preference for a newly introduced identical object only after contextual meaning/shape checks.'
            plan['matched_entries'].append(item)
            source_ids.update(r['source_id'] for r in entry['source_refs'])
    glyphs = {}
    for entry in plan['matched_entries']:
        effective = entry.get('project_latex', entry['preferred_latex'])
        glyphs.setdefault(_normal(effective), []).append(entry['id'])
    for glyph, objects in sorted(glyphs.items()):
        if len(objects) > 1:
            plan['scientific_questions'].append({'kind': 'notation_object_collision', 'symbol': glyph,
                'object_ids': objects, 'question': 'Distinct catalogue objects share this effective notation. Existing manuscript definitions take priority; clarify local scope or an explicit mapping instead of silently merging or renaming them.'})
    plan['source_bindings'] = [dict(id=sid, **data['sources'][sid]) for sid in sorted(source_ids)]
    assert_notation_fresh(plan)
    plan['writer_guidance'].append('Matched entries are source-bound suggestions, not instructions to rewrite existing symbols. Distinguish probability vectors, laws of kernels and sets of laws. Do not import reward-maximization signs or algorithm-specific roles into a cost-minimization manuscript.')
    return plan

def check_notation(text, plan):
    """Report questions only; no mutation and no alleged mathematical pass."""
    assert_notation_fresh(plan)
    findings = []
    clean = _comment_free(text)
    if r'\mathbf' in clean:
        findings.append({'kind': 'bold_macro', 'lane': 'language', 'question': r'Use the authorized \bm convention for bold notation without changing symbols or protected exact text.'})
    if re.search(r'\\(?:citet|Citet|citealp|cite)\s*(?:\[[^\]]*\]\s*)*\{', clean):
        findings.append({'kind': 'citation_form', 'lane': 'language', 'question': r'Use \citep in the authorized revised citation, preserving keys and meaning.'})
    baseline = {_normal(v) for v in plan.get('baseline_symbols', [])}
    known = set()
    for e in plan.get('matched_entries', []):
        for value in [e['preferred_latex'], *e.get('original_latex', []), *e.get('match_aliases', [])]:
            known.update(_normal(v) for v in _math_symbols('$' + value + '$'))
    known.update(_normal(v) for v in plan.get('explicit_overrides', {}).values() if isinstance(v, str))
    for symbol in _math_symbols(clean):
        if _normal(symbol) not in baseline | known:
            findings.append({'kind': 'new_unbound_symbol', 'lane': 'scientific_questions', 'symbol': symbol,
                             'question': 'A new decorated/Greek symbol is not bound to the supplied manuscript inventory or matched reference entries. State its object, domain, indices and shape; do not invent or rename its meaning.'})
    return findings
