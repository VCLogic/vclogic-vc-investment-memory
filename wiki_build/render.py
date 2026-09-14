"""Deterministic Markdown rendering; never let the generator choose output paths."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from .config import DIMENSIONS, LABELS
from .prep_corpus import normalized


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def evidence_page(dimension, entries):
    blocks = [f'# {dimension}', 'Verbatim transcript excerpts; whitespace normalized. Labels describe the cited statement.']
    for e in entries:
        if LABELS.get(e['label']) != dimension:
            continue
        blocks.append(f"[ev:{e['id']}] label={e['label']} direction={e['direction']} source={e['source']}\n"
                      f"> \"{normalized(e['quote'])}\"\n\n"
                      f"Support: {e['support']}. Interpretation: {e['interpretation']}")
    if len(blocks) == 2:
        blocks.append('Insufficient evidence in the admitted corpus.')
    return '\n\n'.join(blocks) + '\n'


def render(path, prepared, entries, synthesis, generation):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    (path / 'evidence').mkdir()
    for dimension in DIMENSIONS:
        (path / 'evidence' / f'{dimension}.md').write_text(evidence_page(dimension, entries), encoding='utf-8')
    for key, filename in [('persona', 'persona.md'), ('theses', 'theses.md'),
                          ('portfolio_and_constraints', 'portfolio_and_constraints.md')]:
        (path / filename).write_text(synthesis[key].strip() + '\n', encoding='utf-8')
    source_index = ['# Source index', 'The prepared snapshot retains full admitted text and attribution metadata.']
    for d in prepared['documents']:
        source_index.append(f"## {d['doc_id']}\n\n{d['title']}\n\n"
                            f"URL: {d.get('url') or 'Unknown'}\n\nPublication date: {d.get('published_at') or 'Unknown'}\n\n"
                            f"Input: `{d['input_path']}:{d['input_line']}`\n\nSHA-256: `{d['sha256']}`")
    (path / 'sources.md').write_text('\n\n'.join(source_index) + '\n', encoding='utf-8')
    enriched = []
    docs = {d['doc_id']: d for d in prepared['documents']}
    for e in entries:
        start = normalized(docs[e['source']]['text']).find(normalized(e['quote']))
        enriched.append({**e, 'normalized_char_start': start,
                         'normalized_char_end': start + len(normalized(e['quote']))})
    write_json(path / 'evidence.json', enriched)
    write_json(path / 'prepared.json', prepared)
    manifest = {k: prepared[k] for k in ('vc_slug', 'corpus_chars', 'thin_corpus', 'no_pitch_sources')}
    manifest.update(sources_consumed=[d['doc_id'] for d in prepared['documents']],
                    evidence_count=len(entries), persona_tokens=math.ceil(len(synthesis['persona'].strip() + '\n') / 4),
                    persona_tokens_method='ceil_characters_divided_by_4_estimate', taxonomy_version='v_final',
                    generated_at=datetime.now(timezone.utc).isoformat(), schema_version='1.0',
                    generation=generation, warnings=prepared['warnings'],
                    input_hashes=prepared['input_hashes'])
    write_json(path / '_manifest.json', manifest)
    lines = ['# Build report', f"Investor: {prepared['vc_slug']}",
             f"Generator: {generation.get('model', 'unknown')}",
             f"Sources: {len(prepared['documents'])}; evidence excerpts: {len(entries)}.",
             '## Data limitations'] + ['- ' + w for w in prepared['warnings']]
    lines += ['\n## Coverage', '| Dimension | Evidence excerpts |', '|---|---:|']
    for dimension in DIMENSIONS:
        lines.append(f"| {dimension} | {sum(LABELS[e['label']] == dimension for e in entries)} |")
    lines += ['\n## Interpretation limits',
              'Quotes match the supplied transcript, not independently checked audio. Automated validation checks '
              'provenance and structure, not whether a synthesis logically follows. Inferred heuristics are '
              'tentative; missing evidence does not establish a negative preference. See sources.md and prepared.json.']
    (path / 'BUILD_REPORT.md').write_text('\n\n'.join(lines[:6]) + '\n' + '\n'.join(lines[6:]) + '\n', encoding='utf-8')
    (path / 'README.md').write_text(
        f"# {prepared['identity']['canonical_name']} — investment memory\n\n"
        '[Decision policy](persona.md) · [Theses](theses.md) · '
        '[Portfolio and constraints](portfolio_and_constraints.md) · [Sources](sources.md) · '
        '[Build report](BUILD_REPORT.md)\n\n'
        'This is a source-grounded research memory. Read the evidence and uncertainty notes before treating '
        'an inferred heuristic as an investment rule.\n', encoding='utf-8')
