# Investor Memory Implementation Plan

**Goal:** Generate a cited investor wiki from the new export using Sol.
**Architecture:** Standard-library Python prepares an auditable snapshot, calls Codex Sol with bounded structured prompts, renders a compatible wiki and checks it before publication.
**Tech Stack:** Python 3.11+, unittest, installed authenticated Codex CLI, Markdown/JSON.

- [x] Add source-admission regression fixtures in tests/test_prep_corpus.py; run `python -m unittest discover -s tests -v` and observe missing implementation. Implement wiki_build/prep_corpus.py with canonical precedence, identity checks, clean-manifest requirement, source filtering, deduplication and provenance; rerun.
- [x] Add evidence and wiki validation fixtures in tests/test_check_wiki.py; demonstrate rejection of invented quotes, duplicate IDs, wrong dimensions, uncited claims, unknown references and missing files. Implement wiki_build/check_wiki.py and deterministic rendering in wiki_build/render.py; rerun.
- [x] Add transport/cache and pipeline tests in tests/test_pipeline.py. Implement wiki_build/generator.py with Sol subprocess invocation, timeout, content-addressed cache and structured JSON schemas; implement wiki_build/__main__.py prepare/build/check commands. Keep input roots disjoint from output destinations.
- [x] Write agent instructions in wiki_build/AGENT.md, package metadata and README.md with no external-repository runtime dependencies. Extract only label/definition/coarse_parent fields to wiki_build/taxonomy.json.
- [x] Execute `python -m wiki_build build data/michael-hyatt --output wiki/michael-hyatt`. Review generated claims against exact evidence, repair any systematic defects, run offline suite and independent check. Record real run counts, limitations and reproduction commands in docs/hyatt-trial.md.

Execute inline, preserving the user's source data. The requested Sol generator performs the bounded extraction/synthesis work. No additional implementation agents needed.
