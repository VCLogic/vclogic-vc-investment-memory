# Investor investment memory

Generate an investor-specific, cited Markdown wiki from a curated source export. Python prepares and validates the evidence; **gpt-5.6-sol** extracts quotations and writes the synthesis through the authenticated Codex CLI.

Start with the [Michael Hyatt trial wiki](wiki/michael-hyatt/README.md), its [decision policy](wiki/michael-hyatt/persona.md), [build report](wiki/michael-hyatt/BUILD_REPORT.md), and [trial results](docs/hyatt-trial.md).

## Run

Requires Python 3.10+ and an installed, authenticated `codex` CLI supporting `exec`, `--ignore-user-config`, and `--output-schema`. No Python runtime dependencies and no separate API SDK/key setup are needed when the CLI is already authenticated. Generation uses model calls under that CLI account. Preparation and validation are offline.

From this repository:

```bash
# Inspect what will be admitted; no model calls.
python -m wiki_build prepare data/michael-hyatt

# Generate into a NEW directory. Default model: gpt-5.6-sol.
python -m wiki_build build data/michael-hyatt --output wiki/michael-hyatt

# Independently validate a built wiki, without model calls.
python -m wiki_build check wiki/michael-hyatt

# Offline regression suite.
python -m unittest discover -s tests -v
```

The committed Hyatt wiki already occupies that output path. To reproduce locally, choose `--output wiki/michael-hyatt-rebuild`. Successful cached model calls are reused if their complete prompts, model, schemas, and generator revision match. New model output is not guaranteed to be identical when cache is absent. An optional `pip install -e .` exposes the `investor-memory` command.

## Input contract

Pass one investor directory, not the parent `data` directory. The directory name is the investor slug.

```text
data/<investor>/
  identity/resolved_identity.json
  corpus/all_documents.jsonl      # preferred canonical input
  portfolio/portfolio.jsonl       # optional verified structured records
```

Canonical rows need `source_item_id` (or `doc_id`), nonempty `text`, matching `investor_slug`, included status, and `material_role` of `spoken_by_target` or `authored_by_target`. Spoken material needs an accepted speaker-attribution status. Explicit exclusions, duplicates and identifiable Pitch Show sources are rejected. A present resolved-identity file must be confirmed and match the slug. Missing identity is disclosed as a warning. Full provenance, URLs, dates, input line numbers, attribution metadata and input SHA-256 hashes are retained.

If canonical input is absent, the tool accepts `corpus/{blog,talks}.jsonl` or root `{blog,talks}.jsonl` only with the corresponding `_manifest.json` explicitly asserting `no_pitch_sources: true`. Legacy exports lack independently checkable speaker metadata; that limitation is recorded. An empty canonical corpus never falls back to raw files. The tool never traverses `processed/`, `raw/`, `discovery/`, `audit/`, or episode transcripts.

The v1 optional portfolio adapter admits flat records with `verification_status: "verified"`, `identity_match: "supported"`, and `source_url`, excluding Pitch sources. Include `company` and any verified relationship/date fields in those records. Unrecognized/unverified rows are counted and excluded, not guessed. Hyatt's actual portfolio file is empty. Empty/missing holdings do **not** imply no investments, and affiliations/cofounder history do not establish holdings. Future nonempty exporter schemas may need an explicit adapter.

## Output

The existing downstream wiki contract is preserved:

- `persona.md`: cited policy across the nine original dimensions; inferred preferences marked explicitly.
- `theses.md`: recurring themes with evidence references and uncertainty.
- `portfolio_and_constraints.md`: verified holdings when available, with unknowns stated.
- `evidence/<dimension>.md`: original `[ev:ID] label=... direction=... source=...` format and exact transcript excerpts.
- `_manifest.json`: source IDs, evidence count, thin-corpus flag, timestamp, model and call provenance. `persona_tokens` is a labeled character-based estimate.

Additional review artifacts: `README.md`, `BUILD_REPORT.md`, `sources.md`, `prepared.json` (full admitted source snapshot), `evidence.json` (normalized quote offsets), and `validation.json`. Generated artifacts contain source text; share them under the same conditions as the source corpus.

## How generation works

1. Deterministic preparation selects curated input, filters inadmissible rows, deduplicates normalized text and records omissions.
2. Each source is split into bounded chunks (default 30,000 characters). Sol receives only the chunk and taxonomy in its prompt and extracts evidence as structured JSON. Every quotation must be a contiguous source match after whitespace normalization.
3. Python assigns evidence IDs and deduplicates identical quotations. IDs are stable for identical ordered extraction results; they are not promised stable across corpus or model changes. Sol synthesizes the three wiki pages from verified evidence and supplied identity/portfolio metadata.
4. Python renders the evidence pages and manifests, checks them, then publishes a staged build into an absent destination. An existing output is never overwritten.

[Generator instructions](wiki_build/AGENT.md) define evidence selection, attribution and synthesis. [Design](docs/superpowers/specs/2026-09-14-investor-memory-design.md) explains the tradeoffs. The bundled taxonomy retains the 44 labels and nine dimensions from the previous `vc-digital-twins/taxonomy/codebook_v_final.json`, omitting study support metadata. No old-repository paths are needed at runtime.

The agent runs in a temporary working directory with a read-only Codex sandbox, no user config, and instructions to use no tools or external knowledge. This is an input and instruction boundary, not an OS-level guarantee that model tools cannot read other files. Model event logs make unexpected tool use reviewable.

## Reliability and limits

Each call keeps its prompt, schema, invocation, event log and raw response under `.wiki-cache/<content-hash>/`. Only accepted responses become reusable `response.json` entries. A rejected response receives one bounded Sol repair attempt with the validation errors; unsuccessful repairs still fail the build. Interrupted raw responses are revalidated before reuse. The default timeout is 900 seconds per call; override with `--timeout`. `--cache-dir`, `--batch-chars`, and `--model` are configurable. Source text travels over stdin without shell interpolation. Repair attempts are retained in their own subdirectories. On failure the command exits nonzero; inspect the reported cache directory, fix the issue and rerun. Valid prior calls are reused.

Validation checks required files/sections, allowed labels/directions, unique evidence IDs, source IDs, snapshot text hashes, quote offsets, verbatim quotations, every policy/thesis bullet's citation, evidence citation resolution across all three pages, portfolio IDs and their source URLs, evidence-page integrity and manifest counts. It does not prove logical entailment or accurate audio transcription. A cited claim can still overstate a source: manual semantic review remains necessary. Historical forecasts with unknown dates remain attributed opinions, not current facts. The initial thin-corpus threshold (600,000 characters) is inherited from the previous pipeline and is a coverage flag, not a statistical confidence score.

V1 processes source chunks sequentially. It fails explicitly if the evidence synthesis input exceeds 240,000 characters rather than silently dropping evidence. It does not discover new sources, infer portfolio records, repair transcript text or evaluate investment outcomes.
