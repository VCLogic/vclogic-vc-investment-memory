import unittest
from wiki_build.full_review import review_errors, review_packets


class FullReviewTests(unittest.TestCase):
    def setUp(self):
        self.packet={'doc_id':'full:one','part':1,'text':'Hyatt said I favor patient founders.', 'kind':'web','metadata':{}}
        self.result={'reviews':[{'source':'full:one','part':1,'identity':'target','reason':'Named investor',
            'evidence':[{'quote':'I favor patient founders.','label':'founder_qualities','direction':'positive','support':'explicit',
                         'interpretation':'Favors patience','attribution_basis':'The sentence explicitly credits Hyatt'}], 'context':[]}]}

    def test_complete_attributed_review_passes(self):
        self.assertEqual(review_errors(self.result,[self.packet]),[])

    def test_omitted_packet_is_error(self):
        self.assertTrue(review_errors({'reviews':[]},[self.packet]))

    def test_other_identity_cannot_contribute_evidence(self):
        self.result['reviews'][0]['identity']='other'
        self.assertTrue(any('identity' in e for e in review_errors(self.result,[self.packet])))

    def test_context_requires_exact_supporting_passage(self):
        self.result['reviews'][0]['context']=[{'quote':'He owns Acme','claim':'Owns Acme','kind':'company_relationship'}]
        self.assertTrue(any('verbatim' in e for e in review_errors(self.result,[self.packet])))

    def test_review_packets_cover_all_characters(self):
        source={**self.packet,'title':'x','url':'x','published_at':None}
        packets=review_packets([source],100)
        self.assertEqual(''.join(p['text'] for p in packets),source['text'])

    def test_wrong_speaker_quote_rejected(self):
        self.packet.update(kind='transcript',text='[SPEAKER_0]\nI favor patient founders.\n[SPEAKER_1]\nI prefer efficient companies.',metadata={'accepted_speaker':'SPEAKER_1'})
        self.assertTrue(any('speaker' in e for e in review_errors(self.result,[self.packet])))

    def test_carried_speaker_checked_against_full_source(self):
        source={**self.packet,'text':'[SPEAKER_0]\n'+'Other words. '*30+'\n[SPEAKER_1]\nI favor patient founders.',
                'kind':'transcript','metadata':{'accepted_speaker':'SPEAKER_1'},'title':'x','url':'x','published_at':None}
        packets=review_packets([source],100)
        self.assertEqual(packets[1]['speaker_at_start'],'SPEAKER_0')

    def test_review_fingerprint_changes_with_identity_attribution_and_rules(self):
        import copy
        from wiki_build.full_review import review_fingerprint
        inv={'identity':{'canonical_name':'Hyatt'}}
        original=review_fingerprint(inv,self.packet)
        packet=copy.deepcopy(self.packet);packet['metadata']['accepted_speaker']='SPEAKER_1'
        self.assertNotEqual(original,review_fingerprint(inv,packet))
        self.assertNotEqual(original,review_fingerprint({'identity':{'canonical_name':'Other'}},self.packet))

    def test_stale_prior_review_is_reprocessed(self):
        from wiki_build.full_review import review_all,review_fingerprint
        source={**self.packet,'title':'x','url':'x','published_at':None}
        inv={'identity':{'canonical_name':'Hyatt'},'sources':[source]}
        stale={**self.result['reviews'][0],'identity':'uncertain','evidence':[],'input_fingerprint':'old'}
        result=self.result
        class Fake:
            calls=0
            def call(self,*args):self.calls+=1;return result
        generator=Fake()
        reviewed=review_all(inv,generator,workers=1,existing_reviews=[stale])
        self.assertEqual(generator.calls,1)
        self.assertEqual(reviewed[0]['identity'],'target')
        review_all(inv,generator,workers=1,existing_reviews=reviewed)
        self.assertEqual(generator.calls,1)
