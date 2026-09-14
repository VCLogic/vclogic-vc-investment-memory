import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from wiki_build.generator import SolGenerator, chunks, build
from test_check_wiki import fixture, evidence, synthesis


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_chunks_cover_every_character_with_bounded_size(self):
        p = fixture(); p['documents'][0]['text'] = 'word ' * 1000
        parts = chunks(p['documents'], 300)
        self.assertTrue(all(len(x['text']) <= 300 for x in parts))
        self.assertEqual(''.join(x['text'] for x in parts), p['documents'][0]['text'])
        self.assertEqual([x['part'] for x in parts], list(range(1, len(parts) + 1)))

    def test_generator_cache_is_keyed_by_model_prompt_and_schema(self):
        g = SolGenerator(self.root / 'cache')
        with patch.object(g, '_invoke', return_value={'ok': True}) as invoke:
            self.assertEqual(g.call('prompt', {'type': 'object'}), {'ok': True})
            g.call('prompt', {'type': 'object'})
            self.assertEqual(invoke.call_count, 1)
            g.call('changed', {'type': 'object'})
            self.assertEqual(invoke.call_count, 2)

    def test_semantically_invalid_response_not_cached(self):
        g = SolGenerator(self.root / 'cache')
        def check(value):
            return ['not acceptable']
        with patch.object(g, '_invoke', return_value={'ok': False}):
            with self.assertRaisesRegex(ValueError, 'not acceptable'):
                g.call('prompt', {}, check)
        self.assertEqual(list((self.root / 'cache').glob('*/response.json')), [])

    def test_offline_end_to_end(self):
        class FakeGenerator:
            model = 'test-fixture'
            calls = []
            def call(self, prompt, schema, check=None):
                if 'TASK: EXTRACT' in prompt:
                    assert schema['properties']['evidence']['items']['properties']['source']['enum'] == ['source:one']
                else:
                    assert '"sources":' in prompt and '"published_at":' in prompt
                result = {'evidence': [{k: v for k, v in evidence()[0].items() if k != 'id'}]} if 'TASK: EXTRACT' in prompt else synthesis()
                if check:
                    errors = check(result)
                    if errors:
                        raise ValueError(str(errors))
                return result
        out = self.root / 'wiki'
        build(fixture(), out, FakeGenerator())
        self.assertTrue((out / 'persona.md').exists())
        self.assertEqual(json.loads((out / 'validation.json').read_text())['errors'], [])

    def test_failed_synthesis_does_not_publish(self):
        class BadGenerator:
            model = 'test-fixture'
            calls = []
            def call(self, prompt, schema, check=None):
                if 'TASK: EXTRACT' in prompt:
                    return {'evidence': [{k: v for k, v in evidence()[0].items() if k != 'id'}]}
                return {'persona': 'garbage', 'theses': '', 'portfolio_and_constraints': ''}
        out = self.root / 'wiki'
        with self.assertRaises(ValueError):
            build(fixture(), out, BadGenerator())
        self.assertFalse(out.exists())

    def test_generator_repairs_invalid_response_once(self):
        g = SolGenerator(self.root / 'cache')
        with patch.object(g, '_invoke', side_effect=[{'ok': False}, {'ok': True}]) as invoke:
            result = g.call('prompt', {}, lambda r: [] if r['ok'] else ['bad response'])
            self.assertTrue(result['ok'])
            self.assertEqual(invoke.call_count, 2)
            self.assertIn('bad response', invoke.call_args.args[1])
