import json
import tempfile
import unittest
from pathlib import Path
from wiki_build.inventory import inventory, html_text


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'test'; self.root.mkdir()
        p=self.root/'identity'; p.mkdir()
        (p/'resolved_identity.json').write_text(json.dumps({'slug':'test','canonical_name':'Test Investor','resolution_status':'confirmed'}))

    def test_html_removes_scripts_preserves_article(self):
        self.assertEqual(html_text('<html><script>secret()</script><nav>Menu</nav><article><h1>Title</h1><p>Real words.</p></article></html>'), 'Title\nReal words.')

    def test_full_inventory_includes_web_and_processed_not_only_canonical(self):
        (self.root/'raw').mkdir();p=self.root/'raw/page.html';p.write_text('<article>Test founded Acme and invests in SaaS.</article>')
        (self.root/'raw/page.meta.json').write_text(json.dumps({'artifact_id':'sha256:abc','relative_path':'raw/page.html','source_url':'https://example.com/test'}))
        d=self.root/'processed';d.mkdir()
        (d/'documents.jsonl').write_text(json.dumps({'source_item_id':'source:talk','text':'Full spoken content here','inclusion_status':'review_required','source_type':'youtube','canonical_url':'https://example.com/talk','speaker_attribution':{'status':'uncertain'}})+'\n')
        result=inventory(self.root)
        self.assertEqual(len(result['sources']),2)
        self.assertEqual(len(result['files']),4)
        self.assertEqual({s['kind'] for s in result['sources']},{'web','transcript'})
        self.assertTrue(all(f['disposition'] for f in result['files']))

    def test_same_content_deduplicates_with_aliases(self):
        p=self.root/'portfolio/sources';p.mkdir(parents=True)
        for n in range(2):
            (p/f'{n}.json').write_text(json.dumps({'text':'Same full text.', 'source_url':f'https://example.com/{n}'}))
        result=inventory(self.root)
        self.assertEqual(len(result['sources']),1)
        self.assertEqual(len(result['sources'][0]['origins']),2)

    def test_escaping_sidecar_path_is_not_read(self):
        (self.root/'bad.json').write_text(json.dumps({'artifact_id':'bad','relative_path':'../private.html','source_url':'x'}))
        result=inventory(self.root)
        self.assertEqual(result['sources'],[])
        self.assertTrue(any('unsafe' in f['disposition'] for f in result['files']))

    def test_full_cached_transcript_is_not_replaced_by_partial_document(self):
        p=self.root/'processed';p.mkdir()
        (p/'documents.jsonl').write_text(json.dumps({'source_item_id':'partial','text':'Partial words.', 'source_type':'youtube','canonical_url':'https://example.com/talk','published_at':'2020-01-01'})+'\n')
        p=self.root/'raw';p.mkdir();(p/'a.wav').write_bytes(b'placeholder')
        (p/'a.metadata.json').write_text(json.dumps({'artifact_id':'a','relative_path':'raw/a.wav','source_url':'https://example.com/talk'}))
        p=self.root/'state/av_transcripts';p.mkdir(parents=True)
        (p/'a.json').write_text(json.dumps({'artifact_id':'a','segments':[{'text':'Partial words. Additional complete material.'}]}))
        inv=inventory(self.root)
        self.assertTrue(any('Additional complete material.' in s['text'] for s in inv['sources']))
        self.assertTrue(any(s['published_at']=='2020-01-01' for s in inv['sources']))

    def test_unconfirmed_textual_resolution_cannot_accept_speaker(self):
        from wiki_build.inventory import apply_resolutions
        p=self.root/'resolutions.json'
        p.write_text(json.dumps({'speaker_resolutions':[{'confirmed':False}]}))
        with self.assertRaisesRegex(ValueError,'explicitly confirmed'):
            apply_resolutions({'identity':{},'sources':[]},p,self.root)

    def test_confirmed_textual_resolution_keeps_acoustic_uncertainty(self):
        from wiki_build.inventory import apply_resolutions
        p=self.root/'resolutions.json'
        p.write_text(json.dumps({'speaker_resolutions':[{'confirmed':True,'source':'s','speaker_label':'SPEAKER_1','quotes':['Hello Michael Hyatt.']}]}))
        source={'doc_id':'s','text':'[SPEAKER_1] Hello Michael Hyatt.','metadata':{'attribution_status':'uncertain'}}
        result=apply_resolutions({'identity':{},'sources':[source]},p,self.root)
        metadata=result['sources'][0]['metadata']
        self.assertEqual(metadata['attribution_status'],'accepted_textual_review')
        self.assertEqual(metadata['upstream_attribution_status'],'uncertain')

    def test_comment_identity_requires_matching_source_and_verified_account(self):
        import hashlib
        from wiki_build.inventory import apply_resolutions
        profile='https://example.com/in/investor'
        raw='<a class="comment__author" href="'+profile+'">Test</a><p class="comment__text">I invested in the seed round.</p>'
        (self.root/'comment.html').write_text(raw)
        sha=hashlib.sha256(raw.encode()).hexdigest()
        inv={'identity':{'authoritative_profiles':['https://example.com/profile']},
             'sources':[{'doc_id':'s','text':'Test I invested in the seed round.','origins':[{'path':'comment.html'}],'metadata':{}}]}
        data={'identity_context':{'verified_social_account':{'input_path':'comment.html','input_sha256':sha,'link_text':profile,'linked_from':'https://example.com/profile','profile':profile}},
              'source_identity_links':[{'source':'s','input_path':'comment.html','input_sha256':sha,'html_receipt':raw,'profile':profile,'quote':'I invested in the seed round.'}]}
        p=self.root/'resolutions.json';p.write_text(json.dumps(data))
        result=apply_resolutions(inv,p,self.root)
        self.assertIn('verified_comment_identity',result['sources'][0]['metadata'])
        data['source_identity_links'][0]['profile']='https://example.com/in/other'
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'receipt mismatch'):apply_resolutions(inv,p,self.root)

    def test_structured_identity_accepts_country_host_alias_but_not_other_account(self):
        import hashlib
        from wiki_build.inventory import apply_resolutions
        profile='https://ca.linkedin.com/in/investor'
        record=json.dumps({'@type':'Person','name':'Investor','sameAs':['http://www.linkedin.com/in/investor']})
        raw='<a href="'+profile+'">Profile</a><script type="application/ld+json">'+record+'</script>'
        (self.root/'page.html').write_text(raw);sha=hashlib.sha256(raw.encode()).hexdigest()
        inv={'identity':{'authoritative_profiles':['official']},'sources':[{'doc_id':'s','origins':[{'path':'page.html'}],'metadata':{}}]}
        data={'identity_context':{'verified_social_account':{'input_path':'page.html','input_sha256':sha,'link_text':profile,'linked_from':'official','profile':profile}},
              'structured_identity_links':[{'source':'s','input_path':'page.html','input_sha256':sha,'json_receipt':record}]}
        p=self.root/'resolution.json';p.write_text(json.dumps(data))
        self.assertIn('verified_structured_identity',apply_resolutions(inv,p,self.root)['sources'][0]['metadata'])
        data['identity_context']['verified_social_account']['profile']='https://linkedin.com/in/other'
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'account receipt mismatch'):apply_resolutions(inv,p,self.root)
