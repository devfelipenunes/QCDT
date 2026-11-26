import itertools
import random
import unittest
from qcdt import contract,bounds
from qcdt.field import mul
from qcdt.general import Tower,check_plan,recover_general
from qcdt.rank_provider import (SearchLimit,exact_symmetric,exact_rank_plan,
    irreducibles,weights_for_forms,practical_base,public_mask_count,
    candidate_plans,public_rank_plan,practical_rank_plan,power_basis,crt_lift)

class RankProviderTests(unittest.TestCase):
    def test_small_exact_ranks(self):
        for k,r in ((1,1),(2,3),(3,6),(4,9)):
            for p in irreducibles(k):
                plan,attempts=exact_symmetric(p)
                self.assertEqual(len(plan),r);self.assertGreater(attempts,0)
                self.assertEqual(weights_for_forms(k,lambda a,b:mul(a,b,p),[a for a,b,w in plan]),plan)
                for a in range(1<<k):
                    for b in range(1<<k):
                        result=0
                        for x,y,w in plan:
                            if (a&x).bit_count()%2 and (b&y).bit_count()%2:result^=w
                        self.assertEqual(result,mul(a,b,p))
        with self.assertRaises(SearchLimit):exact_symmetric(19,1)
        with self.assertRaises(ValueError):weights_for_forms(3,lambda a,b:mul(a,b,11),[1])
        with self.assertRaises(ValueError):crt_lift(19,[(7,practical_base(7))])

    def test_tower_plans(self):
        for m in range(2,17):
            g=Tower(m);p,columns,basis=power_basis(g)
            self.assertEqual(p.bit_length()-1,g.width);self.assertEqual(len(basis),g.width)
            plans=candidate_plans(g)
            for plan in plans.values():check_plan(g,plan)
            self.assertLessEqual(len(practical_rank_plan(g)),len(plans['karatsuba']))
        for m in (5,6):
            g=Tower(m);check_plan(g,exact_rank_plan(g,max_candidates=50000))

    def test_exhaustive_and_public_cost(self):
        triples=list(itertools.combinations(range(5),3));g=Tower(3)
        plans=candidate_plans(g)
        for d in range(1,7):
            name,plan=public_rank_plan(5,d,g)
            self.assertEqual(public_mask_count(5,d,g,plan),min(public_mask_count(5,d,g,p) for p in plans.values()))
        for w in range(1<<len(triples)):
            E={e for i,e in enumerate(triples) if w>>i&1};d=max(1,bounds(E)[0]);calls=[]
            def probe(a,b):calls.append((a,b));return contract(E,a,b)
            name,plan=public_rank_plan(5,d,g)
            got,q,_=recover_general(5,d,probe,plan_factory=lambda _:plan)
            self.assertEqual(got,E);self.assertEqual(q,4*len(calls))
            self.assertEqual(q,4*public_mask_count(5,d,g,plan))

    def test_exact_crt_end_to_end(self):
        E={(0,1,2),(0,1,3),(0,2,3),(4,5,6)}
        n=16;g=Tower(n.bit_length());plan=exact_rank_plan(g,max_candidates=50000)
        got,q,_=recover_general(n,3,lambda a,b:contract(E,a,b),plan_factory=lambda _:plan)
        self.assertEqual(got,E);self.assertEqual(q,4*public_mask_count(n,3,g,plan))
