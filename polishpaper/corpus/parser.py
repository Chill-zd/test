"""Physical-source TeX inventory with exact offsets and conservative boundaries."""
from __future__ import annotations
import hashlib,re
import yaml
from pathlib import Path

SECTION_TYPES=("introduction","related_work","preliminaries","model_setup","theory","algorithm","experiments","conclusion","appendix","unknown")
ATOMIC=("equation","align","theorem","lemma","proposition","corollary","proof","algorithm","figure","table","itemize","enumerate")
SECTION_RE=re.compile(r"\\(part|chapter|section|subsection|subsubsection)\*?\s*\{([^}]*)\}")
ENV_RE=re.compile(r"\\begin\{([a-zA-Z*]+)\}")
INCLUDE_RE=re.compile(r"\\(input|include)\s*\{([^}]+)\}")
CONCEPTS={"MDP":["Markov decision process","MDP"],"RMDP":["robust Markov decision process","RMDP"],"DRMDP":["distributionally robust Markov decision process","DRMDP"],"Bellman operator":["Bellman operator","Bellman update"],"ambiguity set":["ambiguity set","uncertainty set"],"policy":["policy","decision rule"],"value function":["value function","value iteration"],"transition kernel":["transition kernel","transition probability"],"reward":["reward","return"],"cost":["cost function","stage cost"],"state space":["state space","states"],"action space":["action space","actions"],"discount factor":["discount factor","discounted"],"Wasserstein distance":["Wasserstein"],"KL divergence":["Kullback","KL divergence"],"total variation":["total variation"],"optimality":["optimality","optimal policy"],"convergence":["convergence","converges"],"complexity":["complexity","polynomial time"],"dynamic programming":["dynamic programming"],"minimax":["minimax","maximin"],"duality":["duality","dual problem"],"convexity":["convexity","convex"],"stationarity":["stationary policy"],"finite horizon":["finite horizon"],"infinite horizon":["infinite horizon"],"sample complexity":["sample complexity"],"approximation":["approximation","approximate"],"regret":["regret"],"risk measure":["risk measure","CVaR"],"robust optimization":["robust optimization"]}

_RESOURCE_ROOT=Path(__file__).parents[2] if (Path(__file__).parents[2]/"concepts_seed.yaml").exists() else Path(__file__).parents[1]/"resources"
def _resources():
    seed=yaml.safe_load((_RESOURCE_ROOT/"concepts_seed.yaml").read_text())
    mapping=yaml.safe_load((_RESOURCE_ROOT/"section_map.yaml").read_text())
    return seed,mapping
_SEED,_SECTION_MAP=_resources()
CONCEPTS=_SEED["concepts"]
if not isinstance(CONCEPTS,dict) or not 30<=len(CONCEPTS)<=60 or any(not isinstance(v,list) or not v for v in CONCEPTS.values()):raise ValueError("concept seed must map 30–60 keys to surface lists")

def strip_comments(text:str)->str:
    out=[]
    for line in text.splitlines(keepends=True):
        i=0
        while i<len(line):
            if line[i]=="%":
                backslashes=0;j=i-1
                while j>=0 and line[j]=="\\":backslashes+=1;j-=1
                if backslashes%2==0:
                    line=line[:i]+" "*(len(line.rstrip("\n"))-i)+( "\n" if line.endswith("\n") else "")
                    break
            i+=1
        out.append(line)
    return "".join(out)

def section_type(title:str)->str:
    if title in _SECTION_MAP["overrides"]:return _SECTION_MAP["overrides"][title]
    low=title.lower()
    for key,words in _SECTION_MAP["keyword_rules"].items():
        if any(w in low for w in words):return key
    return "unknown"

def _unit(text,clean,start,end,file,paper_id,section_path,stype,kind):
    raw=text[start:end]
    if not raw.strip() or not clean[start:end].strip(): return None
    digest=hashlib.sha256(raw.encode()).hexdigest()
    return {"unit_id":f"{paper_id}:{Path(file).as_posix()}:{start}:{digest[:12]}","paper_id":paper_id,"section_path":[x[1] for x in section_path],"section_numbers":[x[2] for x in section_path],"section_type":stype,"text":raw,"prose_text":clean[start:end],"prose_sha256":hashlib.sha256(clean[start:end].encode()).hexdigest(),"file":str(file),"line_start":text.count("\n",0,start)+1,"line_end":text.count("\n",0,max(start,end-1))+1,"sha256":digest,"concepts":[k for k,v in CONCEPTS.items() if any(re.search(r"(?<!\w)"+re.escape(term)+r"(?!\w)",clean[start:end],re.I) for term in v)],"env_kind":None if kind=="paragraph" else kind,"math_inline_count":len(re.findall(r"(?<!\\)\$(?!\$)",clean[start:end]))//2,"math_display_count":len(re.findall(r"\\\[|\$\$|\\begin\{(?:equation|align)\*?\}",clean[start:end])),"offset_start":start,"offset_end":end}

def _parse_file(path,paper_id,root,section,seen,out,section_overrides,counters=None,appendix_state=None,events=None):
    counters={} if counters is None else counters
    appendix_state=[False] if appendix_state is None else appendix_state
    from pylatexenc.latexwalker import LatexWalker
    path=Path(path).resolve()
    if not path.is_relative_to(root):raise ValueError(f"include escapes corpus: {path}")
    if path in seen:raise ValueError(f"include cycle or duplicate: {path}")
    seen.add(path);text=path.open(encoding="utf8",newline="").read();clean=strip_comments(text)
    # Lexical preflight: malformed nodes remain in source, but macro/environment
    # boundaries are located on the comment-free projection below.
    LatexWalker(clean,tolerant_parsing=True).get_latex_nodes()
    begin=re.search(r"\\begin\{document\}",clean);end_doc=re.search(r"\\end\{document\}",clean)
    start=begin.end() if begin else 0;limit=end_doc.start() if end_doc else len(clean);pos=start
    stype=(section_overrides or {}).get("/".join(x[1] for x in section),(section_overrides or {}).get(section[-1][1],section_type(section[-1][1]))) if section else "unknown"
    token=re.compile(r"\\(?:part|chapter|section|subsection|subsubsection)\*?\s*\{[^}]*\}|\\begin\{[a-zA-Z*]+\}|\\(?:input|include)\s*\{[^}]+\}|\\appendix\b|\r?\n[ \t]*\r?\n")
    def emit(a,b,kind="paragraph"):
        u=_unit(text,clean,a,b,path.relative_to(root),paper_id,section,stype,kind)
        if u:
            out.append(u)
            if events is not None:events.append({"kind":"unit","unit":u})
    while (m:=token.search(clean,pos,limit)):
        s,e=m.span();value=m.group()
        if SECTION_RE.match(value):
            opening=clean.index("{",s,e);depth=1;cursor=opening+1
            while cursor<limit and depth:
                if clean[cursor]=="\\":cursor+=2;continue
                if clean[cursor]=="{":depth+=1
                elif clean[cursor]=="}":depth-=1
                cursor+=1
            if depth:raise ValueError("unbalanced section title")
            e=cursor;value=clean[s:e];section_title=clean[opening+1:e-1]
        if value=="\\appendix":
            emit(start,s);appendix_state[0]=True;stype="appendix";start=e;pos=e;continue
        if value.startswith("\\begin"):
            env=ENV_RE.match(value).group(1);base=env.rstrip("*")
            if base in ATOMIC or base=="abstract":
                depth=1;cursor=e;finish=None
                tags=re.compile(r"\\(begin|end)\{"+re.escape(env)+r"\}")
                for tag in tags.finditer(clean,e,limit):
                    depth+=1 if tag.group(1)=="begin" else -1
                    if depth==0:finish=tag.end();break
                if finish is not None:
                    emit(start,s);emit(s,finish,base);start=finish;pos=finish;continue
            pos=e;continue
        if value.startswith("\\"):
            emit(start,s)
            sm=SECTION_RE.match(value)
            if sm:
                level={"part":1,"chapter":2,"section":3,"subsection":4,"subsubsection":5}[sm.group(1)]
                section=[x for x in section if x[0]<level]
                counters[level]=counters.get(level,0)+1
                for deeper in list(counters):
                    if deeper>level:del counters[deeper]
                number=".".join(str(counters[k]) for k in sorted(counters))
                section.append((level,section_title,number))
                stype="appendix" if appendix_state[0] else (section_overrides or _SECTION_MAP["overrides"]).get("/".join(x[1] for x in section), (section_overrides or {}).get(section_title,section_type(section_title)))
                if events is not None:
                    heading=text[s:e]
                    events.append({"kind":"section","title":section_title,"level":level,"section_path":[x[1] for x in section],"section_type":stype,"file":str(path.relative_to(root)),"offset_start":s,"offset_end":e,"sha256":hashlib.sha256(heading.encode()).hexdigest(),"line_start":text.count("\n",0,s)+1})
            else:
                inc=INCLUDE_RE.match(value)
                if inc:
                    target=path.parent/inc.group(2)
                    if not target.suffix:target=target.with_suffix(".tex")
                    if not target.resolve().is_relative_to(root):raise ValueError("include escapes corpus")
                    if not target.exists():raise FileNotFoundError(target)
                    section=_parse_file(target,paper_id,root,section,seen,out,section_overrides,counters,appendix_state,events)
                    stype=(section_overrides or {}).get("/".join(x[1] for x in section),(section_overrides or {}).get(section[-1][1],section_type(section[-1][1]))) if section else "unknown"
            start=e
        else:emit(start,s);start=e
        pos=e
    emit(start,limit)
    seen.remove(path)
    return section

def parse_file(path:str|Path,paper_id:str,section_overrides:dict|None=None)->list[dict]:
    path=Path(path).resolve();out=[]
    _parse_file(path,paper_id,path.parent,[],set(),out,section_overrides or _SECTION_MAP["overrides"])
    return out

def parse_tree(main:str|Path,paper_id:str,root:str|Path|None=None,section_overrides:dict|None=None)->list[dict]:
    main=Path(main).resolve();root=Path(root or main.parent).resolve();out=[]
    _parse_file(main,paper_id,root,[],set(),out,section_overrides or _SECTION_MAP["overrides"])
    return out


def parse_events(main:str|Path,paper_id:str,root:str|Path|None=None,section_overrides:dict|None=None)->list[dict]:
    """Optional ordered structural projection; legacy parse_tree output is unchanged."""
    main=Path(main).resolve();root=Path(root or main.parent).resolve();out=[];events=[]
    _parse_file(main,paper_id,root,[],set(),out,section_overrides or _SECTION_MAP["overrides"],events=events)
    return events
