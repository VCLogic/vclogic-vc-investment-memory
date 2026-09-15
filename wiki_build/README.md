# Pipeline components

See the root [README](../README.md) for complete-run commands and limitations.

- `inventory.py`: full file census, extraction, deduplication, media coverage, supplemental transcripts and identity receipts.
- `FULL_AGENT.md`, `full_review.py`: Sol identity, attribution, evidence and context review of every source packet; parallel calls and resumable validated reviews.
- `full_build.py`: synthesis of all accepted findings, coverage artifacts, staging and full-build consistency checks.
- `prep_corpus.py`, `AGENT.md`: earlier curated-only preparation and generation policy.
- `config.py`, `taxonomy.json`: Sol defaults and compatible nine-dimension taxonomy.
- `generator.py`: structured Codex calls, cache, bounded repair and curated builds.
- `render.py`: deterministic evidence pages, source index and manifests.
- `check_wiki.py`: offline validation of both source policies.
- `__main__.py`: `inventory`, `full-build`, `prepare`, `build`, `check` commands.

Programmatic full preparation: `from wiki_build.inventory import inventory`.
Programmatic validation: `from wiki_build.check_wiki import validate`.
An empty validation error list confirms mechanical consistency, not semantic correctness of every inference.
