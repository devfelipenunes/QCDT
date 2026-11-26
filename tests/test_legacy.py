import importlib.util
import random
import unittest
from qcdt import contract
from qcdt.legacy import recover_legacy

@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'),'optional historical dependencies')
class LegacyTests(unittest.TestCase):
    def test_exact_variants(self):
        E={(0,1,2),(0,1,3)}
        for version in ('v0.4','v0.5'):
            r=recover_legacy(version,5,2,2,lambda a,b:contract(E,a,b))
            self.assertEqual(r.edges,E);self.assertEqual(r.verification_queries,40)
            self.assertGreater(r.acquisition_queries,0)
    def test_voting_and_simplex(self):
        E={(0,1,2)}
        r=recover_legacy('v0.8',5,1,1,lambda a,b:contract(E,a,b),observations=2048)
        self.assertEqual(r.edges,E);self.assertEqual(r.acquisition_queries,8192)
        rng=random.Random(120)
        def sample(a,b):return contract(E,a,b)^sum((rng.random()<.05)<<i for i in range(5))
        r=recover_legacy('v0.10-simplex',5,1,1,sample,eta=.05)
        self.assertEqual(r.edges,E);self.assertGreater(r.verification_queries,0)
    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):recover_legacy('v0.4',5,1,1,lambda a,b:0,eta=.1)
