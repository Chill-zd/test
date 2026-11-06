# Optional source-bound writing routes

Normal writing reads `data/knowledge/writing_routes.json` when present. Bare writing bypasses the catalog. The catalog is a runtime artifact; private source files and consultation requests remain outside plugin archives.

Routes are alternatives within a section, including internal paragraph functions. The writer checks purpose, prior reader knowledge, neighboring referents, old-to-new information, and the next handoff. It can retain the passage or omit every alternative. Evidence retrieval budgets do not establish phrase quotas, mandatory paragraph sequences, or scientific authority.

Each route separates literal source phrases from authored adaptations and carries complete selected source paragraphs. Physical source-file hashes, raw offsets and line bounds, actual Chin Pang Ho byline spans, source identities, literal anchors, and catalog/request/source-pool hashes are checked before delivery. Byline private details, comments, and unrelated raw neighboring blocks are withheld from prompts. Comment-free projections retain raw physical bindings for audit.

`generator_provenance` (or `basis.consultation`) binds the actual consultation request and its complete input paper IDs. Titles in requests are resolved against a separately bound source pool. Held-out evaluation excludes every generator input family, including version aliases, before delivering either evidence or a compact menu. Unknown generation lineage is withheld. This may withhold a route whose quoted example alone is independent. Single-paper derivations can remain eligible independently.

Selection supports explicit `writing_route_ids` in the task card. Otherwise a small bilingual functional-cue dictionary ranks request, concepts and target text against route purposes. Equal scores use a documented request-dependent ordering; neither mechanism claims semantic understanding. A compact eligible menu is supplied alongside bounded complete examples. Every proposed use still requires the writer's contextual judgment.

A change informed by a route names its exact `writing_route:` evidence ID in `changes.sources`. The reviewer receives that complete delivered item, including source text, literal/adapted phrases and conditions. Dangling route references fail. Cached evidence rechecks source, catalog and generator-request freshness.

Human semantic supplements remain separately scoped to exact approved schemas and contexts. Their approval does not approve new route adaptations, other source units, or scientific claims. Legacy phrase and pattern templates also require actual physical Ho authorship and literal origin; unknown or non-Ho imitative guidance is withheld without modifying historical decisions.

Verification: run `.venv/bin/python -m pytest tests/test_pipeline.py tests/test_evaluation_exclusions.py tests/test_notation_delivery.py tests/test_writing_routes.py -q`. These checks establish delivery and source controls, not measured writing quality or model learning.
