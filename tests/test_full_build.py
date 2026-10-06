import json,tempfile,unittest
from pathlib import Path
from wiki_build.full_build import assemble, full_build
from wiki_build.check_wiki import validate
from wiki_build.prep_corpus import digest
from test_check_wiki import synthesis


class FullBuildTests(unittest.TestCase):
    def test_indexed_synthesis_preserves_every_value_and_source_reference(self):
        from wiki_build.full_build import indexed_synthesis
        data={'identity':{'canonical_name':'Test'},'warnings':['Missing audio'],
              'sources':[{'doc_id':'full:a','title':'First','url':'https://a','published_at':None,'kind':'web'},
                         {'doc_id':'full:b','title':'Second','url':'https://b','published_at':'2020','kind':'web'}],
              'evidence':[{'id':'ev1','source':'full:b','interpretation':'Distinct preference','label':'founder_qualities'},
                          {'id':'ev2','source':'full:a','interpretation':'Another preference','label':'founder_qualities'}],
              'context':[{'id':'ctx1','source':'full:b','claim':'Reported relationship','kind':'company_relationship'}]}
        before=json.loads(json.dumps(data));packed=indexed_synthesis(data)
        decoded={k:packed[k] for k in ('identity','warnings')}
        for name in ('sources','evidence','context'):
            table=packed[name]
            decoded[name]=[dict(zip(table['columns'],row)) for row in table['rows']]
        for row in decoded['evidence']+decoded['context']:
            row['source']=decoded['sources'][row['source']]['doc_id']
        self.assertEqual(decoded,before)
        self.assertEqual(data,before)
        empty=indexed_synthesis({**data,'evidence':[],'context':[]})
        self.assertEqual(empty['evidence'],{'columns':[],'rows':[]})

    def fixture(self):
        text='I value founders who keep their promises.'
        inv={'vc_slug':'test','identity':{'canonical_name':'Test'},'source_policy':'full_investor_export',
             'sources':[{'doc_id':'full:one','text':text,'sha256':digest(text),'title':'Interview','url':'https://example.com',
                         'kind':'transcript','metadata':{},'published_at':None,'origins':[{'path':'raw/x','line':1}]}],
             'files':[{'path':'raw/x','bytes':len(text),'disposition':'source_text_extracted','source_ids':['full:one']}],
             'warnings':[],'input_hashes':{}}
        reviews=[{'source':'full:one','part':1,'identity':'target','reason':'Named investor',
                  'evidence':[{'quote':text,'label':'founder_qualities','direction':'positive','support':'explicit',
                               'interpretation':'Values reliability','attribution_basis':'Named speaker'}],
                  'context':[{'quote':text,'claim':'Source reports reliability preference','kind':'investment_approach'}]}]
        return inv,reviews

    def test_assemble_uses_only_target_material_and_keeps_context_separate(self):
        inv,reviews=self.fixture();p,e,c=assemble(inv,reviews)
        self.assertEqual(len(e),1);self.assertEqual(len(c),1)
        self.assertEqual(p['source_policy'],'full_investor_export')
        self.assertEqual(c[0]['id'],'test-0001')

    def test_full_build_and_missing_review_rejected(self):
        inv,reviews=self.fixture()
        class Fake:
            model='fixture';calls=[]
            def call(self,prompt,schema,check=None):return synthesis()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'wiki';full_build(inv,reviews,out,Fake())
            self.assertEqual(validate(out),[])
            (out/'source_reviews.json').write_text('[]')
            self.assertTrue(any('reviews' in e for e in validate(out)))

    def test_full_manifest_and_rejected_source_hash_are_verified(self):
        inv,reviews=self.fixture()
        rejected={**inv['sources'][0],'doc_id':'full:rejected','text':'Other person source.','sha256':digest('Other person source.')}
        inv['sources'].append(rejected)
        reviews.append({'source':'full:rejected','part':1,'identity':'other','reason':'Different person','evidence':[],'context':[]})
        class Fake:
            model='fixture';calls=[]
            def call(self,*args):return synthesis()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'wiki';full_build(inv,reviews,out,Fake())
            p=out/'inventory.json';data=json.loads(p.read_text());data['sources'][1]['text']='Altered other person source.';p.write_text(json.dumps(data))
            self.assertTrue(any('hash mismatch' in e for e in validate(out)))
            p.write_text(json.dumps(inv))
            p=out/'_manifest.json';data=json.loads(p.read_text());data['sources_reviewed']=999;p.write_text(json.dumps(data))
            self.assertTrue(any('manifest count' in e for e in validate(out)))
