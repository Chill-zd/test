# Design adjudication — 2026-11-04

This is a new, independent plugin commissioned from the user's 13-section specification. GPT-6 Sol began implementation; the user subsequently switched the coding seat to GPT-6.1 Sol, which completed the current implementation. The coordinating agent reviews. Existing Paper Supervisor implementation, knowledge, feedback and configuration are not dependencies. A separately authorized Sonnet consultation used the existing private account credential transiently; no credential is included in this package.

## Specification ambiguities

1. **Four-call hard cap takes precedence over a “free” format retry.** Every dispatched attempt is reserved in the ledger before dispatch, including network retries, format retries and failed calls. A crash may conservatively consume a reservation. No hidden SDK retries. One format retry remains distinct from the single shared validator/reviewer/compiler repair, but neither can exceed the total cap.
2. **Scientific escalation is not acceptance.** Preserve the candidate, audit and questions when review requests user judgment. Do not produce an apply-ready patch for unresolved scientific changes. Malformed or missing review is not a pass.
3. **Full and bare runs are independent variants.** Bind both to the same frozen manuscript. Keep separate artifacts and ledgers; each has its own cap, so a paired comparison can consume twice the per-task budget. Bare mode omits domain evidence and schemas but retains deterministic checks and scientific review.
4. **Verbatim source remains authoritative.** Comment-stripped text is a parsing projection. Retain physical file coordinates, exact source spans and hashes; verify the original before patching. Do not guess a replacement across ambiguous physical spans.
5. **Offline fixtures are synthetic.** Do not call them recorded provider responses or use them as evidence of actual model performance. Real corpus quality, human schema approval and full-versus-bare style acceptance remain separate gates.

## Sonnet consultation

The exact model `claude-sonnet-5.5` was checked against Poe's live catalogue before consultation; price and balance were checked. The completed response and usage are in [sonnet55-design.json](consultations/sonnet55-design.json). This was an engineering opinion, not manuscript review or quality acceptance.

The coordinator accepts the core recommendations above. The following additional Sonnet suggestions are **not adopted**: silently stripping Markdown fences to satisfy strict JSON; merging the separately specified format retry into the shared substantive repair allowance; requiring a new task after every user clarification. These would change the user's contract without necessity.

## Packaging source

The independent package follows the root `plugin.json` and `skills/` layout described in [OpenAI's plugin packaging documentation](https://developers.openai.com/plugins/build/plugins). Creating package files does not prove that the desktop app has loaded or activated the plugin.

## Subsequent real-run decisions

The user asked to use GPT-6.1 Sol through Codex. The local independent CLI rejected that exact model for its login, whereas the current host's explicitly selected GPT-6.1 Sol agents succeeded. The new default `codex_host` prepares immutable requests, reserves the ledger before dispatch, imports an actual host-tool receipt and response, and replays completed identical requests without another reservation. It never copies OAuth tokens or substitutes a model. Sonnet remains on the verified Poe endpoint. The host route enforces four reserved dispatches, not four observable network requests; this explicitly qualifies decision 1 for native transport only. Direct API mode retains attempt accounting. The native-transport consultation is retained at `data/acceptance/native_transport_consultation.json`.

The real pilot exposed TeX-comment leakage and missing seed context. Original physical text and hashes remain available for patch fidelity; knowledge calls and quote checks now use only a comment-free projection with distinct hashes. Lexicon inputs explicitly supply the allowed concept dictionary. All first-round knowledge was archived as diagnostic rather than silently repaired or admitted. Three papers' introductions were regenerated once with clean inputs. The projection consultation is retained at `data/acceptance/comment_projection_consultation.json`. Automated quote binding does not approve the interpretation of a passage or the utility of a schema.
