"""One writing call and at most one strict-format retry, with restartable audit."""
from __future__ import annotations
import json
from pathlib import Path

def write(client,task_id,card,evidence,bib_keys,macros,raw_path):
    from .validators import DRAFT_SCHEMA
    instruction=(Path(__file__).parents[1]/'prompts'/'writer.md').read_text()
    from .evidence import prepare_notation
    notation=evidence.get('notation') or prepare_notation(card,catalog_enabled=False)
    from .adjacent_pilot import writer_projection
    writer_evidence=writer_projection(evidence)
    if writer_evidence is not evidence and evidence.get("writing_profile",{}).get("name")!="handbook":
        # The complete notation dictionary is already supplied at packet.notation.
        writer_evidence.pop('notation',None)
    packet={'output_json_schema':DRAFT_SCHEMA,'no_evidence_clause':'Only edits directly supported by the user request or annotations' if evidence['mode']=='no_domain_evidence' else 'Use evidence only within stated conditions','taskcard':card,'evidence':writer_evidence,'notation':notation,'bib_keys':sorted(bib_keys),'preamble_macros':sorted(macros)}
    from .evidence_catalog import allowed_ids
    packet['allowed_evidence_ids']=sorted(allowed_ids(evidence))
    packet['evidence_id_policy']='Only these IDs are citable. Source/unit/backpointer keys are provenance, not evidence IDs. A selected schema resolves at evidence.schema.'
    from .evaluation import assert_packet
    assert_packet(card,evidence,{**packet,"evidence":evidence})
    assert_packet(card,evidence,packet)
    if evidence.get('writing_profile',{}).get('name')=='handbook':
        from .profile_transport import compact_for_model
        instruction+='\nThis is explicitly language-only handbook writing, not legacy complete full. Preserve mathematical expressions, citation/label identities, technical assertions and comparative meaning. Local uninspected definition lookups confer no scientific authority. If a requested change requires unavailable scientific resolution, retain the original and report a scientific question. No route use or edit is required.'
        from .profile_transport import fit_optional_routes
        budget=getattr(client,'config',{}).get('llm',{}).get('gpt',{}).get('max_input_utf8_bytes')
        fit_optional_routes(packet,instruction,raw_path,budget)
        packet=compact_for_model(packet,raw_path)
        from .profile_transport import decode
        assert_packet(card,evidence,decode(packet))
    capacity_required = evidence.get('writing_profile',{}).get('name') != 'handbook' and evidence.get('schema_status') != 'omitted_bare'
    messages=[{'role':'system','content':instruction},{'role':'user','content':json.dumps(packet,ensure_ascii=False,separators=(",",":"))}]
    # This threshold is a hazard trigger, never a proof that smaller input fits.
    capacity_required = capacity_required and getattr(client,'config',{}).get('llm',{}).get('gpt',{}).get('transport') == 'codex_host' and sum(len(m['content'].encode()) for m in messages) > 100000
    capacity_kwargs = {'require_verified_capacity': True} if capacity_required else {}
    path=Path(raw_path)
    def save(audit):path.write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    if path.exists():audit=json.loads(path.read_text());raw=audit['raw_response']
    else:
        raw=client.complete(provider='gpt',messages=messages,task_id=task_id,purpose='writer',response_format={'type':'json_object'},**capacity_kwargs)
        audit={'messages':messages,'raw_response':raw};save(audit)
    if 'format_repair_response' in audit:return json.loads(audit['format_repair_response'])
    try:return json.loads(raw)
    except json.JSONDecodeError:
        if audit.get('format_repair_requested') and not audit.get('format_repair_host_pending'):raise ValueError('Prior format retry failed; retained audit requires user attention')
        fixed_messages=messages+[{'role':'assistant','content':raw},{'role':'user','content':'Return valid JSON only, same scientific content.'}]
        audit.update(format_repair_requested=True,format_repair_messages=fixed_messages);save(audit)
        from ..llm.host_bridge import PendingHostCall
        try:fixed=client.complete(provider='gpt',messages=fixed_messages,task_id=task_id,purpose='format_repair',response_format={'type':'json_object'},**capacity_kwargs)
        except PendingHostCall:
            audit['format_repair_host_pending']=True;save(audit);raise
        audit['format_repair_response']=fixed;save(audit)
        return json.loads(fixed)
