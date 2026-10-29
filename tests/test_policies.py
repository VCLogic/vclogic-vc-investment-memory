"""Offline contract tests: classifications are fixtures, not semantic judgments."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_check_wiki import evidence, fixture, synthesis
from wiki_build.policies import (SCOPE_FIELDS, POLICIES_SCHEMA, finalize, guidance,
                                 validate_policies, validate_guidance)
from wiki_build.generator import finish_synthesis
from wiki_build.render import render
from wiki_build.check_wiki import validate, validate_evidence


def scope(**values):
    return {f: {'status': 'stated' if f in values else 'not_stated',
                'value': values.get(f, 'not_stated')} for f in SCOPE_FIELDS}


def basis(kind='preference', relationship='not_stated', **values):
    return {'kind': kind, 'relationship': relationship, 'scope': scope(**values)}


def draft():
    return {'schema_version': '1.0', 'policies': [{
        'key': 'reliability', 'statement': 'Values founders who keep their promises.',
        'taxonomy_labels': ['founder_qualities'], 'type': 'preference',
        'decision_effect': 'supports_investment', 'support': 'explicit',
        'evidence_refs': ['ev:test-0001'], 'applicability': scope(),
        'preconditions': [], 'applicability_evidence_needed': 'Evidence of founder reliability; investor vehicle and period remain unestablished.',
        'missing_information_effect': 'unresolved', 'exceptions_status': 'not_stated',
        'exceptions': [], 'uncertainty': 'The source does not establish a requirement or a rejection rule.',
        'conflicting_evidence_refs': [], 'unresolved_applicability': list(SCOPE_FIELDS),
    }], 'relationships': [], 'limitations': 'No supported priorities extracted. Quote interpretation requires semantic review.'}


def new_synthesis():
    return {**synthesis(), 'policies': draft()}


def condition():
    return {'condition': 'An exceptional founder has demonstrated reliability.',
            'evidence_needed': 'Documented prior commitments and delivery.',
            'on_false': 'not_applicable', 'on_unknown': 'unresolved'}


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.e = evidence()
        self.e[0]['policy_basis'] = basis()
        self.d = draft()
        self.p = self.d['policies'][0]

    def errors(self):
        return validate_policies(self.d, self.e, draft=True)

    def test_preference_is_not_hard_gate(self):
        self.p['type'] = 'hard_requirement'
        self.assertTrue(any('explicit requirement' in x for x in self.errors()))
        self.e[0]['policy_basis']['kind'] = 'hard_requirement'
        self.assertEqual(self.errors(), [])

    def test_missing_information_and_false_condition_differ(self):
        self.p['type'] = 'conditional_rule'
        self.p['preconditions'] = [condition()]
        self.assertEqual(self.errors(), [])
        self.p['missing_information_effect'] = 'opposes_investment'
        self.assertTrue(self.errors())
        self.p['missing_information_effect'] = 'unresolved'
        self.p['preconditions'][0]['on_unknown'] = 'failure'
        self.assertTrue(self.errors())

    def test_personal_policy_cannot_be_applied_to_fund(self):
        self.e[0]['policy_basis']['scope'] = scope(vehicle='personal')
        self.p['applicability'] = scope(vehicle='Example Fund')
        self.p['unresolved_applicability'].remove('vehicle')
        self.assertTrue(any('vehicle specificity' in x for x in self.errors()))
        self.p['applicability'] = scope(vehicle='personal')
        self.assertEqual(self.errors(), [])

    def test_dated_statement_cannot_be_made_timeless(self):
        self.e[0]['policy_basis']['scope'] = scope(period='as stated in 2020; continuation unknown')
        self.p['applicability'] = scope(period='timeless')
        self.p['unresolved_applicability'].remove('period')
        self.assertTrue(any('period specificity' in x for x in self.errors()))
        self.p['applicability'] = scope()
        self.p['unresolved_applicability'].append('period')
        self.assertTrue(any('discard stated period' in x for x in self.errors()))

    def test_operating_advice_cannot_be_investment_requirement(self):
        self.e[0]['policy_basis'] = basis('operating_advice')
        self.assertTrue(validate_evidence(self.e, fixture()))
        self.e[0]['support'] = 'inferred'
        self.p.update(type='hard_requirement', support='inferred')
        self.assertTrue(any('explicit requirement' in x for x in self.errors()))
        self.p.update(type='preference')
        self.assertEqual(self.errors(), [])

    def two_policies(self, kind='priority'):
        other = copy.deepcopy(self.p)
        other.update(key='market', statement='Values large markets.', taxonomy_labels=['market_size_assessment'], evidence_refs=['ev:test-0002'])
        self.d['policies'].append(other)
        self.e.append({**copy.deepcopy(self.e[0]), 'id': 'test-0002', 'quote': 'I value large markets.'})
        self.d['relationships'] = [{'key': 'tradeoff', 'from_policy': 'reliability', 'to_policy': 'market',
            'kind': kind, 'statement': 'Founder strength outweighs market concerns.', 'support': 'explicit',
            'evidence_refs': ['ev:test-0001', 'ev:test-0002'], 'conditions': [], 'applicability': scope(), 'resolution': 'supported'}]

    def test_unsupported_founder_override_rejected(self):
        self.two_policies()
        self.assertTrue(any('explicit relationship evidence' in x for x in self.errors()))

    def test_supported_exception(self):
        self.e.append({**copy.deepcopy(self.e[0]), 'id': 'test-0002',
            'quote': 'I make an exception for founders whose prior commitments I can verify.',
            'policy_basis': basis('relationship', 'exception')})
        self.p['exceptions_status'] = 'supported'
        self.p['exceptions'] = [{'statement': 'Verifiable prior commitments permit an exception.',
                                'conditions': [condition()], 'evidence_refs': ['ev:test-0002'], 'applicability': scope()}]
        self.assertEqual(self.errors(), [])
        self.e[1]['policy_basis'] = basis('descriptive_context')
        self.assertTrue(any('explicit relationship evidence' in x for x in self.errors()))

    def test_conflict_resolution_remains_unknown(self):
        self.two_policies('contradiction')
        r = self.d['relationships'][0]
        r.update(statement='These policies conflict in this setting; precedence is unknown.', support='inferred', resolution='unresolved')
        self.assertEqual(self.errors(), [])
        r['resolution'] = 'supported'
        self.assertTrue(any('remain unresolved' in x for x in self.errors()))

    def test_invalid_policy_and_evidence_references(self):
        self.two_policies('contradiction')
        r = self.d['relationships'][0]
        r.update(resolution='unresolved', to_policy='missing')
        self.assertTrue(any('unknown relationship target' in x for x in self.errors()))
        r['to_policy'] = 'market'
        self.p['evidence_refs'] = ['ev:missing']
        self.assertTrue(any('unknown evidence reference' in x for x in self.errors()))

    def test_schema_version_unknowns_and_duplicate_ids(self):
        self.d['schema_version'] = '99'
        self.assertTrue(self.errors())
        self.d['schema_version'] = '1.0'
        self.p['applicability']['stage']['value'] = 'any stage'
        self.assertTrue(any('explicit status' in x for x in self.errors()))
        self.p['applicability'] = scope()
        self.d['policies'].append(copy.deepcopy(self.p))
        self.assertTrue(any('duplicate' in x for x in self.errors()))

    def test_stable_ids_across_evidence_renumbering(self):
        a, _ = finalize(self.d, self.e, [], 'test')
        self.e[0]['id'] = 'test-0099'
        self.p['evidence_refs'] = ['ev:test-0099']
        self.p['key'] = 'different-temporary-key'
        b, _ = finalize(self.d, self.e, [], 'test')
        self.assertEqual(a['policies'][0]['id'], b['policies'][0]['id'])
        self.assertEqual(validate_policies(b, self.e, slug='test'), [])

    def test_guidance_is_traceable_and_tamper_checked(self):
        s, data = finish_synthesis(new_synthesis(), self.e, [], 'test')
        self.assertEqual(validate_guidance(s, data), [])
        s['persona'] = s['persona'].replace('Type: preference', 'Type: hard_requirement')
        self.assertTrue(validate_guidance(s, data))
        s['persona'] = guidance(data)
        s['theses'] += '\n[policy:missing]'
        self.assertTrue(any('unknown policy reference' in x for x in validate_guidance(s, data)))

    def test_additive_output_and_declared_missing_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'wiki'
            s, data = finish_synthesis(new_synthesis(), self.e, [], 'test')
            render(path, fixture(), self.e, s, {}, policies=data)
            self.assertEqual(validate(path), [])
            (path / 'policies.json').unlink()
            self.assertTrue(any('missing policies.json' in x for x in validate(path)))

    def test_published_json_schema_matches_runtime_contract(self):
        schema = json.loads(Path('wiki_build/policies.schema.json').read_text())
        schema.pop('$schema')
        self.assertEqual(schema, POLICIES_SCHEMA)

    def test_fictional_source_offline_end_to_end(self):
        from wiki_build.generator import build
        saved = json.loads(Path('tests/fixtures/policies/saved_source.json').read_text())
        expected = json.loads(Path('docs/examples/policies.json').read_text())
        e = saved['evidence'][0]
        d = copy.deepcopy(expected)
        d.pop('investor_slug')
        d['policies'][0]['key'] = 'reliability'
        d['policies'][0].pop('id')
        s = {k: v.replace('test-0001', e['id'])
             for k, v in synthesis().items()}
        s['policies'] = d
        prepared = {**fixture(), 'vc_slug': saved['vc_slug'], 'identity': saved['identity'],
                    'documents': [saved['document']], 'corpus_chars': len(saved['document']['text'])}

        class CachedFixtureGenerator:
            model = 'offline-saved-source-fixture'
            calls = []
            def call(self, prompt, schema, check=None):
                result = {'evidence': [{**{k: v for k, v in e.items() if k != 'id'}, 'policy_basis': basis('unknown')}]} if 'TASK: EXTRACT' in prompt else s
                if check:
                    errors = check(result)
                    if errors:
                        raise ValueError(errors)
                return result

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'wiki'
            build(prepared, out, CachedFixtureGenerator())
            self.assertEqual(validate(out), [])
            self.assertEqual(json.loads((out / 'policies.json').read_text()), expected)

    def test_conflict_reference_cannot_hide_personal_scope(self):
        self.e[0]['policy_basis']['scope'] = scope(vehicle='personal')
        self.p['conflicting_evidence_refs'] = ['ev:test-0001']
        self.assertTrue(any('discard stated vehicle' in x for x in self.errors()))

    def test_relationship_cannot_transfer_personal_dated_priority_to_fund(self):
        self.two_policies()
        for e, p in zip(self.e, self.d['policies']):
            e['policy_basis']['scope'] = scope(vehicle='Fund A', period='2025')
            p['applicability'] = scope(vehicle='Fund A', period='2025')
            p['unresolved_applicability'] = [f for f in SCOPE_FIELDS if f not in ('vehicle', 'period')]
        self.e.append({**copy.deepcopy(self.e[0]), 'id': 'comparison',
                       'policy_basis': basis('relationship', 'priority', vehicle='personal', period='2010')})
        r = self.d['relationships'][0]
        r['evidence_refs'] = ['ev:comparison']
        r['applicability'] = scope(vehicle='personal', period='2010')
        self.assertTrue(any('incompatible with target' in x for x in self.errors()))
        r['applicability'] = scope(vehicle='Fund A', period='2025')
        self.assertTrue(any('unsupported by evidence scope' in x for x in self.errors()))

    def test_contradiction_can_preserve_conflicting_vehicle_scopes(self):
        self.two_policies('contradiction')
        for e, p, vehicle in zip(self.e, self.d['policies'], ['personal', 'Fund A']):
            e['policy_basis']['scope'] = scope(vehicle=vehicle)
            p['applicability'] = scope(vehicle=vehicle)
            p['unresolved_applicability'].remove('vehicle')
        r = self.d['relationships'][0]
        r.update(resolution='unresolved', support='inferred')
        r['applicability']['vehicle'] = {'status': 'unknown', 'value': 'unknown'}
        self.assertEqual(self.errors(), [])

    def test_bad_references_and_duplicate_content_enter_repair_loop(self):
        from wiki_build.generator import check_synthesis
        s = new_synthesis()
        s['persona'] += '\n[policy:missing]'
        self.assertTrue(any('unknown policy reference' in x for x in check_synthesis(s, self.e)))
        s = new_synthesis()
        p = copy.deepcopy(s['policies']['policies'][0]); p['key'] = 'duplicate'
        s['policies']['policies'].append(p)
        self.assertTrue(any('duplicate policy content' in x for x in check_synthesis(s, self.e)))

    def test_malformed_basis_returns_errors_instead_of_crashing(self):
        self.e[0]['policy_basis'] = None
        self.assertTrue(self.errors())
