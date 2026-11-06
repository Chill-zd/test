"""Real baseline compile results bound to the frozen source and actual log."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,uuid,shutil

def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def status(task):
    task=Path(task);path=task/'baseline_report.json'
    if not path.is_file():return {'status':'unknown','pass':False,'message':'缺少真实基线编译报告；请先检查基线，不能从日志猜测通过。'}
    try:
        report=json.loads(path.read_text())
        if report.get('schema')!='task-baseline-build-1':raise ValueError('未知基线报告格式')
        if _sha(task/'source_manifest.json')!=report['source_manifest_sha256'] or _sha(task/'baseline_build.log')!=report['log_sha256']:
            raise ValueError('基线日志或来源清单发生变化')
        passed=report.get('pass') is True and report.get('returncode')==0 and report.get('timeout') is False
        return {**report,'status':'passed' if passed else 'failed','pass':passed,
            'message':'真实基线编译通过。' if passed else '基线编译未通过；请先处理编译问题。'}
    except (ValueError,KeyError,OSError,TypeError) as exc:return {'status':'invalid','pass':False,'message':'基线报告不可用：'+str(exc)}

def preserve_previous(task):
    task=Path(task);home=task/'baseline_history'/uuid.uuid4().hex;home.mkdir(parents=True)
    for name in ('baseline_report.json','baseline_build.log'):
        if (task/name).is_file():shutil.copy2(task/name,home/name)
    return home

def record(task,result):
    task=Path(task);value={**result,'schema':'task-baseline-build-1','compiled_task_id':task.name,
        'recorded_at':datetime.now(timezone.utc).isoformat(),'log_sha256':_sha(task/'baseline_build.log'),
        'source_manifest_sha256':_sha(task/'source_manifest.json')}
    home=task/'baseline_history'/uuid.uuid4().hex;home.mkdir(parents=True)
    shutil.copy2(task/'baseline_build.log',home/'baseline_build.log')
    with (home/'baseline_report.json').open('x') as handle:json.dump(value,handle,ensure_ascii=False,indent=2)
    (task/'baseline_report.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return value
