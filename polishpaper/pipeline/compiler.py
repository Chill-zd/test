"""Hash-checked contiguous physical patches and forced fresh LaTeX builds."""
from __future__ import annotations
import hashlib,subprocess,shutil,re
from pathlib import Path

def run_build(directory,main,config,log_path):
    cmd=list(config['compile']['cmd'])
    from .task_sources import generated_paths
    bbl=str(Path(main).with_suffix('.bbl'))
    if Path(cmd[0]).name=='latexmk' and (Path(directory)/bbl).is_file() and bbl not in generated_paths(directory,main) and not any(arg.startswith('-bibtex') for arg in cmd):
        cmd.append('-bibtex-') # A supplied bbl-only bibliography is an immutable input.
    if '-g' not in cmd:cmd.append('-g')
    cmd.append(Path(main).name)
    try:
        proc=subprocess.run(cmd,cwd=Path(directory)/Path(main).parent,capture_output=True,text=True,timeout=config['compile']['timeout_sec'])
        log=proc.stdout+proc.stderr;code=proc.returncode;timeout=False
    except subprocess.TimeoutExpired as exc:
        def decode(x):return x.decode(errors='replace') if isinstance(x,bytes) else x or ''
        log=decode(exc.stdout)+decode(exc.stderr)+'\nBUILD TIMEOUT\n';code=None;timeout=True
    except OSError as exc:
        log=type(exc).__name__+': '+str(exc);code=None;timeout=False
    Path(log_path).write_text(log)
    return {'pass':code==0,'returncode':code,'timeout':timeout,'log':str(log_path),'command':cmd}

def target_span(workspace,targets):
    if not targets or len({u['file'] for u in targets})!=1:raise ValueError('targets must occupy one physical file')
    ordered=sorted(targets,key=lambda u:u['offset_start'])
    if targets!=ordered:raise ValueError('targets must be in physical source order')
    rel=Path(ordered[0]['file']);root=Path(workspace).resolve();src=(root/rel).resolve()
    if not src.is_relative_to(root):raise ValueError('target escapes workspace')
    content=src.open(encoding="utf8",newline="").read()
    for i,u in enumerate(ordered):
        a,b=u['offset_start'],u['offset_end']
        if not 0<=a<b<=len(content) or hashlib.sha256(content[a:b].encode()).hexdigest()!=u['sha256']:raise ValueError('source target changed')
        if i and (a<ordered[i-1]['offset_end'] or content[ordered[i-1]['offset_end']:a].strip()):raise ValueError('targets are not contiguous; intervening source must remain untouched')
    return rel,content,ordered[0]['offset_start'],ordered[-1]['offset_end']

def compile_candidate(task_dir,card,draft,config):
    task=Path(task_dir);workspace=task/'workspace';patched=task/'patched'
    rel,content,a,b=target_span(workspace,card['target_units'])
    if patched.exists():shutil.rmtree(patched)
    shutil.copytree(workspace,patched)
    replacement=draft['revised_tex']
    if '\r\n' in content:replacement=replacement.replace('\r\n','\n').replace('\n','\r\n')
    with (patched/rel).open('w',encoding='utf8',newline='') as stream:stream.write(content[:a]+replacement+content[b:])
    report=run_build(patched,(task/'main.txt').read_text().strip(),config,patched/'build.log')
    log=(patched/'build.log').read_text();baseline=(task/'baseline_build.log').read_text()
    final_log=(patched/(task/'main.txt').read_text().strip()).with_suffix('.log')
    if final_log.exists():log=final_log.read_text(errors='replace')
    def warnings(s):return set(re.findall(r'(?:LaTeX|Package [^\n]+) Warning:[^\n]*(?:\n(?!\n)[^\n]*)?',s))
    new=warnings(log)-warnings(baseline)
    relevant=[w for w in new if any(x in w.lower() for x in ('undefined','multiply defined'))]
    report.update({'pass':report['pass'] and not relevant,'new_warnings':sorted(new),'relevant_warnings':sorted(relevant)})
    return report
