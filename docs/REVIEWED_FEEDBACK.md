# Reviewed advisor feedback

`memory.reviewed_feedback` imports a source-bound human review separately from the legacy manuscript-change accept/reject table. `confirm` concerns the displayed advisor case; it does not accept a manuscript revision or verify a scientific claim.

`prepare(intake_dir, candidates_path, output_dir)` creates immutable `records.json`, `objects.json` and `manifest.json`. It checks the intake manifest, exact case/PDF/page/crop bindings, continuation images and any observed later variant. Original files and human notes remain unchanged. PDF visual/human verification is identified explicitly; no TeX source verification is claimed.

The current twenty cases produce twelve confirmed language feedback objects, five literal user-guidance objects whose original cases remain `revise`, and three scientific-question objects. Advisor handwriting, the displayed machine interpretation and literal user notes retain separate attribution. Case 001 keeps its user supplement beside the handwriting; its observed later variant has no accepted-revision status.

After the coordinator checks the prepared manifest, `admit(manifest_path, db_path)` adds records to a separate `reviewed_feedback` table. It is idempotent for the same exact admission and rejects a different version under the same case ID. `memory.feedback.index_objects` includes these objects in the normal SQLite/NumPy index, and `update_index` embeds only changed/new objects using the existing configured embedder. No FAISS or new dependency is required.

`activate(manifest_path, knowledge_dir)` creates an exact `feedback_review_active.json` pointer. The preparation and shadow probe do not create a production pointer. Normal evidence retrieves language feedback and scoped literal user guidance only after activation. Scientific cases enter `inherited_scientific_questions`, outside language evidence IDs, and reach the reviewer without automatically forcing escalation or lowering a language assessment.

Feedback genres are independent of the ordinary ten source-section types. An actual `abstract` target environment routes feedback to the abstract cases while ordinary source retrieval remains `unknown`. Response-letter feedback requires an explicit response-letter task context or an unnegated rebuttal/response-letter editing request. Ordinary introduction requests cannot retrieve abstract cases through this route. The source taxonomy is unchanged.

Index hits and cached evidence recheck the original source and human-intake hashes and compare indexed payloads with the exact prepared objects. Changed source assets, altered index text, an active-review mismatch or a changed knowledge pointer requires fresh preparation rather than a fallback.

`scripts/probe_reviewed_feedback.py` creates a new shadow database/index and uses the existing cached BGE model with offline hub settings. Its final probe uses `parse_tree → locate → taskcard → gather`, saves complete taskcards/evidence, and tests self-retrieval. These are engineering checks of delivery and attribution; they do not demonstrate writing improvement or parameter training.
