# polishpaper

An independent local plugin for source-bound LaTeX language revision. Code, configuration, corpus, knowledge, task artifacts and feedback remain separate from Paper Supervisor.

**Current release: 0.4.8.** Read the single [current status and evidence page](docs/CURRENT_STATUS.md) for approvals, audit denominators, handbook coverage and actual comparison results. Historical reports and signed decisions remain unchanged.

The selected roles are GPT-6.1 Sol (`gpt-6.1-sol`) for routine writing and Sonnet 5.5 (`claude-sonnet-5.5`) for extraction and escalated review. The configured `codex_host` route prepares immutable host requests and imports actual responses with dispatch receipts; it does not require a separate OpenAI API key or extract login tokens. Standalone CLI work pauses for the installed Codex skill to perform the host handoff. Sonnet uses the configured environment variable. Never put secrets in manuscript requests or tracked files.

## Local setup

Use this independent project’s environment and runtime. Python 3.10+, TeX Live and `latexmk` are required.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/polishpaper --help
.venv/bin/python -m pytest -q
```

The installed plugin points to a clean whitelist bundle; private corpora, runtime knowledge, tasks, credentials and environments stay outside the package. The skill identifies the configured runtime. New chats may be needed to refresh skill discovery.

## Language-only handbook writing

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


The exact target-quote channel is separate from advisor annotations. Sources are copied and a real baseline compile must pass. The profile creates a separate variant, freezes math/citation/reference identities and scientific assertions, and allows the original unchanged. Source uncertainty remains a scientific question. The [handbook](docs/CLINT_MDP_WRITING_HANDBOOK.md) contains optional source-bound alternatives, not mandatory templates.

Retrieval counts are maxima. Whole unasked automatic illustration/lexical/pattern options can be omitted before handbook exemplars to fit the explicit byte policy; mandatory context, asked evidence, approved schema and scientific cautions remain. Unrequested external preferences are not operative for frozen existing notation. Complete originals and omission records remain locally bound. The byte policy is not a provider-token guarantee. This profile is not legacy complete full; see [scope and limits](docs/HANDBOOK_PROFILE.md).

Legacy `task run TASK_ID` remains a distinct mode. Its real complete-context capacity failure is preserved. Do not infer that a successful scoped profile repairs that failure, establishes formal M8, or proves writing improvement.

## Review, delivery and feedback

Read the saved revised text, review, patch, compile report and scientific questions before presentation. Human acceptance is recorded only when supplied. Structured authentic annotations use `task new --annotations FILE`; a locator is not an annotation. Only exact delivered evidence IDs are citable, including source-bound schema IDs. Source/unit/backpointer keys are provenance.

```sh
.venv/bin/polishpaper task deliver TASK_ID
.venv/bin/polishpaper ledger show --task TASK_ID
.venv/bin/polishpaper feedback record TASK_ID
```

Each variant retains the four-reservation cap, including failed and pending host calls. Shared repair runs only within that cap. An identical completed request replays without another reservation. Feedback memory is not model-weight training.

## Sources and historical records

The source-admission CLI remains available: `ingest`, `parse`, `extract`, `verify`, `merge` and `index build`. Authentic source versions, attribution and exact decisions must be preserved; an extracted candidate does not approve itself. Consult [source structure delivery](docs/STRUCTURE_IMPLEMENTATION.md), [reviewed feedback](docs/REVIEWED_FEEDBACK.md), [notation handling](docs/NOTATION_GUIDE.md) and [route delivery](docs/WRITING_ROUTES.md).

[ACCEPTANCE.md](ACCEPTANCE.md), earlier release documents and frozen experiment records retain their historical meaning. The paused UI is not required for this workflow. The current release’s narrow changes and package receipts are described in [0.4.8 release details](docs/RELEASE_0.4.8.md).
