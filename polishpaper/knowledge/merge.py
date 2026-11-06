from __future__ import annotations
import json,yaml
from pathlib import Path
PATTERN_FUNCTIONS=("definition","assumption","contribution","transition","theorem_intuition","comparison","limitation","notation_intro")

def merge(raw_dir:str|Path,out_dir:str)->dict:
    raw=Path(raw_dir);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for p in raw.glob("*.verified.json"):records.extend(json.loads(p.read_text()))
    lex={};patterns={k:{} for k in PATTERN_FUNCTIONS};schemas={};variants={}
    for r in records:
        if r.get("admission_status","").startswith("diagnostic"):continue
        kind=r.get("kind")
        for item in r.get("items",[]):
            examples=item.get("examples",[])
            if kind=="lexicon":
                term=item.get("term","").strip();phrase=item.get("phrase","").strip()
                if not term or not phrase:continue
                key=(term.casefold(),phrase.casefold())
                entry=lex.setdefault(key,{"term":term,"phrase":phrase,"sources":set(),"note":item.get("note","")})
                entry["sources"].update(e["source"]["unit_id"] for e in examples)
            elif kind=="patterns" and item.get("function") in patterns:
                key=(item.get("template",""),json.dumps(item.get("condition",""),sort_keys=True))
                old=patterns[item["function"]].setdefault(key,{**item,"examples":[]})
                seen={e["source"]["unit_id"] for e in old["examples"]}
                for e in examples:
                    if e["source"]["unit_id"] not in seen:old["examples"].append(e);seen.add(e["source"]["unit_id"])
            elif kind=="schemas":
                stype=item.get("section_type","unknown")
                paper_ids=sorted({e["source"]["paper_id"] for e in examples})
                source_prefix="+".join(paper_ids) or "unattributed"
                observed_ids=[]
                for move in item.get("moves",[]):
                    local_id=f"{source_prefix}:{stype}:{move['id']}"
                    known={m["id"] for m in schemas.setdefault(stype,[])}
                    if local_id in known:local_id+=":"+str(len(known)+1)
                    schemas[stype].append({**move,"id":local_id,"original_id":move["id"],"source_papers":paper_ids})
                    observed_ids.append(local_id)
                variants.setdefault(stype,[]).append({"kind":"observed_source_sequence","source_papers":paper_ids,"move_ids":observed_ids,"conditions":"Observed in this supplied source section; this is not a universal paragraph sequence.","source_variants":item.get("variants",[])})
    terms={}
    unit_to_paper={}
    for r in records:
        for item in r.get("items",[]):
            for e in item.get("examples",[]):unit_to_paper[e["source"]["unit_id"]]=e["source"]["paper_id"]
    for v in lex.values():
        papers={unit_to_paper[u] for u in v["sources"]}
        groups=[("shared",v["sources"])] if len(papers)>=3 else [("single:"+paper,{u for u in v["sources"] if unit_to_paper[u]==paper}) for paper in sorted(papers)]
        for scope,sources in groups:
            entry={"phrase":v["phrase"],"sources":sorted(sources),"freq":len(sources),"scope":scope,"note":v["note"]}
            terms.setdefault(v["term"],[]).append(entry)
    (out/"lexicon.yaml").write_text(yaml.safe_dump([{"term":term,"entries":entries} for term,entries in sorted(terms.items())],sort_keys=False,allow_unicode=True))
    (out/"patterns").mkdir(exist_ok=True)
    for name,items in patterns.items():(out/"patterns"/f"{name}.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in items.values()))
    (out/"schemas").mkdir(exist_ok=True)
    for name,moves in schemas.items():(out/"schemas"/f"{name}.yaml").write_text(yaml.safe_dump({"moves":moves,"variants":variants.get(name,[]),"review_status":"pending_human","note":"Source-specific observed moves and sequences are retained separately; human review is required before treating any sequence as guidance."},sort_keys=False,allow_unicode=True))
    return {"lexicon_entries":len(lex),"patterns":sum(map(len,patterns.values())),"schemas":len(schemas)}
