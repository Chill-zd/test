"""Bind every claimed example, including schema moves, to verbatim units."""
from __future__ import annotations
import re

def norm(s):return re.sub(r'\s+',' ',s).strip()
def bind_example(example,units):
    if isinstance(example,dict):
        text=example.get('text','');claimed=example.get('source')
        if isinstance(claimed,dict):claimed=claimed.get('unit_id')
    else:text=example;claimed=None
    if not isinstance(text,str) or not norm(text):return None
    for u in units:
        if claimed and claimed!=u['unit_id']:continue
        if norm(text) in norm(u.get('prose_text',__import__('polishpaper.corpus.parser',fromlist=['strip_comments']).strip_comments(u['text']))):return {'text':text,'source':{k:u[k] for k in ('paper_id','unit_id','file','line_start','line_end','sha256')}}
    return None

def verify_batch(items,units,kind):
    good=[];bad=[]
    if not isinstance(items,list):return [],[{'item':items,'reason':'items must be an array'}]
    for item in items:
        try:
            if not isinstance(item,dict):raise ValueError('item must be object')
            if kind=='lexicon':
                from ..corpus.parser import CONCEPTS
                if item.get('term') not in CONCEPTS:raise ValueError('lexicon term is not an allowed concept seed key; preserve as pending suggestion, not admitted lexicon')
                if not all(isinstance(item.get(k),str) and item[k].strip() for k in ('term','phrase')):raise ValueError('term and phrase required')
            if kind=='patterns':
                from .merge import PATTERN_FUNCTIONS
                if item.get('function') not in PATTERN_FUNCTIONS or not isinstance(item.get('template'),str) or not item['template']:raise ValueError('invalid pattern function/template')
            updated=dict(item)
            def bind_all(examples):
                if not isinstance(examples,list) or not examples:raise ValueError('nonempty examples required')
                bound=[bind_example(e,units) for e in examples]
                if not all(bound):raise ValueError('unbound example or false claimed source')
                return bound
            if kind=='schemas':
                from ..corpus.parser import SECTION_TYPES
                if item.get('section_type') not in SECTION_TYPES or not isinstance(item.get('moves'),list) or not item['moves']:raise ValueError('invalid schema section/moves')
                moves=[]
                for move in item['moves']:
                    if not isinstance(move,dict) or not all(isinstance(move.get(k),str) and move[k] for k in ('id','move')):raise ValueError('schema move requires id/move')
                    moves.append({**move,'evidence':bind_all(move.get('evidence',move.get('examples',[])))})
                if len({m['id'] for m in moves})!=len(moves):raise ValueError('schema move IDs must be unique within one source schema')
                updated['moves']=moves;updated['review_status']='pending_human'
                updated['examples']=[e for m in moves for e in m['evidence']]
            else:
                updated['examples']=bind_all(item.get('examples',[]))
                if kind=='lexicon' and not any(norm(item['phrase']) in norm(e['text']) for e in updated['examples']):raise ValueError('lexicon phrase is not verbatim in its claimed evidence')
            good.append(updated)
        except (ValueError,TypeError,KeyError) as exc:bad.append({'item':item,'reason':str(exc)})
    return good,bad
