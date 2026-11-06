"""Strict, explicit configuration; no implicit model or credential choices."""
from __future__ import annotations
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

_PROVIDER = {"type":"object","additionalProperties":False,"required":["base_url","api_key_env","model","max_output_tokens"],"properties":{"transport":{"type":"string","enum":["openai","codex","codex_host"]},"executable":{"type":"string","minLength":1},"timeout_sec":{"type":"integer","minimum":1},"base_url":{"type":"string","format":"uri"},"api_key_env":{"type":"string","minLength":1},"model":{"type":"string","minLength":1},"max_output_tokens":{"type":"integer","minimum":1}}}
_PROVIDER["properties"]["max_input_utf8_bytes"]={"type":"integer","minimum":1}
_PROVIDER["properties"].update({"context_limit_tokens":{"type":"integer","minimum":1},"message_framing_reserve_tokens":{"type":"integer","minimum":0},"capacity_tokenizer":{"type":"object","additionalProperties":False,"required":["path","sha256","model"],"properties":{k:{"type":"string","minLength":1} for k in ("path","sha256","model")}}})
_SCHEMA={"type":"object","additionalProperties":False,"required":["llm","budget","embedding","retrieval","review","compile","validators"],"properties":{
 "llm":{"type":"object","additionalProperties":False,"required":["gpt","sonnet","retry","temperature_extract","temperature_write"],"properties":{"gpt":_PROVIDER,"sonnet":_PROVIDER,"retry":{"type":"integer","minimum":0},"temperature_extract":{"type":"number","minimum":0,"maximum":2},"temperature_write":{"type":"number","minimum":0,"maximum":2}}},
 "budget":{"type":"object","additionalProperties":False,"required":["max_calls_per_task","max_calls_extract_total"],"properties":{"max_calls_per_task":{"type":"integer","minimum":1,"maximum":4},"max_calls_extract_total":{"type":"integer","minimum":1,"maximum":400}}},
 "embedding":{"type":"object","additionalProperties":False,"required":["model_name","device"],"properties":{"model_name":{"type":"string","minLength":1},"device":{"type":"string","enum":["cpu"]}}},
 "retrieval":{"type":"object","additionalProperties":False,"required":["max_evidence_units","max_lexicon_entries","max_pattern_entries","max_feedback_entries"],"properties":{k:{"type":"integer","minimum":0} for k in ("max_evidence_units","max_lexicon_entries","max_pattern_entries","max_feedback_entries")}},
 "review":{"type":"object","additionalProperties":False,"required":["escalation_claim_words"],"properties":{"escalation_claim_words":{"type":"array","items":{"type":"string","minLength":1}}}},
 "compile":{"type":"object","additionalProperties":False,"required":["cmd","timeout_sec"],"properties":{"cmd":{"type":"array","minItems":1,"items":{"type":"string"}},"timeout_sec":{"type":"integer","minimum":1}}},
 "validators":{"type":"object","additionalProperties":False,"required":["max_unsourced_changes","max_diff_ratio"],"properties":{"max_unsourced_changes":{"type":"integer","minimum":0},"max_diff_ratio":{"type":"number","minimum":0,"maximum":1}}}
}}

_SCHEMA["properties"]["retrieval"]["properties"]["max_structure_packet_chars"]={"type":"integer","minimum":1}

def load_config(path: str|Path) -> dict:
    config=yaml.safe_load(Path(path).read_text(encoding="utf8"))
    Draft202012Validator(_SCHEMA).validate(config)
    return config

def schema() -> dict:
    return json.loads(json.dumps(_SCHEMA))
