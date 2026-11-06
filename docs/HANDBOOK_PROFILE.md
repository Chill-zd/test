# Language-only handbook profile

For a newly scoped language task, use the ordinary CLI:

For the current user's handbook work, use the dedicated production handbook home below. Its GPT request policy is the tested **85,000 bytes**; Sonnet remains 120,000. This does not lower the main project's provider/extraction policies. Its data path links to the authoritative live project data, so later papers, feedback, knowledge and index updates remain visible. The frozen comparison home is evidence only. It is not a universal token-capacity guarantee.

```sh
export POLISHPAPER_HOME="/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/profiles/handbook"
PP="/Users/yuzhuodong/Documents/ChatGPT/wolfram/polishpaper/.venv/bin/polishpaper"
"$PP" task new --tex /absolute/main.tex --bib /absolute/refs.bib \
  --request /absolute/request.txt --target-quote /absolute/target.txt --kind revise
"$PP" task run TASK_ID --handbook
"$PP" task run TASK_ID --handbook --bare
```

The production home is for new ordinary tasks and shares the authoritative live task/ledger paths. The frozen comparison remains in its separate evaluation home and is not the destination for future work. Each new task retains its source bindings and four-call cap; no old ledger is reset. The main-project default 120,000-byte policy was not the successful _01 writer configuration.


`--target-quote` is a separate, frozen locator channel. It is not an advisor annotation. It must identify one complete physical source unit exactly, after whitespace normalization. Ambiguous quotes fail without fuzzy search or a model call. The profile creates a separate task variant; it does not overwrite the original task or reset its call ledger.

This profile freezes mathematical expressions, citation keys, label identities, technical assertions and comparative meaning. Existing `\citep`/`\bm` conventions may be applied only with the same keys and symbols. The writer can retain the original unchanged. Scientific changes require a separately authorized scope. Mechanical checks protect math, citation/reference identities and comparison terms; the independent reviewer assesses prose fidelity and new scientific facts. These checks do not prove mathematical truth or semantic equivalence.

The model receives the exact target and immediate neighbors, the selected approved source-specific schema, allowed lexical/pattern/feedback evidence and selected complete handbook examples. Direct labeled equation/theorem envelopes and their immediate explanatory joins are included when available. Whole-section reference identities and same-glyph definition candidates are local lookup information; their uninspected content is not delivered scientific authority. Unknown or multiple candidates remain explicit scientific questions and cannot justify changing the corresponding assertion. Inherited uncertainty alone is not a language defect.

Legacy organization observations and whole-manuscript notation delivery remain in an untouched, hash-bound full source audit. They are explicitly omitted from the language profile. This mode is **not legacy complete full**. Mechanical fields and deep retrieval diagnostics are archived with a reversible proof; selected prose, conditions and evidence are not clipped. Exact-value sharing removes duplication.

Selected schema IDs are addressable evidence: the writer receives the exact allowed ID catalog, while internal source/unit/backpointer IDs remain provenance. A schema descriptor points once to the complete selected schema. The reviewer receives original support when that schema is actually cited. Existing receipts are not rewritten, and arbitrary `schema:` strings are not accepted.

The production handbook home uses GPT 85,000 / Sonnet 120,000 UTF-8-byte request policies, **not a provider token-capacity guarantee**. It is checked before a ledger reservation. Retrieval counts are maxima, not mandatory quotas. If needed, whole lowest-ranked automatic illustration, lexical and pattern records are omitted before handbook exemplars, with explicit IDs/reasons. Required IDs/papers, requested notation, annotations, the approved schema, target/neighbors and scientific cautions remain. External notation preferences have no operative role for frozen existing math unless explicitly requested; their full catalog remains in the immutable local audit. No source item is clipped. An oversized required packet fails before dispatch; no strings are silently shortened. If an operator configures a context-token limit, a matching explicitly declared offline tokenizer and framing/output reserve are also required. No host allocation or tokenizer identity is guessed.

Recording-transport smoke runs exercised the real ordinary command, validators and LaTeX build for both handbook and bare variants. They establish transport/build behavior. A separately declared ordinary task subsequently completed actual Sol writing, Sonnet review and real compilation in both handbook and bare modes; their academic outputs are identical. This is not evidence of a handbook advantage or universal capacity fit. The legacy complete-full capacity failure remains, and formal M8 is unestablished. See the current-status page for the bound records.

The production home is `profiles/handbook/`: its config applies the tested task policy, while `data` is a symlink to the main project’s authoritative live data. Run source ingestion, extraction and index maintenance from the main project; both homes then see the same updates. The evaluation trial remains frozen evidence and is not reused as a future task home.
