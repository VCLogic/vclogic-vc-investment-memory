# Mark Phillips — October 16, 2026 refresh

[Open the refreshed wiki](../wiki/mark-phillips-11-tribes-ventures-2026-10-16/README.md) · [Investment policy](../wiki/mark-phillips-11-tribes-ventures-2026-10-16/persona.md) · [Theses](../wiki/mark-phillips-11-tribes-ventures-2026-10-16/theses.md) · [Portfolio](../wiki/mark-phillips-11-tribes-ventures-2026-10-16/portfolio_and_constraints.md) · [Coverage](../wiki/mark-phillips-11-tribes-ventures-2026-10-16/coverage.md)

Fresh synthesis with `gpt-5.6-sol` from the updated collector export, with no date cutoff. All 56 previous packet reviews passed fingerprint and content revalidation; Sol reviewed 378 additional packets in 110 batches. The [earlier wiki](../wiki/mark-phillips-11-tribes-ventures/README.md) remains unchanged.

## Scope

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 238 | 1,648 |
| Text sources reviewed | 54 | 267 |
| Text packets reviewed | 56 | 434 |
| Evidence excerpts | 85 | 443 |
| Context facts | 143 | 413 |
| Admitted source IDs | 52 | 99 |

The inventory adds 213 transcript sources to the previous 54 web sources. Counts include transcript variants, overlapping excerpts and repeated reports, not independent interviews. All 434 packets have decisions: 161 target, 151 other, 114 uncertain and 8 unusable. All uncertain decisions concern transcript packets. A target packet can contain no decision-relevant evidence. Of the evidence excerpts, 317 are labelled explicit and 126 inferred.

## Remaining coverage gaps

**This memory is partial.** Thirty-three media files lack linked transcripts, including some duplicate recordings and short preview clips. The inventory links 235 media files to transcript sources and represents 116 cached transcript files; these are file counts, not unique recordings. One saved HTML page contains no visible text. There were no non-media extraction warnings. The 114 uncertain packet decisions remain visible in the audit and do not contribute investor-policy evidence. No new transcription or web collection was performed during this run.

## Generation and provenance

```bash
python -m wiki_build full-build /home/dpasch01/vclogic-vc-trace-collector/outputs/mark-phillips-11-tribes-ventures \
  --output wiki/mark-phillips-11-tribes-ventures-2026-10-16 \
  --cache-dir .wiki-cache/mark-phillips-2026-10-16 \
  --reviews wiki/mark-phillips-11-tribes-ventures/source_reviews.json \
  --model gpt-5.6-sol --workers 8 --timeout 1200
```

One batch retained a context quote shorter than the validator's minimum length after its normal bounded repair. Generation resumed from the saved inventory and accepted caches, using the repaired response as the starting point for another bounded Sol repair. Original responses and a provenance note remain in the cache; quote and speaker checks were not bypassed. All 434 reviews then passed.

The final synthesis received all 443 evidence excerpts, 413 context facts and admitted source records in 481,496 characters; no size reduction was needed. Use an absent destination for another run. To replay this exact snapshot, add `--inventory .wiki-cache/mark-phillips-2026-10-16/inventory.json`; that snapshot cannot establish coverage of later collector additions.

The output retains the inventory, source reviews, evidence/context ledgers, full source snapshots, coverage and manifest. Local prompts, raw responses, repairs and editorial notes remain in the ignored cache. No downstream onboarding bundle or retrieval index was rebuilt.

## Validation and claim review

The generated wiki and final editorial version both passed `python -m wiki_build check`. Coverage confirms `review_count == packet_count == 434`. Synthesis needed one bounded repair for two uncited thesis bullets; Sol converted the unsupported-asset-class summaries to prose. No generator code changed.

The agent read all three synthesis pages, the build report and coverage summary, and checked selected policy and relationship receipts. A separate agent reviewed portfolio claims. Editorial corrections:

- Preserved all earlier named investments, and retained the unresolved company identity behind the episode title “Josh Pitches The Pitch.”
- Confirmed NQS's initial check, valuation, March 2025 round date, Long Run Capital leadership, Phillips's governance-board role and the reported follow-ons against their receipts. Follow-on timing remains unclear where only relative dates are given.
- Qualified “Cylon” and Cyber Popup/company-founder spellings as transcript renderings in both the structured context and portfolio page. Retained the existing Rise spelling caveat and restored the caveat that Alloy naming variants are not explicitly reconciled.
- Restored The Table Group's founder-summit relationship as program collaboration, and retained the historical qualifying-stock/five-year holding expectation without presenting it as a tax determination.
- Added the missing receipt supporting the earlier eight-company Fund II count.
- Corrected the valuation summary: a sub-$8 million pre-money target came from an early Fund II fundraising account, not a Fund I rule.
- Removed the unsupported implication that an undated preferred revenue range is necessarily current, and qualified differing investment-committee descriptions rather than asserting a precisely established governance change.

Structured source reviews, prepared data and context were regenerated consistently; counts and citation IDs did not change. Original generated files and the editorial script remain in the local cache. Replaying generation alone does not apply the documented editorial corrections.

Mechanical validation checks quotes, attribution constraints, source hashes, citations and consistency across artifacts. It does not independently establish truth or logical entailment. This was targeted agent review, not human approval or an exhaustive re-audit of every excerpt. The earlier wiki is unchanged.
