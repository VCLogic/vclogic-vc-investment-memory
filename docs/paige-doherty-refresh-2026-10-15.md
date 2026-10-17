# Paige Doherty — October 15, 2026 refresh

[Open the refreshed wiki](../wiki/paige-doherty-behind-genius-ventures-2026-10-15/README.md) · [Investment policy](../wiki/paige-doherty-behind-genius-ventures-2026-10-15/persona.md) · [Theses](../wiki/paige-doherty-behind-genius-ventures-2026-10-15/theses.md) · [Portfolio](../wiki/paige-doherty-behind-genius-ventures-2026-10-15/portfolio_and_constraints.md) · [Coverage](../wiki/paige-doherty-behind-genius-ventures-2026-10-15/coverage.md)

This is a fresh synthesis with `gpt-5.6-sol` from the updated Paige Doherty collector export. All 87 previous packet reviews passed fingerprint and content revalidation; Sol reviewed the additional 372 packets in 26 batches. No date cutoff was applied. The [earlier wiki](../wiki/_archived/paige-doherty-behind-genius-ventures/README.md) remains unchanged.

## Scope and results

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 328 | 6,483 |
| Text sources reviewed | 82 | 423 |
| Text packets reviewed | 87 | 459 |
| Evidence excerpts | 311 | 455 |
| Context facts | 236 | 382 |
| Admitted source IDs | 68 | 225 |

The source inventory adds 341 transcript text sources to the earlier 82-source inventory. Source counts are not counts of independent interviews: excerpts, transcript variants and repeated reports can overlap. The refreshed memory adds 144 investor-evidence excerpts and 146 context facts.

All 459 packets have review decisions: 255 target, 184 uncertain, 18 other, and 2 unusable. A target packet can contain no useful investment evidence. The admitted source count is distinct from the packet count.

## Remaining coverage gaps

**This memory is partial.** The supplied export has 487 media files without transcripts. The inventory links 680 media files to transcript sources and represents 339 nonempty cached transcript files. These are file counts, not unique-recording counts. The 184 uncertain packet decisions remain visible in the coverage audit and do not supply investor-policy evidence.

No raw media was transcribed during this run. The collector's `processed/year_capped_processing_selection.json` describes an upstream processing selection of the newest 100 uploads per year from Paige's channel. This generation reviewed all text present in the supplied export; it does not establish exhaustive processing of every downloaded recording or every public statement. There were no non-media extraction warnings in the saved inventory. PDF parsing emitted recoverable object-offset warnings; affected extracted text remains in the source snapshot for inspection.

## Validation and claim review

`python -m wiki_build check` passed after generation and again after editorial corrections. Coverage confirms `review_count == packet_count == 459`. Validation checks quotes, attribution constraints, source hashes, citations and artifact consistency; it does not independently establish truth or human-verified speech.

The agent read all three synthesis pages, inspected newly extracted company-relationship claims and selected underlying policy receipts, and corrected:

- An undated statement about attraction to seed investing presented as a chronological allocation change. The wiki now leaves timing and implementation unresolved.
- “Verified speech” wording that overstated automated source attribution.
- A capital-efficiency preference presented as a universal requirement; it is now an inferred diligence consideration.
- “Zen Cape” and “Excel Scout Fund” transcript spellings presented as established entity identities. The spellings remain explicit and unresolved; the corresponding company context claim was qualified too.
- Unrelated BlueCat template text.

These checks are a targeted agent claim review, not human approval or an exhaustive independent re-audit of all 455 excerpts. Fund-size discrepancies, historical holdings, coauthored material and unspecified investment vehicles remain qualified in the wiki.

## Reproduction and provenance

Input: `/home/dpasch01/vclogic-vc-trace-collector/outputs/paige-doherty-behind-genius-ventures`.

The run used this command from the investment-memory checkout:

```bash
python -m wiki_build full-build /home/dpasch01/vclogic-vc-trace-collector/outputs/paige-doherty-behind-genius-ventures \
  --output wiki/paige-doherty-behind-genius-ventures-2026-10-15 \
  --cache-dir .wiki-cache/paige-doherty-2026-10-15 \
  --reviews wiki/_archived/paige-doherty-behind-genius-ventures/source_reviews.json \
  --model gpt-5.6-sol --workers 4 --timeout 1200
```

The output directory must be absent when generating; use a fresh destination for another run. The new wiki includes its inventory, reviewed source packets, evidence/context, prepared sources, coverage, manifest and validation result. Local model prompts, responses, repair attempts and editorial-change notes remain in `.wiki-cache/paige-doherty-2026-10-15/`. Replaying generation alone does not apply the documented post-generation editorial corrections.

The repository's generator code was unchanged. No downstream onboarding bundle or retrieval index was rebuilt by this run.
