import math
import unittest
from qcdt.phase_feasibility import phase_diagonal,derivative_distribution
from benchmarks.phase_feasibility import run

class PhaseFeasibilityTests(unittest.TestCase):
    def test_fixed_time_alias(self):
        terms=[(0,1,2)]
        a=phase_diagonal(3,terms,[0.])
        b=phase_diagonal(3,terms,[2*math.pi])
        self.assertTrue(all(abs(u-v)<1e-12 for u,v in zip(a,b)))
        # Turning a pi phase into 2pi produces the identity, hiding the term.
        c=phase_diagonal(3,terms,[math.pi])
        self.assertTrue(all(abs(v-1)<1e-12 for v in c))
    def test_coherent_phase_error(self):
        r=run()
        self.assertEqual(sum(len(x['observations']) for x in r['rows']),840)
        self.assertTrue(all(x['max_word_error']<=x['bound']+1e-10 for x in r['rows']))
        self.assertTrue(all(x['max_word_error']<1e-10 for x in r['rows'] if x['phase_offset_max']==0))
        self.assertGreater(max(x['max_word_error'] for x in r['rows']),.5)
