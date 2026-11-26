"""Finite checks supporting a combinatorial proof, not a substitute for it."""
from collections import Counter
from itertools import combinations
from math import comb,factorial
import unittest

class LinearLowerBoundTests(unittest.TestCase):
    def test_integer_packing_inequalities(self):
        checks=0
        for n in range(96,513):
            for d in range(1,(n-1)//2+1):
                m=n*d//48
                self.assertGreaterEqual(96*m,n*d)
                avail=n-(3*m)//d
                self.assertGreaterEqual(20*(comb(avail,3)-3*m*(n-2)),n**3)
                checks+=1
        self.assertEqual(checks,63071)

    def test_ordered_paths_and_distinct_families(self):
        for n,d,k,expected in ((5,1,2,0),(6,1,2,10),(6,2,3,120),
                               (7,2,3,1470),(8,2,3,9240)):
            triples=list(combinations(range(n),3))
            multiplicity=Counter()
            def walk(edges,degree,pairs):
                if len(edges)==k:
                    multiplicity[tuple(sorted(edges))]+=1
                    return
                for e in triples:
                    ps=set(combinations(e,2))
                    if not ps & pairs and all(degree[i]<d for i in e):
                        walk(edges+[e],degree+Counter(e),pairs|ps)
            walk([],Counter(),set())
            self.assertEqual(len(multiplicity),expected)
            self.assertTrue(all(v==factorial(k) for v in multiplicity.values()))
