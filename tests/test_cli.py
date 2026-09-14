import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'wiki_build', *map(str, args)],
                              capture_output=True, text=True)

    def test_output_cannot_overlap_input(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            result = self.run_cli('prepare', p, '--output', p / 'snapshot.json')
            self.assertEqual(result.returncode, 1)
            self.assertIn('outside the input', result.stderr)
            self.assertFalse((p / 'snapshot.json').exists())

    def test_cache_cannot_write_inside_input(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory); source = p / 'source'; source.mkdir()
            result = self.run_cli('build', source, '--output', p / 'wiki', '--cache-dir', source / 'cache')
            self.assertEqual(result.returncode, 1)
            self.assertIn('Cache must be outside', result.stderr)
            self.assertFalse((source / 'cache').exists())

    def test_missing_wiki_returns_nonzero_json(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli('check', Path(directory) / 'missing')
            self.assertEqual(result.returncode, 1)
            self.assertIn('"valid": false', result.stdout)
            self.assertNotIn('Traceback', result.stderr)
