# Operational details

## Supplements and incomplete material

The engine extracts saved text, HTML/PDF, and existing transcripts. It does **not** automatically transcribe all raw media. The file inventory reports material without transcripts and failed or unlinked text extraction.

First inspect existing collector transcript artifacts and any supplied supplements. If a suitable transcription tool is available within the task scope, use it to recover missing speech into a separate supplement, keeping the original media unchanged. Preserve media references, transcript method, source hashes, and speaker-attribution evidence. Do not label textual speaker identification as an acoustic match. If recovery cannot be completed, retain the gap in the report and describe the wiki as partial.

Supplement adapters and receipt verification are implemented in `wiki_build/inventory.py` (`apply_supplements`, `apply_resolutions`). Inspect these functions before authoring a new supplement; the existing JSON examples are not a universal schema for arbitrary collector outputs. Incorrectly attributed material should remain uncertain until actual source evidence resolves it.

For the repository's existing **Michael Hyatt export only**, append these arguments to `full-build`:

```bash
--supplements supplements/michael-hyatt.json \
--identity-resolutions supplements/michael-hyatt-identity.json
```

The transcript supplement recovers a Tank Talk interview. The identity file contains profile links, explicit textual speaker confirmation, and saved HTML/JSON-LD identity receipts. Identity receipts are checked against actual source files and hashes; if they do not match a new export, investigate the mismatch rather than disabling validation. Do not attach these files to another investor.

A raw `inventory` command does not apply these supplements. Read the supplemented inventory saved by `full-build` before interpreting final media coverage.

## Failure and resumption

Accepted model batches are cached; a rejected response receives one bounded Sol repair attempt. Keep the cache on failure. Inspect the reported directory's response, prompt, validation feedback, event log, and stderr to distinguish quote errors from unavailable models, authentication, timeouts, or malformed input. Do not print credentials or dump the entire corpus into the user-facing report.

An identical rerun reuses accepted calls. When a transient failure is resolved, rerun the original command. Increase `--timeout` for demonstrated timeouts if appropriate; do not endlessly retry an unchanged deterministic failure. If two unchanged retries fail for the same reason, diagnose and fix the cause or report the specific blocker.

After all reviews succeed, the cache contains `reviews.json`. To resume synthesis or reuse validated decisions:

```bash
python -m wiki_build full-build /path/to/collector/investor-slug \
  --output wiki/investor-slug-resumed \
  --cache-dir .wiki-cache/investor-slug \
  --reviews .wiki-cache/investor-slug/reviews.json \
  --model gpt-5.6-sol
```

Retain the same applicable supplement and identity-resolution arguments. Reviews are revalidated and reused only when their identity, packet metadata/text, taxonomy, and review-policy fingerprints match. Do not rewrite fingerprints to make old decisions appear current. If only some batches succeeded, consolidated `reviews.json` may not exist; rerun using the cache rather than inventing that file or discarding accepted work.

`--inventory snapshot.json` deliberately reuses a saved snapshot instead of rescanning the input. Use it only for an intentional snapshot replay after establishing which material it represents. For a changed collection, rescan. Do not call an old snapshot a complete review of newly supplied files.

The current engine bounds synthesis input; it fails explicitly if the supported size is exceeded. Preserve the extracted work and report or address the implementation limit. Do not silently truncate evidence or switch to curated mode.

## Completion evidence

The final output has 17 Markdown files plus JSON receipts and snapshots. `check` is offline and verifies evidence, hashes, attribution, citations, and full-build consistency. Read warnings independently: a structurally valid partial corpus is still partial.

For code changes, run `python -m unittest discover -s tests -v`. Normal generation does not require rerunning a paid end-to-end generation merely to test the skill. Validate the actual produced wiki, then review the three synthesis pages for meaning.

`context.json` contains source-reported relationship facts, not an independently verified holdings database. `prepared.json` contains full admitted source texts; `inventory.json` also preserves rejected sources for auditing. `source_reviews.json` records packet decisions. `coverage.json` carries file and packet counts and dispositions. `_manifest.json` includes admitted source IDs, evidence/context counts, and generation metadata.
