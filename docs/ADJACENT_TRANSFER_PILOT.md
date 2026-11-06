# Optional adjacent-sentence evidence pilot

This is an experimental source-bound delivery path, not an admitted writing rule, training result, or demonstrated improvement. Frozen 0.4.6 and historical comparisons are unchanged.

The normal independent pipeline `pipeline.evidence.gather` calls `knowledge.adjacent_transfers.select` only when the current taskcard explicitly sets `adjacent_transfer_pilot: true`. An explicit `adjacent_transfer_ids` list selects cards; without named IDs the selector delivers none. New tasks can use `task new --adjacent-transfer-pilot --adjacent-transfer-id adjacent-12` (repeat the ID flag as needed), without editing frozen taskcards. The catalog must be at the selected knowledge directory's `adjacent_transfers.json`. No production catalog is installed by this change. Current candidate cards live under `data/evaluation/transition_pilot_20261105/`.

For a reproducible handoff, prepare two separate new task directories from identical original bytes, target locator, neighbors, macro and citation context, request, exclusions, knowledge inputs and configuration. Leave the pilot field absent in the control; set it to true in the experimental task. Do not reuse an existing cached evidence file: normal CLI caching does not turn an old evidence artifact into a new intervention. Bind evaluation exclusions on both taskcards. The selector withholds all cards without exclusions and checks both the quoted source and generator-input lineage. Preserve the exact taskcards, evidence, resulting writer messages and hashes before dispatch. Use normal non-handbook writing for this delivery comparison. The bare CLI branch constructs its own evidence and bypasses gather, so it cannot read this catalog.

Writer and reviewer receive complete selected items through the ordinary evidence item/catalogue path, including physical adjacent sentences, complete source examples, provenance, conditions and pending semantic status. A delivered item can be cited as `adjacent_transfer:<id>`. Selection does not establish contextual applicability. The source interpretation remains pending; explicit opt-in is permission for exploratory delivery, not semantic admission. Scientific claims and conditions come from the target manuscript only. Existing source-review/admission rules continue to apply; no new blanket approval requirement is introduced.

Freshness checks revalidate the catalog hash and each selected source pair/generator binding. Full-pair physical validation, lineage exclusions, optional omission and on/off non-pilot equality are covered by offline tests. Those tests establish delivery mechanics only. Actual fresh Sol calls, independent ratings, authentic user-target applicability, compile acceptance and writing improvement must be reported separately. Public-text coordinator requests are exploratory and do not substitute for an authentic user-manuscript comparison.

Run offline checks with `.venv/bin/python -m pytest tests/test_adjacent_pipeline.py tests/test_adjacent_transfers.py -q` from the project directory.

## Choosing evidence for the next paper

Use the isolated profile to inspect the menu before creating a task:

```
POLISHPAPER_HOME=/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/profiles/adjacent_pilot /Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/.venv/bin/polishpaper adjacent-menu
```

The menu displays six cards with Chinese reader tasks, omission conditions and exact source previews. An optional `--section conclusion` filter is a convenience, not evidence of contextual fit. Choose by the paragraph's concrete question and required sentence relationship, then pass the displayed ID with `--adjacent-transfer-id`. There is no automatic section-based selection. Supply `--evaluation-exclusions FILE` once at task creation with the target paper's identity/family and relevant family aliases; creation validates and copies this manifest, and locate binds the copy. The CLI rejects pilot creation without IDs or exclusions. Unrelated default tasks do not acquire new evidence fields or consult the catalog.

The normal writer receives a compact projection only for selected adjacent cards: exact pair, reader task, relationship, omission/transfer conditions, pending semantic status, evidence ID, source unit locator and complete-item hash. Full route dictionaries, physical paths and catalog bindings stay in the saved complete evidence and reviewer/audit; the full selected item is not duplicated in the writer prompt. No literal source wording or applicability condition is shortened by this projection. Completed exploratory dispatches are preserved unchanged.

Observed normal-pipeline delivery proof uses isolated task `5f302b8de995` (real public 2602.11387 source): task creation compiled the untouched source, exact locate selected the conclusion, evidence selected adjacent-12 with independent candidate/generator-family checks, and a recording-only client captured the ordinary writer boundary without a model call. The captured pre-projection boundary remains historical; newly generated requests use the compact projection. These are delivery checks, not an additional effectiveness experiment or M8 completion.
