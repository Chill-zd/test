"""STAGING ONLY: explicitly scoped handbook writing; never legacy complete full."""
import copy,hashlib,json,re
from pathlib import Path
from ..corpus.parser import strip_comments
from ..knowledge.notation import _math_symbols
from .evidence import prepare_notation
from .evaluation import resolve

class ProfileAmbiguity(ValueError):pass

def binding(path):return {'path':str(Path(path).resolve()),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}
def refs(text):return {v.strip() for group in re.findall(r'\\(?:[cC]ref|ref|eqref|autoref)\{([^}]+)\}',text) for v in group.split(',')}
def text(unit):return unit.get('prose_text',unit.get('text',''))

def manuscript_closure(card,baseline,direct_only=False):
    units=baseline['units'];labels={}
    for u in units:
        for label in re.findall(r'\\label\{([^}]+)\}',text(u)):
            if label in labels:raise ProfileAmbiguity('Ambiguous duplicate manuscript label: '+label)
            labels[label]=u
    roots=card.get('target_units',[])+card.get('neighbor_units',card.get('neighbors',[]))
    required=set().union(*(refs(text(u)) for u in roots)) if roots else set()
    symbols=set(_math_symbols('\n'.join(text(u) for u in roots)))
    definitions=[u for u in baseline['definition_contexts'] if symbols & set(_math_symbols(text(u)))]
    # Definitions stay in the exact complete audit. These locators do not supply
    # uninspected definitions or authorize a change to an inherited assertion.
    lookup={}
    for u in definitions:
        lookup[u['unit_id']]={k:u[k] for k in ('unit_id','file','offset_start','offset_end','prose_sha256')}
    unresolved=[{'kind':'uninspected_definition_candidates','symbol':symbol,'candidate_ids':[u['unit_id'] for u in definitions if symbol in _math_symbols(text(u))],
                 'question':'Literal same-glyph candidates are not semantic definitions. Preserve the original notation and assertion; resolving identity is outside this language-only profile.'} for symbol in sorted(symbols)]
    unavailable=sorted(required-labels.keys())
    direct=[]
    for label in sorted(required & labels.keys()):
        u=labels[label]
        # A whole section label is identity lookup only; direct equation/theorem
        # envelopes plus exact immediate explanatory joins are supplied in full.
        if re.fullmatch(r'\s*\\label\{[^}]+\}\s*',text(u)):continue
        i=units.index(u)
        for j in (i-1,i,i+1):
            if 0<=j<len(units) and units[j]['section_path']==u['section_path'] and units[j] not in direct:direct.append(units[j])
    return {'scope':'language-only; mathematical expressions, citations, labels and technical assertions frozen; original scientific truth is not certified',
            'reference_label_identity':{label:({'unit_id':labels[label]['unit_id'],'file':labels[label]['file']} if label in labels else None) for label in sorted(required)},
            'direct_reference_contexts':direct,'definition_candidate_lookup':lookup,'unavailable_reference_labels':unavailable,'scientific_questions':unresolved+[{'kind':'unavailable_manuscript_reference','label':label,'question':'Reference identity is unavailable. Preserve the original and surface uncertainty; do not add a supporting claim.'} for label in unavailable],
            'definition_policy':'Lookup is local proof of physical candidates only; these definitions were not delivered or inspected by the writer. No semantic identity or scientific fact may be inferred.'}

def prepare(card,evidence,baseline,knowledge_dir,task,bare=False,direct_only=False):
    if card['task_kind'] not in ('language','revise'):raise ProfileAmbiguity('Staged handbook profile supports authorized language tasks only')
    request=card.get('user_request','')
    if re.search(r'\b(?:prove|derive|establish)\s+(?:a\s+)?new\b|\bchange\s+(?:the\s+)?(?:objective|assumption|theorem)\b',request,re.I):
        raise ProfileAmbiguity('Requested scientific alteration exceeds the explicitly language-only handbook profile')
    task=Path(task);archive=task/'handbook_full_source_audit.json'
    complete={'taskcard':card,'evidence':evidence,'baseline':baseline}
    if archive.exists():
        if json.loads(archive.read_text())!=complete:raise ProfileAmbiguity('Immutable full audit differs')
    else:archive.write_text(json.dumps(complete,ensure_ascii=False,indent=2)+'\n')
    closure=manuscript_closure(card,baseline,direct_only=direct_only)
    e=copy.deepcopy(evidence);omitted=[i['evidence_id'] for i in e['items'] if i['evidence_id'].startswith('structure:')]
    e['items']=[i for i in e['items'] if i['evidence_id'] not in omitted]
    e.pop('structure',None);e.pop('structure_warning',None)
    scoped_card=copy.deepcopy(card)
    scoped_card['neighbor_units']=list(card.get('neighbor_units',card.get('neighbors',[])))
    e['notation']=prepare_notation(scoped_card,knowledge_dir,catalog_enabled=not bare,exclusions=resolve(card))
    e['notation']['manuscript_definition_reference_closure']=closure
    e['notation']['limitations'].append('Handbook profile has physical target-symbol candidate/reference lookup only, not delivered scientific definitions or the legacy whole-manuscript notation delivery. Unavailable references remain scientific questions.')
    e['writing_profile']={'name':'handbook','bare':bare,'legacy_complete_full':False,'full_source_audit':binding(archive),'omitted_legacy_structure_evidence_ids':omitted,
       'omission_policy':'Legacy organization observations remain locally archived and were not delivered. Selected approved schema, allowed lexical/pattern/feedback/handbook examples and conditions remain exact.',
       'language_only_science_frozen':True,'unchanged_original_allowed':True,'selector_policy':'Existing lexical bilingual retrieval only; not semantic fit. No forced route use or edit.'}
    return e


def assert_profile_fresh(evidence,knowledge_dir):
    profile=evidence['writing_profile'];bound=profile['full_source_audit'];path=Path(bound['path'])
    if binding(path)!=bound:raise ValueError('Handbook full source audit changed')
    original=json.loads(path.read_text())
    if profile.get('bare'):
        from .notation_baseline import assert_fresh as baseline_fresh
        baseline_fresh(original['baseline'])
        return
    # Omitted legacy structure is archived history, not a selected lane. Validate
    # the current selected lanes and original manuscript source instead.
    from ..knowledge.semantic_supplement import assert_fresh as supplement_fresh
    from ..knowledge.writing_routes import assert_fresh as routes_fresh
    from ..knowledge.human_review import assert_fresh as review_fresh
    from ..knowledge.source_families import assert_fresh as family_fresh
    from ..memory.reviewed_feedback import assert_evidence_fresh
    from .evaluation import assert_fresh as exclusion_fresh
    from .notation_baseline import assert_fresh as baseline_fresh
    from ..knowledge.notation import assert_notation_fresh
    supplement_fresh(evidence.get('semantic_supplement'),knowledge_dir)
    routes_fresh(evidence,knowledge_dir);review_fresh(evidence,knowledge_dir)
    family_fresh(evidence,knowledge_dir);exclusion_fresh(evidence)
    assert_evidence_fresh(evidence,knowledge_dir);baseline_fresh(original['baseline'])
    assert_notation_fresh(evidence['notation'])


def science_freeze(original,revised,evidence):
    if not evidence.get('writing_profile',{}).get('language_only_science_frozen'):return []
    from .validators import _math
    from collections import Counter
    errors=[]
    normalize=lambda x:[v.replace(r'\mathbf',r'\bm') for v in _math(x)]
    if normalize(original)!=normalize(revised):errors.append('handbook language-only profile: mathematical expressions changed')
    def citations(s):return Counter(tuple(k.strip() for k in keys.split(',')) for keys in re.findall(r'\\[Cc]ite\w*(?:\[[^]]*\])*\{([^}]+)\}',s))
    if citations(original)!=citations(revised):errors.append('handbook language-only profile: citation keys changed')
    if Counter(re.findall(r'\\(?:label|[cC]ref|ref|eqref)\{([^}]+)\}',original))!=Counter(re.findall(r'\\(?:label|[cC]ref|ref|eqref)\{([^}]+)\}',revised)):
        errors.append('handbook language-only profile: label/reference identity changed')
    comparison=r'\b(?:faster|slower|greater|smaller|higher|lower|more than|less than|at least|at most|strictly|uniquely|always|never)\b'
    if Counter(v.casefold() for v in re.findall(comparison,original,re.I))!=Counter(v.casefold() for v in re.findall(comparison,revised,re.I)):
        errors.append('handbook language-only profile: comparison/quantifier wording changed; unavailable science cannot justify it')
    return errors
