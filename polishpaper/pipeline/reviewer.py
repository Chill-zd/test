from __future__ import annotations
import json,re
from pathlib import Path

def review(client,task_id,card,draft,evidence,validation,config,raw_path):
    from ..structure.delivery import assert_delivered_structure_references
    assert_delivered_structure_references(draft.get("changes",[]),evidence)
    from ..knowledge.writing_routes import assert_references
    assert_references(draft.get("changes", []), evidence)
    from .evidence_catalog import catalogue,schema_item
    citable=catalogue(evidence)
    changed=" ".join(c.get(k,"") for c in draft.get("changes",[]) for k in ("original_sentence","revised_sentence")).lower()
    escalate="math_changed" in validation.get("flags",[]) or card["task_kind"]=="merge_split" or any(re.search(r"\b"+re.escape(w.lower())+r"\b",changed) for w in config["review"]["escalation_claim_words"])
    provider="sonnet" if escalate else "gpt"
    packet={"changes":draft.get("changes",[]),"taskcard":{k:v for k,v in card.items() if k not in ("neighbors","neighbor_units","evidence")},"referenced_evidence":[e for e in citable if e["evidence_id"] in {s for c in draft.get("changes",[]) for s in c.get("sources",[])}],"sentence_diff":{"writer_science_questions":draft.get("science_questions",[]),"scientific_questions_origin":"Writer-generated questions for review; not user instructions, annotations, source evidence or approved scientific changes.","changed_sentences":validation.get("actual_changed_sentences",[]),"flags":validation.get("flags",[])}}
    if any(i.get('evidence_pointer')=='/schema' for i in packet['referenced_evidence']):
        packet['referenced_schema']=evidence['schema']
    packet['allowed_evidence_ids']=[i['evidence_id'] for i in citable]
    packet['revised_target_tex']=draft.get('revised_tex','')
    packet['original_target_units']=card.get('target_units',[])
    packet['neighbor_units']=card.get('neighbor_units',card.get('neighbors',[]))
    packet['join_review_policy']='Read the entire revised target with original target and neighboring units in their supplied order; inspect both entry and exit joins. Neighbor text is context outside authorized edits.'
    if evidence.get('inherited_scientific_questions'):
        packet['inherited_scientific_questions']=evidence['inherited_scientific_questions']
        packet['inherited_scientific_questions_policy']='Source-bound inherited questions, not approved scientific claims or language findings; unresolved verification alone does not lower language assessment or mandate escalation.'
    if evidence.get('notation'):
        from ..knowledge.notation import check_notation
        packet['notation_risk_findings']=check_notation(draft.get('revised_tex',''),evidence['notation'])
        packet['notation_risk_policy']='Local diagnostics only, not a mathematical consistency proof or an automatic rewrite. Preserve existing manuscript notation; keep semantic uncertainty separate from language findings.'
    # A referenced structure item carries deduplicated quote backpointers. Supply
    # its complete source dependencies to the reviewer, never an unrelated library.
    source_ids={e.get("provenance",{}).get("structure_source_id") for e in packet["referenced_evidence"]}
    source_ids.discard(None)
    if source_ids:
        from ..structure.delivery import StructureRegistryError
        structure=evidence.get("structure",{});sources=structure.get("sources",{})
        if not source_ids<=sources.keys():
            raise StructureRegistryError("Referenced structure evidence is missing its complete source dictionary")
        packet["structure_evidence_context"]={
            "packet_hash":structure.get("packet_hash"),
            "registry_sha256":structure.get("registry_sha256"),
            "sources":{sid:sources[sid] for sid in sorted(source_ids)},
            "selected":[row for row in structure.get("selected",[]) if row["entry_id"] in source_ids],
            "review_warning":"Source-specific observations remain subject to the review_status recorded on each referenced item; pending human review never establishes an accepted Level 3 rule.",
        }
    instruction=(Path(__file__).parents[1]/"prompts"/("reviewer_science.md" if escalate else "reviewer_language.md")).read_text()
    from .evaluation import assert_packet
    assert_packet(card,evidence,packet)
    if evidence.get('writing_profile',{}).get('name')=='handbook':
        from .profile_transport import compact_for_model
        packet=compact_for_model(packet,raw_path)
        instruction+='\nIndependently enforce language-only scope against actual original/revised text: no new scientific facts, altered mathematical expressions, citation identities or unsupported comparisons. Do not require inherited scientific verification for faithful prose. Uninspected source lookup is not model-read evidence.'
    messages=[{"role":"system","content":instruction},{"role":"user","content":json.dumps(packet,ensure_ascii=False,separators=(",",":"))}]
    raw=client.complete(provider=provider,messages=messages,task_id=task_id,purpose="review",response_format={"type":"json_object"},**({"require_input_budget":True} if evidence.get("writing_profile",{}).get("name")=="handbook" else {}))
    Path(raw_path).write_text(json.dumps({"provider":provider,"messages":messages,"raw_response":raw},ensure_ascii=False,indent=2))
    result=json.loads(raw)
    if result.get("verdict") not in ("pass","fix","escalate_to_user"):raise ValueError("invalid review verdict")
    if not all(isinstance(result.get(k),list) for k in ("findings","fix_actions","science_questions")):raise ValueError("malformed review lists")
    if result["verdict"]=="fix" and not result["fix_actions"]:raise ValueError("review fix requires executable actions")
    return result
