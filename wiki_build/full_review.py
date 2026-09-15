"""Sol reviews every full-export source packet with explicit attribution and coverage."""
import json
import hashlib
import difflib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import TAXONOMY
from .generator import object_schema, STRING, EVIDENCE_SCHEMA, chunks
from .check_wiki import validate_evidence
from .prep_corpus import normalized

RULES = Path(__file__).with_name('FULL_AGENT.md').read_text()
evidence_properties = dict(EVIDENCE_SCHEMA['properties']['evidence']['items']['properties'])
evidence_properties.pop('source')
evidence_properties['attribution_basis'] = STRING
CONTEXT_SCHEMA = object_schema({'quote': STRING, 'claim': STRING, 'kind': {
    'type': 'string', 'enum': ['biography', 'company_relationship', 'investment_approach', 'dated_event']}})
REVIEW_SCHEMA = object_schema({'reviews': {'type': 'array', 'items': object_schema({
    'source': STRING, 'part': {'type': 'integer'},
    'identity': {'type': 'string', 'enum': ['target', 'other', 'uncertain', 'unusable']},
    'reason': STRING,
    'evidence': {'type': 'array', 'items': object_schema(evidence_properties)},
    'context': {'type': 'array', 'items': CONTEXT_SCHEMA}})}})


def review_packets(sources, limit=22000):
    packets = []
    for source in sources:
        for part in chunks([source], limit):
            part.update(kind=source['kind'], metadata=source.get('metadata', {}))
            if source['kind'] == 'transcript':
                before = source['text'][:part['char_start']]
                labels = re.findall(r'\[(SPEAKER_[^\]]+)\]', before)
                part['speaker_at_start'] = labels[-1] if labels else None
            packets.append(part)
    return packets


def review_errors(result, packets):
    if not isinstance(result, dict) or not isinstance(result.get('reviews'), list):
        return ['expected reviews array']
    expected = {(p['doc_id'], p['part']): p for p in packets}
    errors = []; seen = set()
    for review in result['reviews']:
        key = (review.get('source'), review.get('part'))
        if key not in expected or key in seen:
            errors.append(f'unknown or duplicate reviewed packet {key}'); continue
        seen.add(key); packet = expected[key]
        if review.get('identity') not in ('target', 'other', 'uncertain', 'unusable'):
            errors.append(f'{key}: invalid identity decision')
        if review.get('identity') != 'target' and (review.get('evidence') or review.get('context')):
            errors.append(f'{key}: non-target identity cannot contribute evidence/context')
        if not review.get('reason'): errors.append(f'{key}: missing review reason')
        entries = [{**e, 'source': key[0], 'id': f'trial-{i}'} for i,e in enumerate(review.get('evidence', []))]
        evidence_errors = validate_evidence(entries, {'documents': [{'doc_id': key[0], 'text': packet['text']}]})
        errors += [error for error in evidence_errors if 'verbatim' not in error]
        for i,e in enumerate(review.get('evidence', [])):
            error = quote_error(e.get('quote'),packet['text'])
            if error: errors.append(f'{key}: evidence[{i}] '+error)
        for e in review.get('evidence', []):
            if not e.get('attribution_basis'): errors.append(f'{key}: missing attribution basis')
            accepted = packet.get('metadata', {}).get('accepted_speaker')
            if packet.get('kind') == 'transcript' and accepted:
                allowed = speaker_spans(packet,accepted)
                if not any(normalized(e.get('quote','')) in normalized(span) for span in allowed):
                    errors.append(f'{key}: quote is not wholly in accepted speaker {accepted} turns; offending quote: '+json.dumps(e.get('quote'))+'; quote only that speaker, never the host or another guest.')
        for c in review.get('context', []):
            quote = c.get('quote')
            if not isinstance(quote,str) or len(normalized(quote)) < 15 or normalized(quote) not in normalized(packet['text']):
                errors.append(f'{key}: context quote not verbatim: '+quote_error(quote,packet['text']))
            if not c.get('claim'): errors.append(f'{key}: empty context claim')
    if seen != set(expected): errors.append(f'missing source packet reviews: {set(expected) - seen}')
    return errors




def speaker_spans(packet, accepted):
    current=packet.get('speaker_at_start');start=0;allowed=[]
    for match in re.finditer(r'\[(SPEAKER_[^\]]+)\]',packet['text']):
        if current==accepted:allowed.append(packet['text'][start:match.start()])
        current=match.group(1);start=match.end()
    if current==accepted:allowed.append(packet['text'][start:])
    return allowed


def quote_error(quote, text):
    if not isinstance(quote,str): return 'quote must be a string'
    q=normalized(quote);t=normalized(text)
    if len(q)>=15 and q in t:return None
    match=difflib.SequenceMatcher(None,q.lower(),t.lower(),autojunk=False).find_longest_match(0,len(q),0,len(t))
    start=max(0,match.b-match.a-100);end=min(len(t),match.b-match.a+len(q)+180)
    return ('quote is not verbatim (minimum 15 characters). Offending quote: '+json.dumps(quote)+
            '. Copy a CONTIGUOUS excerpt from this exact source neighborhood, preserving case and punctuation and '
            'never crossing speaker headers; extend short quotes: '+json.dumps(t[start:end]))


def review_fingerprint(inv, packet):
    """Bind reusable decisions to identity, attribution, text, and review policy."""
    payload = {"identity": inv["identity"], "packet": packet, "rules": RULES, "taxonomy": TAXONOMY}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def review_all(inv, generator, workers=3, batch_chars=60000, existing_reviews=None):
    packets = review_packets(inv['sources'])
    known = {}
    expected = {(p['doc_id'],p['part']):p for p in packets}
    for review in existing_reviews or []:
        key=(review.get('source'),review.get('part'))
        if (key in expected and review.get('input_fingerprint') == review_fingerprint(inv, expected[key])
                and not review_errors({'reviews':[review]},[expected[key]])):
            known[key]=review
    pending_packets=[p for p in packets if (p['doc_id'],p['part']) not in known]
    batches = []; batch = []; size = 0
    for packet in pending_packets:
        if batch and size + len(packet['text']) > batch_chars:
            batches.append(batch); batch=[]; size=0
        batch.append(packet); size += len(packet['text'])
    if batch: batches.append(batch)
    results = {}; failures = []; completed = 0
    def run(index, group):
        prompt = RULES + '\nRESOLVED_IDENTITY:\n' + json.dumps(inv['identity']) + '\nTAXONOMY:\n' + json.dumps(TAXONOMY) + '\nSOURCE_PACKETS:\n' + json.dumps(group,ensure_ascii=False)
        schema = json.loads(json.dumps(REVIEW_SCHEMA))
        schema['properties']['reviews']['items']['properties']['source'] = {'type':'string','enum':sorted({p['doc_id'] for p in group})}
        response = generator.call(prompt, schema, lambda r: review_errors(r,group))
        errors = review_errors(response,group)
        if errors: raise ValueError('; '.join(errors))
        return response['reviews']
    print(f'Reviewing {len(inv["sources"])} sources / {len(packets)} packets: {len(known)} revalidated prior reviews; {len(batches)} pending batches using {workers} Sol workers',flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(run,i,group):i for i,group in enumerate(batches)}
        for future in as_completed(pending):
            index=pending[future];completed+=1
            try: results[index]=future.result()
            except (ValueError,RuntimeError,OSError) as exc:
                failures.append(f'batch {index+1}: {exc}')
            print(f'Review completed: {completed}/{len(batches)} batches (batch {index+1}; failures {len(failures)})',flush=True)
    if failures: raise ValueError('Some source reviews failed; accepted batches remain cached: '+ '; '.join(failures))
    for i in range(len(batches)):
        for review in results[i]:known[(review['source'],review['part'])]=review
    return [{**known[(p['doc_id'],p['part'])], 'input_fingerprint':review_fingerprint(inv,p)} for p in packets]
