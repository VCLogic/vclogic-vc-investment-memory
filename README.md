# VC Investment Memory

Turn a venture investor’s collected source material into a cited investment wiki: how they evaluate companies, what themes they follow, and which investments and company relationships sources report.

**Start with the [Michael Hyatt example](wiki/michael-hyatt/README.md)**: [investment policy](wiki/michael-hyatt/persona.md), [investment themes](wiki/michael-hyatt/theses.md), and [portfolio and relationships](wiki/michael-hyatt/portfolio_and_constraints.md).

The [Mac Conwell memory](wiki/mac-conwell/README.md) covers his supplied collector export, with recovered audio and an explicit coverage audit. See its [investment policy](wiki/mac-conwell/persona.md), [reported relationships](wiki/mac-conwell/portfolio_and_constraints.md), and [run report](docs/mac-conwell-full-run.md).

The [October 2026 batch report](docs/batch-2026-10-06.md) links the completed text-based memories for 17 additional investors. These exports have untranscribed media, so their memories cover available text and are labelled partial.

## Dependencies across VCLogic repositories

This repository is the investment-memory stage of the [VCLogic](https://github.com/VCLogic) workflow. The arrows below show data flow; package dependencies are described separately.

```text
vclogic-vc-trace-collector
  │ Complete investor folder: identity, source text, transcripts, metadata
  ▼
vclogic-vc-investment-memory  (this repository)
  │ Validated, cited wiki in wiki/<investor-slug>/
  ▼
vclogic-vc-investor-onboarding
  │ Investor bundle: wiki, identity, retrieval indexes, assessment configs
  ▼
vclogic-vc-agentic-assessment
  │ Investor-specific pitch assessments and founder rehearsal
  ▼
vclogic-web-application
    Web interface and API for profiles, assessments, comparisons and rehearsal
```

| Repository | Relationship to this repository | Handoff / responsibility |
|---|---|---|
| [VC Trace Collector](https://github.com/VCLogic/vclogic-vc-trace-collector) | **Upstream data producer.** Its Python package is not imported here. | Resolves investor identity and collects public traces, transcripts and portfolio source pages. Pass the whole `outputs/<slug>/` folder to this repository. |
| [Investor Onboarding](https://github.com/VCLogic/vclogic-vc-inverstor-onboarding) | **Direct downstream consumer.** Depends on this repository's `vc-investment-memory` package for wiki validation, and on the assessment engine for runtime formats and validation. | Consumes `wiki/<slug>/`, prepares identity/configuration and retrieval indexes, and produces a validated bundle. It can optionally add historical pitches and evidence-linked decisions from The Pitch. |
| [Agentic Assessment](https://github.com/VCLogic/vclogic-vc-agentic-assessment) | **Downstream assessment engine.** Not required to generate a wiki here. | Uses the prepared investor knowledge and indexes to investigate pitch rationales, synthesize decisions and run rehearsal. Onboarding can install a bundle into this repository's workspace. |
| [Web Application](https://github.com/VCLogic/vclogic-web-application) | **Downstream application.** Depends on the assessment engine; not required to generate a wiki here. | Provides the React interface and FastAPI API. Discovers prepared investor bundles/installed profiles and executes assessments through the engine. It does not generate wikis or build missing indexes through the browser. |

**For wiki generation only:** install this repository and supply an investor export. If you already have the export, you do not need to run the collector again or install onboarding, assessment or the web application. Portfolio pages from the collector are source material; the investment and relationship analysis happens here. Follow the [collector setup instructions](https://github.com/VCLogic/vclogic-vc-trace-collector#readme) when collecting new material.

### Local checkout layout for the full workflow

Onboarding's `uv` configuration uses editable sibling dependencies on investment-memory and assessment. The web application's `uv` configuration uses an editable sibling dependency on assessment. Use this layout when working across the projects:

```text
<workspace>/
├── vclogic-vc-trace-collector/       # Optional once you have the export
├── vclogic-vc-investment-memory/    # This repository
├── vclogic-vc-investor-onboarding/
├── vclogic-vc-agentic-assessment/
└── vclogic-web-application/
```

The onboarding repository's current **GitHub name contains `inverstor`**, while its package and expected local directory use `investor`. Clone it with an explicit destination:

```bash
# Run from the shared parent directory.
git clone https://github.com/VCLogic/vclogic-vc-inverstor-onboarding.git vclogic-vc-investor-onboarding
```

A generated wiki is the handoff to onboarding, not yet an indexed assessment bundle. After generating and checking it here, follow the [onboarding workflow](https://github.com/VCLogic/vclogic-vc-inverstor-onboarding#readme) to prepare/check a bundle and install it into the assessment workspace. Then follow the [assessment setup](https://github.com/VCLogic/vclogic-vc-agentic-assessment#readme) and, if needed, the [web application setup](https://github.com/VCLogic/vclogic-web-application#readme). Each repository manages its own environment and credentials; this repository's Sol/Codex setup does not configure downstream model providers.

## What you need

| Requirement | Purpose |
|---|---|
| An investor export from [vc-trace-collector](https://github.com/VCLogic/vclogic-vc-trace-collector) | Input source material and resolved identity |
| Python 3.10+ | Run this repository’s preparation and validation tools |
| This package with its `full` dependencies | Extract saved HTML/PDF and transcript content |
| An installed, authenticated Codex CLI with access to `gpt-5.6-sol` | Generate the source reviews and wiki pages |

Claude Code or Codex can orchestrate the workflow through the included skill. **Both use the Codex CLI for Sol generation**; Claude authentication alone does not provide that backend. The CLI must support `exec`, `--ignore-user-config`, and `--output-schema`.

## 1. Install this repository

```bash
git clone https://github.com/VCLogic/vclogic-vc-investment-memory.git
cd vclogic-vc-investment-memory
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[full]'
```

## 2. Supply the investor data

Use the **whole investor folder**, for example the collector’s `outputs/michael-hyatt/`. You can leave it in the collector checkout and pass its path, or copy it into `data/michael-hyatt/` here. Raw data is not included in this repository’s Git history.

The folder must include a confirmed `identity/resolved_identity.json` whose slug matches the folder name. Preserve the collector’s directory structure and relative paths:

```text
<investor-slug>/
├── identity/       # Resolved identity and attribution references
├── discovery/      # Source candidates and collection metadata
├── corpus/         # Curated exports, when available
├── processed/      # Collected documents and audiovisual attribution
├── raw/            # Saved pages, PDFs, and media
├── state/          # Cached transcripts and collection state
└── portfolio/      # Downloaded portfolio source pages and provenance
```

Available folders vary by collection. Do not supply only `corpus/all_documents.jsonl`, a portfolio handoff file, or a generated wiki: those omit material needed for a full collection review. Missing transcripts and extraction failures are reported; this tool does not automatically transcribe raw media.

## 3. Generate the wiki

Choose either the agent skill or the command line. **No date cutoff is applied.**

### With Codex or Claude Code

Open this repository in your harness and provide the actual investor folder path.

**Codex:**

```text
$investor-memory Generate a complete wiki from ../vclogic-vc-trace-collector/outputs/michael-hyatt.
```

**Claude Code:**

```text
/investor-memory Generate a complete wiki from ../vclogic-vc-trace-collector/outputs/michael-hyatt.
```

The [shared skill](.agents/skills/investor-memory/SKILL.md) checks prerequisites, inventories the data, runs the full pipeline, validates the result, and reviews the generated claims. It chooses a fresh output directory and reports unresolved material.

### With the command line

Run from this repository. Replace the example input path with your collector export:

```bash
# Inspect available material; no model calls.
python -m wiki_build inventory ../vclogic-vc-trace-collector/outputs/michael-hyatt

# Generate with Sol. The output directory must not already exist.
python -m wiki_build full-build ../vclogic-vc-trace-collector/outputs/michael-hyatt \
  --output wiki/michael-hyatt-new \
  --cache-dir .wiki-cache/michael-hyatt

# Check the generated result offline.
python -m wiki_build check wiki/michael-hyatt-new
```

Use **`full-build`** for the whole collection. The older `prepare` and `build` commands process a narrower curated subset.

To reproduce the committed Hyatt example from its original export, add `--supplements supplements/michael-hyatt.json --identity-resolutions supplements/michael-hyatt-identity.json` to `full-build`. These files contain a recovered transcript and identity receipts tied to that export; they are not generic inputs for other investors or changed exports. See the [Hyatt run report](docs/hyatt-full-run.md).

## What gets generated

| Files | Contents |
|---|---|
| `README.md` | Entry point into the generated wiki |
| `persona.md` | Investment policy across nine dimensions, with inferred preferences labelled |
| `theses.md` | Recurring investment themes and tensions |
| `portfolio_and_constraints.md` | Reported investments, company relationships, mandate, and constraints |
| `evidence/*.md`, `evidence.json` | Investor quotations and their interpretations, referenced as `[ev:…]` |
| `context.md`, `context.json` | Source-reported facts and supporting passages, referenced as `[ctx:…]` |
| `sources.md`, `prepared.json` | Admitted source index and full source text |
| `coverage.md`, `coverage.json`, `source_reviews.json`, `inventory.json` | File inventory, packet review decisions, exclusions, and source snapshots |
| `BUILD_REPORT.md`, `_manifest.json`, `validation.json` | Build metadata, counts, and validation results |

The portfolio is a cited relationship inventory, not an independently verified register of current holdings. Founder, adviser, board, acquisition, fund, and investment roles are distinguished. Undated and historical material remains labelled as such.

“Complete” means the supplied collection was accounted for. It does not mean all material about an investor has been discovered. A build with missing transcripts or unprocessed content remains partial even if its structural checks pass. Validation checks exact quotations, attribution, citations, hashes, and coverage; reviewing the synthesis is still necessary to catch overstated interpretations.

## Operations and development

Model calls are cached. Keep the cache after an interruption and rerun the same command to reuse accepted work. Inventory and validation are offline; generation sends source text to Sol through the authenticated CLI. Generated snapshots also contain source text.

- [Resume runs, use supplements, and handle missing material](.agents/skills/investor-memory/references/operations.md)
- [Pipeline components and developer entry points](wiki_build/README.md)
- [Complete Hyatt run: scope, repairs, and verification](docs/hyatt-full-run.md)
- [Mac Conwell run: coverage, recovered media, and limitations](docs/mac-conwell-full-run.md)

Run the offline regression suite after code changes:

```bash
python -m unittest discover -s tests -v
```

The canonical skill lives in `.agents/skills/investor-memory/`; `.claude/skills/investor-memory` links to it. If the skill is not visible, start a new harness session in the repository. On systems that check out symlinks as plain text, replace the Claude link with a copy of the canonical skill folder.
