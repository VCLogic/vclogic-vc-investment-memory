# Pipeline components

See the root [README](../README.md) for commands, schemas and operational limits.

- `prep_corpus.py`: curated export admission, deduplication and provenance.
- `config.py`, `taxonomy.json`: Sol/model defaults and compatible nine-dimension taxonomy.
- `AGENT.md`: evidence extraction and synthesis instructions used in every Sol call.
- `generator.py`: bounded chunks, structured Codex responses, validation-aware cache, staging.
- `render.py`: deterministic evidence files, source index and manifests.
- `check_wiki.py`: offline evidence and wiki validation.
- `__main__.py`: `prepare`, `build`, `check` commands.

Programmatic preparation: `from wiki_build.prep_corpus import prepare; prepared = prepare(path)`.
Programmatic validation: `from wiki_build.check_wiki import validate; errors = validate(wiki_dir)`.
An empty errors list means the mechanical checks passed, not that every inference is justified.
