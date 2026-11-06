from __future__ import annotations
from pathlib import Path
import difflib,re,json

class NeedsUser(RuntimeError):pass

def _number(s):
    if s.isdigit():return int(s)
    digits=dict(zip('一二三四五六七八九',range(1,10)))
    if s=='十':return 10
    if '十' in s:
        a,b=s.split('十');return digits.get(a,1)*10+digits.get(b,0)
    return digits.get(s)

def locate(units,request,client=None,task_id='',kind='revise',annotations=None):
    anchors=re.findall(r'[“"「]([^”"」]{4,})[”"」]',request)
    anchors += [a['anchor'] for a in annotations or [] if isinstance(a.get('anchor'),str)]
    candidates=[];basis=''
    if len(anchors)>1:
        selected=[]
        for anchor in anchors:
            try:matched=locate(units,'“'+anchor+'”',None,task_id,kind)
            except NeedsUser:break
            if matched[0]['unit_id'] not in {u['unit_id'] for u in selected}:selected.extend(matched)
        else:
            order={u['unit_id']:i for i,u in enumerate(units)}
            return sorted(selected,key=lambda u:order[u['unit_id']])
    if anchors:
        q=' '.join(anchors[0].split());basis='quotation: exact or sliding fuzzy match >=0.90'
        for u in units:
            text=' '.join(u['text'].split())
            ratio=1.0 if q in text else max((difflib.SequenceMatcher(None,q,text[i:i+len(q)],autojunk=False).ratio() for i in range(max(1,len(text)-len(q)+1))),default=0)
            if ratio>=.90:candidates.append(u)
    else:
        m=re.search(r'(?:section|sec\.?|第)\s*([\d.]+|[一二三四五六七八九十]+)\s*(?:节|節)?.*?(?:(?:paragraph|para\.?)\s*|第)([\d]+|[一二三四五六七八九十]+)\s*(?:段)?',request,re.I)
        if m:
            section=m.group(1);section=str(_number(section)) if not section[0].isdigit() else section
            ordinal=_number(m.group(2));basis='section number and prose paragraph ordinal'
            subset=[u for u in units if section in u.get('section_numbers',[]) and u['env_kind'] in (None,'paragraph')]
            if ordinal and 0<ordinal<=len(subset):candidates=[subset[ordinal-1]]
    if len(candidates)==1:return [{**candidates[0],'locate_basis':basis}]
    candidates=candidates or units
    if client is None:raise NeedsUser('Target needs an exact quotation or section and paragraph')
    result=client.json(provider='gpt',messages=[{'role':'system','content':(Path(__file__).parents[1]/'prompts'/'locate_disambiguate.md').read_text()},{'role':'user','content':json.dumps({'request':request,'candidates':[{'index':i,'text':u['text'],'section_path':u['section_path']} for i,u in enumerate(candidates)]},ensure_ascii=False)}],task_id=task_id,purpose='locate')
    i=result.get('index');basis=result.get('locate_basis',result.get('basis'))
    if isinstance(i,bool) or not isinstance(i,int) or not 0<=i<len(candidates) or not isinstance(basis,str) or not basis.strip():raise NeedsUser('Model could not disambiguate target')
    return [{**candidates[i],'locate_basis':basis}]

def card(targets,units,request,kind='revise',annotations=None):
    ids={u['unit_id'] for u in targets};positions=[i for i,u in enumerate(units) if u['unit_id'] in ids];neighbors=[]
    for i in positions:
        for j in (i-1,i+1):
            if 0<=j<len(units) and units[j]['unit_id'] not in ids and units[j] not in neighbors:neighbors.append(units[j])
    annotations=annotations or []
    from ..corpus.parser import CONCEPTS
    extra=[k for k,terms in CONCEPTS.items() if any(term.lower() in json.dumps(annotations,ensure_ascii=False).lower() for term in terms)]
    return {'target_units':targets,'neighbors':neighbors,'neighbor_units':neighbors,'locate_basis':[u.get('locate_basis','explicit target') for u in targets],'user_request':request,'annotations':annotations,'section_type':targets[0]['section_type'],'concepts':sorted(set(extra+[c for u in targets for c in u['concepts']])),'task_kind':kind}
