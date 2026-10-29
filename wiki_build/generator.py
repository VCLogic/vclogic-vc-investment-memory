"""Bounded Sol map/reduce with auditable, content-addressed response caching."""
import json
import os
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from .config import MODEL, BATCH_CHARS, TAXONOMY
from .prep_corpus import digest, normalized
from .check_wiki import validate, validate_evidence, validate_synthesis
from .render import render, write_json
from .policies import BASIS_SCHEMA, DRAFT_SCHEMA, finalize, guidance, validate_policies, MARKER

REVISION = 'investor-memory-v1'
INSTRUCTIONS = Path(__file__).with_name('AGENT.md').read_text(encoding='utf-8')


def object_schema(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


STRING = {'type': 'string'}
EVIDENCE_SCHEMA = object_schema({'evidence': {'type': 'array', 'items': object_schema({
    'source': STRING, 'quote': STRING, 'label': {'type': 'string', 'enum': [e['label'] for e in TAXONOMY]},
    'direction': {'type': 'string', 'enum': ['positive', 'negative', 'neutral']},
    'support': {'type': 'string', 'enum': ['explicit', 'inferred']}, 'interpretation': STRING,
    'policy_basis': BASIS_SCHEMA})}})
SYNTHESIS_SCHEMA = object_schema({**{k: STRING for k in ('persona', 'theses', 'portfolio_and_constraints')},
                                  'policies': DRAFT_SCHEMA})
POLICY_RULES = Path(__file__).with_name('POLICIES.md').read_text(encoding='utf-8')


def check_synthesis(result, entries, context=(), portfolio=None):
    errors = validate_synthesis(result, entries, portfolio, context)
    policy_errors = validate_policies(result.get('policies') if isinstance(result, dict) else None, entries, context, draft=True)
    errors += policy_errors
    if not policy_errors:
        valid = {'policy': {p['key'] for p in result['policies']['policies']},
                 'relationship': {r['key'] for r in result['policies']['relationships']}}
        for page in ('persona', 'theses', 'portfolio_and_constraints'):
            for kind, key in re.findall(r'\[(policy|relationship):([^\]]+)\]', str(result.get(page, ''))):
                if key not in valid[kind]:
                    errors.append(f'{page}: unknown {kind} reference {key}')
    if isinstance(result, dict) and MARKER in str(result.get('persona', '')):
        errors.append('persona: policy guidance section is reserved for deterministic rendering')
    return errors


def finish_synthesis(result, entries, context, slug):
    policies, mapping = finalize(result['policies'], entries, context, slug)
    synthesis = {k: re.sub(r'\[(policy|relationship):([^\]]+)\]',
                 lambda m: '[' + m[1] + ':' + mapping.get(m[2], m[2]) + ']', result[k])
                 for k in ('persona', 'theses', 'portfolio_and_constraints')}
    synthesis['persona'] = synthesis['persona'].rstrip() + '\n\n' + guidance(policies)
    return synthesis, policies


class HarnessGenerator:
    def __init__(self, cache_dir, model=None, timeout=900, harness="codex"):
        if harness not in ("codex", "claude"):
            raise ValueError("Unsupported generation harness: " + harness)
        self.harness = harness
        model = model or (MODEL if harness == "codex" else "sonnet")
        self.cache_dir = Path(cache_dir).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model, self.timeout, self.calls = model, timeout, []

    def call(self, prompt, schema, check=None):
        cache_revision = REVISION if self.harness == "codex" else REVISION + ":claude-v1"
        key = digest(json.dumps([cache_revision, self.model, prompt, schema], sort_keys=True))
        directory = self.cache_dir / key
        directory.mkdir(exist_ok=True)
        response_path = directory / 'response.json'
        cached = response_path.exists()
        started = time.monotonic()
        raw_path = directory / 'raw-response.json'
        if cached:
            response = json.loads(response_path.read_text(encoding='utf-8'))
        elif raw_path.exists():
            # Interrupted/rejected raw responses are never trusted without revalidation.
            try:
                response = json.loads(raw_path.read_text(encoding='utf-8'))
            except ValueError:
                response = self._invoke(directory, prompt, schema)
        else:
            response = self._invoke(directory, prompt, schema)
        errors = check(response) if check else []
        repaired = False
        if errors:
            write_json(directory / 'errors.json', errors)
            repair_dir = Path(tempfile.mkdtemp(prefix='repair-', dir=directory))
            repair_prompt = (prompt + '\n\nCORRECTION REQUIRED: The previous response failed validation. '
                             'Return a corrected complete JSON response. Do not explain schema or citation '
                             'templates to readers. Preserve valid content. Validation errors:\n'
                             + json.dumps(errors) + '\nPrevious response:\n' + json.dumps(response, ensure_ascii=False))
            print('Repairing rejected generator response once', flush=True)
            response = self._invoke(repair_dir, repair_prompt, schema)
            errors = check(response)
            repaired, cached = True, False
            if errors:
                write_json(repair_dir / 'errors.json', errors)
                raise ValueError(f'Generator response rejected after repair ({repair_dir}): ' + '; '.join(errors))
        if not cached:
            write_json(response_path, response)
        self.calls.append({'key': key, 'cached': cached, 'repaired': repaired,
                           'seconds': round(time.monotonic() - started, 2)})
        return response

    def _invoke(self, directory, prompt, schema):
        write_json(directory / 'schema.json', schema)
        (directory / 'prompt.txt').write_text(prompt, encoding='utf-8')
        # Use authenticated installed CLI. No shell interpolation; source text goes through stdin.
        command = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
                   '--model', self.model, '--sandbox', 'read-only', '--color', 'never', '--json',
                   '-c', 'model_reasoning_effort="medium"',
                   '--output-schema', str(directory / 'schema.json'),
                   '--output-last-message', str(directory / 'raw-response.json'), '-']
        if self.harness == 'claude':
            command = ['claude', '--print', '--model', self.model, '--output-format', 'json',
                       '--json-schema', json.dumps(schema), '--tools', '', '--safe-mode',
                       '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence']
        write_json(directory / 'invocation.json', {'command': command, 'model': self.model, 'harness': self.harness})
        # Isolated cwd contains no project source; prompt supplies all inputs.
        with tempfile.TemporaryDirectory(prefix='investor-memory-harness-') as cwd:
            with (directory / 'events.jsonl').open('w') as stdout, (directory / 'stderr.log').open('w') as stderr:
                proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                        text=True, cwd=cwd, start_new_session=True)
                try:
                    proc.communicate(prompt, timeout=self.timeout)
                except subprocess.TimeoutExpired as exc:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.communicate()
                    raise RuntimeError(f'{self.harness} timed out after {self.timeout}s; see {directory}') from exc
        if proc.returncode:
            raise RuntimeError(f'{self.harness} exited {proc.returncode}; verify CLI authentication and model access; see {directory}/stderr.log and events.jsonl')
        if self.harness == 'claude':
            try:
                envelope = json.loads((directory / 'events.jsonl').read_text(encoding='utf-8'))
                if not isinstance(envelope, dict) or envelope.get('is_error') or not isinstance(envelope.get('structured_output'), dict):
                    raise ValueError('missing successful structured output')
                write_json(directory / 'raw-response.json', envelope['structured_output'])
            except (OSError, ValueError) as exc:
                raise ValueError(f'Claude Code did not return successful structured JSON; check authentication/model access and {directory}/events.jsonl') from exc
        try:
            return json.loads((directory / 'raw-response.json').read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise ValueError(f'{self.harness} did not return valid JSON; see {directory}') from exc


# Preserve the original programmatic API and Codex cache keys.
SolGenerator = HarnessGenerator


def chunks(documents, limit=BATCH_CHARS):
    if limit < 100:
        raise ValueError('Batch size must be at least 100 characters')
    result = []
    for doc in documents:
        start, part = 0, 0
        while start < len(doc['text']):
            end = min(start + limit, len(doc['text']))
            if end < len(doc['text']):
                boundary = doc['text'].rfind('\n', start + limit // 2, end)
                if boundary < 0:
                    boundary = doc['text'].rfind(' ', start + limit // 2, end)
                if boundary > start:
                    end = boundary + 1
            part += 1
            result.append({k: doc.get(k) for k in ('doc_id', 'title', 'url', 'published_at', 'material_role')}
                          | {'part': part, 'char_start': start, 'text': doc['text'][start:end]})
            start = end
    return result


def build(prepared, output, generator, batch_chars=BATCH_CHARS):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f'Output already exists: {output}; choose a new --output')
    parts = chunks(prepared['documents'], batch_chars)
    entries, seen = [], set()
    for number, part in enumerate(parts, 1):
        print(f'Extracting source chunk {number}/{len(parts)} with {generator.model}', flush=True)
        prompt = INSTRUCTIONS + '\n\nTASK: EXTRACT\nTAXONOMY:\n' + json.dumps(TAXONOMY) + '\nSOURCE_DATA:\n' + json.dumps(part, ensure_ascii=False)
        def check_map(result):
            if not isinstance(result, dict) or not isinstance(result.get('evidence'), list):
                return ['expected evidence array']
            trial = [{**e, 'id': f'trial-{i}'} for i, e in enumerate(result['evidence']) if isinstance(e, dict)]
            if len(trial) != len(result['evidence']):
                return ['evidence entry must be an object']
            return validate_evidence(trial, {'documents': [{'doc_id': part['doc_id'], 'text': part['text']}]})
        schema = json.loads(json.dumps(EVIDENCE_SCHEMA))
        schema['properties']['evidence']['items']['properties']['source'] = {
            'type': 'string', 'enum': [part['doc_id']]}
        result = generator.call(prompt, schema, check_map)
        errors = check_map(result)
        if errors:
            raise ValueError('; '.join(errors))
        for e in result['evidence']:
            key = (e['source'], normalized(e['quote']))
            if key in seen:
                continue
            seen.add(key)
            entries.append({**e, 'id': f"{prepared['vc_slug']}-{len(entries) + 1:04d}"})
    if not entries:
        raise ValueError('Sol found no admissible investment-relevant evidence; no wiki published')
    # Bounded reduce input; fail visibly rather than silently drop evidence on huge corpora.
    data = {'identity': prepared['identity'], 'warnings': prepared['warnings'],
            'portfolio': prepared['portfolio'], 'evidence': entries,
            'sources': [{k: d.get(k) for k in ('doc_id', 'title', 'url', 'published_at')}
                        for d in prepared['documents']]}
    payload = json.dumps(data, ensure_ascii=False)
    if len(payload) > 240_000:
        raise ValueError('Evidence exceeds v1 synthesis limit (240,000 characters); use a narrower curated corpus')
    print(f'Synthesizing {len(entries)} verified excerpts with {generator.model}', flush=True)
    prompt = INSTRUCTIONS + POLICY_RULES + '\n\nTASK: SYNTHESIZE\nEVIDENCE_DATA:\n' + payload
    synthesis = generator.call(prompt, SYNTHESIS_SCHEMA, lambda r: check_synthesis(r, entries, portfolio=prepared['portfolio']))
    errors = check_synthesis(synthesis, entries, portfolio=prepared['portfolio'])
    if errors:
        raise ValueError('; '.join(errors))
    synthesis, policies = finish_synthesis(synthesis, entries, [], prepared['vc_slug'])
    output.parent.mkdir(parents=True, exist_ok=True)
    # Retain failed staging artifact for diagnosis, never expose it as the requested wiki.
    stage = Path(tempfile.mkdtemp(prefix=f'.{output.name}-build-', dir=output.parent)) / 'wiki'
    render(stage, prepared, entries, synthesis, {'model': generator.model,
           'revision': REVISION, 'harness': getattr(generator, 'harness', 'codex'), 'calls': generator.calls, 'source_chunks': len(parts)}, policies=policies)
    errors = validate(stage)
    write_json(stage / 'validation.json', {'valid': not errors, 'errors': errors})
    if errors:
        raise ValueError(f'Wiki validation failed; retained {stage}: ' + '; '.join(errors))
    if output.exists():
        raise FileExistsError(f'Output appeared during generation: {output}; retained {stage}')
    stage.rename(output)
    stage.parent.rmdir()
    return output
