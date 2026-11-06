"""Explicit configured capacity preflight; no undocumented provider capacities."""
import hashlib,json
from pathlib import Path

class CapacityExceeded(ValueError):pass
class CapacityUnverified(ValueError):pass

def check_capacity(cfg,messages,*,required=False):
    limit=cfg.get('context_limit_tokens')
    if limit is None:
        if required:
            raise CapacityUnverified('Complete-input dispatch blocked before reservation: configure the actual exact-model worker context_limit_tokens, a hash-bound matching capacity_tokenizer and explicit message_framing_reserve_tokens; a byte budget or advertised model maximum does not establish worker capacity')
        return {'status':'unknown_capacity_not_configured'}
    spec=cfg.get('capacity_tokenizer')
    if not isinstance(limit,int) or limit<=0 or not spec:
        raise CapacityUnverified('Explicit positive context limit and matching offline tokenizer required before reservation')
    if spec.get('model')!=cfg['model']:
        raise CapacityUnverified('Configured tokenizer model differs from provider model')
    path=Path(spec['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:
        raise CapacityUnverified('Configured capacity tokenizer hash changed')
    # Tokenizer identity, context limit and framing reserve are explicitly
    # operator configured; code cannot certify the actual host allocation.
    try:
        from tokenizers import Tokenizer
    except ImportError as exc:
        raise CapacityUnverified('Required offline tokenizers runtime unavailable; dispatch blocked before reservation') from exc
    tokenizer=Tokenizer.from_file(str(path));tokenizer.no_truncation();tokenizer.no_padding()
    count=sum(len(tokenizer.encode(m['content'],add_special_tokens=False).ids) for m in messages)
    framing=cfg.get('message_framing_reserve_tokens')
    if not isinstance(framing,int) or framing<0:raise CapacityUnverified('Explicit framing reserve required')
    output=cfg['max_output_tokens'];total=count+framing+output
    audit={'status':'configured_tokenizer_count','input_tokens':count,'framing_reserve':framing,'output_reserve':output,'context_limit':limit,'tokenizer_sha256':spec['sha256'],'model':spec['model']}
    if total>limit:raise CapacityExceeded('Input plus explicit framing/output reserve exceeds configured capacity: '+json.dumps(audit))
    return audit
