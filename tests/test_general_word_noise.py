import itertools,random,unittest
from qcdt import contract,bounds,recover
from qcdt.general import Tower,karatsuba_plan,check_plan,recover_general
from qcdt.word_noise import Majority,repetitions,certify,holdout_count

class GeneralWordNoiseTests(unittest.TestCase):
    def test_bilinear_and_bad_plan(self):
        for m in range(2,10):
            g=Tower(m);plan=karatsuba_plan(g)
            self.assertEqual(check_plan(g,plan),plan)
        with self.assertRaises(ValueError):check_plan(Tower(3),[(1,1,1)])
    def test_all_five_vertex_graphs(self):
        T=list(itertools.combinations(range(5),3))
        for word in range(1<<len(T)):
            E={e for j,e in enumerate(T) if word>>j&1};d=max(1,bounds(E)[0]);calls=[]
            def probe(a,b):calls.append((a,b));return contract(E,a,b)
            got,q,rank=recover_general(5,d,probe)
            self.assertEqual(got,E);self.assertEqual(q,4*len(calls));self.assertLessEqual(q,8*d*rank)
    def test_majority_early_equivalent(self):
        rng=random.Random(32)
        for _ in range(500):
            seq=[rng.randrange(32) for i in range(15)];i1=iter(seq);i2=iter(seq)
            a=Majority(5,lambda:next(i1),15);b=Majority(5,lambda:next(i2),15,early=False)
            self.assertEqual(a(),b());self.assertLessEqual(a.shots,b.shots)
        with self.assertRaises(ValueError):Majority(5,lambda:31,15,budget=4)()
    def test_conditional_word_noise(self):
        E={(0,1,2),(0,1,3)};eta=.15
        for seed in range(12):
            rng=random.Random(seed);last=0
            def sample(a,b):
                nonlocal last
                v=contract(E,a,b)
                if rng.random()<eta:v^=last or 31
                last=(v+1)%32;return v
            # Public cap for n=5,d=2,lambda=2: 4*3*2*3+5=77 probes.
            R=repetitions(77,eta,.01);p=Majority(5,sample,R)
            got=recover(5,2,2,p,checks=5,seed=32)
            self.assertEqual(got.edges,E);self.assertLessEqual(p.calls,77)
        self.assertGreater(holdout_count(.25,.01),holdout_count(.05,.01))
        with self.assertRaises(ValueError):holdout_count(.4,.01)
