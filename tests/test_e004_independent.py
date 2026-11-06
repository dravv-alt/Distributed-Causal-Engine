import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_e004 import credit, reference
from dce_foundation.symbolic_e004 import credits, digest, extract, infer, uniform_rank


class IndependentTests(unittest.TestCase):
    def test_forward_and_reverse_reachability(self):
        for pairs in ([], [('a','b')], [('a','b'),('b','c')], [('a','b'),('b','a'),('b','c')],
                      [('c','a'),('a','b'),('b','c')], [('a','a')]):
            f={'nodes':['a','b','c','z'],'observation_counts':dict.fromkeys(['a','b','c','z'],2),
               'edges':[{'source':a,'target':b,'multiplicity':1,'evidence':['p','c']} for a,b in pairs]}
            self.assertEqual(reference(f),infer(f))

    def test_independent_ties(self):
        r=uniform_rank(['a','b','c','d'])
        for root in ['a','d','absent']:
            for k in [1,3]:
                self.assertEqual(credits(r,root,k),credit(r['ranking'],root,k))

    def spans(self):
        a='resource:'+digest('a'); b='resource:'+digest('b')
        parent={'object_id':'p','event_ns':1,'signal':'span','resource_id':a,'trace_id':'t',
                'span_id':'p','parent_span_id':None,'duration_raw':'1','duration_unit':'UNKNOWN'}
        child={**parent,'object_id':'c','event_ns':2,'resource_id':b,'span_id':'c','parent_span_id':'p'}
        edge={'id':'edge','source':a,'target':b,'relation':'CALLS','evidence':['p','c'],'epistemic_status':'OBSERVED'}
        return {'observations':[parent,child],'edges':[edge],
                'trace_states':{'missing_parent_or_root_unknown':1,'resolved_parent':1},'start_ns':0,'cutoff_ns':2}

    def test_supported_trace_integration(self):
        f=extract(self.spans())
        self.assertEqual(infer(f),reference(f))
        self.assertEqual(len(f['edges']),1)

    def test_evidence_conservation(self):
        p=self.spans(); p['edges']=[]
        with self.assertRaises(ValueError):extract(p)

    def test_cross_trace_rejected(self):
        p=self.spans(); p['observations'][1]['trace_id']='different'
        with self.assertRaises(ValueError):extract(p)

    def test_wrong_endpoint_rejected(self):
        p=self.spans(); p['edges'][0]['target']=p['edges'][0]['source']
        with self.assertRaises(ValueError):extract(p)

    def test_future_parent_rejected(self):
        p=self.spans(); p['observations'][0]['event_ns']=3
        with self.assertRaises(ValueError):extract(p)

    def test_missing_parent_is_not_edge(self):
        p=self.spans(); p['observations']=p['observations'][1:]; p['edges']=[]; p['trace_states']={'unresolved_parent':1}
        f=extract(p)
        self.assertTrue(infer(f)['symbolic_topology_v1']['abstention'])

    def test_values_do_not_affect_rank(self):
        p=self.spans(); old=infer(extract(p))
        for o in p['observations']:o['duration_raw']='999999999999'
        self.assertEqual(infer(extract(p)),old)


if __name__=='__main__':unittest.main()
