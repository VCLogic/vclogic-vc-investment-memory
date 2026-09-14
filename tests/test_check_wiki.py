import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from wiki_build.check_wiki import validate, validate_evidence
from wiki_build.render import render
from wiki_build.config import DIMENSIONS


def fixture():
    return {'vc_slug': 'test', 'identity': {'canonical_name': 'Test'},
            'documents': [{'doc_id': 'source:one', 'text': 'I value founders who keep their promises.',
                           'sha256': hashlib.sha256(b'I value founders who keep their promises.').hexdigest(), 'url': 'https://example.com', 'title': 'Interview',
                           'published_at': None, 'input_path': 'corpus/all_documents.jsonl', 'input_line': 1}],
            'portfolio': [], 'warnings': ['Thin corpus'], 'corpus_chars': 41,
            'thin_corpus': True, 'no_pitch_sources': True, 'input_hashes': {}}


def evidence():
    return [{'id': 'test-0001', 'source': 'source:one', 'quote': 'I value founders who keep their promises.',
             'label': 'founder_qualities', 'direction': 'positive', 'support': 'explicit',
             'interpretation': 'Value reliable founders.'}]


def synthesis():
    return {'persona': '# Test\n\n' + '\n\n'.join('## ' + d + '\n\n' +
        ('- In: Value reliable founders. [ev:test-0001]' if d == 'founder_team' else 'Insufficient evidence.')
        for d in DIMENSIONS) + "\n\n## Distinctive / doesn't-fit-the-taxonomy\n\nInsufficient evidence.",
        'theses': '# Theses\n\n- Reliability matters. [ev:test-0001]',
        'portfolio_and_constraints': '# Portfolio\n\nNo verified holdings available. Mandate unknown.'}


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'wiki'
        render(self.path, fixture(), evidence(), synthesis(), {'model': 'gpt-5.6-sol'})

    def test_good_wiki(self):
        self.assertEqual(validate(self.path), [])

    def test_invented_quote_rejected(self):
        ev = evidence(); ev[0]['quote'] = 'I require a billion dollar market.'
        self.assertTrue(any('verbatim' in e for e in validate_evidence(ev, fixture())))

    def test_whitespace_normalization_allowed(self):
        ev = evidence(); ev[0]['quote'] = 'I value founders\nwho keep their promises.'
        self.assertEqual(validate_evidence(ev, fixture()), [])

    def test_duplicate_id_and_wrong_label(self):
        ev = evidence() * 2
        self.assertTrue(any('duplicate' in e for e in validate_evidence(ev, fixture())))
        ev = evidence(); ev[0]['label'] = 'made_up'
        self.assertTrue(any('label' in e for e in validate_evidence(ev, fixture())))

    def test_unknown_source_and_invalid_direction(self):
        ev = evidence(); ev[0].update(source='missing', direction='maybe')
        errors = validate_evidence(ev, fixture())
        self.assertTrue(any('source' in e for e in errors))
        self.assertTrue(any('direction' in e for e in errors))

    def test_missing_file_and_unresolved_citations(self):
        (self.path / 'theses.md').unlink()
        with (self.path / 'persona.md').open('a') as f:
            f.write('\n- Unsupported policy [ev:missing]\n')
        errors = validate(self.path)
        self.assertTrue(any('theses.md' in e for e in errors))
        self.assertTrue(any('unresolved' in e for e in errors))

    def test_uncited_policy_rejected(self):
        with (self.path / 'persona.md').open('a') as f:
            f.write('\n- Out: Never invest in consumer companies.\n')
        self.assertTrue(any('uncited' in e for e in validate(self.path)))

    def test_evidence_markdown_tampering_rejected(self):
        p = self.path / 'evidence/founder_team.md'
        p.write_text(p.read_text().replace('keep their promises', 'sell their company'))
        self.assertTrue(any('evidence page' in e for e in validate(self.path)))

    def test_manifest_counts_checked(self):
        p = self.path / '_manifest.json'; m = json.loads(p.read_text()); m['evidence_count'] = 99
        p.write_text(json.dumps(m))
        self.assertTrue(any('evidence_count' in e for e in validate(self.path)))

    def test_refuses_existing_destination(self):
        with self.assertRaises(FileExistsError):
            render(self.path, fixture(), evidence(), synthesis(), {})

    def test_fabricated_portfolio_citation_rejected(self):
        (self.path / 'portfolio_and_constraints.md').write_text('Owns Acme [portfolio:999] https://example.com/fake')
        self.assertTrue(any('portfolio' in e for e in validate(self.path)))

    def test_snapshot_hash_and_offsets_checked(self):
        p = self.path / 'prepared.json'
        data = json.loads(p.read_text()); data['documents'][0]['sha256'] = 'wrong'
        p.write_text(json.dumps(data))
        q = self.path / 'evidence.json'
        data = json.loads(q.read_text()); data[0]['normalized_char_start'] = 55
        q.write_text(json.dumps(data))
        errors = validate(self.path)
        self.assertTrue(any('hash' in e for e in errors))
        self.assertTrue(any('offset' in e for e in errors))
