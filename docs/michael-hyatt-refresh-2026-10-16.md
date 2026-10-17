# Michael Hyatt — October 16, 2026 refresh

[Open the refreshed wiki](../wiki/_archived/michael-hyatt-2026-10-16/README.md) · [Investment policy](../wiki/_archived/michael-hyatt-2026-10-16/persona.md) · [Theses](../wiki/_archived/michael-hyatt-2026-10-16/theses.md) · [Portfolio](../wiki/_archived/michael-hyatt-2026-10-16/portfolio_and_constraints.md) · [Coverage](../wiki/_archived/michael-hyatt-2026-10-16/coverage.md)

Fresh generation with `gpt-5.6-sol` from the Canadian technology investor's current collector export, with no date cutoff. The [earlier wiki](../wiki/_archived/michael-hyatt/README.md) remains unchanged. The target is associated with BlueCat and Dyadem, not the US publishing/productivity author or other namesakes.

## Scope

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 1,082 | 1,951 |
| Text sources reviewed | 250 | 380 |
| Text packets reviewed | 317 | 516 |
| Evidence excerpts | 328 | 398 |
| Context facts | 483 | 528 |
| Admitted source IDs | 146 | 159 |

The snapshot contains 235 web, 135 transcript and 10 report sources, including the previously recovered Tank Talk interview. Counts include duplicates and overlapping variants, not independent interviews. All 516 packets have decisions: 185 target, 293 other, 26 uncertain and 12 unusable. A target packet need not yield investment evidence. Of the 398 excerpts, 243 are labelled explicit and 155 inferred.

## Remaining coverage gaps

**This memory is partial.** Fifty-three media files lack linked transcripts. The inventory links 171 media files to regular transcript sources and one to the existing recovered supplement, represents 86 cached transcript files, and identifies two reference-voice assets. These are file counts, not unique recordings. Two saved files have no visible text; there were no non-media extraction warnings. The 26 uncertain packets remain visible in the audit and do not contribute investor-policy evidence. No new transcription or web collection was performed during this refresh.

## Snapshot and provenance

Original input: `/home/dpasch01/vclogic-vc-trace-collector/outputs/michael-hyatt`.

The collector was actively adding transcripts. The first inventory attempt failed when a transcript arrived after the file census but before transcript processing; no model review had started. A fixed local snapshot was captured at **2026-10-16 17:26:09 UTC**, containing 1,951 files. Content-addressed media files were hardlinked; all other files were copied with size/mtime stability checks. Neither the collector files nor the original wiki were edited. Later collector additions are outside this snapshot.

The existing Tank Talk supplement's media hash matched its stored content-addressed filename. Existing HTML/JSON-LD account receipts, affiliation quotes and the textual speaker resolution were checked by the pipeline before use. These are reused recovery/identity artifacts, not newly performed transcription or acoustic verification.

```bash
python -m wiki_build full-build .wiki-cache/michael-hyatt-2026-10-16/input-snapshot/michael-hyatt \
  --output wiki/michael-hyatt-2026-10-16 \
  --cache-dir .wiki-cache/michael-hyatt-2026-10-16 \
  --reviews wiki/_archived/michael-hyatt/source_reviews.json \
  --supplements supplements/michael-hyatt.json \
  --identity-resolutions supplements/michael-hyatt-identity.json \
  --model gpt-5.6-sol --workers 8 --timeout 1200
```

The collector's identity-resolution timestamp differed from the earlier wiki. Prior fingerprints therefore did not qualify for reuse; Sol reviewed all 516 packets in 110 batches. Responses needing exact-quote repairs passed the normal bounded repair process; no validation was bypassed. All 110 batches succeeded.

Synthesis retained every interpretation, context claim and admitted source record in 299,507 characters. Because the full receipt payload exceeded the first synthesis size threshold, verbatim quotes and attribution explanations were omitted from the synthesis input only; they remain in the wiki ledgers and source snapshots. No findings were dropped.

Use an absent destination for another run. Intentional replay can use `--inventory .wiki-cache/michael-hyatt-2026-10-16/inventory.json`; this snapshot already includes supplements and identity receipts, so do not apply them twice. It does not establish coverage of later collector changes. Final output retains the inventory, source reviews, evidence/context ledgers, full source snapshots, coverage and manifest. Local prompts, raw responses, repairs, snapshot provenance and editorial notes remain in the ignored cache. No downstream onboarding bundle or retrieval index was rebuilt.

## Validation and claim review

The generated wiki passed `python -m wiki_build check wiki/michael-hyatt-2026-10-16` after editorial corrections: exact-quote, source attribution, citation, ledger consistency, source-hash and full packet-coverage checks all passed. No engine code changed.

An agent read all three synthesis pages and checked selected claims against their receipts; a second agent independently reviewed the portfolio and compared it with the earlier wiki. This was automated claim review, not human approval or independent verification of every source claim.

Editorial corrections preserved the original source text and quotes:

- Qualified “Second Clause” and its rendered founder names as uncertain transcript text, potentially referring to Second Closet; updated the review/context/prepared records without changing receipt IDs or counts.
- Restored the failed unnamed juice-startup investment and supported BMO, CBC, TechExit.io, Dress for Success, Common Table, St. Michael’s Hospital and Seneca relationships.
- Kept DataStealth’s relative closing date unresolved and distinguished philanthropic matching commitments from actual disbursements.
- Corrected the allocation summary to reflect the distinct CNBC and Markets Group descriptions; removed unsupported chronological claims about changes in AI preferences and investment roles.
- Retained the Markets Group family-office backing list as source-reported. Congratulatory posts, aggregator listings, advisory positions and corporate financing rounds do not independently establish personal investments.

The original wiki remains unchanged. The new README, coverage page and build report prominently disclose the 53 untranscribed media files and 26 uncertain packets. Raw generation output and pre-edit artifacts remain in the ignored cache.
