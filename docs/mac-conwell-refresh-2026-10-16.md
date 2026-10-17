# Mac Conwell — October 16, 2026 refresh

[Open the refreshed wiki](../wiki/mac-conwell-2026-10-16/README.md) · [Investment policy](../wiki/mac-conwell-2026-10-16/persona.md) · [Theses](../wiki/mac-conwell-2026-10-16/theses.md) · [Portfolio](../wiki/mac-conwell-2026-10-16/portfolio_and_constraints.md) · [Coverage](../wiki/mac-conwell-2026-10-16/coverage.md)

Fresh synthesis with `gpt-5.6-sol` from Mac Conwell's updated collector export, with no date cutoff. All 485 earlier packet reviews passed fingerprint and content revalidation; Sol reviewed 607 additional packets in 207 batches. The [earlier wiki](../wiki/_archived/mac-conwell/README.md) remains unchanged.

## Scope

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 2,021 | 3,759 |
| Text sources reviewed | 287 | 549 |
| Text packets reviewed | 485 | 1,092 |
| Evidence excerpts | 885 | 2,082 |
| Context facts | 1,094 | 1,971 |
| Admitted source IDs | 206 | 310 |

The snapshot includes 367 transcript and 182 web sources, including eight previously recovered transcript supplements. Counts include overlapping excerpts, variants and repeated reports; they are not counts of independent interviews. All 1,092 packets have review decisions: 504 target, 389 other, 192 uncertain and 7 unusable. A target packet can contain no useful investment evidence.

## Remaining coverage gaps

**This memory is partial.** Fourteen media files still lack transcripts. The inventory links 518 media files to regular transcripts and 15 to previously recovered transcripts, represents 259 cached transcript files, and excludes two copies of placeholder website audio. These are file counts, not unique recordings. Three previously recovered Spotify recordings are approximately one-minute previews, not complete episodes. The 192 uncertain packets remain visible in the audit and do not contribute investor-policy evidence. No new transcription or web collection was performed during this refresh.

## Generation and provenance

Input: `/home/dpasch01/vclogic-vc-trace-collector/outputs/mac-conwell`.

The fresh inventory was augmented with the existing `supplements/mac-conwell.json`, five textual speaker resolutions from `supplements/mac-conwell-identity.json`, and the prior media audit. Original media hashes, derivative hashes and textual resolution quotes were checked before reuse. The selected reference clip was classified as a reference asset using its selection receipt; no new acoustic identity verification was performed.

An empty optional identity field introduced while applying resolutions initially invalidated the prior fingerprints. The initial run was stopped, the empty field omitted, and all 485 unchanged prior reviews then revalidated. Three new batches required an additional bounded Sol repair for exact-quote mismatches; original responses and repair provenance remain in the local cache. Validation was not bypassed.

Final synthesis resumed with the complete validated review ledger:

```bash
python -m wiki_build full-build /home/dpasch01/vclogic-vc-trace-collector/outputs/mac-conwell \
  --output wiki/mac-conwell-2026-10-16 \
  --cache-dir .wiki-cache/mac-conwell-2026-10-16 \
  --inventory .wiki-cache/mac-conwell-2026-10-16/inventory.json \
  --reviews .wiki-cache/mac-conwell-2026-10-16/reviews.json \
  --model gpt-5.6-sol --workers 8 --timeout 1200
```

Use an absent destination for another run. This saved inventory intentionally replays the reviewed snapshot; it cannot establish coverage of subsequent collector changes. The output retains inventory, reviews, evidence/context ledgers, source snapshots and coverage. Local prompts, raw responses and repairs remain in the ignored cache. No downstream onboarding bundle or retrieval index was rebuilt.

The synthesis input initially exceeded the 650,000-character limit. A small generator change stores repeated rationale labels, directions, support types and context kinds in per-table dictionaries. Decoding restores every original value; all findings and source records reach synthesis. The resulting input is 629,656 characters. Exact quotes remain in the wiki ledgers. The full 55-test suite passes, including a round-trip test and a check that small tables avoid counterproductive encoding.

## Validation and claim review

The generated wiki and final editorial version both passed `python -m wiki_build check`. Coverage confirms `review_count == packet_count == 1092`. Synthesis needed one bounded repair for a citation with a missing leading zero. All 55 tests passed; independent code review found no blockers. The actual Mac synthesis payload also round-tripped exactly, including every source, evidence and context value.

The agent read all three synthesis pages, the coverage summary and build report, and checked selected policy and relationship receipts. A separate agent reviewed portfolio claims. Editorial corrections:

- Preserved all 42 exact firm-page company names and the earlier non-investment roles, remapping citations only where source IDs and exact quotes matched.
- Kept Electric/Accelerated Dream Adventures as an accelerator relationship, not a startup name. Preserved the conditional treatment of traction benchmarks rather than inventing universal product, team or revenue gates.
- Qualified ScholarMe/ScalarMe and WoveMade/Wove entity equivalence; removed an irrelevant BlueCat reference.
- Corrected the claim that SuperCircle lacked a primary relationship receipt: the firm lists “Supercircle,” without transaction details.
- Distinguished ClearMask company milestones from investment dates, and removed unsupported interview ordering for Rebundle and Elite Gaming Live.
- Distinguished Tracxn’s conflicting founding year from investment counts reported at different dates, which can reflect growth.
- Added the unnamed Uganda-based Fund I investment; narrowed the geography summary to its cited receipts.
- Replaced “verified speech” with “attributed speech” and described traction as a preference rather than a universal requirement.

Structured evidence and context were unchanged; citation IDs and counts remain stable. Original synthesis pages and the editorial script remain in the local cache. Replaying generation alone does not apply these editorial corrections.

Mechanical validation checks exact quotes, attribution constraints, source hashes, citations and artifact consistency. It does not independently establish truth or logical entailment. This was targeted agent review, not human approval or an exhaustive re-audit of every excerpt. The earlier wiki remains unchanged.
