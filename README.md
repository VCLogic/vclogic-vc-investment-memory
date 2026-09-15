# Investor investment memory

Build a cited investor wiki from an entire collected investor directory. **gpt-5.6-sol** reviews every source packet, separates the intended investor from namesakes, extracts exact quotations, and synthesizes the investment memory. Python inventories the files and validates evidence, attribution, citations, and coverage before publishing.

Read [Michael Hyatt’s memory](wiki/michael-hyatt/README.md), [decision policy](wiki/michael-hyatt/persona.md), [company relationships](wiki/michael-hyatt/portfolio_and_constraints.md), and [coverage ledger](wiki/michael-hyatt/coverage.md). The [complete-run report](docs/hyatt-full-run.md) records scope, attribution repairs, and limitations.

## Run the complete collection

Requires Python 3.10+, `pip install -e '.[full]'`, and an authenticated Codex CLI supporting `exec`, `--ignore-user-config`, and `--output-schema`. Model calls use that CLI account. Inventory and validation run offline.

```bash
# Inspect all collected files without model calls.
python -m wiki_build inventory data/michael-hyatt --output /tmp/hyatt-inventory.json

# Review every extracted source and publish into a NEW directory.
python -m wiki_build full-build data/michael-hyatt \
  --output wiki/michael-hyatt-rebuild \
  --supplements supplements/michael-hyatt.json \
  --identity-resolutions supplements/michael-hyatt-identity.json

python -m wiki_build check wiki/michael-hyatt-rebuild
python -m unittest discover -s tests -v
```

Pass one investor folder with a confirmed `identity/resolved_identity.json`. The full pipeline reads canonical and processed documents, full diarized transcripts, cached transcripts, saved HTML/PDF pages, and portfolio source reports. It deduplicates text while preserving provenance. Discovery snippets and metadata support inventory and identity; they are not investment evidence. Every input file receives a disposition, including duplicates, media represented by transcripts, and unusable material. Namesakes and uncertain identities receive explicit source review decisions.

The Hyatt supplements recover a downloaded Tank Talk interview that lacked a transcript and document source-backed identity links. Its transcript was generated with Whisper turbo and attributed against the collection’s reference voice. A separate E55 interview uses explicitly documented textual speaker attribution; its acoustic result remains recorded as uncertain. Supplements do not alter the original collection. These are Hyatt-specific receipts, not requirements for other investors.

## Output and evidence

- `persona.md`, `theses.md`, `portfolio_and_constraints.md`: the investment memory, preserving the original nine-dimension wiki contract.
- `evidence/*.md`, `evidence.json`: investor statements with taxonomy labels, attribution, source IDs, and exact quote offsets.
- `context.md`, `context.json`: source-reported biography, company relationships, and dated events, kept distinct from investor statements.
- `sources.md`, `prepared.json`: admitted source index and full text snapshot.
- `inventory.json`, `source_reviews.json`, `coverage.json`, `coverage.md`: complete inventory, every packet’s decision, and coverage accounting, including rejected source texts.
- `_manifest.json`, `BUILD_REPORT.md`, `validation.json`: model provenance and validation results.

Company founding, employment, advisory work, board seats, ownership, and investments are distinct relationships. A cited company association does not establish a current holding or personal investment. Historical predictions remain attributed opinions. Complete collection processing does not imply that every fact about the investor or every holding is known.

## Resuming and reproducing

Full runs default to three concurrent Sol calls (`--workers`), 22,000-character source packets, and 1,200 seconds per call (`--timeout`). Prompts, schemas, event logs, raw responses, and validated responses are cached under `.wiki-cache/full-review`. A failed call gets one bounded repair attempt. Accepted batches survive failures. Repeating an identical invocation reuses accepted cache entries.

`--inventory saved.json` reuses a specific inventory snapshot instead of scanning the current folder. `--reviews reviews.json` reuses prior packet reviews only when their identity, attribution, source packet, taxonomy, and review-instruction fingerprint still matches, then revalidates their receipts. Older reviews without fingerprints are reprocessed. The cache directory stores consolidated `inventory.json` and, after review succeeds, `reviews.json`. Use the same supplements and identity resolutions when resuming. A changed identity policy may require deliberately omitting prior uncertain decisions so Sol reconsiders them. Cache keys include full prompts, schemas, model, and generator revision.

The full pipeline synthesizes all accepted evidence and context. Large synthesis inputs omit repeated quote text while retaining every interpretation and context claim; exact receipts remain in the artifacts. Inputs exceeding the supported synthesis bound fail explicitly. Output is staged, validated, and published only into an absent destination.

The earlier curated-only `prepare` and `build` commands remain available. Their narrower admission policy excludes Pitch sources and does not traverse raw or processed material. Full mode intentionally lifts that study-specific exclusion and records its different source policy. See [pipeline components](wiki_build/README.md) and the historical [three-talk pilot](docs/hyatt-trial.md).

## Validation limits

Checks enforce complete source-packet accounting, valid taxonomy, exact quotes, accepted transcript speaker turns, source hashes and offsets, rendered evidence consistency, resolvable citations, and receipts on portfolio table rows. They do not prove a claim’s logical entailment or the accuracy of automated transcription. Source-reported facts and uncertain identity decisions remain reviewable. Generated snapshots contain collected source text and should be handled under the same conditions as the inputs.

Sol runs in a temporary read-only Codex workspace with user configuration disabled and instructions not to use tools or outside knowledge. Event logs allow tool-use auditing; this is not an operating-system guarantee that model tools cannot access other files.
