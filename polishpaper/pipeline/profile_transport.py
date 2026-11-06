"""Offline staging-only semantic-preserving packet experiment; no production hook."""
import json,hashlib
from pathlib import Path
from ..structure.message_compaction import encode,decode

MECHANICAL={'sha256','prose_sha256','raw_span_sha256','projection_span_sha256','source_sha256','file_sha256','analysis_sha256','inventory_hash','packet_hash','catalog_sha256','active_pointer_sha256','registry_sha256','overlay_hash','offset_start','offset_end','projection_start','projection_end','line_start','line_end','start','end','logical_order','delivered_packet_chars','max_packet_chars','input_text_sha256','math_inline_count','math_display_count','source_files','parsed_unit_count','math_fragment_count','hash_bound_workspace_tex_files','parsed_body_source_files','preamble_declaration_locators'}
# These are eligibility/debug ledgers, not the selected observations/conditions.
DIAGNOSTIC={'evaluation_exclusions','lexicon_review','feedback_review','concept_derivation','locate_basis','source_family_correction','pattern_origin_audit','lexicon_origin_withheld'}

def project(packet):
 removed=[]
 def walk(value,path=()):
  if isinstance(value,list):return [walk(v,path+(i,)) for i,v in enumerate(value)]
  if not isinstance(value,dict):return value
  result={}
  for k,v in value.items():
   if k in MECHANICAL or k in DIAGNOSTIC:
    removed.append({'pointer':list(path+(k,)),'value':v,'reason':'mechanical provenance or eligibility diagnostic; complete selected semantic conditions retained'})
   elif k=='text' and value.get('prose_text')==v:
    removed.append({'pointer':list(path+(k,)),'value':v,'reason':'exact same prose supplied under prose_text'})
   else:result[k]=walk(v,path+(k,))
  return result
 result=walk(packet)
 # All source prose, schema/unit observations, dependencies, scientific questions,
 # limitations and contextual conditions are left intact by this projection.
 return result,removed

def restore(projected,removed):
 result=json.loads(json.dumps(projected))
 for entry in sorted(removed,key=lambda x:len(x['pointer'])):
  at=result
  for key in entry['pointer'][:-1]:at=at[key]
  at[entry['pointer'][-1]]=entry['value']
 return result

def _audit_folder(packet,raw_path,removed=None):
    """Reuse exact legacy bindings; changed/new packets get immutable hash paths."""
    raw_path=Path(raw_path);base=raw_path.parent/(raw_path.stem+'_profile_audit')
    serialized=json.dumps(packet,ensure_ascii=False,separators=(',',':'))
    if removed is None:_,removed=project(packet)
    mechanical=json.dumps(removed,ensure_ascii=False,separators=(',',':'))
    original=base/'original.complete.json';archive=base/'mechanical_fields.json'
    if original.is_file() and archive.is_file() and original.read_text()==serialized and archive.read_text()==mechanical:
        return base
    return base/hashlib.sha256(serialized.encode()).hexdigest()


def compact_for_model(packet,raw_path):
    raw_path=Path(raw_path);projected,removed=project(packet)
    folder=_audit_folder(packet,raw_path,removed);folder.mkdir(parents=True,exist_ok=True)
    if restore(projected,removed)!=packet:raise ValueError('Profile mechanical archive roundtrip failed')
    original=folder/'original.complete.json';archive=folder/'mechanical_fields.json'
    for path,value in [(original,packet),(archive,removed)]:
        serialized=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        if path.exists() and path.read_text()!=serialized:raise ValueError('Immutable profile packet changed')
        if not path.exists():path.write_text(serialized)
    projected['profile_local_audit']={'original':{'path':str(original.resolve()),'sha256':hashlib.sha256(original.read_bytes()).hexdigest()},'mechanical_fields':{'path':str(archive.resolve()),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},'policy':'Exact semantic packet retained; only mechanical/deep diagnostic fields archived. These local archives are not claimed model-read. This is language-only handbook profile, not legacy complete full.'}
    encoded=encode(projected,min_chars=64,share_lines=True)
    if decode(encoded)!=projected:raise ValueError('Profile exact sharing failed')
    return encoded


def preview(packet,raw_path):
    raw_path=Path(raw_path);projected,removed=project(packet)
    folder=_audit_folder(packet,raw_path,removed)
    serialize=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':'))
    projected['profile_local_audit']={'original':{'path':str((folder/'original.complete.json').resolve()),'sha256':hashlib.sha256(serialize(packet).encode()).hexdigest()},'mechanical_fields':{'path':str((folder/'mechanical_fields.json').resolve()),'sha256':hashlib.sha256(serialize(removed).encode()).hexdigest()},'policy':'Exact semantic packet retained; only mechanical/deep diagnostic fields archived. These local archives are not claimed model-read. This is language-only handbook profile, not legacy complete full.'}
    return encode(projected,min_chars=64,share_lines=True)


def fit_optional_routes(packet,instruction,raw_path,max_bytes):
    """Pack MAX-count retrieval lanes; required evidence is never optional."""
    if max_bytes is None:raise ValueError('Handbook profile requires an explicit byte budget before reservation')
    from .evidence_catalog import allowed_ids
    from .evaluation import family
    e=packet['evidence'];card=packet['taskcard'];required=set(card.get('required_evidence_ids',[]))
    explicit=set(card.get('writing_route_ids',[]));papers={family(p) for p in card.get('reference_paper_ids',[])}
    request=card.get('user_request','')
    notation=e.get('notation',{})
    missing=required-allowed_ids(e)
    if missing:raise ValueError('Explicitly required evidence was not selected/eligible: '+', '.join(sorted(missing)))
    required_notation=set(card.get('required_notation_entry_ids',[]))|set(card.get('notation_overrides',{}))
    available_notation={v['id'] for v in notation.get('matched_entries',[])}
    if required_notation-available_notation:raise ValueError('Explicitly required notation evidence was not selected/eligible')
    if e.get('writing_profile',{}).get('language_only_science_frozen') and not card.get('external_notation_required') and notation.get('matched_entries'):
        omitted=[v['id'] for v in notation['matched_entries'] if v['id'] not in required_notation]
        notation['matched_entries']=[v for v in notation['matched_entries'] if v['id'] in required_notation]
        required_sources={r['source_id'] for v in notation['matched_entries'] for r in v.get('source_refs',[])}
        notation['source_bindings']=[v for v in notation.get('source_bindings',[]) if v['id'] in required_sources]
        if not notation['matched_entries']:
            notation['status']='external_preferences_omitted_existing_notation_frozen';notation['catalog_enabled']=False
        notation['external_preference_scope']={'notation_entry_ids_not_delivered':omitted,'reason':'No external notation preference requested; existing mathematical notation is frozen. Original catalog and full plan remain in immutable full_source_audit, not claimed read.'}
        packet['notation']=notation
        e['writing_profile']['external_notation_preferences_delivered']=bool(notation['matched_entries'])
    def protected(item):
        if item['evidence_id'] in required or item['evidence_id'] in request:return True
        if item.get('source_tag') in ('user_request','real_annotation','user_guidance'):return True
        if item.get('provenance',{}).get('kind') in ('feedback','user_guidance','science_question'):return True
        if item.get('writing_route',{}).get('id') in explicit:return True
        def source_papers(value):
            result=set()
            if isinstance(value,dict):
                for key,v in value.items():
                    if key in ('paper_id','paper_ids','source_papers'):
                        result.update(family(x) for x in (v if isinstance(v,list) else [v]) if isinstance(x,str))
                    else:result.update(source_papers(v))
            elif isinstance(value,list):
                for v in value:result.update(source_papers(v))
            elif isinstance(value,str):
                import re
                result.update(family(x) for x in re.findall(r'(?:arxiv[_:/])?\d{4}\.\d{4,5}(?:v\d+)?',value))
                if family(value.split(':')[0]) in papers:result.add(family(value.split(':')[0]))
            return result
        return bool(papers & source_papers(item))
    def measured():
        encoded=preview(packet,raw_path)
        messages=[{'role':'system','content':instruction},{'role':'user','content':json.dumps(encoded,ensure_ascii=False,separators=(',',':'))}]
        return len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
    dropped=[]
    while measured()>max_bytes:
        optional=[i for i in e['items'] if not protected(i) and (i['evidence_id'].startswith(('lexicon:','pattern:','new-context:')) or (i['evidence_id'].startswith('retrieved:') and i.get('provenance',{}).get('kind')=='unit'))]
        routes=[i for i in e['items'] if not protected(i) and i['evidence_id'].startswith('writing_route:')]
        candidates=optional or routes
        if not candidates:
            raise ValueError('Required handbook language packet exceeds configured byte budget before reservation; no required facts or source strings were clipped')
        item=candidates[-1];e['items'].remove(item);dropped.append(item['evidence_id'])
        e['writing_profile'].setdefault('optional_cards_not_delivered',[]).append({'evidence_id':item['evidence_id'],'reason':'whole lowest-ranked automatic retrieval option exceeds explicit byte policy; retrieval counts are maxima, not obligations; no semantic rejection'})
        packet['allowed_evidence_ids']=sorted(allowed_ids(e))
        if not any(i['evidence_id'].startswith('writing_route:') for i in e['items']):e['writing_profile']['handbook_exemplars_delivered']=False
        if not e.get('schema') and all(i['evidence_id']=='user_request' for i in e['items']):
            e['mode']='no_domain_evidence';packet['no_evidence_clause']='Only edits directly supported by the user request or annotations'
    return dropped,measured()
