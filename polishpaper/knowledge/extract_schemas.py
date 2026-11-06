from .extract_lexicon import _extract

def extract(client,paper_id,section_type,units,raw_dir):return _extract(client,"schemas","sonnet",paper_id,section_type,units,raw_dir)
