"""Staging-only explicit model-citable evidence catalogue; internal IDs stay distinct."""
import hashlib,json

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def schema_item(evidence):
    schema=evidence.get('schema')
    if not schema or schema.get('schema')!='approved-source-specific-schema-1':return None
    approval=schema.get('schema_approval',{});snapshot=evidence.get('semantic_supplement') or {}
    expected='schema:'+schema.get('section_type','')
    if approval.get('id')!=expected or not schema.get('section_type') or not schema.get('source',{}).get('paper_id'):
        raise ValueError('Selected schema lacks exact source-specific identity')
    if schema.get('review_status')!='approved' or schema.get('human_approval') is not True or approval.get('supplement_sha256')!=snapshot.get('supplement_sha256'):
        raise ValueError('Selected schema approval is not bound to the evidence supplement')
    return {'evidence_id':expected,'source_tag':'source_specific_schema','text':'Selected source-specific organization schema; original support resolves once at evidence.schema.',
            'conditions':schema.get('conditions',[]),'provenance':{'schema_sha256':digest(schema),'source':schema['source'],'schema_approval':approval},'evidence_pointer':'/schema'}

def catalogue(evidence):
    items=list(evidence.get('items',[]));item=schema_item(evidence)
    if item:
        existing=[i for i in items if i['evidence_id']==item['evidence_id']]
        if existing and existing!=[item]:raise ValueError('Conflicting schema evidence catalogue ID')
        if not existing:items.append(item)
    ids=[i['evidence_id'] for i in items]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate evidence catalogue ID')
    return items

def allowed_ids(evidence):return {i['evidence_id'] for i in catalogue(evidence)}
