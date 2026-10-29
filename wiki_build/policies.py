"""Additive public-source policies; structural checks are not semantic entailment."""
import copy
import hashlib
import json
import re

from .config import LABELS
from .prep_corpus import normalized

VERSION = '1.0'
SCOPE_FIELDS = ('investor', 'vehicle', 'period', 'stage', 'sector', 'geography', 'decision_setting')
KINDS = ('hard_requirement', 'preference', 'conditional_rule', 'descriptive_context')
RELATIONS = ('priority', 'qualification', 'exception', 'contradiction')
MARKER = '## Evidence-grounded policy guidance'


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def enum(*values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string', 'minLength': 1}
REFS = {'type': 'array', 'items': TEXT, 'minItems': 1, 'uniqueItems': True}
OPTIONAL_REFS = {**REFS, 'minItems': 0}
SCOPE_VALUE = obj({'status': enum('stated', 'unknown', 'not_stated'), 'value': TEXT})
SCOPE = obj({field: SCOPE_VALUE for field in SCOPE_FIELDS})
BASIS_SCHEMA = obj({
    'kind': enum(*KINDS, 'operating_advice', 'relationship', 'unknown'),
    'relationship': enum(*RELATIONS, 'not_stated'),
    'scope': SCOPE,
})
CONDITION = obj({'condition': TEXT, 'evidence_needed': TEXT,
                 'on_false': enum('not_applicable'), 'on_unknown': enum('unresolved')})
CONDITIONS = {'type': 'array', 'items': CONDITION}
EXCEPTION = obj({'statement': TEXT, 'conditions': {**CONDITIONS, 'minItems': 1}, 'evidence_refs': REFS,
                 'applicability': SCOPE})
POLICY_FIELDS = {
    'statement': TEXT, 'taxonomy_labels': {'type': 'array', 'items': enum(*LABELS), 'minItems': 1, 'uniqueItems': True},
    'type': enum(*KINDS), 'decision_effect': enum('supports_investment', 'opposes_investment', 'context_dependent'),
    'support': enum('explicit', 'inferred'), 'evidence_refs': REFS, 'applicability': SCOPE,
    'preconditions': CONDITIONS, 'applicability_evidence_needed': TEXT,
    'missing_information_effect': enum('unresolved'),
    'exceptions_status': enum('supported', 'unknown', 'not_stated'),
    'exceptions': {'type': 'array', 'items': EXCEPTION},
    'uncertainty': TEXT, 'conflicting_evidence_refs': OPTIONAL_REFS,
    'unresolved_applicability': {'type': 'array', 'items': enum(*SCOPE_FIELDS), 'uniqueItems': True},
}
RELATION_FIELDS = {
    'from_policy': TEXT, 'to_policy': TEXT, 'kind': enum(*RELATIONS), 'statement': TEXT,
    'support': enum('explicit', 'inferred'), 'evidence_refs': REFS, 'conditions': CONDITIONS,
    'applicability': SCOPE,
    'resolution': enum('supported', 'unresolved'),
}


def artifact_schema(draft=False):
    identifier = 'key' if draft else 'id'
    properties = {'schema_version': enum(VERSION)}
    if not draft:
        properties['investor_slug'] = TEXT
    properties.update(
        policies={'type': 'array', 'items': obj({identifier: TEXT, **POLICY_FIELDS})},
        relationships={'type': 'array', 'items': obj({identifier: TEXT, **RELATION_FIELDS})},
        limitations=TEXT,
    )
    return obj(properties)


DRAFT_SCHEMA = artifact_schema(True)
POLICIES_SCHEMA = artifact_schema()


def schema_errors(value, schema, path='policies'):
    """Validate the small closed JSON-schema vocabulary used by this contract offline."""
    errors = []
    kind = schema.get('type')
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str)}.get(kind, False)
    if not valid:
        return [f'{path}: expected {kind}']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: invalid value {value!r}')
    if kind == 'object':
        for key in schema['required']:
            if key not in value:
                errors.append(f'{path}: missing {key}')
        for key in value:
            if key not in schema['properties']:
                errors.append(f'{path}: unexpected field {key}')
            else:
                errors += schema_errors(value[key], schema['properties'][key], f'{path}.{key}')
    if kind == 'array':
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{path}: too few entries')
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f'{path}: duplicate entries')
        for i, item in enumerate(value):
            errors += schema_errors(item, schema['items'], f'{path}[{i}]')
    if kind == 'string' and not value.strip():
        errors.append(f'{path}: empty text; use explicit unknown/not_stated')
    return errors


def scope_errors(scope, path):
    errors = []
    for field, item in scope.items():
        if item['status'] != 'stated' and item['value'] != item['status']:
            errors.append(f'{path}.{field}: unstated scope must use its explicit status as value')
        if item['status'] == 'stated' and item['value'] in ('unknown', 'not_stated'):
            errors.append(f'{path}.{field}: stated scope needs a supported value')
    return errors


def basis_errors(basis):
    errors = schema_errors(basis, BASIS_SCHEMA, 'policy_basis')
    if errors:
        return errors
    errors += scope_errors(basis['scope'], 'policy_basis.scope')
    if (basis['kind'] == 'relationship') != (basis['relationship'] != 'not_stated'):
        errors.append('policy_basis: relationship kind and relationship classification disagree')
    return errors


def receipts(entries, context):
    return {**{'ev:' + e['id']: e for e in entries}, **{'ctx:' + c['id']: c for c in context}}


def _fingerprint(ref, ledger):
    entry = ledger[ref]
    # Ordinal evidence IDs and source ordering can change between builds.
    return [ref.split(':', 1)[0], entry['source'], normalized(entry['quote'])]


def _id(prefix, payload):
    return prefix + hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def policy_id(policy, ledger, slug):
    content = {k: v for k, v in policy.items() if k not in ('id', 'key')}
    # Hash content, not temporary keys, evidence ordinals or list ordering.
    content['evidence_refs'] = sorted([_fingerprint(r, ledger) for r in policy['evidence_refs']])
    content['conflicting_evidence_refs'] = sorted([_fingerprint(r, ledger) for r in policy['conflicting_evidence_refs']])
    content['taxonomy_labels'] = sorted(content['taxonomy_labels'])
    content['unresolved_applicability'] = sorted(content['unresolved_applicability'])
    content['exceptions'] = [{**x, 'evidence_refs': sorted([_fingerprint(r, ledger) for r in x['evidence_refs']])}
                             for x in content['exceptions']]
    return _id('pol-', [slug, content])


def relation_id(relation, ledger, slug):
    content = {k: v for k, v in relation.items() if k not in ('id', 'key')}
    content['evidence_refs'] = sorted([_fingerprint(r, ledger) for r in relation['evidence_refs']])
    return _id('rel-', [slug, content])


def validate_policies(data, entries, context=(), slug=None, draft=False):
    errors = schema_errors(data, DRAFT_SCHEMA if draft else POLICIES_SCHEMA)
    if errors:
        return errors
    ledger = receipts(entries, context)
    for ref, entry in ledger.items():
        if 'policy_basis' in entry:
            errors.extend(f'{ref}: {e}' for e in basis_errors(entry['policy_basis']))
    if errors:
        return errors
    identifier = 'key' if draft else 'id'
    ids = [p[identifier] for p in data['policies']]
    rids = [r[identifier] for r in data['relationships']]
    if len(set(ids + rids)) != len(ids + rids):
        errors.append('policies: duplicate policy/relationship IDs')
    if any(not re.fullmatch(r'[a-zA-Z0-9_-]+', x) for x in ids + rids):
        errors.append('policies: invalid identifier')
    if not draft and data['investor_slug'] != slug:
        errors.append('policies: investor_slug mismatch')

    def referenced(refs, where):
        missing = set(refs) - set(ledger)
        errors.extend(f'{where}: unknown evidence reference {ref}' for ref in sorted(missing))
        return [ledger[ref] for ref in refs if ref in ledger]

    def direct_relation(refs, kind, where):
        items = referenced(refs, where)
        if not any(r.startswith('ev:') and r in ledger and ledger[r].get('support') == 'explicit'
                   and ledger[r].get('policy_basis', {}).get('kind') == 'relationship'
                   and ledger[r]['policy_basis'].get('relationship') == kind for r in refs):
            errors.append(f'{where}: {kind} needs explicit relationship evidence, not separate positive/negative examples')
        return items

    def relationship_scope(applicability, refs, where, targets, allow_conflicts=False):
        errors.extend(scope_errors(applicability, where + '.applicability'))
        for field in SCOPE_FIELDS:
            known = {ledger[r]['policy_basis']['scope'][field]['value'] for r in refs if r in ledger
                     and ledger[r].get('policy_basis', {}).get('scope', {}).get(field, {}).get('status') == 'stated'}
            value = applicability[field]
            if value['status'] == 'stated':
                if known != {value['value']}:
                    errors.append(f'{where}: relationship {field} specificity unsupported by evidence scope')
                for target in targets:
                    other = target['applicability'][field]
                    if other['status'] == 'stated' and other['value'] != value['value']:
                        errors.append(f'{where}: relationship {field} scope incompatible with target policy')
            elif known and not (allow_conflicts and len(known) > 1 and value['status'] == 'unknown'):
                errors.append(f'{where}: relationship cannot discard stated {field} scope; retain separate scoped claims')

    for policy in data['policies']:
        where = policy[identifier]
        items = referenced(policy['evidence_refs'], where)
        referenced(policy['conflicting_evidence_refs'], where)
        errors += scope_errors(policy['applicability'], where)
        unknown = {f for f in SCOPE_FIELDS if policy['applicability'][f]['status'] != 'stated'}
        if set(policy['unresolved_applicability']) != unknown:
            errors.append(f'{where}: unresolved_applicability must enumerate all unknown/not_stated scope fields')
        evs = [ledger[r] for r in policy['evidence_refs'] if r.startswith('ev:') and r in ledger]
        if policy['type'] != 'descriptive_context' and not evs:
            errors.append(f'{where}: decision policy needs investor evidence, not context alone')
        if policy['support'] == 'explicit' and policy['type'] != 'descriptive_context':
            if not any(e.get('support') == 'explicit' for e in evs):
                errors.append(f'{where}: explicit policy requires explicitly stated investor selection evidence')
        if policy['type'] == 'hard_requirement':
            if policy['support'] != 'explicit' or not any(
                e.get('support') == 'explicit' and e.get('policy_basis', {}).get('kind') == 'hard_requirement' for e in evs
            ):
                errors.append(f'{where}: hard requirement needs explicit requirement evidence; preference/advice is insufficient')
        if policy['type'] == 'conditional_rule' and not policy['preconditions']:
            errors.append(f'{where}: conditional rule needs preconditions')
        if policy['type'] == 'descriptive_context' and policy['decision_effect'] != 'context_dependent':
            errors.append(f'{where}: descriptive context cannot directly support or oppose investment')
        if evs and all(e.get('policy_basis', {}).get('kind') == 'operating_advice' for e in evs):
            if policy['support'] != 'inferred' and policy['type'] != 'descriptive_context':
                errors.append(f'{where}: operating advice applied to selection must be inferred')
        # Scope may be narrower only after new supporting extraction; never guess a merge.
        for field in SCOPE_FIELDS:
            known = {e['policy_basis']['scope'][field]['value'] for e in evs
                     if e.get('policy_basis', {}).get('scope', {}).get(field, {}).get('status') == 'stated'}
            scope = policy['applicability'][field]
            if scope['status'] == 'stated' and (not known or known != {scope['value']}):
                errors.append(f'{where}: {field} specificity is not supported consistently by evidence scope')
            if known and scope['status'] != 'stated':
                conflicting = {ledger[r]['policy_basis']['scope'][field]['value']
                               for r in policy['conflicting_evidence_refs'] if r in ledger
                               and ledger[r].get('policy_basis', {}).get('scope', {}).get(field, {}).get('status') == 'stated'}
                if len(known | conflicting) < 2 or not conflicting or scope['status'] != 'unknown':
                    errors.append(f'{where}: cannot discard stated {field} scope without distinct conflicting scope evidence and unknown status')
        if policy['exceptions'] and policy['exceptions_status'] != 'supported':
            errors.append(f'{where}: exceptions require supported status')
        if not policy['exceptions'] and policy['exceptions_status'] == 'supported':
            errors.append(f'{where}: supported exception status requires an exception')
        for exception in policy['exceptions']:
            direct_relation(exception['evidence_refs'], 'exception', where)
            relationship_scope(exception['applicability'], exception['evidence_refs'], where, [policy])
        if policy['conflicting_evidence_refs'] and policy['uncertainty'] in ('not_stated', 'unknown'):
            errors.append(f'{where}: conflicting evidence needs an unresolved-conflict explanation')
    policies = {p[identifier]: p for p in data['policies']}
    for relation in data['relationships']:
        where = relation[identifier]
        if relation['from_policy'] not in policies or relation['to_policy'] not in policies:
            errors.append(f'{where}: unknown relationship target')
        if relation['from_policy'] == relation['to_policy']:
            errors.append(f'{where}: self relationship')
        referenced(relation['evidence_refs'], where)
        # A contradiction can explicitly connect incompatible scopes; it is never operative.
        relationship_scope(relation['applicability'], relation['evidence_refs'], where,
                           [] if relation['kind'] == 'contradiction' else
                           [policies[t] for t in (relation['from_policy'], relation['to_policy']) if t in policies], allow_conflicts=relation['kind'] == 'contradiction')
        if relation['kind'] in ('priority', 'exception', 'qualification'):
            direct_relation(relation['evidence_refs'], relation['kind'], where)
            if relation['support'] != 'explicit' or relation['resolution'] != 'supported':
                errors.append(f'{where}: operative relationship must be explicitly supported')
        if relation['kind'] == 'exception' and not relation['conditions']:
            errors.append(f'{where}: exception needs conditions')
        if relation['kind'] == 'contradiction':
            if relation['resolution'] != 'unresolved':
                errors.append(f'{where}: contradictions remain unresolved; no automatic precedence')
            for target in (relation['from_policy'], relation['to_policy']):
                if target in policies and not set(policies[target]['evidence_refs']) & set(relation['evidence_refs']):
                    errors.append(f'{where}: contradiction must cite evidence from both policies')
    if draft and not errors:
        hashes = [policy_id(p, ledger, slug) for p in data['policies']]
        if len(set(hashes)) != len(hashes):
            errors.append('policies: duplicate policy content would produce duplicate IDs')
        hashes = [relation_id(r, ledger, slug) for r in data['relationships']]
        if len(set(hashes)) != len(hashes):
            errors.append('policies: duplicate relationship content would produce duplicate IDs')
    if not draft and not errors:
        for policy in data['policies']:
            if policy['id'] != policy_id(policy, ledger, slug):
                errors.append(f'{policy["id"]}: content-derived policy ID mismatch')
        for relation in data['relationships']:
            if relation['id'] != relation_id(relation, ledger, slug):
                errors.append(f'{relation["id"]}: content-derived relationship ID mismatch')
    return errors


def finalize(draft, entries, context, slug):
    errors = validate_policies(draft, entries, context, slug, draft=True)
    if errors:
        raise ValueError('; '.join(errors))
    data = copy.deepcopy(draft)
    ledger = receipts(entries, context)
    mapping = {p['key']: policy_id(p, ledger, slug) for p in data['policies']}
    for policy in data['policies']:
        policy['id'] = mapping[policy.pop('key')]
    for relation in data['relationships']:
        relation['from_policy'] = mapping[relation['from_policy']]
        relation['to_policy'] = mapping[relation['to_policy']]
        relation['id'] = relation_id(relation, ledger, slug)
        mapping[relation.pop('key')] = relation['id']
    data['investor_slug'] = slug
    return data, mapping


def guidance(data):
    def cite(refs):
        return ' '.join('[' + ref + ']' for ref in refs)

    def conditions(items):
        return '; '.join(f"{x['condition']} (establish using: {x['evidence_needed']}; false: not applicable; unknown: unresolved)"
                         for x in items) or 'not_stated'

    blocks = [MARKER, 'Public-source guidance, not a calibrated prediction model. Missing pitch information means unresolved, '
              'not failure. Establish applicability before using a policy. No unstated priority or symmetric In/Out rule is implied.']
    for p in data['policies']:
        refs = cite(p['evidence_refs'])
        blocks += [f"### [policy:{p['id']}] {p['statement']}",
                   f"Type: {p['type']}; effect: {p['decision_effect']}; support: {p['support']}. {refs}",
                   'Applicability: ' + '; '.join(f"{field}: {v['value']} ({v['status']})" for field, v in p['applicability'].items()) + f'. {refs}',
                   f"Preconditions: {conditions(p['preconditions'])}. {refs}",
                   f"Evidence needed to establish applicability: {p['applicability_evidence_needed']}. {refs}",
                   f"Exceptions: {p['exceptions_status']}. {refs}"]
        for x in p['exceptions']:
            blocks.append(f"Exception: {x['statement']}. Conditions: {conditions(x['conditions'])}. "
                          + 'Applicability: ' + '; '.join(f"{f}: {v['value']} ({v['status']})" for f, v in x['applicability'].items())
                          + '. ' + cite(x['evidence_refs']))
        blocks.append(f"Uncertainty: {p['uncertainty']}. Conflicting evidence: {cite(p['conflicting_evidence_refs']) or 'not_stated'}.")
    blocks.append('### Policy relationships')
    if not data['relationships']:
        blocks.append('No supported policy relationships extracted. Priorities, overrides and conflict resolutions are not established.')
    for r in data['relationships']:
        blocks.append(f"[relationship:{r['id']}] {r['kind']}: [policy:{r['from_policy']}] → [policy:{r['to_policy']}]. "
                      f"{r['statement']} Support: {r['support']}; resolution: {r['resolution']}. "
                      f"Conditions: {conditions(r['conditions'])}. "
                      + 'Applicability: ' + '; '.join(f"{f}: {v['value']} ({v['status']})" for f, v in r['applicability'].items())
                      + '. ' + cite(r['evidence_refs']))
    blocks.append('Limitations: ' + data['limitations'])
    return '\n\n'.join(blocks) + '\n'


def validate_guidance(synthesis, data):
    errors = []
    ids = {p['id'] for p in data['policies']}
    rids = {r['id'] for r in data['relationships']}
    persona = synthesis.get('persona', '')
    if persona.count(MARKER) != 1 or persona.split(MARKER, 1)[-1] != guidance(data).split(MARKER, 1)[-1]:
        errors.append('persona: structured policy guidance missing or differs from policies.json')
    for name, text in synthesis.items():
        for ref in re.findall(r'\[policy:([^\]]+)\]', text):
            if ref not in ids:
                errors.append(f'{name}: unknown policy reference {ref}')
        for ref in re.findall(r'\[relationship:([^\]]+)\]', text):
            if ref not in rids:
                errors.append(f'{name}: unknown relationship reference {ref}')
    return errors
