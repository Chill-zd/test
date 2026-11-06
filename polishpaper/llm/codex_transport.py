"""Explicit native Codex invocation transport using normal logged-in auth.

The ledger measures CLI invocations. Internal provider network attempts cannot be
observed reliably and are never represented as an exact network-request cap.
"""
from __future__ import annotations
import json,subprocess,tempfile,shutil
from pathlib import Path
from types import SimpleNamespace

class CodexTransportError(RuntimeError):pass

DISABLED_FEATURES=('shell_tool','apps','plugins','multi_agent','multi_agent_v2','browser_use','computer_use','in_app_browser','image_generation','view_image','memories','hooks','skill_search','workspace_dependencies','code_mode_host','tool_suggest')


def command(executable,model,work,instructions,schema,last):
    args=[executable,'exec','--ignore-user-config','--ignore-rules','--ephemeral','--skip-git-repo-check','--strict-config','--json','--color','never','--model',model,'-C',str(work),'-s','read-only','--output-schema',str(schema),'-o',str(last)]
    for feature in DISABLED_FEATURES:args+=['--disable',feature]
    for value in ['web_search="disabled"','project_doc_max_bytes=0','agents.enabled=false','model_instructions_file='+json.dumps(str(instructions))]:args+=['-c',value]
    return args+['-']


def complete(cfg,messages,audit_dir,call_id,task_id,purpose,runner=subprocess.run):
    executable=shutil.which(cfg.get('executable','codex'))
    if not executable:raise CodexTransportError('Configured codex executable is unavailable')
    directory=Path(audit_dir);directory.mkdir(parents=True,exist_ok=True);stem=directory/str(call_id)
    audit={'transport':'codex','accounting_unit':'cli_invocations','network_attempt_count':'unobservable','call_id':call_id,'task_id':task_id,'purpose':purpose,'requested_model':cfg['model'],'status':'reserved','messages':messages,'outer_retries':0,'internal_retry_control':'unavailable for reserved built-in provider; internal attempts unobservable','configured_output_token_hint':cfg['max_output_tokens'],'output_token_limit_enforced':False}
    def save():stem.with_suffix('.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    save()
    try:
        version=runner([executable,'--version'],capture_output=True,text=True,timeout=15);audit['codex_version']=version.stdout.strip()
        with tempfile.TemporaryDirectory(prefix='polishpaper-codex-') as temp:
            work=Path(temp);instructions=work/'instructions.txt';schema=work/'response.schema.json';last=work/'last.json'
            instructions.write_text('Execute only the supplied conversation as a text transformation. Never call tools or inspect files, projects, memory or external sources. Preserve the supplied system/user roles. Return the requested final JSON serialized as the json_response string in the output wrapper. Do not add commentary. Keep the inner JSON within the requested output-token hint.\n')
            schema.write_text(json.dumps({'type':'object','properties':{'json_response':{'type':'string'}},'required':['json_response'],'additionalProperties':False}))
            args=command(executable,cfg['model'],work,instructions,schema,last);audit['command']=args;save()
            prompt=json.dumps({'conversation':messages,'requested_output_token_hint':cfg['max_output_tokens'],'output_wrapper':{'json_response':'Serialize the exact requested JSON response as a string here.'}},ensure_ascii=False)
            try:
                process=runner(args,input=prompt,capture_output=True,text=True,timeout=cfg.get('timeout_sec',180))
                stdout,stderr=process.stdout,process.stderr;returncode=process.returncode
            except subprocess.TimeoutExpired as exc:
                decode=lambda value:value.decode(errors='replace') if isinstance(value,bytes) else value or ''
                stdout,stderr=decode(exc.stdout),decode(exc.stderr);stem.with_suffix('.events.jsonl').write_text(stdout);stem.with_suffix('.stderr.log').write_text(stderr)
                audit.update(status='timeout_unknown',timeout_sec=cfg.get('timeout_sec',180));save();raise CodexTransportError('Native invocation timed out; do not automatically resend') from None
            stem.with_suffix('.events.jsonl').write_text(stdout);stem.with_suffix('.stderr.log').write_text(stderr)
            events=[]
            for line in stdout.splitlines():
                try:events.append(json.loads(line))
                except json.JSONDecodeError:raise CodexTransportError('Native event stream contains malformed JSON') from None
            tool_items=[event.get('item',{}) for event in events if event.get('type') in ('item.started','item.completed') and event.get('item',{}).get('type') not in ('agent_message','reasoning','error')]
            completed_turns=sum(event.get('type')=='turn.completed' for event in events)
            observed_models=sorted({event['model'] for event in events if isinstance(event.get('model'),str)})
            audit.update(completed_turns=completed_turns,observed_models=observed_models,model_identity_basis='observed event field' if observed_models else 'explicit CLI requested model only')
            usage=next((event.get('usage',{}) for event in reversed(events) if event.get('type')=='turn.completed'),{})
            audit.update(error_events=[e for e in events if e.get('type') in ('error','turn.failed') or e.get('item',{}).get('type')=='error'],returncode=returncode,tool_activity=tool_items,usage=usage,events_file=str(stem.with_suffix('.events.jsonl')))
            if returncode:raise CodexTransportError('Native invocation failed; inspect retained audit')
            if tool_items:raise CodexTransportError('Unexpected native tool activity; candidate rejected')
            if completed_turns!=1:raise CodexTransportError('Native invocation must contain exactly one completed turn')
            if not last.exists():raise CodexTransportError('Native invocation produced no final output')
            wrapper=last.read_text();audit['raw_final_response']=wrapper
            parsed=json.loads(wrapper)
            if not isinstance(parsed,dict) or set(parsed)!={'json_response'} or not isinstance(parsed['json_response'],str):raise CodexTransportError('Invalid native response wrapper')
            # Validate strict inner JSON now; the normal writer/reviewer contract follows.
            json.loads(parsed['json_response']);audit.update(status='completed',raw_response=parsed['json_response']);save()
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=parsed['json_response']))],usage=SimpleNamespace(prompt_tokens=usage.get('input_tokens'),completion_tokens=usage.get('output_tokens')))
    except Exception as exc:
        if audit['status'] not in ('timeout_unknown','completed'):audit.update(status='failed',error_type=type(exc).__name__);save()
        raise
