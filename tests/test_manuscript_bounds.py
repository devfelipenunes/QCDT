"""Finite checks for manuscript Section 4, not evidence of asymptotic novelty."""
import itertools
import math
import random
import unittest
from qcdt import contract

def mask_family(n,d):
    edges=list(itertools.combinations(range(n),2))
    s=min(2*d,len(edges))
    differences=[p for p in range(1,1<<len(edges)) if p.bit_count()<=s]
    k=0
    while len(differences)*5**k>=8**k:k+=1
    def signature(a,b):
        return sum((((a>>i&1)*(b>>j&1))^((a>>j&1)*(b>>i&1)))<<p
                   for p,(i,j) in enumerate(edges))
    rng=random.Random(3601+n+d)
    # Sampling is only a finite test fixture. The proof uses finite exhaustive
    # search for deterministic uniform construction; no oracle is needed.
    for _ in range(200):
        masks=[(rng.randrange(1<<n),rng.randrange(1<<n)) for _ in range(k)]
        rows=[signature(a,b) for a,b in masks]
        if all(any((w&r).bit_count()%2 for r in rows) for w in differences):
            return masks,edges
    raise AssertionError('failed to find small separating fixture')

class ManuscriptBoundsTests(unittest.TestCase):
    def test_universal_sketch_and_classical_simulation(self):
        n=5
        triples=list(itertools.combinations(range(n),3))
        masks,pairs=mask_family(n,math.comb(n-1,2))
        lookups=[]
        for i in range(n):
            admissible=[(j,k) for j,k in pairs if i not in (j,k)]
            lookup={}
            for word in range(1<<len(admissible)):
                link=[p for t,p in enumerate(admissible) if word>>t&1]
                sig=tuple(sum(((a>>j&1)*(b>>k&1))^((a>>k&1)*(b>>j&1))
                              for j,k in link)%2 for a,b in masks)
                self.assertNotIn(sig,lookup)
                lookup[sig]=link
            lookups.append(lookup)
        for word in range(1<<len(triples)):
            E={e for j,e in enumerate(triples) if word>>j&1}
            observations=[contract(E,a,b) for a,b in masks]
            got=set()
            for i in range(n):
                sig=tuple(v>>i&1 for v in observations)
                got.update(tuple(sorted((i,j,k))) for j,k in lookups[i][sig])
            self.assertEqual(got,E)
            # Verify value-query simulation including lower-degree nuisance terms
            # on a fixed subset of fixtures to keep this finite test lightweight.
            if word%31==0:
                terms=[sum(1<<j for j in e) for e in E]+[0,1,6]
                f=lambda x:sum((x&m)==m for m in terms)%2
                for (a,b),v in zip(masks,observations):
                    for i in range(n):
                        c=1<<i
                        self.assertEqual(v>>i&1,sum(f(x) for x in (0,a,b,c,a^b,a^c,b^c,a^b^c))%2)
    def test_sparse_matrix_separation(self):
        for d in (1,2,3):
            masks,pairs=mask_family(5,d)
            for word in range(1,1<<len(pairs)):
                if word.bit_count()>2*d:continue
                L=[p for t,p in enumerate(pairs) if word>>t&1]
                self.assertTrue(any(sum(((a>>j&1)*(b>>k&1))^((a>>k&1)*(b>>j&1))
                                        for j,k in L)%2 for a,b in masks))
