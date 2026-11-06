"""Current-manuscript notation context from the same physical-source parser.

Full parsed body stays local; the writer receives exact math/definition contexts
and source bindings, not the complete manuscript prose or inferred symbol types.
"""
from pathlib import Path
import hashlib,json,re
from ..corpus.parser import parse_tree,strip_comments


def _binding(path):
    path=Path(path).resolve();return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def build(workspace,main,paper_id,artifact_path):
    workspace=Path(workspace).resolve();main=(workspace/main).resolve()
    units=parse_tree(main,paper_id,workspace)
    # Conservative freshness closure also covers heading-only/empty includes and
    # preamble TeX that yields no body units. Binding does not imply it was parsed.
    files=sorted({main,*[p.resolve() for p in workspace.rglob('*.tex')]})
    if any(not p.is_relative_to(workspace) for p in files):raise ValueError('Notation source escapes task workspace')
    math=[];definitions=[];contexts=[]
    pattern=re.compile(r'(?<!\\)(\${1,2})(.+?)(?<!\\)\1|\\\(.+?\\\)|\\\[.+?\\\]',re.S)
    for unit in units:
        text=unit['prose_text'];base={k:unit[k] for k in ('unit_id','file','section_type','section_path','env_kind','offset_start','offset_end','prose_sha256')}
        contexts.append({**base,'prose_text':text})
        spans=[(m.start(),m.end()) for m in pattern.finditer(text)]
        if unit['env_kind'] in ('equation','equation*','align','align*'):spans=[(0,len(text))]
        for start,end in spans:math.append({**base,'start':start,'end':end,'text':text[start:end]})
        if (spans and re.search(r'\b(?:denote\w*|define\w*|let|where|represent\w*|notation|symbol\w*)\b',text,re.I)) or re.search(r'\\(?:newcommand|renewcommand|def)\b',text):
            definitions.append({**base,'text':text,'status':'literal_definition_context_not_semantically_verified'})
    raw=main.read_text();match=re.search(r'\\begin\{document\}',strip_comments(raw))
    preamble=strip_comments(raw[:match.start()]) if match else ''
    declarations=[]
    for m in re.finditer(r'\\(?:newcommand|renewcommand|DeclareMathOperator)\*?\s*\{?\s*(\\[A-Za-z]+)|\\def\s*(\\[A-Za-z]+)',preamble):
        declarations.append({'file':str(main.relative_to(workspace)),'line':raw.count('\n',0,m.start())+1,
            'macro':m.group(1) or m.group(2),'status':'literal_preamble_declaration_locator_only; macro not expanded'})
    baseline={'schema':'current-manuscript-notation-baseline-1','scope':'whole_parsed_manuscript',
        'main':str(main),'workspace':str(workspace),'parsed_unit_count':len(units),
        'parsed_body_source_files':sorted({u['file'] for u in units}),
        'hash_bound_workspace_tex_files':[str(p.relative_to(workspace)) for p in files],
        'source_bindings':[_binding(p) for p in files],'units':contexts,'math_fragments':math,'definition_contexts':definitions,
        'preamble_context':preamble,'preamble_declaration_locators':declarations,
        'limitations':['Scope is the main document and actual input/include files reached by the physical-source parser.',
            'All workspace TeX files are hash-bound conservatively; only main/input/include body units are parsed. Preamble declarations are recorded separately with limited coverage, not interpreted or expanded.',
            'Image-only notation, macro expansions and unparsed external dependencies may remain unknown.',
            'Literal math and definition contexts do not certify semantic identity, definition adequacy, or scientific truth.']}
    path=Path(artifact_path)
    if path.exists():
        if json.loads(path.read_text())!=baseline:raise ValueError('Existing immutable manuscript notation baseline differs')
    else:
        with path.open('x') as handle:json.dump(baseline,handle,ensure_ascii=False,indent=2);handle.write('\n')
    return {**baseline,'artifact':_binding(path)}


def summary(baseline):
    """Send symbol spellings/definition paragraphs, never all proof formulas."""
    result={k:v for k,v in baseline.items() if k not in ('units','workspace','main','preamble_context','math_fragments','definition_contexts')}
    symbols={}
    pattern=re.compile(r'\\(?:bm|mathbf|mathcal|mathbb|mathfrak)\s*\{[^{}]+\}(?:_\{[^{}]+\}|_[A-Za-z0-9])?|\\(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|nu|pi|rho|sigma|tau|phi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega)\b|(?<![\\A-Za-z])[A-Za-z](?:_\{[^{}]+\}|_[A-Za-z0-9])?(?![A-Za-z])')
    for fragment in baseline['math_fragments']:
        for match in pattern.finditer(fragment['text']):
            symbols.setdefault(match.group(),{'spelling':match.group(),'unit_id':fragment['unit_id'],'file':fragment['file'],'offset_start':fragment['offset_start']+fragment['start']+match.start()})
    result['observed_symbol_spellings']=list(symbols.values())
    result['math_fragment_count']=len(baseline['math_fragments'])
    result['definition_contexts']=[c for c in baseline['definition_contexts'] if c['env_kind'] in (None,'paragraph','definition')]
    result['definition_context_policy']='Literal prose definition candidates only; formulas/proof bodies stay in the local artifact. Selection is conservative and does not certify exhaustive definitions or semantic identity.'
    return result


def assert_fresh(summary):
    for item in summary.get('source_bindings',[])+([summary['artifact']] if summary.get('artifact') else []):
        path=Path(item['path'])
        if not path.is_file() or _binding(path)['sha256']!=item['sha256']:raise ValueError('Manuscript notation baseline/source changed: '+str(path))
