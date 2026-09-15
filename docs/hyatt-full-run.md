# Michael Hyatt: complete collection run

This run replaces the three-talk pilot with a complete review of the locally collected Hyatt export. The Python tool and all extraction/synthesis calls use the full-export pipeline, with **gpt-5.6-sol** as generator.

| Measure | Result |
|---|---:|
| Original files inventoried | 1,082 |
| Unique text sources, including recovered interview | 250 |
| Characters submitted for source review | 3,290,406 |
| Source packets reviewed | 317 / 317 |
| Target / other / uncertain / unusable packets | 168 / 135 / 5 / 9 |
| Sources admitted to the memory | 146 |
| Investor evidence excerpts | 328 |
| Source-reported context receipts | 483 |
| Downloaded media still missing a transcript | 0 |

The pilot reviewed three curated talks and produced 32 excerpts. The complete run includes saved web pages, PDFs, full audiovisual transcripts, and portfolio reports; namesakes and unusable pages remain visible in the coverage ledger. Counts include repeated reporting and are not counts of independent corroborating witnesses.

## Repairs and attribution

One downloaded Tank Talk interview had no transcript. It was transcribed with Whisper turbo, diarized, and matched to the collector’s Hyatt reference voice: accepted-model score 0.854694, margin 0.325857. The separately stored supplement preserves the recovered transcript, original media reference, and attribution metadata. The original input directory was not edited.

The E55 interview failed the acoustic acceptance threshold. A separate Sol review confirmed textual attribution from the host’s named introduction and the responding speaker’s matching BlueCat/Dyadem biography. It is explicitly marked `accepted_textual_review`; the original uncertain acoustic status is retained.

The authoritative investor profile links to Hyatt’s LinkedIn account. Saved HTML comment-author links establish the author of the Bounce seed-investment comment and Float congratulations. Saved JSON-LD links three misspelled aggregator listings to that same account. These identity receipts establish which person is described; they do not independently verify the aggregator’s portfolio statistics or turn congratulations into an investment.

Five packets remain uncertain: an unattributed CREATE clip, two text-only copies of a Float comment, an unresolved Michael W. Hyatt preview, and a Tracxn listing without a conclusive identity anchor. The linked HTML versions of the Float comment are included. All five uncertain decisions remain in `source_reviews.json` and `coverage.md`.

## Reproduction and review

```bash
python -m wiki_build full-build data/michael-hyatt \
  --output wiki/michael-hyatt-rebuild \
  --supplements supplements/michael-hyatt.json \
  --identity-resolutions supplements/michael-hyatt-identity.json
python -m wiki_build check wiki/michael-hyatt-rebuild
python -m unittest discover -s tests -v
```

The collection is deliberately ignored by Git. The committed wiki contains source snapshots and receipts needed for offline validation. Model prompts and raw call logs remain in the local `.wiki-cache/full-review` directory.

This run used an initial full review followed by targeted re-review of uncertain packets as identity receipts were established. Original review-prompt provenance is preserved; earlier reviews are not relabelled as having received later identity context. Future `--reviews` reuse requires the exact current identity/packet/policy fingerprint, so changed policies or metadata may cause an earlier review to run again.

The memory distinguishes reported direct investments, family-office activity, founder exits, advisory roles, board seats, and weaker aggregator claims. It is a complete processing of the available collection, not an independently verified register of current holdings. Publication dates are sparse; historical opinions and forecasts should be read in their source context.

## Verification

The offline suite has 51 passing tests, including wrong-speaker quotes, chunk-boundary speaker attribution, fuller cached transcripts, stale identity-review reuse, unconfirmed speaker resolutions, source-linked comment/JSON-LD identity receipts, uncited portfolio rows, rejected-source hash tampering, and manifest/coverage consistency. A code review found no remaining implementation blockers. A semantic review corrected inferred decision gates and an unsupported DataStealth closing date in the synthesis instructions.

The final wiki passed the independent offline validator. A cache-only rebuild, configured to fail on any fresh model invocation, reproduced all 17 Markdown files byte-for-byte. The final three synthesis pages passed follow-up semantic review. The package wheel built successfully with both agent instruction files included.
