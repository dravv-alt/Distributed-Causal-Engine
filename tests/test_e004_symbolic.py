import copy
import inspect
import unittest
from dce_foundation.symbolic_e004 import (METHODS, activity_rank, credits, digest,
                                          extract, infer, topology_rank, uniform_rank)


def resource(name):
    return 'resource:'+digest(name)


class SymbolicTests(unittest.TestCase):
    def test_direction(self):
        r = topology_rank(['a','b','c'], [('a','b'),('b','c')])
        self.assertEqual([(x['resource_id'],x['score']) for x in r['ranking']], [('c',2),('b',1),('a',0)])

    def test_cycles(self):
        r = topology_rank(['a','b','c'], [('a','b'),('b','a'),('b','c')])
        self.assertEqual(r['ranking'][0]['supporting_callers'], ['a','b'])

    def test_parallel_edges(self):
        self.assertEqual(topology_rank(['a','b'], [('a','b')]), topology_rank(['b','a'], [('a','b')]*3))

    def test_self_loop_abstention(self):
        self.assertIsNotNone(topology_rank(['a'], [('a','a')])['abstention'])

    def test_disconnected(self):
        self.assertEqual(topology_rank(['a','b','z'], [('a','b')])['ranking'][-1]['score'],0)

    def test_missing_endpoint(self):
        with self.assertRaises(ValueError): topology_rank(['a'], [('a','b')])

    def test_activity_independence(self):
        self.assertEqual(list(inspect.signature(activity_rank).parameters), ['counts'])
        self.assertEqual(activity_rank({'a':4,'b':1})['ranking'][0]['resource_id'], 'a')

    def test_uniform(self):
        self.assertEqual(credits(uniform_rank(['a','b','c','d']), 'd',1)['tie_aware'], .25)

    def test_tie_boundary(self):
        r = activity_rank({'a':5,'b':2,'c':2,'d':2})
        self.assertEqual(credits(r,'d',3)['tie_aware'], 2/3)

    def test_root_absent(self):
        self.assertEqual(credits(uniform_rank(['a']), 'missing',3)['tie_aware'],0)

    def test_empty(self):
        self.assertTrue(all(r['abstention'] for r in infer({'nodes':[], 'edges':[], 'observation_counts':{}}).values()))

    def test_repeat_and_no_mutation(self):
        f={'nodes':['a','b'], 'edges':[{'source':'a','target':'b'}], 'observation_counts':{'a':1,'b':2}}
        old = copy.deepcopy(f)
        self.assertEqual(infer(f), infer(f,reverse=True))
        self.assertEqual(f,old)

    def test_labels_not_arguments(self):
        self.assertEqual(list(inspect.signature(topology_rank).parameters), ['nodes','edges'])
        f={'nodes':['a'], 'edges':[], 'observation_counts':{'a':1}}
        old=infer(f)
        labels={'root_entity':'a'}
        labels['root_entity']='b'
        self.assertEqual(infer(f),old)

    def fixture(self):
        return {'observations':[{'object_id':'o','event_ns':1,'signal':'log',
            'resource_id':resource('a'),'severity':'UNKNOWN','message_available':False}],
            'edges':[],'trace_states':{},'start_ns':0,'cutoff_ns':2}

    def test_extract(self):
        self.assertEqual(extract(self.fixture())['observation_counts'],{resource('a'):1})

    def test_future_rejected(self):
        f=self.fixture(); f['observations'][0]['event_ns']=3
        with self.assertRaises(ValueError): extract(f)

    def test_answer_field_rejected(self):
        f=self.fixture(); f['observations'][0]['root_entity']='a'
        with self.assertRaises(ValueError): extract(f)

    def test_duplicate_rejected(self):
        f=self.fixture(); f['observations']*=2
        with self.assertRaises(ValueError): extract(f)

    def test_unknown_not_healthy(self):
        f=extract(self.fixture())
        self.assertNotIn('healthy', str(f))
        self.assertEqual(infer(f)[METHODS[0]]['abstention'],'NO_OBSERVED_INTER_COMPONENT_CALLS')


if __name__=='__main__':
    unittest.main()
