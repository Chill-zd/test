#!/usr/bin/env python3
"""Prepare human review from a JSON list of explicit original analysis paths.

No model calls, activation, installation or human approval. Relative paths resolve
against the selection JSON. Missing analyses require an explicit section_id.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from polishpaper.structure.prepare_review import prepare_review


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phrase-audit',type=Path)
    parser.add_argument('--inventory',type=Path,action='append',default=[],help='Additional corpus inventory for honest full-corpus coverage')
    parser.add_argument('--target-author',default='Wolfram Wiesemann')
    args=parser.parse_args();selection=args.selection.resolve()
    entries=json.loads(selection.read_text())
    for entry in entries:
        for key in ('analysis_path','inventory_path'):entry[key]=str((selection.parent/entry[key]).resolve())
        if entry.get('atomic_sidecar_paths'):entry['atomic_sidecar_paths']=[str((selection.parent/p).resolve()) for p in entry['atomic_sidecar_paths']]
    print(json.dumps(prepare_review(entries,args.output,args.target_author,args.phrase_audit,args.inventory),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
