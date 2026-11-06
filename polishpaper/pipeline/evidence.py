from __future__ import annotations
import json,yaml
from pathlib import Path

_EXPLICIT_NOTATION_RULES=[
    'Preserve the manuscript\'s existing symbol identities and mathematical meaning. Do not rename or replace established notation without explicit authorization.',
    'Keep notation consistent within this manuscript; a reference catalog is not authority to impose different existing symbols.',
    r'Use \bm{...} for bold mathematics and \citep{...} for manuscript citations within the authorized scope; preserve symbols, citation keys and scientific meaning.',
    'Report unresolved notation conflicts as scientific questions rather than silently choosing new mathematical meaning.'
]


def prepare_notation(card,knowledge_dir=None,*,catalog_enabled=True,baseline=None,exclusions=None):
    """The source catalog is full-only; explicit user constraints also cover bare."""
    import hashlib
    units=[];seen=set()
    for unit in card.get('target_units',[])+card.get('neighbor_units',card.get('neighbors',[])):
        key=unit.get('unit_id') or id(unit)
        if key in seen:continue
        seen.add(key);units.append(unit)
    text='\n\n'.join([baseline.get('preamble_context','')]+[u['prose_text'] for u in baseline['units']]) if baseline else '\n\n'.join(u.get('prose_text',u.get('text','')) for u in units)
    catalog=Path(knowledge_dir)/'notation.json' if knowledge_dir is not None else None
    from ..knowledge.notation import build_notation_plan
    extra={'source_filter':lambda entry,refs:exclusions.allow('notation',refs,entry['id'])} if exclusions else {}
    plan=build_notation_plan(text,catalog_path=catalog,overrides=card.get('notation_overrides'),enabled=catalog_enabled,**extra)
    if not catalog_enabled:plan['status']='catalog_disabled_bare'
    plan.update(catalog_enabled=catalog_enabled,explicit_user_rules=list(_EXPLICIT_NOTATION_RULES),
        input_text_sha256=hashlib.sha256(text.encode()).hexdigest(),
        input_scope='whole_parsed_manuscript' if baseline else 'scoped_context',
        input_scope_note='Main/input/include parsed body plus separately recorded unexpanded preamble context; reference prose is excluded.' if baseline else 'Only supplied target and neighbor units; no whole-manuscript inventory is claimed.')
    if baseline:
        from .notation_baseline import summary
        plan['manuscript_baseline']=summary(baseline)
    return plan

def gather(card:dict,knowledge_dir:str|Path,config:dict,search=None,notation_baseline=None,evaluation_exclusions=None)->dict:
    root=Path(knowledge_dir);limits=config["retrieval"];items=[]
    from .evaluation import resolve
    exclusions=resolve(card,evaluation_exclusions)
    if exclusions and not card.get('evaluation_exclusions'):raise ValueError('Evaluation exclusions must be bound to the taskcard')
    for i,a in enumerate(card["annotations"]):
        items.append({"evidence_id":a.get("annotation_id",f"annotation:{i}"),"source_tag":a.get("source_tag","real_annotation"),"text":a.get("text",""),"conditions":a.get("conditions",[]),"provenance":a.get("provenance",{})})
    items.append({"evidence_id":"user_request","source_tag":"user_request","text":card["user_request"],"conditions":[],"provenance":{"task":"current"}})
    lex=[]
    if (root/"lexicon.yaml").exists():
        data=yaml.safe_load((root/"lexicon.yaml").read_text()) or []
        for row in data:
            if row.get("term") in card["concepts"]:lex.extend({**e,'term':row['term']} for e in row.get("entries",[]))
    if exclusions:lex=exclusions.select('lexicon',lex)
    from ..knowledge.human_review import apply_review
    lex,lexicon_review=apply_review(root,lex)
    from ..knowledge.source_families import apply as correct_families
    lex,family_correction=correct_families(root,lex)
    from ..knowledge.writing_routes import verified_legacy_examples
    lex_origin_withheld=sum(not verified_legacy_examples(e,root) for e in lex)
    lex=[e for e in lex if verified_legacy_examples(e,root)]
    for i,e in enumerate(lex[:limits["max_lexicon_entries"]]):
        items.append({"evidence_id":f"lexicon:{i}","source_tag":"coauthor_text","text":e["phrase"],"conditions":[e.get("scope","")]+(["Independent registered work-family count is below three; this legacy shared entry must not be treated as a shared writing rule. Preserve its original narrow reviewed scope."] if e.get("scope")=="shared" and e.get("source_family_correction",{}).get("meets_shared_threshold") is False else []),"provenance":{k:v for k,v in e.items() if k not in ("phrase","scope")}})
    stype=card["section_type"]
    funcs={"related_work":["comparison","transition"],"theory":["theorem_intuition","definition"]}.get(stype,["transition"])
    if any("assumption" in a.get("text","").lower() for a in card["annotations"]):funcs.append("assumption")
    patterns=[]
    for fn in funcs:
        p=root/"patterns"/f"{fn}.jsonl"
        if p.exists():patterns.extend(json.loads(line) for line in p.read_text().splitlines() if line.strip())
    if exclusions:patterns=exclusions.select('patterns',patterns)
    from ..knowledge.writing_routes import verified_legacy_examples
    pattern_origin_audit={'withheld_unknown_or_non_clint':sum(not verified_legacy_examples(p,root) for p in patterns)}
    patterns=[p for p in patterns if verified_legacy_examples(p,root)]
    for i,p in enumerate(patterns[:limits["max_pattern_entries"]]):
        items.append({"evidence_id":f"pattern:{i}","source_tag":"coauthor_text","text":p.get("template",""),"conditions":p.get("condition",[]),"provenance":{"examples":p.get("examples",[])}})
    from ..knowledge.semantic_supplement import select as select_supplement
    supplement_selected=select_supplement(card,root,exclusions,max_contexts=limits["max_lexicon_entries"])
    items.extend(supplement_selected["items"])
    schema_file=root/"schemas"/f"{stype}.yaml"
    schema=yaml.safe_load(schema_file.read_text()) if schema_file.exists() else None
    if schema and exclusions and not exclusions.allow('schema',schema,stype):schema=None
    if supplement_selected["schema"] is not None:
        schema=supplement_selected["schema"]
    from ..structure.delivery import select_evidence
    extra={'source_filter':lambda inventory,eid:exclusions.allow('structure',inventory,eid)} if exclusions else {}
    structure_items,structure=select_evidence(card,root,limits["max_evidence_units"],max_packet_chars=limits.get("max_structure_packet_chars",250000),**extra)
    items.extend(structure_items)
    from ..knowledge.writing_routes import select as select_routes
    route_items, route_audit = select_routes(card, root, exclusions)
    items.extend(route_items)
    # Explicit pilot opt-in; catalog presence alone never activates pending interpretations.
    adjacent_items=[]
    adjacent_audit={"status":"disabled","selected":[]}
    if card.get("adjacent_transfer_pilot") is True:
        from ..knowledge.adjacent_transfers import select as select_adjacent
        adjacent_items,adjacent_audit=select_adjacent(card,root,exclusions)
        items.extend(adjacent_items)
    remaining_units=max(0,limits["max_evidence_units"]-len(structure_items))
    from ..memory.reviewed_feedback import active,assert_object_fresh,feedback_context
    feedback_review=active(root)
    feedback_scope=feedback_context(card)
    domain=[];feedback=[];science=[]
    if search is not None:
        def find(section,kinds,limit):
            extra={'exclude':lambda obj:not exclusions.allow(kinds[0],obj)} if exclusions else {}
            return search(card['user_request'],section,card['concepts'],kinds,limit,**extra)
        if remaining_units:domain=find(stype,["unit"],remaining_units)
        feedback_stype=feedback_scope['section_type']
        feedback=find(feedback_stype,["feedback"],limits["max_feedback_entries"])
        if feedback_review:
            guidance=find(feedback_stype,["user_guidance"],limits["max_feedback_entries"])
            feedback=sorted(list(feedback)+list(guidance),key=lambda h:h.get('score',0),reverse=True)
            science=list(find(feedback_stype,["science_question"],limits["max_feedback_entries"]))
        checked=[];cache={}
        for hit in list(feedback)+science:
            if hit.get('provenance',{}).get('schema')=='reviewed-advisor-feedback-1':
                if not feedback_review:continue
                if hit['provenance']['admission_manifest']!=feedback_review['manifest']:raise ValueError('Feedback index belongs to a different active human review')
                assert_object_fresh(hit,cache)
            checked.append(hit)
        feedback=[h for h in checked if h.get('kind')!='science_question']
        science=[h for h in checked if h.get('kind')=='science_question']
    for i,h in enumerate(list(feedback)[:limits["max_feedback_entries"]]+list(domain)[:remaining_units]):
        tag=h.get("source_tag","coauthor_text")
        items.append({"evidence_id":f"retrieved:{i}","source_tag":tag,"text":h["text"],"conditions":h.get("conditions",[]),"provenance":h})
    supplement_snapshot=supplement_selected["snapshot"]
    supplement_scope=supplement_selected["selected_ids"]
    result={"semantic_supplement":supplement_snapshot,"semantic_supplement_scope":supplement_scope,"semantic_supplement_policy":"Exact reviewed schema/context scope only; approval does not endorse new routes, other source units or scientific claims.","items":items,"schema":schema,"schema_status":schema.get("review_status") if schema else "absent","schema_warning":"schema is pending human review" if schema and schema.get("review_status")!="approved" else None,"writing_routes":route_audit,"pattern_origin_audit":pattern_origin_audit,"lexicon_origin_withheld":lex_origin_withheld,"structure":structure,"structure_warning":"; ".join(structure["warnings"]) or None,"lexicon_review":lexicon_review,"feedback_review":feedback_review,"feedback_context":feedback_scope,"inherited_scientific_questions":science,"notation":prepare_notation(card,root,baseline=notation_baseline,exclusions=exclusions),"mode":"normal" if domain or feedback or lex or patterns or structure_items or route_items or adjacent_items or supplement_selected["items"] or supplement_selected["schema"] else "no_domain_evidence"}
    if card.get("adjacent_transfer_pilot") is True:
        result["adjacent_transfers"]=adjacent_audit
    from .evidence_catalog import schema_item
    schema_reference=schema_item(result)
    if schema_reference:result["items"].append(schema_reference)
    if family_correction:result['source_family_correction']=family_correction
    if exclusions:result['evaluation_exclusions']=exclusions.audit()
    return result


def assert_fresh(evidence,knowledge_dir):
    from .adjacent_pilot import assert_fresh as adjacent_fresh
    adjacent_fresh(evidence)
    if evidence.get("writing_profile",{}).get("name")=="handbook":
        from .handbook_profile import assert_profile_fresh
        assert_profile_fresh(evidence,knowledge_dir)
        return
    from ..knowledge.semantic_supplement import assert_fresh as supplement_fresh
    supplement_fresh(evidence.get("semantic_supplement"),knowledge_dir)
    from ..knowledge.writing_routes import assert_fresh as routes_fresh
    routes_fresh(evidence,knowledge_dir)
    from ..knowledge.source_families import assert_fresh as family_fresh
    family_fresh(evidence,knowledge_dir)
    from .evaluation import assert_fresh as exclusion_fresh
    exclusion_fresh(evidence)
    from ..structure.delivery import assert_fresh as structure_fresh
    from ..knowledge.human_review import assert_fresh as review_fresh
    from ..memory.reviewed_feedback import assert_evidence_fresh
    structure_fresh(evidence,knowledge_dir);review_fresh(evidence,knowledge_dir)
    assert_evidence_fresh(evidence,knowledge_dir)
    import hashlib
    catalog=Path(knowledge_dir)/'notation.json';plan=evidence.get('notation',{})
    if plan.get('manuscript_baseline'):
        from .notation_baseline import assert_fresh as baseline_fresh
        baseline_fresh(plan['manuscript_baseline'])
    if plan.get('catalog_enabled',True):
        actual=hashlib.sha256(catalog.read_bytes()).hexdigest() if catalog.is_file() else None
        if actual!=plan.get('catalog_sha256'):raise ValueError('Notation catalog changed; prepare evidence again')
        for item in plan.get('source_bindings',[]):
            if isinstance(item,dict) and 'path' in item and 'sha256' in item:
                from ..memory.reviewed_feedback import checked
                checked(item)
        from ..knowledge.notation import assert_notation_fresh
        assert_notation_fresh(plan)
