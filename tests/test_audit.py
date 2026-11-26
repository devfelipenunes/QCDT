"""Regression and exact model audit. No hardware or universal certification."""
import itertools
import random
import unittest
from qcdt import recover,contract
from qcdt.field import BCH
from qcdt.budget import circuit_cap,odd_shots,dense_certified

class AuditTests(unittest.TestCase):
    def test_bch_all_sparse_vectors(self):
        count=0
        for n in (3,4,5,6,7,8,9):
            for k in range(1,n+1):
                H=BCH(n,k)
                for w in range(1<<n):
                    if w.bit_count()>k:continue
                    self.assertEqual(H.decode([(w&a).bit_count()%2 for a in H.masks]),
                                     [j for j in range(n) if w>>j&1])
                    count+=1
        self.assertEqual(count,5101)

    def test_slack_promises_and_public_budget(self):
        rng=random.Random(20261126); count=0
        for n in (3,4,5,6,7,8,9,16,32):
            for _ in range(18):
                d=rng.randint(1,min(4,n-1));lam=rng.randint(1,d)
                E=set();deg=[0]*n;ps={}
                for _ in range(n*12):
                    e=tuple(sorted(rng.sample(range(n),3)));pairs=list(itertools.combinations(e,2))
                    if e in E or any(deg[i]>=d for i in e) or any(ps.get(p,0)>=lam for p in pairs):continue
                    E.add(e)
                    for i in e:deg[i]+=1
                    for p in pairs:ps[p]=ps.get(p,0)+1
                calls=[]
                def probe(a,b):
                    calls.append((a,b))
                    return contract(E,a,b)
                r=recover(n,d,lam,probe,seed=123)
                self.assertEqual(r.edges,E)
                self.assertEqual(r.acquisition_queries+r.verification_queries,4*len(calls))
                self.assertLessEqual(len(calls),circuit_cap(n,d,lam,'qcdt'))
                count+=1
        self.assertEqual(count,162)

    def test_same_public_promise_different_hidden_plans(self):
        E1={(0,1,2),(0,3,4)}
        E2=E1|{(1,3,5),(2,4,5)}
        costs=[]
        for E in (E1,E2):
            r=recover(6,2,1,lambda a,b:contract(E,a,b),seed=32)
            costs.append((r.acquisition_queries+r.verification_queries)//4)
        self.assertEqual(costs,[17,23])
        cap=circuit_cap(6,2,1,'qcdt')
        self.assertGreaterEqual(cap,max(costs))
        s=odd_shots(2048,cap)
        self.assertEqual(s%2,1)
        self.assertLessEqual(s*cap,2048)

    def test_dense_same_holdout(self):
        E={(0,1,2),(0,3,4)};calls=[]
        def probe(a,b):
            calls.append((a,b))
            return contract(E,a,b)
        self.assertEqual(dense_certified(6,2,1,probe),E)
        self.assertEqual(len(calls),circuit_cap(6,2,1,'dense-certified'))
        with self.assertRaises(ValueError):odd_shots(1,2)
