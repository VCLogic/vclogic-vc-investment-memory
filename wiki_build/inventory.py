"""Inventory the full collected export without confusing derivatives with sources."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .prep_corpus import digest, normalized, read_rows


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'noscript', 'svg', 'header', 'footer'):
            self.skip += 1
        if not self.skip and tag in ('p', 'div', 'article', 'main', 'section', 'li', 'br', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'noscript', 'svg', 'header', 'footer'):
            self.skip = max(0, self.skip - 1)
        if not self.skip and tag in ('p', 'div', 'article', 'main', 'section', 'li', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def html_text(html):
    parser = TextParser(); parser.feed(html)
    return '\n'.join(normalized(line) for line in ''.join(parser.parts).splitlines() if normalized(line))


def url_key(url):
    p = urlsplit(url or '')
    return urlunsplit((p.scheme, p.netloc.lower().removeprefix('www.'), p.path.rstrip('/'), p.query, ''))


def aligned_text(segments):
    """Combine consecutive speaker turns, retaining labels instead of mixing voices."""
    blocks = []; speaker = None; words = []
    for seg in segments:
        label = seg.get('speaker_label', 'UNKNOWN')
        if label != speaker and words:
            blocks.append(f'[{speaker}]\n' + ' '.join(words)); words = []
        speaker = label
        if seg.get('text'): words.append(seg['text'].strip())
    if words: blocks.append(f'[{speaker}]\n' + ' '.join(words))
    return '\n\n'.join(blocks)


def inventory(root):
    root = Path(root).resolve()
    identity = json.loads((root / 'identity/resolved_identity.json').read_text())
    if identity.get('resolution_status') != 'confirmed' or identity.get('slug') != root.name:
        raise ValueError('Full export requires a confirmed matching identity')
    files = {}
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel = str(p.relative_to(root))
        disposition = ('raw_media_derivative' if p.suffix in ('.wav', '.webm', '.m4a', '.mp3', '.mp4') else
                       'search_discovery_not_collected_evidence' if rel.startswith(('discovery/', 'state/source_search/')) else
                       'operational_metadata_or_derivative')
        files[rel] = {'path': rel, 'bytes': p.stat().st_size, 'disposition': disposition, 'source_ids': []}
    candidates = {d['candidate_id']: d for _, d in read_rows(root / 'discovery/source_candidates.jsonl')}
    sources = []; hashes = {}; warnings = []; seen = {}; by_url = {}

    def add(text, url, title, kind, origins, metadata=None, published_at=None):
        text = text.strip()
        if not text: return None
        key = digest(normalized(text))
        source = seen.get(key)
        if source is None:
            source = {'doc_id': 'full:' + key[:24], 'text': text, 'sha256': digest(text),
                      'url': url, 'title': title or url or key, 'kind': kind,
                      'published_at': published_at, 'metadata': metadata or {}, 'origins': []}
            sources.append(source); seen[key] = source
            by_url.setdefault(url_key(url), []).append(source)
        if published_at and not source.get('published_at'): source['published_at'] = published_at
        for origin in origins:
            if origin not in source['origins']: source['origins'].append(origin)
            rel = origin['path']
            if rel in files:
                files[rel]['disposition'] = 'source_text_extracted'
                if source['doc_id'] not in files[rel]['source_ids']: files[rel]['source_ids'].append(source['doc_id'])
                p = root / rel
                hashes[rel] = digest(p.read_text(encoding='utf-8', errors='replace')) if p.suffix != '.pdf' else __import__('hashlib').sha256(p.read_bytes()).hexdigest()
        return source

    # Full diarized transcripts supersede partial target_speech exports of the same URL.
    avpath = root / 'processed/av_attribution_results.jsonl'
    for line, row in read_rows(avpath):
        candidate = candidates.get(row['candidate_id'], {})
        result = row['result']; attr = result.get('attribution', {})
        text = aligned_text(result.get('aligned_segments', []))
        add(text, candidate.get('canonical_url', candidate.get('url')), candidate.get('title'), 'transcript',
            [{'path': str(avpath.relative_to(root)), 'line': line}],
            {'attribution_status': attr.get('status'), 'accepted_speaker': attr.get('speaker_label') if attr.get('status') in ('accepted_model', 'accepted_manual') else None,
             'candidate_id': row['candidate_id'], 'artifact_id': row.get('artifact_id'),
             'identity_confidence': candidate.get('identity_confidence'), 'channel': candidate.get('channel')})
    for rel in ('corpus/all_documents.jsonl', 'processed/documents.jsonl'):
        for line, row in read_rows(root / rel):
            url = row.get('canonical_url', row.get('url')); existing = by_url.get(url_key(url), [])
            if existing and row.get('source_type') == 'youtube':
                source = existing[0]; source['origins'].append({'path': rel, 'line': line})
                if row.get('published_at') and not source.get('published_at'):
                    source['published_at'] = row['published_at']
                files[rel]['disposition'] = 'source_text_represented_by_full_transcript'
                files[rel]['source_ids'].append(source['doc_id'])
                continue
            add(row.get('text', ''), url, row.get('title'),
                'transcript' if row.get('source_type') == 'youtube' else 'web', [{'path': rel, 'line': line}],
                {'upstream_status': row.get('inclusion_status'), 'upstream_reason': row.get('exclusion_reason'),
                 'attribution_status': (row.get('speaker_attribution') or {}).get('status'),
                 'accepted_speaker': (row.get('speaker_attribution') or {}).get('speaker_label')}, published_at=row.get('published_at'))
    # Saved collected articles, including profiles and third-party reports, are evidence candidates.
    for p in sorted(root.rglob('*.json')):
        rel = str(p.relative_to(root))
        if rel.startswith(('discovery/', 'state/', 'audit/', 'identity/')): continue
        try: row = json.loads(p.read_text())
        except (ValueError, UnicodeError): continue
        if not isinstance(row, dict): continue
        if rel.startswith('portfolio/sources/'):
            add(row.get('text', ''), row.get('source_url'), row.get('title'), 'report', [{'path': rel}],
                published_at=row.get('published_at'))
        elif row.get('relative_path') and row.get('artifact_id'):
            target = (root / row['relative_path']).resolve()
            if root not in target.parents:
                files[rel]['disposition'] = 'unsafe_sidecar_path'; continue
            if not target.is_file():
                files[rel]['disposition'] = 'missing_sidecar_target'; continue
            target_rel = str(target.relative_to(root))
            if target.suffix not in ('.html', '.htm', '.pdf'): continue
            if files[target_rel]['source_ids']: continue
            try:
                if target.suffix == '.pdf':
                    from pypdf import PdfReader
                    text = '\n\n'.join(page.extract_text() or '' for page in PdfReader(target).pages)
                else: text = html_text(target.read_text(encoding='utf-8', errors='replace'))
            except (ImportError, ValueError, OSError) as exc:
                files[target_rel]['disposition'] = 'text_extraction_failed'
                warnings.append(f'{target_rel}: {exc}'); continue
            meta = row.get('original_metadata', {}); cand = candidates.get(meta.get('candidate_id'), {})
            source = add(text, row.get('source_url'), cand.get('title', meta.get('title')), 'web',
                         [{'path': target_rel}, {'path': rel}],
                         {'candidate_id': meta.get('candidate_id'), 'collection_method': row.get('collection_method'),
                          'identity_confidence': cand.get('identity_confidence')})
            if source is None: files[target_rel]['disposition'] = 'no_visible_text'
    # Explicitly identify file classes still not represented in the source index.
    for file in files.values():
        rel = file['path']
        if file['source_ids']: continue
        if rel.endswith(('.html', '.pdf')) and file['disposition'] == 'operational_metadata_or_derivative':
            if rel.startswith('portfolio/raw/'):
                file['disposition'] = 'raw_portfolio_copy_represented_by_source_reports'
            else:
                file['disposition'] = 'unlinked_raw_text_requires_review'
                warnings.append(f'Unlinked raw text: {rel}')
    return complete_media_inventory({'schema_version': '2.0', 'source_policy': 'full_investor_export', 'vc_slug': root.name,
            'identity': identity, 'sources': sources, 'files': list(files.values()),
            'input_hashes': hashes, 'warnings': warnings}, root)


def complete_media_inventory(inv, root):
    """Connect media and cached transcripts to reviewed text; expose genuine gaps."""
    root = Path(root).resolve(); files = {f['path']: f for f in inv['files']}
    transcript_urls = {url_key(s['url']): s for s in inv['sources'] if s['kind'] == 'transcript'}
    artifacts = {}
    for p in sorted((root / 'raw').rglob('*.json')):
        try: meta = json.loads(p.read_text())
        except (ValueError, UnicodeError): continue
        if isinstance(meta,dict) and meta.get('artifact_id') and meta.get('relative_path'):
            artifacts[meta['artifact_id']] = meta
    for p in sorted((root / 'state/av_transcripts').glob('*.json')):
        row = json.loads(p.read_text()); meta = artifacts.get(row.get('artifact_id'), {})
        url = meta.get('source_url'); rel = str(p.relative_to(root))
        if not url:
            files[rel]['disposition'] = 'unlinked_cached_transcript_requires_review'
            inv['warnings'].append(f'Unlinked cached transcript: {rel}'); continue
        source = transcript_urls.get(url_key(url))
        text = '\n'.join(s.get('text', '') for s in row.get('segments', []))
        source_text = re.sub(r'\[SPEAKER_[^\]]+\]', '', source['text']) if source else ''
        if source is None or normalized(text) not in normalized(source_text):
            if not text.strip(): continue
            key = digest(normalized(text))
            source = {'doc_id': 'full:' + key[:24], 'text': text, 'sha256': digest(text),
                      'url': url, 'title': (meta.get('original_metadata') or {}).get('title', url),
                      'kind': 'transcript', 'published_at': None, 'metadata': {'attribution_status':'unavailable', 'accepted_speaker':None},
                      'origins':[{'path':rel}]}
            duplicate = next((s for s in inv['sources'] if s['doc_id']==source['doc_id']), None)
            if duplicate: source = duplicate
            else: inv['sources'].append(source)
            transcript_urls[url_key(url)] = source
        elif {'path': rel} not in source['origins']:
            source['origins'].append({'path':rel})
        files[rel]['disposition'] = 'cached_transcript_represented_by_source'
        files[rel]['source_ids'] = [source['doc_id']]
    for meta in artifacts.values():
        rel = meta['relative_path']; file = files.get(rel)
        if not file or file['source_ids'] or not rel.endswith(('.wav','.webm','.m4a','.mp3','.mp4')): continue
        source = transcript_urls.get(url_key(meta.get('source_url')))
        file['disposition'] = 'media_represented_by_transcript' if source else ('reference_voice_sample' if rel.startswith('raw/voice/') else 'media_without_transcript')
        if source: file['source_ids'] = [source['doc_id']]
        elif not rel.startswith('raw/voice/'): inv['warnings'].append(f'Media without transcript: {rel}')
    return inv


def apply_supplements(inv, path):
    """Merge separately generated transcripts without modifying source exports."""
    rows = json.loads(Path(path).read_text())
    for source in rows:
        if source['sha256'] != digest(source['text']): raise ValueError('Supplement text hash mismatch')
        if source['doc_id'] not in {s['doc_id'] for s in inv['sources']}:
            inv['sources'].append(source)
        media = source.get('metadata', {}).get('media_path')
        for file in inv['files']:
            if media and file['path'] == media:
                file['disposition'] = 'media_represented_by_supplemental_transcript'
                file['source_ids'] = [source['doc_id']]
        inv['warnings'] = [w for w in inv['warnings'] if w != f'Media without transcript: {media}']
    return inv


def apply_resolutions(inv, path, root):
    """Apply source-backed identity links and explicitly labelled textual speaker reviews."""
    import hashlib
    data=json.loads(Path(path).read_text());root=Path(root).resolve()
    context=data.get('identity_context',{})
    account=context.get('verified_social_account')
    if account:
        source=(root/account['input_path']).resolve()
        if root not in source.parents:raise ValueError('Unsafe identity link source')
        raw=source.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=account['input_sha256'] or account['link_text'] not in raw.decode('utf-8',errors='replace'):
            raise ValueError('Identity account link does not match source receipt')
        if account['linked_from'] not in inv['identity'].get('authoritative_profiles',[]):
            raise ValueError('Identity account link must originate at an authoritative resolved profile')
    sources={s['doc_id']:s for s in inv['sources']}
    affiliation=context.get('additional_affiliation')
    if affiliation and normalized(affiliation['quote']) not in normalized(sources[affiliation['source']]['text']):
        raise ValueError('Identity affiliation receipt mismatch')
    inv['identity']['collection_identity_links']=context
    for link in data.get('source_identity_links', []):
        source=sources[link['source']]
        raw_path=(root/link['input_path']).resolve()
        if root not in raw_path.parents or link['input_path'] not in {o['path'] for o in source['origins']}:
            raise ValueError('Comment identity receipt must belong to its source')
        raw=raw_path.read_bytes()
        receipt=link['html_receipt']
        if (hashlib.sha256(raw).hexdigest()!=link['input_sha256'] or receipt not in raw.decode('utf-8')
                or not account or link['profile']!=account['profile']
                or link['profile'] not in receipt or receipt.count('comment__author')!=1
                or normalized(link['quote']) not in normalized(html_text(receipt))
                or normalized(link['quote']) not in normalized(source['text'])):
            raise ValueError('Comment identity receipt mismatch')
        source['metadata']['verified_comment_identity']={k:v for k,v in link.items() if k!='html_receipt'}
    for link in data.get('structured_identity_links', []):
        source=sources[link['source']]
        raw_path=(root/link['input_path']).resolve()
        if root not in raw_path.parents or link['input_path'] not in {o['path'] for o in source['origins']}:
            raise ValueError('Structured identity receipt must belong to its source')
        raw=raw_path.read_bytes();receipt=link['json_receipt'];record=json.loads(receipt)
        def account_key(url):
            parsed=urlsplit(url)
            return ('linkedin.com' if parsed.hostname=='linkedin.com' or (parsed.hostname or '').endswith('.linkedin.com') else parsed.hostname, parsed.path.rstrip('/'))
        if (not account or hashlib.sha256(raw).hexdigest()!=link['input_sha256']
                or receipt not in raw.decode('utf-8') or record.get('@type')!='Person'
                or not any(account_key(url)==account_key(account['profile']) for url in record.get('sameAs',[]))):
            raise ValueError('Structured identity account receipt mismatch')
        source['metadata']['verified_structured_identity']={'record':record,'input_path':link['input_path'],
            'input_sha256':link['input_sha256'],'basis':'The saved JSON-LD sameAs links this named listing to the verified investor account. The aggregator claims remain unverified, not investor statements.'}
    for resolution in data.get('speaker_resolutions',[]):
        if resolution.get('confirmed') is not True:
            raise ValueError('Textual speaker resolution must be explicitly confirmed')
        source=sources[resolution['source']]
        if not resolution.get('quotes') or not all(normalized(q) in normalized(source['text']) for q in resolution['quotes']):
            raise ValueError('Textual speaker resolution receipts mismatch')
        if f"[{resolution['speaker_label']}]" not in source['text']:raise ValueError('Unknown resolved speaker label')
        source['metadata'].setdefault('upstream_attribution_status',source['metadata'].get('attribution_status'))
        source['metadata']['attribution_status']='accepted_textual_review'
        source['metadata']['accepted_speaker']=resolution['speaker_label']
        source['metadata']['textual_attribution_review']=resolution
    return inv
