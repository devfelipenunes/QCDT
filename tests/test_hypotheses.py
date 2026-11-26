import itertools
import math
import random
import unittest
from qcdt import contract,bounds
from qcdt.known_support import recover_linear
from qcdt.deterministic_codes import basis_of,prefix_count,deterministic_codes
from qcdt.phase_feasibility import phase_diagonal
from qcdt.phase_cycling import distribution,sector_variances,relative_bit_probability,relative_cost

class HypothesisTests(unittest.TestCase):
    def test_prefix_counts(self):
        rng=random.Random(301)
        for width in range(2,9):
            for _ in range(12):
                basis=basis_of(rng.randrange(1<<width) for _ in range(rng.randrange(width+1)))
                span=[0]
                for v in basis.values():span += [w^v for w in span]
                for length in range(width+1):
                    for p in range(1<<length):
                        self.assertEqual(prefix_count(basis,width,length,p),
                            sum(v>>(width-length)==p for v in span))
    def test_linear_exhaustive_and_large(self):
        T=list(itertools.combinations(range(6),3));count=0
        def walk(start,E,pairs):
            nonlocal count
            d,_=bounds(E)
            self.assertEqual(recover_linear(6,max(1,d),lambda a,b:contract(E,a,b),deterministic=True)[0],E)
            count+=1
            for j in range(start,len(T)):
                p=set(itertools.combinations(T[j],2))
                if not p&pairs:walk(j+1,E|{T[j]},pairs|p)
        walk(0,set(),set());self.assertEqual(count,271)
        for n in (24,48,96):
            E={tuple(i+x for x in e) for i in range(0,n,6)
               for e in ((0,1,2),(0,3,4),(1,3,5),(2,4,5))}
            self.assertEqual(recover_linear(n,2,lambda a,b:contract(E,a,b),deterministic=True)[0],E)
        for n in (16,32,64):
            N=[{(i-1)%n,(i+1)%n,(i-3)%n,(i+3)%n} for i in range(n)]
            masks,labels=deterministic_codes(N)
            self.assertEqual((masks,labels),deterministic_codes(N))
            self.assertTrue(all(len(basis_of(labels[v] for v in ns))==len(ns) for ns in N))
    def test_full_vector_detection_bound(self):
        # Exact count via rank of b -> D(a,b). All nonzero cubic graphs n=4,5.
        for n in (4,5):
            T=list(itertools.combinations(range(n),3));size=1<<n
            maximum=0
            for m in range(1,1<<len(T)):
                E=[e for i,e in enumerate(T) if m>>i&1]
                zeros=sum(1<<(n-len(basis_of(contract(E,a,1<<j) for j in range(n)))) for a in range(size))
                self.assertLessEqual(32*zeros,11*size*size)
                maximum=max(maximum,zeros)
            self.assertEqual(32*maximum,11*size*size)
    def test_phase_cycling_and_relative_bit(self):
        rng=random.Random(130)
        for n in (3,4):
            terms=[(),(0,),(1,2),(0,1,2)]
            E={(0,1,2)};size=1<<n
            ideal=phase_diagonal(n,terms)
            offsets=[rng.uniform(-.5,.5) for _ in terms]
            actual=phase_diagonal(n,terms,offsets)
            theta=[sum(t for e,t in zip(terms,offsets) if all(x>>i&1 for i in e)) for x in range(size)]
            var=sum((x-sum(theta)/size)**2 for x in theta)/size
            for a in range(size):
                for b in range(size):
                    variances=sector_variances(theta,a,b);errors=[]
                    self.assertAlmostEqual(sum(variances.values()),16*var)
                    for sector,v in variances.items():
                        target=contract(E,a,b)
                        self.assertAlmostEqual(distribution(ideal,a,b,sector)[target],1.)
                        probs=distribution(actual,a,b,sector)
                        self.assertAlmostEqual(sum(probs),1.)
                        err=1-probs[target];errors.append(err)
                        self.assertLessEqual(err,v+1e-10)
                    self.assertLessEqual(sum(errors)/4,4*var+1e-10)
            for x in range(size):
                expected=int(ideal[x]!=ideal[0])
                self.assertAlmostEqual(relative_bit_probability(ideal,x),expected)
                self.assertEqual(relative_cost(x)['oracle_calls'],int(x!=0))
