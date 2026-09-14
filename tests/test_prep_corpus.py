import json
import tempfile
import unittest
from pathlib import Path

from wiki_build.prep_corpus import prepare


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r) + '\n' for r in rows))


def document(**changes):
    d = dict(source_item_id='source:one', text='Build something customers need.',
             investor_slug='test', inclusion_status='included', material_role='spoken_by_target',
             speaker_attribution={'status': 'accepted_model'}, canonical_url='https://example.com/talk',
             title='Investor interview', modality='audiovisual')
    d.update(changes)
    return d


class PrepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'test'
        write_json(self.root / 'identity/resolved_identity.json',
                   {'slug': 'test', 'canonical_name': 'Test Investor', 'resolution_status': 'confirmed'})

    def corpus(self, rows):
        write_rows(self.root / 'corpus/all_documents.jsonl', rows)

    def test_canonical_precedence_dedup_and_provenance(self):
        self.corpus([document(), document(source_item_id='source:duplicate')])
        write_rows(self.root / 'talks.jsonl', [{'text': 'DO NOT READ'}])
        p = prepare(self.root)
        self.assertEqual(len(p['documents']), 1)
        self.assertEqual(p['documents'][0]['doc_id'], 'source:one')
        self.assertEqual(p['documents'][0]['input_line'], 1)
        self.assertTrue(p['documents'][0]['sha256'])
        self.assertEqual(len(p['excluded']), 1)

    def test_rejects_wrong_identity_excluded_unattributed_and_pitch(self):
        self.corpus([document(), document(source_item_id='2', investor_slug='other'),
                     document(source_item_id='3', inclusion_status='excluded'),
                     document(source_item_id='4', speaker_attribution={'status': 'unavailable'}),
                     document(source_item_id='5', canonical_url='https://www.thepitch.show/episodes/1')])
        p = prepare(self.root)
        self.assertEqual(len(p['documents']), 1)
        self.assertEqual(len(p['excluded']), 4)

    def test_empty_canonical_does_not_fall_back_to_raw(self):
        self.corpus([])
        write_rows(self.root / 'processed/documents.jsonl', [document()])
        with self.assertRaisesRegex(ValueError, 'No admissible'):
            prepare(self.root)

    def test_conflicting_source_id_fails(self):
        self.corpus([document(), document(text='Different text')])
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            prepare(self.root)

    def test_legacy_requires_clean_manifest(self):
        write_rows(self.root / 'talks.jsonl', [{'doc_id': 'talk:1', 'text': 'Some words'}])
        with self.assertRaisesRegex(ValueError, 'manifest'):
            prepare(self.root)
        write_json(self.root / '_manifest.json', {'no_pitch_sources': True})
        self.assertEqual(len(prepare(self.root)['documents']), 1)

    def test_unconfirmed_identity_fails(self):
        self.corpus([document()])
        write_json(self.root / 'identity/resolved_identity.json', {'resolution_status': 'ambiguous'})
        with self.assertRaisesRegex(ValueError, 'identity'):
            prepare(self.root)

    def test_legacy_rejects_explicit_contradictions(self):
        write_json(self.root / '_manifest.json', {'no_pitch_sources': True})
        write_rows(self.root / 'talks.jsonl', [
            {'doc_id': 'talk:ok', 'text': 'Valid legacy text'},
            {'doc_id': 'talk:wrong', 'text': 'Other person text', 'investor_slug': 'other'},
            {'doc_id': 'talk:rejected', 'text': 'Rejected speaker text', 'speaker_attribution': {'status': 'rejected'}}])
        p = prepare(self.root)
        self.assertEqual(len(p['documents']), 1)
        self.assertEqual(len(p['excluded']), 2)
