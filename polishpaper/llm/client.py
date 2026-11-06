"""OpenAI-compatible chat calls. Each retry consumes a ledger reservation."""
from __future__ import annotations
import json, os, time
from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError, InternalServerError
from .ledger import Ledger

class ModelNotConfigured(RuntimeError): pass

class LLMClient:
    def __init__(self,config:dict,ledger:Ledger,transport=None):
        self.config=config;self.ledger=ledger;self.transport=transport;self.last_response_metadata={}
    def complete(self,*,provider:str,messages:list[dict],task_id:str,purpose:str,extract:bool=False,response_format:dict|None=None,require_input_budget:bool=False,require_verified_capacity:bool=False)->str:
        cfg=self.config["llm"][provider]
        if cfg["model"].startswith("REPLACE_"): raise ModelNotConfigured(f"Configure llm.{provider}.model")
        from .capacity_guard import check_capacity
        self.last_input_preflight=check_capacity(cfg,messages,required=require_verified_capacity)
        max_bytes=cfg.get('max_input_utf8_bytes')
        measured=len(json.dumps(messages,ensure_ascii=False,separators=(',',':')).encode())
        if max_bytes is not None and measured>max_bytes:
            raise ValueError(f'Input exceeds explicitly configured byte budget before reservation ({measured}>{max_bytes}); provider token capacity remains separately unverified')
        if require_input_budget and max_bytes is None:
            raise ValueError('Handbook profile requires an explicit pre-reservation max_input_utf8_bytes budget; it is not a token-capacity guarantee')
        host=cfg.get("transport","openai")=="codex_host" and self.transport is None
        native=cfg.get("transport","openai")=="codex" and self.transport is None
        if native and provider!="gpt":raise ModelNotConfigured("codex transport is supported only for the explicit GPT role")
        key=os.environ.get(cfg["api_key_env"])
        if not key and self.transport is None and not native and not host: raise ModelNotConfigured(f"Set {cfg['api_key_env']}")
        scope="extract" if extract else "task"
        ledger_task="global" if extract else task_id
        cap=self.config["budget"]["max_calls_extract_total" if extract else "max_calls_per_task"]
        if host:
            if provider!="gpt":raise ModelNotConfigured("codex_host transport is only for the explicit GPT role")
            from .host_bridge import request as host_request
            raw=host_request(self.ledger,{"provider":provider,"model":cfg["model"],"messages":messages,"task_id":task_id,"purpose":purpose,"extract":extract,"response_format":response_format,"max_output_tokens":cfg["max_output_tokens"]},scope,ledger_task,cap)
            self.last_response_metadata={"transport":"codex_host","requested_model":cfg["model"],"returned_model":None,"model_identity_basis":"operator-supplied actual host dispatch receipt; see host request audit","finish_reason":"host_response_imported","usage":None}
            return raw
        error=None
        for attempt in range(1 if native else self.config["llm"]["retry"]+1):
            call_id=self.ledger.reserve(scope=scope,task_id=ledger_task,provider=provider,purpose=purpose,cap=cap,model=cfg["model"])
            try:
                request=dict(model=cfg["model"],messages=messages)
                if provider=="gpt" and cfg["model"]=="gpt-6.1-sol":
                    request["max_completion_tokens"]=cfg["max_output_tokens"]
                else:
                    request.update(temperature=self.config["llm"]["temperature_extract" if extract else "temperature_write"],max_tokens=cfg["max_output_tokens"])
                if response_format is not None: request["response_format"]=response_format
                if native:
                    from .codex_transport import complete as codex_complete
                    result=codex_complete(cfg,messages,self.ledger.path.parent/"native_calls",call_id,task_id,purpose)
                elif self.transport is not None:
                    result=self.transport(provider,request)
                else:
                    result=OpenAI(api_key=key,base_url=cfg["base_url"],max_retries=0,timeout=90).chat.completions.create(**request)
                content=result if isinstance(result,str) else result.choices[0].message.content
                if not isinstance(content,str) or not content.strip(): raise ValueError("empty model response")
                usage=getattr(result,"usage",None) if not isinstance(result,str) else None
                self.last_response_metadata={"call_id":call_id,"requested_model":cfg["model"],"returned_model":getattr(result,"model",None),"finish_reason":getattr(result.choices[0],"finish_reason",None) if not isinstance(result,str) else None,"usage":usage.model_dump() if hasattr(usage,"model_dump") else {"input_tokens":getattr(usage,"prompt_tokens",None),"output_tokens":getattr(usage,"completion_tokens",None)}}
                self.ledger.finish(call_id,"completed",input_tokens=getattr(usage,"prompt_tokens",None),output_tokens=getattr(usage,"completion_tokens",None));return content
            except Exception as exc:
                error=exc;self.ledger.finish(call_id,"failed",type(exc).__name__)
                if not isinstance(exc,(APIConnectionError,APITimeoutError,RateLimitError,InternalServerError)) or attempt >= self.config["llm"]["retry"]: raise
                time.sleep(min(2**attempt,4))
        raise error
    def json(self,**kwargs):
        raw=self.complete(**kwargs,response_format={"type":"json_object"})
        return json.loads(raw)
