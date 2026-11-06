# Version 0.4.1 stable patch

Source metadata is 0.4.1. The exact production provenance-correction sidecar was activated after frozen-run freshness verification. Build and installation are recorded separately under `data/evaluation/release_activation_0.4.1_20261105/`; no new knowledge approval is implied by this patch.

## Stable changes

- Require a real baseline compile result bound to the frozen input manifest and actual log. Failed or unreported baselines cannot start writing. Preserve old checks when explicitly rechecking a task.
- Preserve pre-existing build artifacts outside the frozen manuscript-input set; retain figure PDFs and bbl-only inputs as source material. Do not re-freeze source after compilation to hide changes.
- Read citation keys from actual BibTeX or original `\bibitem` records. Protect supplied bbl-only bibliographies during latexmk execution.
- Support explicit evaluation source-family manifests across every reference lane, before candidate limits and top K. Withhold mixed or unidentified origins conservatively; ordinary tasks retain their existing defaults.
- Recognize plural MDP/RMDP/DRMDP concept spellings without changing canonical concept keys or frozen inventories.
- Apply a source-provenance-only family correction. It exposes current family counts while preserving raw lexicon bytes, original scope and human-review states. Production received only the exact correction sidecar; no pending contexts or schemas were admitted.

The correction candidate is `data/evaluation/shared_family_audit_20261105/source_family_corrections.candidate.json`. Its exact-file SHA is `1d6da840505c2293d19038e2677770f8af184a93b776171cea61a3090fb44f6d`; its internal payload SHA is `9aae1071273e659ded118c880b2c0debb1f680acdb6e6f7c28a9d177a8197688`. The candidate bytes are copied without changing its original descriptive fields; the live filename and activation receipt record production activation. The original 157 knowledge and three index files remain byte-identical. The independent human filter retains 40 entries: 14 existing approved scopes and 26 pending legacy scopes; this patch does not expand either scope.

## Current knowledge and acceptance limits

The old 15 shared registrations have two independent work families, because 2205.14202 and its 2602.05591 extension are one family. They do not satisfy the original three-family threshold. A new offline scan finds 16 phrase candidates with literal support in at least three families; 20 new contexts remain pending. Literal support, applicability, prior review scope and future admission are separate.

The structural learning claim covers eight representative sections within an inventory of 69 actual sections, not the whole corpus. Seven source-specific section interpretations are approved. All eight new type-level schema projections, the Related Work route correction and the RMDP abstract/keyword/body interpretation remain pending. The standalone 30-item approval attachment uses exact new IDs and package hashes; it does not change historical judgments or activate anything.

The first full writer dispatch failed because the complete context was too large. A later actual GPT-6.1 Sol candidate passed local deterministic validation; engineering checks do not establish language quality. Complete current first-pair outcomes belong to the independent R4 execution report and actual stage receipts. The experimental first-pair adapter/runner is not a generic completed workflow, is not promoted to the default plugin payload, and does not prove queryable local evidence was read. Formal 32-variant M8 evaluation, its human review and measured writing improvement are not established.

## Item-level discard accounting

`data/evaluation/extraction_item_denominator_20261105/report.json` reconstructs 12 exact selected legacy extraction batches: 164 raw `items` objects, 163 retained, one dropped, or 0.6098%. Every batch was replayed through the original strict whitespace-only verifier against its immutable supplied source projection; saved verified/dropped records matched. Earlier diagnostics and replaced/truncated attempts remain separate.

This denominator covers the current lexical seeds, patterns and legacy Introduction schema extraction lineage. Not every retained seed was selected into the final canonical lexicon. Structure observations, deterministic enrichment and new offline pending projections use other contracts; a complete final knowledge-set item discard rate remains unestablished. The earlier 111/111 quote checks and 344/370 mixed literal-support declarations are not extraction-item rates and do not replace this limitation.

## Packaging gate and exclusions

The release sequence backs up existing knowledge/index files, activates only the exact provenance correction, leaves pending schemas/contexts unchanged, verifies actual gather and freshness, updates `plugin.json` and `pyproject.toml` together, builds both ZIP and wheel from the clean whitelist stage, and uses the supported local marketplace installation route. Installed/enabled metadata, cache-file hashes and the editable runtime are checked in separate receipts. The coordinator's final 248-test run remains applicable while core source hashes are unchanged; packaging does not replace those checks or establish M8. Older bundles are retained.

The default package excludes runtime knowledge, source corpora, task and review exports, credentials, credential paths, environments, caches, paused UI work and first-pair experimental tools. The existing source and feedback CLI update channels remain available. `ACCEPTANCE.md` and historical experiment records are preserved. Current truthful approval/coverage status is in [the independent acceptance status](ACCEPTANCE_PENDING_20261105.md); source-family holdout and baseline operation are documented in [evaluation exclusions](EVALUATION_EXCLUSIONS.md).
