"""Source-bound human decisions, separate from immutable machine/source artifacts."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import yaml

class HumanReviewError(ValueError):
    pass

def _hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def _digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _binding(path):return {'path':str(Path(path).resolve()),'sha256':_hash(path)}
def _read(binding):
    path=Path(binding['path'])
    if not path.is_file()or _hash(path)!=binding['sha256']:raise HumanReviewError('Human-review bound artifact changed or missing')
    return json.loads(path.read_text())
def _write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if json.loads(path.read_text())!=value:raise HumanReviewError('Refusing to overwrite different human-review artifact')
    else:
        with path.open('x')as handle:json.dump(value,handle,ensure_ascii=False,indent=2);handle.write('\n')

def stage_review(intake_dir,registry_path,lexicon_path,output_path):
    """Prepare actual supplied decisions; never activate or change source analyses.

    The original signed export covers its own decisions only. Additional decisions
    must be exactly the source-bound supplemental declaration, not a copied signature.
    """
    root=Path(intake_dir);names=['original_export.verbatim.json','supplemental_declaration.json','added_64_manifest.json','merged_review.importable.json','current_review_data.snapshot.json','intake_manifest.json']
    bindings={name:_binding(root/name)for name in names};values={name:_read(b)for name,b in bindings.items()}
    original=values[names[0]];declaration=values[names[1]];added=values[names[2]];merged=values[names[3]];snapshot=values[names[4]];manifest=values[names[5]]
    if not original.get('reviewer')or not original.get('confirmed_at')or not original.get('attestation'):raise HumanReviewError('Original human export lacks its own provenance')
    for field in ['packet_fingerprint','dataset_fingerprint','lexicon_fingerprint','feedback_fingerprint']:
        expected=snapshot.get(field)if field in snapshot else snapshot.get(field.replace('_fingerprint',''),{}).get('fingerprint')
        if any(obj.get(field)!=expected for obj in [original,merged,declaration['binding']]):raise HumanReviewError('Human-review snapshot fingerprint mismatch')
    if declaration['binding']['original_export_sha256']!=bindings[names[0]]['sha256']or declaration['binding']['current_dataset_file_sha256']!=bindings[names[4]]['sha256']:raise HumanReviewError('Supplement is not bound to exact original export and snapshot')
    for name,record in manifest['files'].items():
        if _hash(root/name)!=record['sha256']:raise HumanReviewError('Intake manifest file changed')
    decisions=merged['decisions'];base=original['decisions'];additions=added['added_decisions']
    if any(decisions.get(k)!=v for k,v in base.items()):raise HumanReviewError('Original human choice or literal note was altered')
    if set(decisions)-set(base)!={d['id']for d in additions}:raise HumanReviewError('Supplement decision IDs differ from explicit source-bound mapping')
    if [q['text']for q in declaration['quotes']]!=['后64项我认为没有问题','原始批注我还没看']:raise HumanReviewError('Supplemental scope declaration is not the supplied user statement')
    if len(additions)!=64 or any(decisions[d['id']]!={'decision':'approve','notes':''}for d in additions):raise HumanReviewError('Supplement decisions differ from actual declaration')
    registry_binding=_binding(registry_path);registry=_read(registry_binding)
    from ..structure.inventory import digest
    if registry.get('schema')!='structure-delivery-1'or digest({k:v for k,v in registry.items()if k!='packet_hash'})!=registry.get('packet_hash'):raise HumanReviewError('Registry packet changed')
    sources={s['id']:s for c in snapshot['cards']for s in c['sources']};entries=[];known=set()
    for entry in registry['entries']:
        sid=entry['section_id'];source=sources.get(sid)
        if not source:raise HumanReviewError('Reviewed source section does not match registry')
        analysis=_read(entry['analysis']);inventory=_read(entry['inventory'])
        if analysis['section_id']!=sid or inventory['paper_id']!=source['paper_id']or analysis['section_observation']!=source['observation']:raise HumanReviewError('Section analysis is not the exact reviewed observation')
        units={u['id']:u for u in source['units']};unit_decisions={}
        for uid,u in units.items():
            canonical=inventory['units'][uid]
            if u['text']!=canonical['prose_text']or u['sha256']!=canonical['prose_sha256']:raise HumanReviewError('Reviewed unit is not the exact original source')
            if u['kind']=='source_metadata':continue
            records=[v for v in analysis['units']if v['unit_instance_id']==uid]
            if records!=u['analysis']:raise HumanReviewError('Unit analysis differs from reviewed snapshot')
            unit_decisions[uid]=copy.deepcopy(decisions[uid]);known.add(uid)
        known.add(sid);entries.append({'entry_id':entry['entry_id'],'section_id':sid,'analysis_sha256':entry['analysis']['sha256'],'inventory_sha256':entry['inventory']['sha256'],'section_decision':copy.deepcopy(decisions[sid]),'unit_decisions':unit_decisions})
    lex_binding=_binding(lexicon_path)
    if lex_binding['sha256']!=snapshot['lexicon']['lexicon_sha256']:raise HumanReviewError('Lexicon differs from reviewed snapshot')
    lexical=[];source_files={}
    raw_lexicon=yaml.safe_load(Path(lexicon_path).read_text())or []
    for group in raw_lexicon:
        for item in group.get('entries',[]):
            if item.get('scope')!='shared':continue
            for source in item.get('source_enrichment',{}).get('source_occurrences',[]):
                binding={'path':source['source_path'],'sha256':source['source_file_sha256']}
                if _hash(binding['path'])!=binding['sha256']:raise HumanReviewError('Reviewed lexical source file changed')
                if binding['path']in source_files and source_files[binding['path']]!=binding:raise HumanReviewError('Conflicting lexical source binding')
                source_files[binding['path']]=binding
    for item in snapshot['lexicon']['entries']:
        known.add(item['id']);context_roles=[]
        if decisions[item['id']]['decision']=='needs_revision':
            for example in item['examples']:
                before=example['context'][:example['match_start']];after=example['context'][example['match_end']:]
                keyword=before.rfind('\\textbf{Keywords');abstract=before.rfind('\\begin{abstract}')
                role='keyword_list'if keyword>=0 and keyword>abstract else 'abstract_prose'if abstract>=0 else 'model_setup_body'if 'finite state space'in after else 'source_context_unclassified'
                context_roles.append({'paper_id':example['paper_id'],'unit_id':example['unit_id'],'sha256':example['sha256'],'matched_text':example['matched_text'],'role':role,'classification_status':'source_layout_or_local_context_only_not_approved_template','literal_context':example['context']})
        lexical.append({'id':item['id'],'term':item['term'],'phrase':item['phrase'],'decision':copy.deepcopy(decisions[item['id']]),'source_contexts':context_roles,'original_note':item['note'],'note_scope':copy.deepcopy(item['note_scope']),'example_bindings':[{k:x[k]for k in ['paper_id','unit_id','sha256']}for x in item['examples']]})
    if set(decisions)!=known or len(known)!=132:raise HumanReviewError('Ordinary decisions do not exactly cover reviewed items')
    if any(d['decision']not in ['approve','needs_revision','not_applicable']or not isinstance(d['notes'],str)for d in decisions.values()):raise HumanReviewError('Unknown human choice')
    overlay={'schema':'ordinary-human-review-1','decision_origin':'human_supplied_export_and_supplement','source_bindings':bindings,'registry':registry_binding,'registry_packet_hash':registry['packet_hash'],'lexicon':lex_binding,'lexical_source_files':list(source_files.values()),'packet_fingerprint':snapshot['packet_fingerprint'],'dataset_fingerprint':snapshot['dataset_fingerprint'],'structure_entries':entries,'lexicon_entries':lexical,'policy':{'section_approval_cascades':False,'unit_approval_cascades':False,'corrected_interpretations_auto_approved':False,'scientific_truth_verified':False,'guidance_auto_emitted':False}}
    overlay['overlay_hash']=_digest(overlay);_write_new(output_path,overlay);return overlay

def activate_review(overlay_path,knowledge_dir):
    """Explicit coordinator activation; preparation alone never changes retrieval."""
    binding=_binding(overlay_path);_validate_overlay(_read(binding));pointer={'schema':'ordinary-human-review-active-1','overlay':binding}
    path=Path(knowledge_dir)/'ordinary_human_review_active.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n');return pointer

def _validate_overlay(value):
    if value.get('schema')!='ordinary-human-review-1'or _digest({k:v for k,v in value.items()if k!='overlay_hash'})!=value.get('overlay_hash'):raise HumanReviewError('Human-review overlay hash/schema mismatch')
    required={'original_export.verbatim.json','supplemental_declaration.json','added_64_manifest.json','merged_review.importable.json','current_review_data.snapshot.json','intake_manifest.json'}
    if set(value.get('source_bindings',{}))!=required or value.get('decision_origin')!='human_supplied_export_and_supplement':raise HumanReviewError('Human-review source provenance is incomplete')
    records={name:_read(binding)for name,binding in value['source_bindings'].items()}
    supplied=records['merged_review.importable.json']['decisions'];seen=set()
    for entry in value['structure_entries']:
        if entry['section_decision']!=supplied.get(entry['section_id']):raise HumanReviewError('Overlay changed supplied section decision')
        seen.add(entry['section_id'])
        for uid,decision in entry['unit_decisions'].items():
            if decision!=supplied.get(uid):raise HumanReviewError('Overlay changed supplied unit decision')
            seen.add(uid)
    for entry in value['lexicon_entries']:
        if entry['decision']!=supplied.get(entry['id']):raise HumanReviewError('Overlay changed supplied lexical decision')
        seen.add(entry['id'])
    if seen!=set(supplied):raise HumanReviewError('Overlay omitted or invented supplied decisions')
    for binding in value.get('lexical_source_files',[]):
        if _hash(binding['path'])!=binding['sha256']:raise HumanReviewError('Reviewed lexical original source changed')
    _read(value['registry'])
    if _hash(value['lexicon']['path'])!=value['lexicon']['sha256']:raise HumanReviewError('Reviewed lexicon changed')
    return value

def load_review(knowledge_dir,registry=None):
    path=Path(knowledge_dir)/'ordinary_human_review_active.json'
    if not path.exists():return None
    try:
        pointer=json.loads(path.read_text())
        if pointer['schema']!='ordinary-human-review-active-1':raise HumanReviewError('Unknown human-review pointer')
        overlay=_validate_overlay(_read(pointer['overlay']))
        local_lexicon=Path(knowledge_dir)/'lexicon.yaml'
        if not local_lexicon.is_file()or _hash(local_lexicon)!=overlay['lexicon']['sha256']:raise HumanReviewError('Retrieval lexicon is not the reviewed exact file')
        if registry is not None:
            if registry['packet_hash']!=overlay['registry_packet_hash']:raise HumanReviewError('Human review is for another structure packet')
            reviewed={e['entry_id']:e for e in overlay['structure_entries']}
            for e in registry['entries']:
                h=reviewed.get(e['entry_id'])
                if not h or h['analysis_sha256']!=e['analysis']['sha256']or h['inventory_sha256']!=e['inventory']['sha256']:raise HumanReviewError('Human review differs from exact registry analysis/source')
        return {**overlay,'active_pointer_sha256':_hash(path)}
    except (OSError,KeyError,TypeError,ValueError)as exc:raise HumanReviewError('Explicit human review failed validation; no fallback: '+str(exc))from exc

def apply_review(knowledge_dir,entries):
    """Filter reviewed exceptions; retain original narrower notes, never infer use."""
    overlay=load_review(knowledge_dir);out=[];audit={'status':'absent','excluded':[],'literal_user_guidance':[]}
    if overlay is None:return entries,audit
    audit.update(status='active',active_pointer_sha256=overlay['active_pointer_sha256'],overlay_hash=overlay['overlay_hash'])
    reviewed={(v['term'].casefold(),v['phrase'].casefold()):v for v in overlay['lexicon_entries']}
    for item in entries:
        record=reviewed.get((item.get('term','').casefold(),item.get('phrase','').casefold()))if item.get('scope')=='shared'else None
        if record is None:
            out.append({**copy.deepcopy(item),'human_review_status':'pending_human','human_review_scope':'Literal source entry only; no human semantic approval supplied.'});continue
        if item.get('note')!=record['original_note']or item.get('note_scope',{}).get('source_unit_ids')!=record['note_scope']['source_unit_ids']or item.get('note_scope',{}).get('generalizes_to_new_occurrences')is not False:raise HumanReviewError('Reviewed phrase lost its original narrow source note or scope')
        decision=record['decision'];provenance={'review_item_id':record['id'],'overlay_hash':overlay['overlay_hash'],'decision':decision['decision'],'literal_user_note':decision['notes'],'section_approval_cascades':False}
        if decision['decision']!='approve':
            audit['excluded'].append(provenance)
            if decision['notes']:audit['literal_user_guidance'].append({**provenance,'authority':'literal_user_note_only','emission_authorized':False,'not_a_corrected_approved_interpretation':True})
            continue
        out.append({**copy.deepcopy(item),'human_review_status':'approved','human_review':provenance})
    return out,audit

def assert_fresh(evidence,knowledge_dir):
    overlay=load_review(knowledge_dir);record=evidence.get('lexicon_review',{})
    if overlay is None:
        if record.get('status')=='active':raise HumanReviewError('Cached lexical review lost its active overlay')
    elif record.get('active_pointer_sha256')!=overlay['active_pointer_sha256']or record.get('overlay_hash')!=overlay['overlay_hash']:raise HumanReviewError('Cached lexical evidence predates current human review')
