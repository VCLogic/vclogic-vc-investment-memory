"""Read curated exports only; preserve admission decisions and source provenance."""
import hashlib
import json
import re
from pathlib import Path

from .config import THIN_CORPUS_CHARS


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def normalized(text):
    return ' '.join(text.split())


def read_rows(path):
    if not path.exists():
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f'{path}:{number}: malformed JSON: {exc.msg}') from exc
        if not isinstance(row, dict):
            raise ValueError(f'{path}:{number}: expected JSON object')
        rows.append((number, row))
    return rows


def pitch_source(row):
    # Inspect provenance, not arbitrary quoted speech mentioning a podcast.
    metadata = {k: v for k, v in row.items() if k not in ('text', 'target_segments')}
    text = json.dumps(metadata, ensure_ascii=False).lower()
    return bool(re.search(r'thepitch\.show|the\s+pitch\s+show', text))


def prepare(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f'Investor directory not found: {root}')
    slug = root.name
    identity_path = root / 'identity/resolved_identity.json'
    identity = json.loads(identity_path.read_text()) if identity_path.exists() else {
        'slug': slug, 'canonical_name': slug.replace('-', ' ').title(), 'resolution_status': 'unavailable'}
    if identity_path.exists() and (identity.get('resolution_status') != 'confirmed'
                                  or identity.get('slug', slug) != slug):
        raise ValueError('Investor identity must be confirmed and match the directory slug')
    warnings = []
    if not identity_path.exists():
        warnings.append('No resolved identity file; identity relies on the curated export.')
    canonical = root / 'corpus/all_documents.jsonl'
    modern = canonical.exists()
    if modern:
        paths = [canonical]
    else:
        base = root / 'corpus' if (root / 'corpus/_manifest.json').exists() else root
        manifest = base / '_manifest.json'
        if not manifest.exists() or json.loads(manifest.read_text()).get('no_pitch_sources') is not True:
            raise ValueError('Legacy exports require an explicit no_pitch_sources=true manifest')
        paths = [base / 'blog.jsonl', base / 'talks.jsonl']
        warnings.append('Legacy export: speaker attribution and source metadata cannot be independently checked.')
    documents, excluded = [], []
    seen_ids, seen_text = {}, set()
    input_hashes = {}
    for path in paths:
        if path.exists():
            input_hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line, row in read_rows(path):
            doc_id = row.get('source_item_id') or row.get('doc_id')
            text = row.get('text')
            reason = None
            if not isinstance(text, str) or not text.strip():
                reason = 'empty_text'
            elif not isinstance(doc_id, str) or not re.fullmatch(r'[\w:./-]+', doc_id):
                reason = 'missing_or_unsafe_source_id'
            elif pitch_source(row):
                reason = 'pitch_source'
            elif row.get('duplicate_of'):
                reason = 'upstream_duplicate'
            elif row.get('exclusion_reason') or row.get('inclusion_status', 'included') != 'included':
                reason = 'upstream_excluded'
            elif (modern or 'investor_slug' in row) and row.get('investor_slug') != slug:
                reason = 'wrong_investor'
            elif (modern or 'material_role' in row) and row.get('material_role') not in ('spoken_by_target', 'authored_by_target'):
                reason = 'not_target_material'
            elif ((modern and row.get('material_role') == 'spoken_by_target') or row.get('speaker_attribution')) and (
                    row.get('speaker_attribution') or {}).get('status') not in ('accepted_model', 'accepted_manual', 'verified', 'human_verified'):
                reason = 'unverified_speaker'
            if not reason:
                sha = digest(normalized(text))
                if doc_id in seen_ids and seen_ids[doc_id] != sha:
                    raise ValueError(f'conflicting text for source ID {doc_id}')
                if doc_id in seen_ids or sha in seen_text:
                    reason = 'duplicate_content'
                seen_ids[doc_id] = sha
                seen_text.add(sha)
            if reason:
                excluded.append({'doc_id': doc_id, 'input_path': str(path.relative_to(root)),
                                 'input_line': line, 'reason': reason})
                continue
            documents.append({
                'doc_id': doc_id, 'text': text, 'sha256': digest(text),
                'title': row.get('title', doc_id), 'url': row.get('canonical_url') or row.get('url'),
                'published_at': row.get('published_at'), 'source_type': row.get('source_type', row.get('source')),
                'material_role': row.get('material_role', 'curated_legacy'),
                'speaker_attribution': row.get('speaker_attribution'),
                'identity_confidence': row.get('identity_confidence'),
                'input_path': str(path.relative_to(root)), 'input_line': line,
                'document_version_id': row.get('document_version_id'),
            })
    if not documents:
        raise ValueError(f'No admissible curated documents in {root}; exclusions={excluded}')
    # Empty is an explicit unknown. Do not promote discovery claims or affiliations to holdings.
    portfolio_path = root / 'portfolio/portfolio.jsonl'
    portfolio, portfolio_excluded = [], []
    for line, row in read_rows(portfolio_path):
        if row.get('verification_status') == 'verified' and row.get('identity_match') == 'supported' and row.get('source_url') and not pitch_source(row):
            portfolio.append({**row, 'record_id': f'portfolio:{line}'})
        else:
            portfolio_excluded.append({'input_line': line, 'reason': 'unsupported_portfolio_record_schema_or_verification'})
    for path in (identity_path, portfolio_path):
        if path.exists():
            input_hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    chars = sum(len(d['text']) for d in documents)
    if chars < THIN_CORPUS_CHARS:
        warnings.append('Thin corpus: fewer than 600,000 characters; avoid extrapolating hard investment rules.')
    if not portfolio:
        warnings.append('No admissible verified portfolio records; holdings and mandate are unknown.')
    if any(not d['published_at'] for d in documents):
        warnings.append('Some source publication dates are unknown; historical statements are not current facts.')
    if any((d.get('identity_confidence') or {}).get('score', 1) < .8 for d in documents):
        warnings.append('Some documents have low search identity confidence; admission relies on accepted speaker attribution.')
    if portfolio_excluded:
        warnings.append('Some portfolio rows were not admitted; see portfolio_excluded and documented v1 schema.')
    return {'schema_version': '1.0', 'vc_slug': slug, 'identity': identity,
            'documents': documents, 'portfolio': portfolio, 'portfolio_excluded': portfolio_excluded,
            'excluded': excluded, 'input_hashes': input_hashes, 'corpus_chars': chars,
            'thin_corpus': chars < THIN_CORPUS_CHARS, 'no_pitch_sources': True,
            'warnings': warnings}
