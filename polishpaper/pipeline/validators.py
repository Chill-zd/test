"""Eight explicit checks over the full target and a candidate."""
from __future__ import annotations
import difflib,re

STANDARD={"citep","ref","eqref","label","begin","end","textbf","emph","textit","bm","mathcal","mathbb","frac","sum","min","max","left","right","mathrm","operatorname","alpha","beta","gamma","delta","epsilon","varepsilon","pi","theta","lambda","mu","nu","rho","sigma","tau","phi","psi","omega","in","le","ge","to","rightarrow","cdot","times","mid","bigl","bigr","big","Big","nonumber","notag","quad","qquad","text","item","footnote","url","underline","partial","nabla","infty","forall","exists","sup","inf","argmax","argmin","subseteq","subset","cup","cap","setminus","top","bot","geq","leq","neq","approx","sim","Pr","mathbbm","tilde","hat","bar","overline","underbrace","overset","leftarrow","Rightarrow","Leftrightarrow","sqrt","ldots","dots","geqslant","leqslant","substack","limits","displaymath"}

def sentences(s):return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n\s*\n",s) if x.strip()]
def commands(s):return re.findall(r"\\([A-Za-z]+)",s)
def _math(s):
    pattern=r"(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|\\begin\{(?:equation|align)\*?\}[\s\S]*?\\end\{(?:equation|align)\*?\}"
    return [re.sub(r"\s+","",m.group()) for m in re.finditer(pattern,s)]
DRAFT_SCHEMA={"type":"object","required":["revised_tex","changes","science_questions","evidence_usage","annotations_addressed"],"properties":{
"revised_tex":{"type":"string"},
"changes":{"type":"array","items":{"type":"object","required":["change_id","original_sentence","revised_sentence","reason","sources"],"properties":{**{k:{"type":"string"} for k in ("change_id","original_sentence","revised_sentence","reason")},"sources":{"type":"array","minItems":1,"uniqueItems":True,"items":{"type":"string","minLength":1}}}}},
"science_questions":{"type":"array","items":{"type":"string"}},
"evidence_usage":{"type":"array","items":{"type":"object","required":["evidence_id","used","why"],"properties":{"evidence_id":{"type":"string"},"used":{"type":"boolean"},"why":{"type":"string","minLength":1}}}},
"annotations_addressed":{"type":"array","items":{"type":"object","required":["annotation_id","addressed"],"properties":{"annotation_id":{"type":"string"},"addressed":{"type":"boolean"},"how":{"type":"string"},"reason":{"type":"string"}},"anyOf":[{"required":["how"],"properties":{"how":{"minLength":1}}},{"required":["reason"],"properties":{"reason":{"minLength":1}}}]}}
}}
def check_contract(draft,errors):
    from jsonschema import Draft202012Validator
    for error in Draft202012Validator(DRAFT_SCHEMA).iter_errors(draft):errors.append("contract: "+".".join(map(str,error.path))+": "+error.message)
    if not isinstance(draft,dict):return
    changes=draft.get("changes")
    if not isinstance(changes,list):return
    ids=[c.get("change_id") for c in changes if isinstance(c,dict) and isinstance(c.get("change_id"),str)]
    if len(ids)!=len(set(ids)):errors.append("duplicate change IDs")
    for c in changes:
        if isinstance(c,dict) and not c.get("original_sentence") and not c.get("revised_sentence"):errors.append("change cannot have empty original and revised")
def check_cites(original,revised,bib_keys,errors):
    for cmd,keys in re.findall(r"\\([Cc]ite\w*)(?:\[[^]]*\])*\{([^}]*)\}",revised):
        if cmd!="citep":errors.append("citation form must be citep")
        for key in keys.split(","):
            if key.strip() not in bib_keys:errors.append("unknown bibliography key: "+key.strip())
def check_labels(original,revised,all_labels,errors):
    old=set(re.findall(r"\\label\{([^}]*)\}",original));new=set(re.findall(r"\\label\{([^}]*)\}",revised))
    if not old<=new:errors.append("original labels removed")
    for key in re.findall(r"\\(?:eqref|ref|autoref|cref)\{([^}]*)\}",revised):
        if key not in all_labels|new:errors.append("unresolved ref: "+key)
def check_macros(original,revised,macros,errors):
    introduced=set(commands(revised))-set(commands(original))-macros-STANDARD
    if introduced:errors.append("new undefined macros: "+",".join(sorted(introduced)))
    if "\\mathbf{" in revised and "\\mathbf{" not in original:errors.append("bold mathematics must use bm")
def check_math(original,revised,flags):
    if _math(original)!=_math(revised):flags.append("math_changed")
def _hunks(original,revised):
    old,new=sentences(original),sentences(revised)
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    return [(old[a:b],new[c:d]) for tag,a,b,c,d in sm.get_opcodes() if tag!="equal"],len(old)
def check_change_map(original,revised,changes,evidence_ids,errors):
    hunks,_=_hunks(original,revised)
    valid=[]
    for c in changes:
        if not isinstance(c,dict):continue
        o,n=c.get("original_sentence"),c.get("revised_sentence")
        if not isinstance(o,str) or not isinstance(n,str):continue
        if o and o not in original:errors.append("fabricated original sentence")
        if n and n not in revised:errors.append("fabricated revised sentence")
        if isinstance(c.get("sources"),list) and all(isinstance(x,str) for x in c["sources"]) and not set(c["sources"])<=evidence_ids:errors.append("unresolved change sources")
        valid.append((o,n))
    from collections import Counter
    expected_old=Counter(s for old,_ in hunks for s in old);expected_new=Counter(s for _,new in hunks for s in new)
    mapped_old=Counter(o for o,_ in valid if o);mapped_new=Counter(n for _,n in valid if n)
    if expected_new-mapped_new:errors.append("changed sentence missing from map")
    if expected_old-mapped_old:errors.append("deleted sentence missing from map")
    if mapped_new-expected_new or mapped_old-expected_old:errors.append("change map does not match actual sentence occurrences")
    if not hunks and changes:errors.append("change map lists no actual change")
def check_annotations(card,draft,errors):
    expected={a.get("annotation_id") for a in card.get("annotations",[]) if isinstance(a,dict)}
    actual={a.get("annotation_id") for a in (draft.get("annotations_addressed") if isinstance(draft.get("annotations_addressed"),list) else []) if isinstance(a,dict) and isinstance(a.get("annotation_id"),str)}
    if actual!=expected:errors.append("annotations not completely accounted for")
def check_diff_ratio(original,revised,kind,limit,errors):
    hunks,n=_hunks(original,revised);ratio=sum(max(len(a),len(b)) for a,b in hunks)/max(1,n)
    if ratio>limit and kind!="restructure":errors.append("diff ratio exceeded")
    return ratio,hunks

def validate(draft,card,bib_keys,macros,config,all_labels=None):
    errors=[];flags=[];check_contract(draft,errors)
    if not isinstance(draft,dict) or not isinstance(draft.get("revised_tex"),str):return {"pass":False,"errors":errors,"flags":[],"diff_ratio":None,"actual_changed_sentences":[]}
    original="\n\n".join(u["text"] for u in card["target_units"]);revised=draft["revised_tex"]
    check_cites(original,revised,bib_keys,errors);check_labels(original,revised,all_labels or set(),errors);check_macros(original,revised,macros,errors);check_math(original,revised,flags)
    from ..knowledge.writing_routes import unresolved_slots
    errors.extend("unresolved route adaptation slot: "+slot for slot in unresolved_slots(original,revised,card.get("evidence",{})))
    from .handbook_profile import science_freeze
    errors.extend(science_freeze(original,revised,card.get("evidence",{})))
    from .evidence_catalog import allowed_ids
    evidence_ids=allowed_ids(card.get("evidence",{}))
    for usage in draft.get("evidence_usage",[]) if isinstance(draft.get("evidence_usage"),list) else []:
        if isinstance(usage,dict) and isinstance(usage.get("evidence_id"),str) and usage["evidence_id"] not in evidence_ids:errors.append("unresolved evidence usage")
    check_change_map(original,revised,draft.get("changes",[]) if isinstance(draft.get("changes"),list) else [],evidence_ids,errors)
    check_annotations(card,draft,errors)
    ratio,hunks=check_diff_ratio(original,revised,card["task_kind"],config["validators"]["max_diff_ratio"],errors)
    return {"pass":not errors,"errors":errors,"flags":flags,"diff_ratio":ratio,"actual_changed_sentences":[s for _,new in hunks for s in new]}
