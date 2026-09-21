# Mac Conwell: investment memory from the supplied export

[Open the wiki](../wiki/mac-conwell/README.md), [investment policy](../wiki/mac-conwell/persona.md), [themes](../wiki/mac-conwell/theses.md), or [reported investments and relationships](../wiki/mac-conwell/portfolio_and_constraints.md).

The investor is **Mac (McKeever) Conwell of RareBreed Ventures**, as confirmed by the user and the collector’s resolved identity. This run uses **gpt-5.6-sol** for source review, textual attribution review, and synthesis, with **no date cutoff**. The input is the collector’s `outputs/mac-conwell/` export. Original input files were preserved.

## Coverage

| Measure | Result |
|---|---:|
| Original files inventoried | 2,021 |
| Unique text sources, including recovered recordings | 287 |
| Characters submitted for source review | 6,176,324 |
| Source packets reviewed | 485 / 485 |
| Target / other / uncertain / unusable packets | 294 / 143 / 43 / 5 |
| Sources admitted to the memory | 206 |
| Investor evidence excerpts | 885 |
| Source-reported context receipts | 1,094 |
| Rationale labels with evidence | 42 / 44 |
| Downloaded non-placeholder media still lacking a transcript | 0 |

Forty-three packet decisions remain uncertain; their reasons are retained in `coverage.md` and `source_reviews.json`. Source-review completion does not imply that every speaker could be identified.

The review covers saved articles, PDF text, full diarized transcripts, and recovered recordings. Repeated versions of an interview may remain separate text sources; excerpt and source counts are not counts of independent corroboration. The 152 records in `corpus/reviewer_approved_documents.jsonl` were checked against `processed/documents.jsonl`: all their normalized texts were already represented. The approval export is a derivative, not additional missing material or proof that every record is about Mac.

## Media recovery and attribution

Eight collected audio files lacked linked transcripts. They were transcribed with local Whisper turbo and diarized with Pyannote 3.1. Speaker matching used the collector’s human-approved Mac reference profile, with a 0.75 score threshold and 0.10 margin threshold. The [transcript supplement](../supplements/mac-conwell.json) preserves the source URLs, media hashes, duration, speaker labels, and acoustic attribution results.

Three of these files are approximately 60-second Spotify previews: Investing in Startups E10, High Flyers, and GHOGH episode 31. They are not full episodes. Longer recovered recordings include Seed to Harvest, 20VC, Winners Welcome, Building Out Loud, and Venture Unlocked 020. The Winners Welcome recording features another investor; collection into Mac’s folder does not establish that its speech is his.

The ninth flagged original is an InvestHer webpage’s `placeholder_audio.mp3`, not the advertised interview. Its derived WAV is the same placeholder. Fifteen original/derived media files were linked to recovered transcripts; the two placeholder files were classified separately. The reference-voice WAV is an identity asset, not an unprocessed interview. The [media audit](../supplements/mac-conwell-media-audit.json) records the nine originals and their dispositions; `inventory.json` records the derivative links.

Five source-level textual speaker resolutions are stored in the [identity supplement](../supplements/mac-conwell-identity.json): BITTechTalk episode 110, Startup Mac Vlog E17, the existing and recovered versions of 20VC, and recovered Building Out Loud. These use named introductions or self-identification and exact supporting passages. They are marked `accepted_textual_review`, retaining the original acoustic status; they are not upgraded acoustic matches. Other uncertain speakers remain excluded where attribution cannot be established.

## Limits of the collection

The collector’s saved run summary reports partial collection and processing: 329 collection failures, three processing failures, and 69 unresolved candidates. These are the collector’s recorded counts, not a new assessment that each represents a unique missing source. Full episodes behind the three previews and the advertised InvestHer interview were not recovered by browsing. This is a complete review of the supplied usable text and recovered recordings, with a partial underlying collection.

There is no dedicated portfolio export. The portfolio page therefore inventories relationships reported in the reviewed material. It separates RareBreed/TEDCO investments, founder history, advice, fund relationships, and companies discussed as examples. It is not a verified register of Mac’s personal or current holdings. Publication dates are often absent, and collection dates are not substituted for transaction or publication dates.

## Reproduction

The committed wiki contains all reviewed source snapshots, including excluded sources, plus exact quotations, decisions, and coverage. Offline validation does not require the collector checkout:

```bash
python -m wiki_build check wiki/mac-conwell
```

To regenerate synthesis from this exact snapshot and revalidate its saved reviews, use an absent destination and the original export path:

```bash
python -m wiki_build full-build ../vclogic-vc-trace-collector/outputs/mac-conwell \
  --inventory wiki/mac-conwell/inventory.json \
  --reviews wiki/mac-conwell/source_reviews.json \
  --output wiki/mac-conwell-replay \
  --cache-dir .wiki-cache/mac-conwell \
  --model gpt-5.6-sol
```

The snapshot already includes the supplements, speaker resolutions, and audited media dispositions; do not apply them twice. A changed export must be rescanned rather than replaying this old inventory. For a fresh scan of the same original export, the two applicable inputs are `--supplements supplements/mac-conwell.json --identity-resolutions supplements/mac-conwell-identity.json`; separately reconcile derivative/placeholder dispositions using the media audit. Model calls and transcription intermediates remain in ignored local caches.

## Verification

The final wiki passed the independent offline validator with no errors. A cache-only rebuild revalidated all 485 saved packet decisions, made no fresh model calls, and reproduced all 17 Markdown files byte-for-byte. A separate completeness check confirmed that all 42 company names in the longer RareBreed firm-page receipt appear in portfolio table rows.

Independent provenance review checked the eight transcript text hashes, nine original audio hashes, five textual speaker resolutions, WAV parent links, placeholder enclosure, and derivative document coverage. Semantic review caught an accelerator name misread as a startup alias, a conditional competitive benchmark interpreted too broadly, and omissions from the firm-company list. Sol corrected the source interpretations and synthesis; the original quotes were preserved. The [review corrections](../supplements/mac-conwell-review-corrections.json) retain before/after interpretations and source receipts. Local cache provenance links the original synthesis to its Sol semantic repair.

The final follow-up semantic review of all three synthesis pages found no remaining material blockers.

No pipeline code changed in this run. Validation and replay were performed on the generated Mac artifacts.
