# Source-family holdouts for writing evaluations

Ordinary tasks retain their existing retrieval behavior. An evaluation task can
opt in when it is created:

```sh
polishpaper task new --tex /path/main.tex --bib /path/main.bbl \
  --request /path/request.md --evaluation-exclusions /path/holdout.json
```

`--bib` accepts the actual `.bib` or original `.bbl`; keys are read from real
BibTeX entries or `\bibitem` records. No replacement bibliography is invented.

The holdout manifest has this format (use actual absolute paths and hashes):

```json
{
  "schema": "evaluation-exclusions-1",
  "paper_ids": ["arxiv_2602.05591v1"],
  "aliases": {
    "arxiv_2205.14202": "arxiv_2602.05591",
    "ho2022phi": "arxiv_2205.14202",
    "yu2023wasserstein": "independently_identified_DRMDP_family"
  },
  "source_bindings": [
    {"path": "/absolute/original.tex", "sha256": "actual SHA256", "paper_id": "arxiv_2602.05591v1"}
  ]
}
```

The example declares the 2205 conference paper and 2602 extension as one family.
Aliases are explicit experimental judgments, not title-similarity guesses.
ArXiv version suffixes are removed. The notation catalog's source aliases must
be assigned to their true paper families; when the DRMDP paper is the target,
`yu2023wasserstein` must map to that excluded family. An alias self-mapping can
identify a separate known family. Each declared original source is hash-checked.

An optional `independent_source_bindings` list has the same `path`, `sha256`,
`paper_id` fields. It allows an exact, independently identified original when a
record lacks a paper ID. An arbitrary extraction/manifest file hash does not
prove independent origin. Unknown origins are withheld from evaluation evidence.

The task copies this manifest into its frozen inputs, and the taskcard binds its
exact path/hash. Retrieval excludes targets before top K and relaxes concept
matching only within the original section/kind rules. Structure exclusion happens
before candidate selection; other lanes filter before their limits. Mixed-source
phrases, schemas, patterns and notation entries are withheld whole: their original
frequency, source list and human-review scope are never rewritten.

The evidence artifact records an audit for schema, lexicon, patterns, structure,
units, feedback, user guidance, scientific questions and notation. Audit rows
contain IDs/hashes and reasons, not rejected source text. Writer and reviewer
packets are checked again before dispatch. Original target manuscript context,
annotations, request and explicit user notation rules remain available in both
variants. This mechanism establishes source separation, not writing quality or
human acceptance.

Baseline compilation saves its actual result and source/log bindings in
`baseline_report.json`. A missing legacy report is unknown, never inferred from
a log. Use `polishpaper task baseline-check TASK_ID` to obtain a real check;
old reports/logs are preserved. Failed baselines cannot start writing. Existing
build artifacts are preserved outside the workspace's frozen input set, while
figure PDFs and explicit or non-reproducible `.bbl` inputs remain frozen. For a
supplied bbl-only bibliography, latexmk's bibliography regeneration is disabled;
the actual command is recorded with the build result.
