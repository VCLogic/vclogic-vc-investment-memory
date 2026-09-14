# Michael Hyatt trial — 2026-09-14

Completed a real end-to-end run with **gpt-5.6-sol**, producing [the wiki](../wiki/michael-hyatt/README.md) and [decision policy](../wiki/michael-hyatt/persona.md).

## Result

- 3 canonical, admitted talk documents; 50,103 characters; 4 bounded source chunks.
- 32 verbatim evidence excerpts: 14 tagged explicit, 18 tagged inferred.
- All nine evidence pages and persona sections, plus theses, portfolio/constraints, source index, prepared snapshot, manifest and build report.
- Zero verified portfolio records. Holdings, current mandate, stage and check-size parameters remain unknown.
- 28 offline regression tests pass. Independent new validator passes. The previous repository's validator also passes and parses all 32 evidence definitions.
- Cache-only replay used five cached responses and reproduced every Markdown file byte-for-byte. Timestamp and cache-use metadata naturally differ.
- Built a standalone wheel and successfully ran its preparation command from an isolated temporary directory, without importing the repository package or previous pipeline.
- Original canonical corpus, resolved identity and portfolio file hashes still match their pre-generation values. Raw input data was not changed.

## Semantic review

Read all 32 extracted quotations/interpretations and the three generated pages. The strongest direct themes are long-term founder relationships, character, ambition, customer purchases and expansion purchases, a personal B2B preference, selective use of the investor's time, and willingness to syndicate for helpful partners. The family-office/no-deployment-pressure description is an attributed historical statement, not independently verified current organization data.

General operating advice about focus, perseverance, bootstrapping and incremental progress is marked inferred. Technology forecasts remain historical/undated; their factual numbers were not independently verified. The synthesis does not turn cofounder affiliations into holdings or invent numerical investment gates. Several dimensions reuse related evidence from other taxonomy dimensions; zero exclusively tagged excerpts in a dimension does not mean its prose is uncited. Market/defensibility/terms coverage is weak and deserves caution.

This was a source-faithfulness review, not investment advice, current-fact verification, audio re-transcription or validation of how the real investor would decide on a new deal. Three video documents do not necessarily represent three independent bodies of evidence.

## Trial-driven fixes

The first extraction attempt for one chunk returned its URL instead of its document ID. Quote/source validation rejected it; the extraction schema now constrains the source to exactly the current document ID.

The first synthesis included an example portfolio citation token in an explanation of missing data. Portfolio-reference validation rejected it. A bounded repair call to Sol removed that template artifact; persona and theses were preserved. Generated text was not manually rewritten to obtain a pass.

An independent code review identified and confirmed fixes for contradictory legacy attribution, portfolio citation checks, snapshot hashes/offsets, and source dates reaching synthesis. The reviewer reported no remaining must-fix findings in that scope.

## Run accounting

Nine model requests completed across initial attempts, corrected extraction and synthesis repair. CLI logs report 245,439 input tokens (including 27,264 cached input tokens), 18,433 output tokens, and 2,219 reasoning output tokens. These are recorded CLI usage fields, not an independently calculated bill. The successful pipeline consists of four extraction stages and one synthesis stage; only accepted results are reusable.

No model tool actions appeared in the generation event logs. The installed CLI reported an existing local hooks.json format warning; it did not prevent the model requests or structured output. User configuration was not modified.

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m wiki_build check wiki/michael-hyatt
python -m wiki_build build data/michael-hyatt --output wiki/michael-hyatt-rebuild
```

The original output is deliberately protected from overwrite. Source snapshots and generated wiki are present in the repository; the 1.9 GB input export and local `.wiki-cache/` remain ignored by git and available in this workspace. Fresh model calls require authenticated Codex access; preparation and checking do not.
