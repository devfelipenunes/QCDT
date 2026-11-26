import itertools
import math
import unittest
from qcdt import bounds,contract,recover
from qcdt.matched import balanced_dense,label_bits,classical_sparse
from qcdt.backends import truth_table_probe

class MatchedTests(unittest.TestCase):
    def test_small_exhaustive(self):
        T=list(itertools.combinations(range(5),3))
        for mask in range(1<<len(T)):
            E={e for j,e in enumerate(T) if mask>>j&1}
            p=lambda a,b:contract(E,a,b)
            self.assertEqual(balanced_dense(5,p),(E,16))
            d,lam=bounds(E)
            if lam<=1:self.assertEqual(label_bits(5,max(1,d),p)[0],E)
    def test_mixed_and_pasch(self):
        for E in ({(0,1,2),(0,3,4),(1,3,5),(2,4,5)}, {(0,1,2),(0,1,3)},set()):
            n=6;d,lam=bounds(E); terms=E|{(),(0,),(1,2)}
            p=truth_table_probe(n,terms)
            masks=[sum(1<<i for i in t) for t in terms]
            f=lambda x:sum((x&m)==m for m in masks)&1
            self.assertEqual(balanced_dense(n,p)[0],E)
            self.assertEqual(classical_sparse(n,max(1,d),f,seed=32)[0],E)
            if lam<=1:self.assertEqual(label_bits(n,max(1,d),p)[0],E)
