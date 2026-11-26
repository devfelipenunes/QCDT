import itertools as it
import random
import unittest
from qcdt import bounds, contract, recover
from qcdt.backends import truth_table_probe, qiskit_probe

PASCH = [ {(0,1,2),(0,3,4),(1,3,5),(2,4,5)},
          {(0,1,3),(0,2,4),(1,2,5),(3,4,5)} ]

class ReferenceTests(unittest.TestCase):
    def check_graph(self, n, E, backend=None):
        d, lam = bounds(E)
        if backend is None:
            backend = lambda a, b: contract(E, a, b)
        r = recover(n, max(d, 1), max(lam, 1), backend, seed=42)
        self.assertEqual(r.edges, E)
        return r

    def test_exhaustive_five(self):
        triples = list(it.combinations(range(5), 3))
        for m in range(1 << len(triples)):
            E = {e for j, e in enumerate(triples) if m >> j & 1}
            self.check_graph(5, E)

    def test_linear_six(self):
        T = list(it.combinations(range(6), 3))
        def visit(start, E, pairs):
            self.check_graph(6, E)
            for j in range(start, len(T)):
                p = set(it.combinations(T[j], 2))
                if not p & pairs:
                    visit(j + 1, E | {T[j]}, pairs | p)
        visit(0, set(), set())

    def test_pasch_and_truth_table(self):
        for E in PASCH:
            r = self.check_graph(6, E, truth_table_probe(6, E | {(0,), (1,2), ()}))
            self.assertGreater(r.color_bits, 0)

    def test_independent_derivative(self):
        E = {(0,1,2), (0,2,3)}
        f = truth_table_probe(4, E | {(1,), (2,3), ()})
        for a in range(16):
            for b in range(16):
                self.assertEqual(f(a,b), contract(E,a,b))

    def test_quartic_rejected_by_backend(self):
        with self.assertRaises(ValueError):
            truth_table_probe(4, {(0,1,2,3)})(1,2)

    def test_scale(self):
        for n in (32, 128, 256):
            E = {(i,i+1,i+2) for i in range(0,n-2,3)}
            r = self.check_graph(n, E)
            self.assertLessEqual(r.acquisition_queries, 8*n.bit_length())

    def test_qiskit_optional(self):
        try:
            from qiskit import QuantumCircuit
        except ImportError:
            self.skipTest("Qiskit not installed")
        for E in PASCH:
            oracle = QuantumCircuit(6)
            oracle.z(0); oracle.cz(1,2)
            for i,j,k in E: oracle.ccz(i,j,k)
            self.check_graph(6, E, qiskit_probe(oracle))

if __name__ == '__main__': unittest.main()
