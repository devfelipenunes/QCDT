import itertools
import random
import unittest
from qcdt import contract, recover, bounds
from qcdt.baselines import dense_cubic, classical_cubic
from qcdt.backends import truth_table_probe

class BaselineTests(unittest.TestCase):
    def test_matched_models(self):
        rng = random.Random(92)
        for n in (4, 5, 6, 8):
            for _ in range(5):
                E = set(rng.sample(list(itertools.combinations(range(n),3)), min(4, n)))
                terms = E | {(0,), (1, 2), ()}
                masks = [sum(1 << i for i in e) for e in terms]
                f = lambda x: sum((x & m) == m for m in masks) % 2
                probe = truth_table_probe(n, terms)
                d, lam = bounds(E)
                self.assertEqual(recover(n,d,lam,probe,seed=92).edges,E)
                self.assertEqual(dense_cubic(n,probe),(E,2*n*(n-1)))
                self.assertEqual(classical_cubic(n,f),(E,sum(__import__('math').comb(n,k) for k in range(4))))
