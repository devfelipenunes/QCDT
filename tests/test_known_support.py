import itertools
import unittest
from qcdt import bounds, contract
from qcdt.known_support import local_codes, solve_local, recover_linear

class KnownSupportTests(unittest.TestCase):
    def test_local_codes(self):
        n=32;N=[{(i-1)%n,(i+1)%n,(i-3)%n,(i+3)%n} for i in range(n)]
        masks,labels=local_codes(N,seed=91)
        self.assertLess(len(masks),n)
        for ns in N:
            for r in range(1<<len(ns)):
                truth={j for t,j in enumerate(sorted(ns)) if r>>t&1}
                w=0
                for j in truth:w^=labels[j]
                self.assertEqual(solve_local(labels,ns,w),truth)
    def test_exhaustive_linear(self):
        T=list(itertools.combinations(range(6),3))
        count=0
        def walk(start,E,pairs):
            nonlocal count
            d,_=bounds(E);got,_,_=recover_linear(6,max(1,d),lambda a,b:contract(E,a,b))
            self.assertEqual(got,E);count+=1
            for j in range(start,len(T)):
                ps=set(itertools.combinations(T[j],2))
                if not ps&pairs:walk(j+1,E|{T[j]},pairs|ps)
        walk(0,set(),set())
        self.assertEqual(count,271)
    def test_disjoint_pasch_blocks(self):
        for n in (24,48,96):
            E={tuple(x+i for x in e) for i in range(0,n,6)
               for e in ((0,1,2),(0,3,4),(1,3,5),(2,4,5))}
            self.assertEqual(recover_linear(n,2,lambda a,b:contract(E,a,b))[0],E)
