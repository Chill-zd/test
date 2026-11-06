"""Restartable local manuscript task commands."""
from __future__ import annotations
import json,hashlib,shutil,subprocess,re,uuid,os
from pathlib import Path
import click
from .config import load_config
from .llm.ledger import Ledger
from .llm.client import LLMClient
from .llm.host_bridge import PendingHostCall
from .corpus.ingest import ingest
from .corpus.parser import parse_tree
from .pipeline.taskcard import locate,card,NeedsUser
from .pipeline.evidence import gather
from .pipeline.writer import write
from .pipeline.validators import validate
from .pipeline.reviewer import review
from .pipeline.compiler import compile_candidate,run_build
from .pipeline.deliver import deliver
from .memory.feedback import record
from .pipeline.baseline import status as baseline_status,record as record_baseline,preserve_previous as preserve_baseline

ROOT=Path(os.environ.get("POLISHPAPER_HOME",Path.cwd() if (Path.cwd()/"config.yaml").exists() else Path(__file__).parents[1])).resolve()
DATA=ROOT/"data"
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def read(path):return json.loads(Path(path).read_text())
def taskdir(task_id):return DATA/"tasks"/task_id
def cfg():return load_config(ROOT/"config.yaml")
def client():return LLMClient(cfg(),Ledger(DATA/"ledger.sqlite"))
def frozen(task):
    inputs=task/"input_manifest.json"
    if inputs.exists():
        for rel,digest in read(inputs).items():
            if not (task/rel).exists() or hashlib.sha256((task/rel).read_bytes()).hexdigest()!=digest:raise click.ClickException("task input changed; create a new task: "+rel)
    manifest=read(task/"source_manifest.json")
    for rel,digest in manifest.items():
        p=task/"workspace"/rel
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise click.ClickException(f"frozen source changed: {rel}")
def corpus_roots():
    root=DATA/"corpus"/"raw"
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.exists() else []
def put_manifest(task):
    from .pipeline.task_sources import generated_paths
    workspace=task/"workspace";generated=generated_paths(workspace,(task/'main.txt').read_text().strip())
    save(task/"source_manifest.json",{str(p.relative_to(workspace)):hashlib.sha256(p.read_bytes()).hexdigest() for p in workspace.rglob("*") if p.is_file() and str(p.relative_to(workspace)) not in generated})
def audit_ledger(task):
    rows=Ledger(DATA/"ledger.sqlite").rows(task.name)
    (task/"ledger.jsonl").write_text("".join(json.dumps(dict(zip(("id","scope","provider","purpose","status","created","detail","model","input_tokens","output_tokens"),r)))+"\n" for r in rows))
    return rows

@click.group()
def main():pass

@main.command("ingest")
@click.argument("directory",type=click.Path(exists=True,file_okay=False,path_type=Path))
@click.option("--main", "main_file")
def ingest_cmd(directory,main_file):
    result=ingest(directory,DATA/"corpus",main_file,config=cfg());click.echo(json.dumps(result,indent=2))
    if result["status"]!="ready":raise click.ClickException("ingest quarantined; inspect baseline log")

@main.command("parse")
@click.argument("paper",required=False)
@click.option("--all","all_papers",is_flag=True)
def parse_cmd(paper,all_papers):
    if not all_papers and not paper:raise click.UsageError("provide PAPER or --all")
    roots=corpus_roots() if all_papers else [DATA/"corpus"/"raw"/paper]
    failures=[]
    for root in roots:
        meta=read(root/"metadata.json");units=parse_tree(root/meta["main"],meta["paper_id"],root)
        save(root/"units.json",units)
        meta["unit_count"]=len(units);save(root/"metadata.json",meta)
        import yaml
        (root/"meta.yaml").write_text(yaml.safe_dump(meta,sort_keys=False,allow_unicode=True))
        parsed=DATA/"corpus"/"parsed";parsed.mkdir(parents=True,exist_ok=True)
        (parsed/(meta["paper_id"]+".jsonl")).write_text("".join(json.dumps(u,ensure_ascii=False)+"\n" for u in units))
        unknown=sum(u["section_type"]=="unknown" for u in units)/max(1,len(units))
        report={"units":len(units),"unknown_ratio":unknown,"pass":unknown<=.15};save(root/"parse_report.json",report)
        click.echo(f"{meta['paper_id']}: {len(units)} units; unknown {unknown:.1%}")
        if unknown>.15:failures.append(meta["paper_id"])
    if failures:raise click.ClickException("unknown sections exceed 15%: "+", ".join(failures))

@main.group("extract")
def extract_group():pass
for _kind in ("lexicon","patterns","schemas"):
    def _make(kind):
        @extract_group.command(kind)
        @click.option("--paper")
        def command(paper):
            from importlib import import_module
            mod=import_module(".knowledge.extract_"+kind,__package__)
            for root in corpus_roots():
                if paper and root.name!=paper:continue
                units=read(root/"units.json")
                for section in sorted({u["section_type"] for u in units}):
                    group=[u for u in units if u["section_type"]==section]
                    mod.extract(client(),root.name,section,group,DATA/"knowledge"/"_raw")
        return command
    _make(_kind)

@main.group("verify")
def verify_group():pass
@verify_group.command("knowledge")
def verify_knowledge():
    from .knowledge.verify import verify_batch
    raw=DATA/"knowledge"/"_raw";good_count=bad_count=0;invalid=[]
    stems={p.name.removesuffix(".verified.json") for p in raw.glob("*.verified.json")} | {p.name.removesuffix(".raw.json") for p in raw.glob("*.raw.json")}
    for stem in sorted(stems):
        canonical=raw/(stem+".verified.json");kind=stem.rsplit("_",1)[-1];units=[]
        for root in corpus_roots():
            meta=read(root/"metadata.json")
            if stem.startswith(root.name+"_"):units.extend(parse_tree(root/meta["main"],meta["paper_id"],root))
        if canonical.exists():records=read(canonical);items=[item for record in records for item in record.get("items",[])]
        else:
            try:items=read(raw/(stem+".raw.json")).get("items",[])
            except (ValueError,AttributeError):invalid.append(stem);continue
        good,bad=verify_batch(items,units,kind)
        save(canonical,[{**(records[0] if canonical.exists() else {}),"kind":kind,"items":good,"reverification":"Rebound to current comment-free parsed source"}]);save(DATA/"knowledge"/"_dropped"/(stem+".reverification.dropped.json"),bad)
        good_count+=len(good);bad_count+=len(bad)
    click.echo(json.dumps({"verified":good_count,"dropped":bad_count,"drop_ratio":bad_count/max(1,bad_count+good_count),"unresolved_invalid_raw_batches":invalid,"attempt_history":"preserved under _raw/_attempts; this command rebinds active canonical claims"}))
    if invalid:raise click.ClickException("Unresolved invalid extraction JSON remains in preserved raw attempts")

@main.group("merge")
def merge_group():pass
@merge_group.command("knowledge")
def merge_knowledge():
    from .knowledge.merge import merge
    click.echo(json.dumps(merge(DATA/"knowledge"/"_raw",DATA/"knowledge")))

@main.group("index")
def index_group():pass
@index_group.command("build")
def index_build():
    from .index.embed import Embedder
    from .index.search import build
    objects=[]
    for p in (DATA/"corpus"/"raw").glob("*/units.json"):
        paper_meta=read(p.parent/"metadata.json")
        from .corpus.parser import strip_comments
        for u in read(p):
            external=paper_meta.get("source_tag")=="author_text"
            source={k:u[k] for k in ("unit_id","paper_id","file","line_start","line_end","sha256","prose_sha256","section_path","env_kind")}
            source.update({"title":paper_meta.get("title","unknown"),"authors":paper_meta.get("authors","unknown"),"group_attribution":paper_meta.get("group_attribution","unknown"),"source_url":paper_meta.get("source_url")})
            objects.append({"kind":"unit","id":u["unit_id"],"text":u.get("prose_text",strip_comments(u["text"])),"section_type":u["section_type"],"concepts":u["concepts"],"source_tag":paper_meta.get("source_tag","coauthor_text"),"conditions":["External attributed author source for domain reference; not evidence of Wiesemann-authored style." if external else "Attributed coauthored passage; observed usage is conditional and does not establish a universal author rule."],"source":source})
    from .memory.feedback import index_objects,raw_objects
    objects.extend(index_objects(DATA/"memory"/"feedback.sqlite"))
    objects.extend(raw_objects(DATA/"corpus"/"feedback_raw"))
    for p in (DATA/"knowledge"/"patterns").glob("*.jsonl"):
        for i,line in enumerate(p.read_text().splitlines()):
            row=json.loads(line);objects.append({"kind":"pattern","id":f"pattern:{p.stem}:{i}","text":row["template"]+"\nConditions: "+str(row.get("condition","")),"section_type":row.get("section_type","unknown"),"concepts":row.get("concepts",[]),"source_tag":"coauthor_text","source":row})
    build(objects,DATA/"index",Embedder(**cfg()["embedding"]));click.echo(f"Indexed {len(objects)} objects")

@main.command("adjacent-menu")
@click.option("--section",default=None,help="Optional section label filter; does not establish applicability.")
def adjacent_menu(section):
    """List optional pilot cards by reader task, omission condition and literal preview."""
    path=DATA/"knowledge"/"adjacent_transfers.json"
    if not path.exists():
        click.echo("当前配置未启用相邻句试验目录。可使用独立 adjacent_pilot 配置。")
        return
    from .knowledge.adjacent_transfers import verify
    for entry in read(path)["items"]:
        if section and section!=entry["section_type"]:continue
        verify(entry)
        click.echo(entry["id"]+" | "+entry["section_type"]+" | "+entry["reader_task"].get("zh",entry["reader_task"].get("en","")))
        click.echo("省略条件："+entry["omit_if"])
        click.echo("原文预览："+entry["literal_contiguous_text"]+"\n")

@main.group("task")
def task_group():pass
@task_group.command("new")
@click.option("--tex",required=True,type=click.Path(exists=True,path_type=Path))
@click.option("--bib",required=True,type=click.Path(exists=True,path_type=Path),help='Actual .bib or original .bbl bibliography; no fabricated entries.')
@click.option("--request",required=True,type=click.Path(exists=True,path_type=Path))
@click.option("--kind",type=click.Choice(["revise","merge_split","restructure"]),default=None)
@click.option("--annotations",type=click.Path(exists=True,path_type=Path))
@click.option('--target-quote',type=click.Path(exists=True,dir_okay=False,path_type=Path),help='Exact target text file; separate from request and advisor annotations, no fuzzy/model lookup.')
@click.option('--evaluation-exclusions',type=click.Path(exists=True,dir_okay=False,path_type=Path),help='Explicit frozen holdout manifest; ordinary tasks omit this.')
@click.option("--adjacent-transfer-pilot",is_flag=True,help="Explicit experimental adjacent-source delivery; requires evaluation exclusions and a pilot catalog.")
@click.option("--adjacent-transfer-id",multiple=True,help="Exact optional pilot card ID; repeat to select more than one.")
def task_new(tex,bib,request,kind,annotations,evaluation_exclusions,target_quote,adjacent_transfer_pilot=False,adjacent_transfer_id=()):
    if adjacent_transfer_pilot and not evaluation_exclusions:
        raise click.ClickException("The experimental pilot requires --evaluation-exclusions with the target source family")
    if adjacent_transfer_pilot and not adjacent_transfer_id:
        raise click.ClickException("The experimental pilot requires an explicit --adjacent-transfer-id")
    if adjacent_transfer_id and not adjacent_transfer_pilot:
        raise click.ClickException("--adjacent-transfer-id requires --adjacent-transfer-pilot")
    if kind is None:
        content=request.read_text().lower()
        kind="restructure" if any(w in content for w in ("restructure","reorganize","reorder","重组","重組","重排")) else "merge_split" if any(w in content for w in ("merge","split","合并","合併","拆分")) else "revise"
    task_id=uuid.uuid4().hex[:12];task=taskdir(task_id);task.mkdir(parents=True)
    source=tex.resolve().parent;workspace=task/"workspace"
    from .pipeline.task_sources import preserve_generated_originals
    preserve_generated_originals(task,source,tex.resolve().relative_to(source))
    shutil.copytree(source,workspace,ignore=shutil.ignore_patterns(".git","*.aux","*.log","*.fdb_latexmk","*.fls",".venv","data"))
    for copied in workspace.rglob("*"):
        if copied.is_file():copied.chmod(copied.stat().st_mode | 0o200)
    rel=tex.resolve().relative_to(source);shutil.copy2(bib,workspace/bib.name)
    (task/"main.txt").write_text(str(rel));(task/"bib.txt").write_text(bib.name);shutil.copy2(request,task/"request.md")
    if target_quote:shutil.copy2(target_quote,task/"target_quote.txt")
    if annotations:shutil.copy2(annotations,task/"annotations.json")
    if evaluation_exclusions:
        from .pipeline.evaluation import Exclusions,binding
        Exclusions(binding(evaluation_exclusions))
        shutil.copy2(evaluation_exclusions,task/'evaluation_exclusions.json')
    save(task/"task_meta.json",{"kind":kind,"status":"created",**({"adjacent_transfer_pilot":True,"adjacent_transfer_ids":list(adjacent_transfer_id)} if adjacent_transfer_pilot else {})});put_manifest(task)
    save(task/"input_manifest.json",{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (task/"request.md",task/"annotations.json",task/"task_meta.json",task/'evaluation_exclusions.json',task/"target_quote.txt") if p.exists()})
    result=run_build(workspace,rel,cfg(),task/"baseline_build.log")
    record_baseline(task,result)
    if not result["pass"]:raise click.ClickException(f"Baseline compile failed; log: {task/'baseline_build.log'}")
    click.echo(task_id)

def stage(task_id,name,func):
    task=taskdir(task_id)
    if not task.exists():raise click.ClickException("unknown task")
    frozen(task)
    baseline=baseline_status(task)
    if not baseline['pass']:raise click.ClickException(baseline['message'])
    existing=task/"evidence.json"
    if existing.exists() and read(existing).get("schema_status")!="omitted_bare":
        from .pipeline.evidence import assert_fresh
        assert_fresh(read(existing),DATA/"knowledge")
    try:return func(task)
    except PendingHostCall as exc:raise click.ClickException(str(exc))
    finally:audit_ledger(task)

def _locate(task):
    out=task/"taskcard.json"
    if out.exists():return read(out)
    main=(task/"main.txt").read_text().strip();units=parse_tree(task/"workspace"/main,task.name,task/"workspace")
    request=(task/"request.md").read_text()
    if (task/"target_quote.txt").is_file():
        quote=" ".join((task/"target_quote.txt").read_text().split())
        targets=[{**u,"locate_basis":"independent exact target-quote channel"} for u in units if quote and quote in " ".join(u["text"].split())]
        if len(targets)!=1:raise click.ClickException("Exact target quote must identify one complete source unit; no fuzzy/model fallback")
    else:targets=locate(units,request,client(),task.name,read(task/"task_meta.json")["kind"],read(task/"annotations.json") if (task/"annotations.json").exists() else [])
    result=card(targets,units,request,read(task/"task_meta.json")["kind"],read(task/"annotations.json") if (task/"annotations.json").exists() else [])
    if (task/'evaluation_exclusions.json').exists():
        from .pipeline.evaluation import binding
        result['evaluation_exclusions']={'manifest':binding(task/'evaluation_exclusions.json')}
    if read(task/"task_meta.json").get("adjacent_transfer_pilot") is True:
        result["adjacent_transfer_pilot"]=True
        result["adjacent_transfer_ids"]=read(task/"task_meta.json").get("adjacent_transfer_ids",[])
    save(out,result);audit_ledger(task);return result

def _evidence(task,bare=False):
    out=task/"evidence.json"
    if out.exists():
        cached=read(out)
        if not bare and cached.get("schema_status")!="omitted_bare":
            from .pipeline.evidence import assert_fresh
            assert_fresh(cached,DATA/"knowledge")
        return cached
    c=_locate(task)
    if (task/'evaluation_exclusions.json').exists():
        from .pipeline.evaluation import binding
        if c.get('evaluation_exclusions')!={'manifest':binding(task/'evaluation_exclusions.json')}:raise click.ClickException('Evaluation taskcard is not bound to the frozen exclusion manifest')
    notation_baseline=None
    if (task/'main.txt').is_file():
        from .pipeline.notation_baseline import build as build_notation_baseline
        notation_baseline=build_notation_baseline(task/'workspace',(task/'main.txt').read_text().strip(),task.name,task/'notation_baseline.json')
    if bare:
        result={"items":[{"evidence_id":"user_request","source_tag":"user_request","text":c["user_request"],"conditions":[],"provenance":{}}],"schema":None,"schema_status":"omitted_bare","mode":"no_domain_evidence"}
        from .pipeline.evidence import prepare_notation
        result['notation']=prepare_notation(c,catalog_enabled=False,baseline=notation_baseline)
        if c.get('evaluation_exclusions'):
            from .pipeline.evaluation import resolve
            result['evaluation_exclusions']=resolve(c).audit()
    else:
        from .index.search import retrieve
        from .index.embed import Embedder
        search=(lambda q,st,cs,k,top,**kw: retrieve(DATA/"index",Embedder(**cfg()["embedding"]),q,st,cs,k,top,**kw)) if (DATA/"index"/"vectors.npy").exists() else None
        result=gather(c,DATA/"knowledge",cfg(),search=search,notation_baseline=notation_baseline)
    if (task/"writing_profile.json").is_file():
        from .pipeline.handbook_profile import prepare
        baseline=read(task/"notation_baseline.json")
        result=prepare(c,result,baseline,DATA/"knowledge",task,bare=bare)
    save(out,result);return result

def _write(task,bare=False):
    out=task/"draft.json"
    if out.exists():return read(out)
    c=_locate(task);e=_evidence(task,bare);main=task/"workspace"/(task/"main.txt").read_text().strip()
    from .pipeline.bibliography import read_keys
    keys=read_keys(task/"workspace"/(task/"bib.txt").read_text().strip());preamble=main.read_text().split("\\begin{document}")[0]
    macros=set(re.findall(r"\\(?:newcommand|renewcommand|DeclareMathOperator)\s*\{\\([A-Za-z]+)\}",preamble))
    draft=write(client(),task.name,c,e,keys,macros,task/"writer_call.json")
    if e.get("writing_profile",{}).get("name")=="handbook":save(task/"evidence.json",e)
    save(out,draft);audit_ledger(task);return draft

def _repair(task,reason,bare=False):
    marker=task/"repair_call.json"
    prior=read(marker) if marker.exists() else None
    old=_write(task,bare);c=_locate(task);e=_evidence(task,bare)
    binding={"task_id":task.name,"bare":bare,"taskcard":c,"evidence":e,"draft":old}
    if prior:
        if prior.get("status") not in ("host_pending","completed"):return False
        bound=prior.get("binding")
        if not bound or prior.get("reason")!=reason:return False
        if prior["status"]=="completed":
            repaired=json.loads(prior["raw_response"])
            if prior.get("applied"):return False
            if old!=repaired and bound!=binding:return False
            # Invalidate before saving so interruption cannot leave stale reports.
            for name in ("review_report.json","validator_report.json","compile_report.json"):
                (task/name).unlink(missing_ok=True)
            save(task/"draft.json",repaired)
            save(marker,{**prior,"applied":True})
            audit_ledger(task)
            return True
        if bound!=binding:return False
    messages=prior["messages"] if prior else [{"role":"system","content":"Repair only the specific listed defects in this academic TeX candidate. Return the same strict JSON contract; preserve all other meaning and source bounds. Do not invent scientific claims or source IDs."},{"role":"user","content":json.dumps({"reason":reason,"taskcard":c,"evidence":e,"draft":old},ensure_ascii=False)}]
    if e.get("writing_profile",{}).get("name")=="handbook" and not prior:
        from .pipeline.profile_transport import compact_for_model
        messages[-1]["content"]=json.dumps(compact_for_model(json.loads(messages[-1]["content"]),marker),ensure_ascii=False,separators=(",",":"))
    record={"status":"reserved","reason":reason,"messages":messages,"binding":binding}
    save(marker,record)
    try:raw=client().complete(provider="gpt",messages=messages,task_id=task.name,purpose="shared_repair",response_format={"type":"json_object"},**({"require_input_budget":True} if e.get("writing_profile",{}).get("name")=="handbook" else {}))
    except PendingHostCall:
        save(marker,{**record,"status":"host_pending"});raise
    save(marker,{**record,"status":"completed","raw_response":raw})
    return _repair(task,reason,bare)

def _review(task,bare=False):
    report=task/"review_report.json"
    marker=task/"repair_call.json"
    if marker.exists():
        pending=read(marker)
        if pending.get("status")=="completed":_repair(task,pending.get("reason"),bare)
    if report.exists():return read(report)
    c=_locate(task);e=_evidence(task,bare);c["evidence"]=e;d=_write(task,bare)
    from .pipeline.bibliography import read_keys
    keys=read_keys(task/"workspace"/(task/"bib.txt").read_text().strip())
    main=(task/"workspace"/(task/"main.txt").read_text().strip()).read_text();labels=set(re.findall(r"\\label\{([^}]*)\}","\n".join(p.read_text() for p in (task/"workspace").rglob("*.tex"))))
    preamble=main.split("\\begin{document}")[0];macros=set(re.findall(r"\\(?:newcommand|renewcommand|DeclareMathOperator)\s*\{\\([A-Za-z]+)\}",preamble))
    v=validate(d,c,keys,macros,cfg(),labels);save(task/"validator_report.json",v)
    if not v["pass"]:
        if _repair(task,{"validator_errors":v["errors"]},bare):return _review(task,bare)
        result={"verdict":"fix","findings":v["errors"],"fix_actions":[]};save(report,result);return result
    try:r=review(client(),task.name,c,d,e,v,cfg(),task/"reviewer_call.json")
    except (ValueError,TypeError) as exc:r={"verdict":"escalate_to_user","findings":["Malformed review: "+str(exc)],"fix_actions":[],"science_questions":[]}
    save(report,r);audit_ledger(task)
    if r["verdict"]=="escalate_to_user":
        from .pipeline.deliver import retain_candidate
        retain_candidate(task,d,v,r,e)
    if r["verdict"]=="fix" and _repair(task,{"review_actions":r.get("fix_actions",[])},bare):return _review(task,bare)
    return r

def _compile(task,bare=False):
    report=task/"compile_report.json"
    if report.exists():return read(report)
    r=_review(task,bare)
    if r["verdict"]!="pass":return {"pass":False,"reason":"review did not pass"}
    result=compile_candidate(task,_locate(task),_write(task,bare),cfg());save(report,result)
    safe_errors=[line for line in Path(result["log"]).read_text().splitlines() if "Undefined control sequence" in line or "Missing } inserted" in line or "Extra }" in line]
    if not result["pass"] and safe_errors and _repair(task,{"technical_compile_errors":safe_errors},bare):return _compile(task,bare)
    return result

for _name,_fn in (("locate",_locate),("evidence",_evidence),("write",_write),("review",_review),("compile",_compile)):
    def _make(name,fn):
        @task_group.command(name)
        @click.argument("task_id")
        def cmd(task_id):click.echo(json.dumps(stage(task_id,name,fn),ensure_ascii=False,indent=2))
        return cmd
    _make(_name,_fn)

@task_group.command("deliver")
@click.argument("task_id")
def task_deliver(task_id):
    def action(task):
        c=_locate(task);e=_evidence(task);d=_write(task);r=_review(task);v=read(task/"validator_report.json");b=_compile(task)
        return deliver(task,c,read(task/"draft.json"),read(task/"validator_report.json"),read(task/"review_report.json"),b,audit_ledger(task),e)
    click.echo(json.dumps(stage(task_id,"deliver",action),indent=2))

@task_group.command("run")
@click.argument("task_id")
@click.option("--bare",is_flag=True)
@click.option("--handbook",is_flag=True,help="Separate language-only handbook profile; scientific assertions and math frozen, not legacy complete full.")
def task_run(task_id,bare,handbook):
    task=taskdir(task_id)
    if bare or handbook:
        variant=taskdir(task_id+("-handbook" if handbook else "")+("-bare" if bare else ""))
        if not variant.exists():
            ignored=shutil.ignore_patterns("taskcard.json","evidence.json","notation_baseline.json","draft.json","*_report.json","*_call.json","patched","deliver","ledger.jsonl")
            shutil.copytree(task,variant,ignore=lambda directory,names:ignored(directory,names) if Path(directory)==task else [])
            if (task/'baseline_report.json').is_file():shutil.copy2(task/'baseline_report.json',variant/'baseline_report.json')
        task=variant
        if handbook:
            save(task/"writing_profile.json",{"name":"handbook","language_only_science_frozen":True,"legacy_complete_full":False})
    def action(t):
        c=_locate(t);e=_evidence(t,bare);d=_write(t,bare);r=_review(t,bare);v=read(t/"validator_report.json");b=_compile(t,bare)
        if r["verdict"]!="pass" or not b["pass"]:
            from .pipeline.deliver import retain_candidate
            retain_candidate(t,read(t/"draft.json"),read(t/"validator_report.json"),read(t/"review_report.json"),e,b)
            return {"status":"needs_user_or_repair","review":read(t/"review_report.json"),"build":b}
        return deliver(t,c,read(t/"draft.json"),read(t/"validator_report.json"),read(t/"review_report.json"),b,audit_ledger(t),e)
    click.echo(json.dumps(stage(task.name,"run",action),indent=2))


@task_group.command('baseline-check')
@click.argument('task_id')
def task_baseline_check(task_id):
    """显式重检原始副本基线；保留旧报告，不启动写作。"""
    task=taskdir(task_id)
    if not task.is_dir():raise click.ClickException('unknown task')
    frozen(task);preserve_baseline(task)
    result=run_build(task/'workspace',(task/'main.txt').read_text().strip(),cfg(),task/'baseline_build.log')
    report=record_baseline(task,result);click.echo(json.dumps(report,ensure_ascii=False,indent=2))
    if not report['pass']:raise click.ClickException('基线编译未通过，未启动写作。')

@main.group("feedback")
def feedback_group():pass
@feedback_group.command("record")
@click.argument("task_id")
def feedback_record(task_id):
    task=taskdir(task_id)
    from .memory.feedback import update_index
    count=record(task,task/"decisions.yaml",DATA/"memory"/"feedback.sqlite")
    from .index.embed import Embedder
    if count:update_index(DATA/"memory"/"feedback.sqlite",DATA/"index",Embedder(**cfg()["embedding"]))
    click.echo(f"recorded {count}; feedback index updated")

@main.group("ledger")
def ledger_group():pass
@ledger_group.command("show")
@click.option("--task")
def ledger_show(task):
    ledger=Ledger(DATA/"ledger.sqlite");click.echo(json.dumps(ledger.summary(task),indent=2))


@main.group("llm")
def llm_group():pass
@llm_group.command("pending")
def llm_pending():
    from .llm.host_bridge import pending
    click.echo(json.dumps(pending(Ledger(DATA/"ledger.sqlite")),indent=2))
@llm_group.command("respond")
@click.argument("request_file",type=click.Path(exists=True,path_type=Path))
@click.option("--response",required=True,type=click.Path(exists=True,path_type=Path))
@click.option("--model",required=True)
@click.option("--receipt",required=True,type=click.Path(exists=True,path_type=Path))
def llm_respond(request_file,response,model,receipt):
    from .llm.host_bridge import respond
    click.echo(json.dumps(respond(Ledger(DATA/"ledger.sqlite"),request_file,response,model,receipt),indent=2))

from .structure.cli import structure_group
main.add_command(structure_group)

if __name__=="__main__":main()
