import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from wiki_build.harnesses import discover, select_harness, check_compatibility
from wiki_build.generator import HarnessGenerator


class HarnessTests(unittest.TestCase):
    def test_discovery_does_not_call_models(self):
        with patch('wiki_build.harnesses.shutil.which', side_effect=lambda name: '/bin/'+name if name == 'claude' else None):
            found = discover()
        self.assertIsNone(found['codex'])
        self.assertEqual(found['claude'], '/bin/claude')

    def test_missing_harness_reports_requirement(self):
        with patch('wiki_build.harnesses.discover', return_value={'codex': None, 'claude': None}):
            with self.assertRaisesRegex(ValueError, 'Requirement: install'):
                select_harness('auto', interactive=False)

    def test_one_installed_selected_and_explicit_missing_rejected(self):
        with patch('wiki_build.harnesses.discover', return_value={'codex': '/bin/codex', 'claude': None}):
            self.assertEqual(select_harness('auto', interactive=False), 'codex')
            with self.assertRaisesRegex(ValueError, 'claude.*not installed'):
                select_harness('claude', interactive=False)

    def test_both_noninteractive_require_choice(self):
        with patch('wiki_build.harnesses.discover', return_value={'codex': '/bin/codex', 'claude': '/bin/claude'}):
            with self.assertRaisesRegex(ValueError, '--harness'):
                select_harness('auto', interactive=False)
            self.assertEqual(select_harness('claude', interactive=False), 'claude')

    def test_interactive_choice_and_cancel(self):
        with patch('wiki_build.harnesses.discover', return_value={'codex': '/bin/codex', 'claude': '/bin/claude'}):
            with patch('questionary.select') as select:
                select.return_value.ask.return_value = 'claude'
                self.assertEqual(select_harness('auto', interactive=True), 'claude')
                offered = [c.value for c in select.call_args.kwargs['choices']]
                self.assertEqual(offered, ['codex', 'claude'])
                select.return_value.ask.return_value = None  # Ctrl+C or Esc
                with self.assertRaisesRegex(ValueError, 'cancelled'):
                    select_harness('auto', interactive=True)

    def test_harness_models_and_caches_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex = HarnessGenerator(tmp)
            claude = HarnessGenerator(tmp, harness='claude')
            self.assertEqual(codex.model, 'gpt-5.6-sol')
            self.assertEqual(claude.model, 'sonnet')
            claude.model = codex.model  # Even identical model strings must not share raw responses.
            with patch.object(codex, '_invoke', return_value={'backend': 'codex'}), patch.object(claude, '_invoke', return_value={'backend': 'claude'}):
                self.assertEqual(codex.call('prompt', {}), {'backend': 'codex'})
                self.assertEqual(claude.call('prompt', {}), {'backend': 'claude'})

    def test_claude_command_and_result_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            g = HarnessGenerator(tmp, harness='claude')
            def popen(command, **kwargs):
                self.assertEqual(command[0], 'claude')
                self.assertIn('--safe-mode', command)
                self.assertEqual(command[command.index('--tools')+1], '')
                self.assertIn('--strict-mcp-config', command)
                self.assertNotIn('private source', ' '.join(command))
                kwargs['stdout'].write(json.dumps({'is_error': False, 'structured_output': {'ok': True}}))
                proc = unittest.mock.Mock(returncode=0)
                return proc
            with patch('wiki_build.generator.subprocess.Popen', side_effect=popen):
                self.assertEqual(g._invoke(root, 'private source', {'type': 'object'}), {'ok': True})
            self.assertEqual(json.loads((root/'raw-response.json').read_text()), {'ok': True})

    def test_claude_failure_or_missing_structure_not_accepted(self):
        for payload in ({'is_error': True, 'structured_output': {'ok': True}}, {'result': 'plain prose'}):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                def popen(command, **kwargs):
                    kwargs['stdout'].write(json.dumps(payload))
                    return unittest.mock.Mock(returncode=0)
                g = HarnessGenerator(tmp, harness='claude')
                with patch('wiki_build.generator.subprocess.Popen', side_effect=popen):
                    with self.assertRaises((ValueError, RuntimeError)):
                        g._invoke(Path(tmp), 'prompt', {})
                self.assertFalse((Path(tmp)/'raw-response.json').exists())

    def test_incompatible_or_unresponsive_cli_fails_before_generation(self):
        with patch('wiki_build.harnesses.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout='old help')):
            with self.assertRaisesRegex(ValueError, 'Update it'):
                check_compatibility('claude')
        with patch('wiki_build.harnesses.subprocess.run', side_effect=subprocess.TimeoutExpired('help', 15)):
            with self.assertRaisesRegex(ValueError, 'repair its installation'):
                check_compatibility('codex')

    def test_cli_no_harness_reports_requirement_without_creating_cache(self):
        from wiki_build.__main__ import main
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            argv = ['investor-memory', 'full-build', str(root/'input'), '--output', str(root/'wiki'), '--cache-dir', str(root/'cache')]
            with patch.object(sys, 'argv', argv), patch('wiki_build.harnesses.discover', return_value={'codex': None, 'claude': None}):
                self.assertEqual(main(), 1)
            self.assertFalse((root/'cache').exists())

    def test_discovery_json_without_harness_is_machine_readable(self):
        from wiki_build.__main__ import main
        import sys
        import io
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['investor-memory', 'harnesses', '--json']), patch('wiki_build.__main__.discover', return_value={'codex': None, 'claude': None}), patch('sys.stdout', stream):
            self.assertEqual(main(), 1)
        self.assertFalse(any(item['installed'] for item in json.loads(stream.getvalue())['harnesses']))
