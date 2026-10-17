# Sheel Mohnot — October 16, 2026 refresh

[Open the refreshed wiki](../wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16/README.md) · [Investment policy](../wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16/persona.md) · [Theses](../wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16/theses.md) · [Portfolio](../wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16/portfolio_and_constraints.md) · [Coverage](../wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16/coverage.md)

Fresh synthesis with `gpt-5.6-sol` from the updated collector export, with no date cutoff. All 60 previous packet reviews passed fingerprint and content revalidation; Sol reviewed the additional 802 packets in 249 batches. The [earlier wiki](../wiki/_archived/sheel-mohnot-better-tomorrow-ventures/README.md) remains unchanged.

## Scope

| Measure | Earlier wiki | Refreshed wiki |
|---|---:|---:|
| Files inventoried | 263 | 2,407 |
| Text sources reviewed | 53 | 459 |
| Text packets reviewed | 60 | 862 |
| Evidence excerpts | 98 | 1,894 |
| Context facts | 238 | 1,204 |
| Admitted source IDs | 49 | 184 |

The inventory contains 406 transcript text sources and 53 web sources. Counts include overlapping excerpts, transcript variants and repeated reports; they are not counts of independent interviews. All 862 packets have review decisions: 315 target, 279 uncertain, 265 other and 3 unusable. A target packet can contain no useful investment evidence.

## Remaining coverage gaps

**This memory is partial.** The supplied export contains 20 media files without transcripts. The inventory links 426 media files to transcript sources and represents 211 cached transcript files. These are file counts, not unique recordings. The 279 uncertain packet decisions remain visible in the audit and do not contribute investor-policy evidence. No raw media was transcribed during this run; no additional web collection was performed. There were no non-media extraction warnings in the saved inventory.

## Generation and provenance

Input: `/home/dpasch01/vclogic-vc-trace-collector/outputs/sheel-mohnot-better-tomorrow-ventures`.

The initial full-build used the earlier wiki's `source_reviews.json`, four Sol workers and a 1,200-second per-call timeout. It resumed from accepted caches with eight workers and the saved inventory. One final quote mismatch required a further bounded Sol repair from the previous repair response; the original response and resume notes remain in the local cache. Quote validation was not bypassed.

The combined synthesis exceeded the 650,000-character input guard after existing lossless table indexing. The engine now also stores repeated citation ID prefixes once per table, explicitly instructing the generator to reconstruct full IDs. This reduced this input from 662,767 to 545,251 characters without removing interpretations, context claims or source records. Exact quotes remain in the complete evidence/context ledgers. A failing-first round-trip regression test verifies the encoding, including leading zeroes, long numeric suffixes, mixed prefixes and input immutability; all 54 tests passed.

The synthesis resume command was:

```bash
python -m wiki_build full-build /home/dpasch01/vclogic-vc-trace-collector/outputs/sheel-mohnot-better-tomorrow-ventures \
  --output wiki/sheel-mohnot-better-tomorrow-ventures-2026-10-16 \
  --cache-dir .wiki-cache/sheel-mohnot-2026-10-16 \
  --reviews .wiki-cache/sheel-mohnot-2026-10-16/reviews.json \
  --inventory .wiki-cache/sheel-mohnot-2026-10-16/inventory.json \
  --model gpt-5.6-sol --workers 8 --timeout 1200
```

Use an absent output destination for another run. The generated wiki retains its inventory, reviewed packets, source snapshot, evidence/context ledgers, coverage and manifest. Local prompts, raw responses and repairs remain in `.wiki-cache/sheel-mohnot-2026-10-16/`. No downstream onboarding bundle or retrieval index was rebuilt.

## Validation and claim review

`python -m wiki_build check` passed on the generated wiki and after editorial corrections. Coverage confirms `review_count == packet_count == 862`. The synthesis required one automatic repair for an uncited bullet; the repaired output passed citation checks. Validation checks exact source quotes, attribution constraints, source hashes, citations and artifact consistency. It does not independently establish truth or human-verified speech.

The agent read all three synthesis pages and inspected selected policy and company-relationship receipts. A separate agent performed targeted portfolio review. Corrections included:

- Qualifying automated attribution rather than claiming “verified speech,” marking trust-building operating advice as an inferred selection preference, and removing an unsupported causal explanation connecting biography to investment preferences.
- Binding the built-product requirement to its source rather than presenting it as a confirmed present-day policy.
- Replacing the Innovative Auctions exit citation with a receipt that explicitly supports 2015, and removing Agree’s unsupported “official partnership” label.
- Restoring Simple as a 500 Startups investment, The Mint as BTV’s accelerator, and Village Global as a reported network role.
- Adding one exact-quote context receipt for Signal’s visible investment table, which extraction omitted. This retains howie, Ethos, Nilus and Kaaj AI as unverified aggregator associations, without conflating Ethos with Ethic or assuming Kaaj AI equals transcript “Kaj.” The page also contains corrupted employment listings, explicitly limiting confidence. The context count increased from 1,203 generated receipts to 1,204 after agent editorial review. All subsequent context IDs were remapped in the narrative pages, and structured reviews, prepared sources, context ledger and manifest were regenerated consistently.

These are targeted agent checks, not human approval or an exhaustive independent re-audit of all 1,894 evidence excerpts. The original Sol output and editorial notes are retained locally. Replaying generation alone does not apply these documented editorial corrections. The old wiki remains unchanged.
