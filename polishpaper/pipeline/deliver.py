from __future__ import annotations
import difflib,json
from pathlib import Path

def deliver(task_dir,card,draft,validation,review,compile_report,ledger_rows,evidence):
    task=Path(task_dir);out=task/"deliver";out.mkdir(exist_ok=True)
    if not validation["pass"] or review.get("verdict")!="pass" or not compile_report["pass"]:raise ValueError("candidate not approved for deliver")
    u=card["target_units"][0];src=(task/"workspace"/u["file"]).open(newline="").read();dst=(task/"patched"/u["file"]).open(newline="").read()
    patch="".join(difflib.unified_diff(src.splitlines(keepends=True),dst.splitlines(keepends=True),fromfile="a/"+u["file"],tofile="b/"+u["file"]))
    (out/"changes.patch").write_text(patch)
    lines=["| Change | Original | New | Reason | Basis |","|---|---|---|---|---|"]
    evidence_map={x["evidence_id"]:x for x in evidence["items"]}
    for c in draft["changes"]:
        esc=lambda s:str(s).replace("|","\\|").replace("\n"," ")
        lines.append("| "+" | ".join(map(esc,[c["change_id"],c["original_sentence"],c["revised_sentence"],c["reason"],"; ".join(s+" ["+evidence_map[s]["source_tag"]+"] "+json.dumps(evidence_map[s].get("provenance",{}),ensure_ascii=False) for s in c["sources"])]))+" |")
    (out/"changes.md").write_text("\n".join(lines)+"\n")
    questions=list(draft.get("science_questions",[]))+list(review.get("science_questions",[]))
    (out/"questions.md").write_text("Scientific questions (separate from language acceptance)\n\n"+("\n".join("- "+str(q) for q in questions) if questions else "No scientific question was supplied.")+"\n")
    report={"build":compile_report,"review":review,"validation":validation,"calls":len(ledger_rows),"mode":evidence["mode"],"schema_status":evidence["schema_status"]}
    (out/"report.md").write_text("# Polish report\n\n"+"\n".join(f"- {k}: {v}" for k,v in report.items())+"\n")
    decisions=task/"decisions.yaml"
    if not decisions.exists():
        import yaml
        decisions.write_text(yaml.safe_dump({c["change_id"]:{"decision":None,"note":""} for c in draft["changes"]},sort_keys=False))
    return report


def retain_candidate(task_dir,draft,validation,review,evidence,build=None):
    task=Path(task_dir);out=task/'deliver';out.mkdir(exist_ok=True)
    (out/'changes.patch').unlink(missing_ok=True)
    (out/'candidate.tex').write_text(draft.get('revised_tex',''))
    questions=list(draft.get('science_questions',[]))+list(review.get('science_questions',[]))
    (out/'questions.md').write_text('Scientific questions (separate from language findings)\n\n'+('\n'.join('- '+str(q) for q in questions) if questions else 'No scientific question was supplied. See the validation/review findings.')+'\n')
    (out/'report.md').write_text('Candidate requires review; no apply-ready patch.\n\n'+json.dumps({'validation':validation,'review':review,'build':build,'mode':evidence['mode']},ensure_ascii=False,indent=2)+'\n')
