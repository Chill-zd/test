"""Opt-in, source-bound holdout exclusions for writing evaluations.

Source families are explicit experimental inputs, never a production blacklist.
Mixed-source objects are withheld whole so their frequency/review scope is intact.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def binding(path):
    path=Path(path).resolve();return {'path':str(path),'sha256':sha(path)}

def family(value):
    found=re.search(r'(?:arxiv[_:/]|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?',str(value),re.I)
    return 'arxiv_'+found[1] if found else str(value).strip().casefold()


class Exclusions:
    def __init__(self,bound):
        self.bound=dict(bound['manifest'] if 'manifest' in bound else bound)
        path=Path(self.bound['path'])
        if sha(path)!=self.bound['sha256']:raise ValueError('Evaluation exclusion manifest changed')
        data=json.loads(path.read_text())
        if data.get('schema')!='evaluation-exclusions-1':raise ValueError('Unknown evaluation exclusion manifest')
        if not isinstance(data.get('paper_ids'),list) or not data['paper_ids'] or not all(isinstance(x,str) and x.strip() for x in data['paper_ids']):raise ValueError('Evaluation exclusions require explicit paper IDs')
        aliases=data.get('aliases',{})
        if not isinstance(aliases,dict) or not all(isinstance(k,str) and isinstance(v,str) and k and v for k,v in aliases.items()):raise ValueError('Malformed evaluation family aliases')
        self.aliases={family(k):family(v) for k,v in aliases.items()}
        # Resolve aliases transitively, reject cycles rather than guess a family.
        def canonical(key):
            seen=set()
            while key in self.aliases and self.aliases[key]!=key:
                if key in seen:raise ValueError('Cyclic evaluation family aliases')
                seen.add(key);key=self.aliases[key]
            return key
        self.canonical=canonical
        self.excluded={canonical(family(x)) for x in data['paper_ids']}
        self.paths=set();self.hashes=set();self.source_bindings=[];self.independent_sources=[]
        for source in data.get('source_bindings',[]):
            if not isinstance(source,dict) or set(('path','sha256'))-source.keys():raise ValueError('Malformed evaluation source binding')
            if not Path(source['path']).is_absolute() or not re.fullmatch(r'[a-f0-9]{64}',source['sha256']):raise ValueError('Evaluation source requires absolute path and SHA256')
            # Only declared source bindings are read, never paths discovered in metadata.
            if sha(source['path'])!=source['sha256']:raise ValueError('Evaluation original source changed')
            if source.get('paper_id') and canonical(family(source['paper_id'])) not in self.excluded:raise ValueError('Excluded source binding belongs to an undeclared family')
            self.paths.add(str(Path(source['path']).resolve()));self.hashes.add(source['sha256']);self.source_bindings.append(dict(source))
            if not isinstance(source.get('aliases',[]),list) or not all(isinstance(a,str) and a for a in source.get('aliases',[])):raise ValueError('Malformed source aliases')
            for alias in source.get('aliases',[]):self.aliases[family(alias)]=canonical(family(source.get('paper_id',data['paper_ids'][0])))
        for source in data.get('independent_source_bindings',[]):
            if not isinstance(source,dict) or not all(source.get(k) for k in ('path','sha256','paper_id')):raise ValueError('Independent source requires explicit family and original binding')
            if canonical(family(source['paper_id'])) in self.excluded:raise ValueError('Independent source allowlist contains an excluded family')
            if not Path(source['path']).is_absolute() or sha(source['path'])!=source['sha256']:raise ValueError('Independent original source changed')
            self.independent_sources.append(dict(source))
        self.lanes={lane:{'kept':[],'dropped':[]} for lane in ('schema','lexicon','patterns','structure','unit','feedback','user_guidance','science_question','notation')}

    def identity(self,value):
        ids=set();paths=set();hashes=set()
        identity_keys={'paper_id','paper_ids','source_papers','source_unit_ids','unit_id','unit_instance_id','source_id','sources','id','file','path','source_path','origin_file','origin_archive','source_url','public_url','source_sha256','sha256','prose_sha256','image_sha256','origin_archive_sha256'}
        def visit(obj,key=None):
            if isinstance(obj,dict):
                for k,v in obj.items():visit(v,k)
            elif isinstance(obj,list):
                for v in obj:visit(v,key)
            elif isinstance(obj,str) and key in identity_keys:
                found=re.findall(r'(?:arxiv[_:/]|arxiv\.org/(?:abs|pdf)/)?\d{4}\.\d{4,5}(?:v\d+)?',obj,re.I)
                ids.update(self.canonical(family(x)) for x in found)
                if key in ('paper_id','paper_ids','source_papers'):ids.add(self.canonical(family(obj)))
                normalized=family(obj.split(':')[0])
                if normalized in self.aliases:ids.add(self.canonical(normalized))
                if key in ('path','file','source_path','origin_file','origin_archive') and Path(obj).is_absolute():paths.add(str(Path(obj).resolve()))
                if key.endswith('sha256') and re.fullmatch(r'[a-f0-9]{64}',obj):hashes.add(obj)
        visit(value)
        independent=any(source['sha256'] in hashes and str(Path(source['path']).resolve()) in paths for source in self.independent_sources)
        return ids,paths,hashes,independent

    def reason(self,value):
        ids,paths,hashes,bound=self.identity(value)
        if ids & self.excluded:return 'excluded_paper_family'
        if paths & self.paths:return 'excluded_source_path'
        if hashes & self.hashes:return 'excluded_source_sha256'
        # Every constituent of an explicitly multi-source reference must have an
        # independent origin; one known source cannot vouch for an unknown one.
        components=[]
        if isinstance(value,list):components=value
        elif isinstance(value,dict):
            if isinstance(value.get('sources'),list):components.extend({'source_id':v} if isinstance(v,str) else v for v in value['sources'])
            if isinstance(value.get('examples'),list):components.extend(v.get('source',{}) for v in value['examples'])
            if isinstance(value.get('moves'),list):components.extend(value['moves'])
        if any(self.reason(v) is not None for v in components):return 'source_identity_unknown'
        if not ids and not bound:return 'source_identity_unknown'
        return None

    def allow(self,lane,value,item_id=None):
        fallback='object:'+hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        identity=value.get('id',value.get('unit_id')) if isinstance(value,dict) else None
        reason=self.reason(value);row={'id':str(item_id or identity or fallback),'reason':reason or 'independent_bound_source'}
        rows=self.lanes.setdefault(lane,{'kept':[],'dropped':[]})['dropped' if reason else 'kept']
        if row not in rows:rows.append(row)
        return reason is None

    def select(self,lane,items):
        return [v for v in items if self.allow(lane,v)]

    def audit(self):
        return {'schema':'evaluation-exclusion-audit-1','manifest':self.bound,'excluded_families':sorted(self.excluded),'aliases':dict(sorted(self.aliases.items())),'source_bindings':self.source_bindings,'independent_source_bindings':self.independent_sources,'lanes':self.lanes,'selection_stage':'Eligible/withheld candidates before lane limits; delivered item IDs are recorded separately in the evidence and structure packet.','policy':'Whole mixed-source items withheld; unknown source identity withheld; manuscript context/request/explicit user rules preserved.'}


def resolve(card=None,explicit=None):
    declared=(card or {}).get('evaluation_exclusions')
    if explicit is not None and declared is not None and explicit!=declared:raise ValueError('Evaluation exclusions differ from frozen taskcard')
    return Exclusions(explicit if explicit is not None else declared) if explicit is not None or declared is not None else None


def assert_fresh(evidence):
    recorded=evidence.get('evaluation_exclusions')
    if recorded:
        current=Exclusions(recorded['manifest'])
        if sorted(current.excluded)!=recorded['excluded_families'] or current.aliases!=recorded['aliases'] or current.source_bindings!=recorded['source_bindings'] or current.independent_sources!=recorded['independent_source_bindings']:raise ValueError('Evaluation exclusion closure changed')


def assert_packet(card,evidence,packet):
    """Check substantive reference payloads; audit IDs and task context are exempt."""
    recorded=evidence.get('evaluation_exclusions')
    if not recorded:
        if card.get('evaluation_exclusions'):raise ValueError('Evaluation task lacks an exclusion audit')
        return
    exclusion=resolve(card)
    if exclusion is None or exclusion.bound!=recorded['manifest']:raise ValueError('Evaluation packet is not bound to its task manifest')
    assert_fresh(evidence)
    for item in packet.get('evidence',evidence).get('items',[])+packet.get('referenced_evidence',[]):
        if item.get('source_tag') in ('user_request','real_annotation') and item.get('evidence_id')=='user_request':continue
        if item.get('evidence_id','').startswith('annotation:') or item.get('evidence_id') in {a.get('annotation_id') for a in card.get('annotations',[])}:continue
        if item.get('evidence_id','').startswith('structure:'):continue # Full dependency dictionary checked below.
        if exclusion.reason(item):raise ValueError('Excluded or unidentified source in actual evaluation packet: '+item['evidence_id'])
    sources=evidence.get('structure',{}).get('sources',{})
    for key,value in sources.items():
        if exclusion.reason(value):raise ValueError('Excluded structure source in actual evaluation packet: '+key)
    for value in evidence.get('inherited_scientific_questions',[]):
        if exclusion.reason(value):raise ValueError('Excluded scientific reference in evaluation packet')
    schema=evidence.get('schema')
    if schema and exclusion.reason(schema):raise ValueError('Excluded schema in evaluation packet')
    notation=evidence.get('notation',{})
    by_id={s['id']:s for s in notation.get('source_bindings',[])}
    for entry in notation.get('matched_entries',[]):
        refs=[{'id':r['source_id'],**by_id.get(r['source_id'],{})} for r in entry.get('source_refs',[])]
        if not refs or exclusion.reason(refs):raise ValueError('Excluded notation reference in evaluation packet')
