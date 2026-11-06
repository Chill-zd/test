from __future__ import annotations
import json,shutil,re,yaml
from pathlib import Path
from .parser import parse_tree,strip_comments
from ..pipeline.compiler import run_build

def find_main(directory,main=None):
    directory=Path(directory)
    if main:
        p=(directory/main).resolve()
        if not p.is_relative_to(directory.resolve()) or not p.is_file():raise ValueError('invalid --main')
        return p
    matches=[p for p in directory.rglob('*.tex') if re.search(r'\\documentclass(?:\[[^]]*\])?\{',strip_comments(p.read_text()))]
    if len(matches)!=1:raise ValueError(f'expected one main TeX file, found {len(matches)}; use --main')
    return matches[0]

def ingest(directory,store,main=None,config=None):
    source=Path(directory).resolve();store=Path(store).resolve();dest=store/'raw'/source.name
    if dest.exists() or (store/'quarantine'/source.name).exists():raise FileExistsError(source.name)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.git','*.aux','*.log','*.fdb_latexmk','*.fls'))
    for copied in dest.rglob('*'):
        if copied.is_file():copied.chmod(copied.stat().st_mode | 0o200)
    meta={'paper_id':source.name,'authors':'unknown','year':'unknown','venue':'unknown','topics':[],'status':'pending'}
    try:
        chosen=find_main(dest,main);meta['main']=str(chosen.relative_to(dest))
        units=parse_tree(chosen,source.name,dest)
        build=run_build(dest,meta['main'],config or {'compile':{'cmd':['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error'],'timeout_sec':300}},dest/'baseline_build.log')
        if not build['pass']:raise ValueError('baseline compilation failed; see baseline_build.log')
        meta['status']='ready';meta['unit_count']=len(units)
        (dest/'units.json').write_text(json.dumps(units,ensure_ascii=False,indent=2))
        parsed=store/'parsed';parsed.mkdir(exist_ok=True)
        (parsed/(source.name+'.jsonl')).write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
    except Exception as exc:
        meta.update(status='quarantined',error=str(exc));quarantine=store/'quarantine';quarantine.mkdir(exist_ok=True)
        dest=Path(shutil.move(str(dest),str(quarantine/source.name)))
    (dest/'metadata.json').write_text(json.dumps(meta,indent=2))
    (dest/'meta.yaml').write_text(yaml.safe_dump(meta,sort_keys=False))
    return meta
