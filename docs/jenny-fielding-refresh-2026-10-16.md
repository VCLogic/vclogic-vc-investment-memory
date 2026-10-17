# Jenny Fielding — October 16, 2026 refresh

[Open the refreshed wiki](../wiki/jenny-fielding-everywhere-ventures-2026-10-16/README.md) · [Investment policy](../wiki/jenny-fielding-everywhere-ventures-2026-10-16/persona.md) · [Theses](../wiki/jenny-fielding-everywhere-ventures-2026-10-16/theses.md) · [Portfolio](../wiki/jenny-fielding-everywhere-ventures-2026-10-16/portfolio_and_constraints.md) · [Coverage](../wiki/jenny-fielding-everywhere-ventures-2026-10-16/coverage.md)

Fresh synthesis with `gpt-5.6-sol` from the updated collector export, with no date cutoff. All 126 previous packet reviews passed fingerprint and content revalidation; Sol reviewed the additional 647 packets in 209 batches. The [earlier wiki](../wiki/_archived/jenny-fielding-everywhere-ventures/README.md) remains unchanged.

## Scope

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 345 | 2,145 |
| Text sources reviewed | 97 | 406 |
| Text packets reviewed | 126 | 773 |
| Evidence excerpts | 21 | 1,724 |
| Context facts | 239 | 1,336 |
| Admitted source IDs | 91 | 226 |

The inventory adds 309 transcript text sources to the earlier 97 web sources. Counts include overlapping excerpts, transcript variants and repeated reports; they are not counts of independent interviews. All 773 packets have review decisions: 359 target, 221 uncertain, 191 other and 2 unusable. A target packet can contain no useful investment evidence.

## Remaining coverage gaps

**This memory is partial.** The export contains seven media files without transcripts. The inventory links 325 media files to transcript sources and represents 161 cached transcript files. These are file counts, not unique recordings. The 221 uncertain packet decisions remain visible in the audit and do not contribute investor-policy evidence. No raw media was transcribed and no additional web collection was performed during this run. There were no non-media extraction warnings in the saved inventory.

## Generation and provenance

Input: `/home/dpasch01/vclogic-vc-trace-collector/outputs/jenny-fielding-everywhere-ventures`.

```bash
python -m wiki_build full-build /home/dpasch01/vclogic-vc-trace-collector/outputs/jenny-fielding-everywhere-ventures \
  --output wiki/jenny-fielding-everywhere-ventures-2026-10-16 \
  --cache-dir .wiki-cache/jenny-fielding-2026-10-16 \
  --reviews wiki/_archived/jenny-fielding-everywhere-ventures/source_reviews.json \
  --model gpt-5.6-sol --workers 8 --timeout 1200
```

One review batch retained a capitalization mismatch in a quoted passage after its bounded repair. The run resumed from the accepted caches and saved inventory, using the previously repaired response as the starting point for another bounded Sol repair. The original response and provenance note remain in the cache; exact-quote checks were not bypassed. All 773 reviews then passed.

The synthesis input used lossless indexed tables and shared citation prefixes, preserving all extracted interpretations, context claims and source records within 540,514 characters. Verbatim receipts remain in the evidence and context ledgers. No generator code changed for this run.

Use an absent destination for another run. For intentional replay of the same input snapshot, add `--inventory .wiki-cache/jenny-fielding-2026-10-16/inventory.json`; do not use that snapshot to claim coverage of later collector changes. The output retains the inventory, source reviews, evidence/context ledgers, source snapshots, coverage and manifest. Local prompts, responses, repairs and editorial notes remain in `.wiki-cache/jenny-fielding-2026-10-16/`. No downstream onboarding bundle or retrieval index was rebuilt.

## Validation and claim review

The generated wiki passed `python -m wiki_build check`, and the final editorial version passed again. Coverage confirms `review_count == packet_count == 773`. Synthesis required one bounded repair for an uncited thesis bullet. Mechanical validation checks exact quotes, attribution constraints, source hashes, citations and consistency across artifacts; it does not independently verify truth or entailment.

The agent read all three synthesis pages, coverage and the build report, and checked selected policy and relationship receipts. A separate agent reviewed the portfolio claims. Editorial corrections:

- Preserved all 286 exact company/location pairs from the primary firm portfolio receipt, verified unchanged from the earlier wiki. This appendix identifies firm-reported relationships, not Jenny’s personal holdings or deal leadership. Interview appearances remain distinct from the independent portfolio listing.
- Strengthened citations for Switch Mobile’s differing 2006/2007 founding accounts and the Techstars 2022 departure account; retained source disagreements rather than inventing one definitive chronology.
- Qualified Musetac, Iana Therapy and The Crew as transcribed names with unresolved spelling/entity equivalence, in both structured context and prose.
- Added the reported New York State venture-fund advisory role and Bitcoin exposure, without turning encouragement to buy in 2015 into a confirmed purchase date.
- Expanded the existing The Pitch context receipt with exact portfolio-card text. Its two $50,000 records total $100,000 but link to episode titles, so company identities and investment vehicle remain unresolved. Episode titles were not converted into company names.
- Added stronger primary firm-list evidence for Particle Health and Clean Cult, and clarified BBC Worldwide’s stated investment in Viki without inferring personal ownership.
- Labelled synthesized defensibility questions as inferred and tentative, and bounded the solo-team preference to its source.

Structured reviews, prepared data and context were regenerated consistently; citation IDs and final counts did not change. Original generated files and editorial notes remain in the local cache. Replaying generation alone does not apply these documented editorial corrections.

This was targeted agent review, not human approval or an exhaustive independent re-audit of all 1,724 evidence excerpts. The earlier wiki is unchanged. No code changes were needed, so validation focused on the actual generated artifacts and documentation links.
