"""Offline structural and source-grounding checks for generated investment memories."""
import json
import re
from pathlib import Path

from .config import DIMENSIONS, LABELS
from .prep_corpus import normalized, digest
from .render import evidence_page

CITATION = re.compile(r'\[ev:([^\]\s]+)\]')


def validate_evidence(entries, prepared):
    if not isinstance(entries, list):
        return ['evidence must be a list']
    errors, seen = [], set()
    docs = {d['doc_id']: d for d in prepared['documents']}
    for index, e in enumerate(entries):
        if not isinstance(e, dict):
            errors.append(f'evidence {index}: expected object'); continue
        eid = e.get('id', f'index-{index}')
        if eid in seen:
            errors.append(f'duplicate evidence ID {eid}')
        seen.add(eid)
        if not isinstance(eid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', eid):
            errors.append(f'{eid}: invalid evidence ID')
        if e.get('label') not in LABELS:
            errors.append(f'{eid}: label not in codebook: {e.get("label")}')
        if e.get('direction') not in ('positive', 'negative', 'neutral'):
            errors.append(f'{eid}: invalid direction')
        if e.get('support') not in ('explicit', 'inferred'):
            errors.append(f'{eid}: invalid support')
        if not isinstance(e.get('interpretation'), str) or not e['interpretation'].strip():
            errors.append(f'{eid}: missing interpretation')
        doc = docs.get(e.get('source'))
        if not doc:
            errors.append(f'{eid}: unknown source {e.get("source")}')
        elif not isinstance(e.get('quote'), str) or len(normalized(e['quote'])) < 15 or normalized(e['quote']) not in normalized(doc['text']):
            errors.append(f'{eid}: quote is not a verbatim contiguous source excerpt (minimum 15 characters)')
    return errors


def validate_synthesis(synthesis, entries, portfolio=None, context=None):
    errors = []
    if not isinstance(synthesis, dict):
        return ['synthesis must be an object']
    holdings = {r['record_id']: r for r in (portfolio or [])}
    ids = {e['id'] for e in entries}
    context_ids = {c['id'] for c in (context or [])}
    for key in ('persona', 'theses', 'portfolio_and_constraints'):
        text = synthesis.get(key)
        if not isinstance(text, str) or not text.strip():
            errors.append(f'missing or empty {key}'); continue
        for c in set(re.findall(r'\[ctx:([^\]\s]+)\]', text)) - context_ids:
            errors.append(f'{key}: unresolved context citation [ctx:{c}]')
        for c in set(CITATION.findall(text)) - ids:
            errors.append(f'{key}: unresolved citation [ev:{c}]')
        lines=text.splitlines()
        for number, line in enumerate(lines, 1):
            if key=='portfolio_and_constraints' and context is not None:
                cited=bool(CITATION.search(line) or re.search(r'\[(?:ctx|portfolio):[^\]]+\]',line))
                if re.match(r'^\s*[-*]\s',line) and not cited: errors.append(f'{key}:{number}: uncited portfolio list item')
                if line.strip().startswith('|') and not re.fullmatch(r'[\s|:-]+',line):
                    is_header=number<len(lines) and bool(re.fullmatch(r'[\s|:-]+',lines[number]))
                    if not is_header and not cited:errors.append(f'{key}:{number}: uncited portfolio table row')
            for ref in re.findall(r'\[(portfolio:[^\]\s]+)\]', line):
                if ref not in holdings:
                    errors.append(f'{key}: unresolved portfolio citation [{ref}]')
                elif holdings[ref]['source_url'] not in line:
                    errors.append(f'{key}: portfolio citation [{ref}] missing its source URL on the same line')
            # Unknowns are prose; every policy/thesis list item must carry evidence.
            if key in ('persona', 'theses') and re.match(r'^\s*(?:[-*]|\d+\.)\s', line) and not (CITATION.search(line) or re.search(r'\[ctx:[^\]]+\]', line)):
                errors.append(f'{key}:{number}: uncited policy or thesis bullet')
    persona = synthesis.get('persona', '')
    for dimension in DIMENSIONS:
        if f'## {dimension}' not in persona.splitlines():
            errors.append(f'persona: missing dimension {dimension}')
    if "## Distinctive / doesn't-fit-the-taxonomy" not in persona.splitlines():
        errors.append('persona: missing distinctive section')
    if entries and not CITATION.search(persona):
        errors.append('persona: no evidence citations')
    return errors


def validate(wiki_dir, codebook_labels=None):
    """Return problems; [] means structurally valid, not semantic proof of correctness."""
    path = Path(wiki_dir)
    required = ['persona.md', 'theses.md', 'portfolio_and_constraints.md', '_manifest.json',
                'prepared.json', 'evidence.json', 'sources.md'] + [f'evidence/{d}.md' for d in DIMENSIONS]
    errors = [f'missing {name}' for name in required if not (path / name).is_file()]
    loaded = {}
    for name in ('_manifest.json', 'prepared.json', 'evidence.json'):
        try:
            loaded[name] = json.loads((path / name).read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'{name}: {exc}')
    if len(loaded) != 3:
        return errors
    prepared, entries, manifest = loaded['prepared.json'], loaded['evidence.json'], loaded['_manifest.json']
    try:
        for doc in prepared['documents']:
            if doc.get('sha256') != digest(doc['text']):
                errors.append(f'{doc["doc_id"]}: source text hash mismatch')
        evidence_errors = validate_evidence(entries, prepared)
        errors.extend(evidence_errors)
        synthesis = {key: (path / filename).read_text(encoding='utf-8') if (path / filename).exists() else ''
                     for key, filename in [('persona', 'persona.md'), ('theses', 'theses.md'),
                                            ('portfolio_and_constraints', 'portfolio_and_constraints.md')]}
        context = json.loads((path / 'context.json').read_text()) if (path / 'context.json').exists() else []
        errors.extend(validate_synthesis(synthesis, entries, prepared.get('portfolio', []), context))
        if codebook_labels:
            errors.extend(f'{e["id"]}: label not in supplied codebook' for e in entries if e['label'] not in codebook_labels)
        if not evidence_errors:
            docs = {d['doc_id']: d for d in prepared['documents']}
            for e in entries:
                start = normalized(docs[e['source']]['text']).find(normalized(e['quote']))
                if e.get('normalized_char_start') != start or e.get('normalized_char_end') != start + len(normalized(e['quote'])):
                    errors.append(f'{e["id"]}: evidence offset mismatch')
            for dimension in DIMENSIONS:
                page = path / 'evidence' / f'{dimension}.md'
                if page.exists() and page.read_text(encoding='utf-8') != evidence_page(dimension, entries):
                    errors.append(f'{dimension}: evidence page differs from verified evidence.json')
        if prepared.get('source_policy') == 'full_investor_export':
            from .full_build import validate_full_artifacts
            errors.extend(validate_full_artifacts(path, prepared, entries, context))
            if manifest.get('source_policy') != 'full_investor_export' or manifest.get('no_pitch_sources') != prepared.get('no_pitch_sources'):
                errors.append('full source policy manifest mismatch')
        elif manifest.get('no_pitch_sources') is not True or prepared.get('no_pitch_sources') is not True:
            errors.append('manifest no_pitch_sources is not true')
        if manifest.get('evidence_count') != len(entries):
            errors.append('manifest evidence_count mismatch')
        if manifest.get('sources_consumed') != [d['doc_id'] for d in prepared['documents']]:
            errors.append('manifest sources_consumed mismatch')
        if manifest.get('corpus_chars') != sum(len(d['text']) for d in prepared['documents']):
            errors.append('manifest corpus_chars mismatch')
    except (KeyError, TypeError, AttributeError, OSError, ValueError) as exc:
        errors.append(f'invalid wiki data structure: {exc}')
    return errors
