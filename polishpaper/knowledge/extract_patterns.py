from .extract_lexicon import _extract

def extract(client,paper_id,section_type,units,raw_dir):return _extract(client,"patterns","gpt",paper_id,section_type,units,raw_dir)
