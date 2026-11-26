import unittest
from qcdt import contract,recover
from qcdt.aer_backend import majority_word,AerProbe

class AerRecoveryTests(unittest.TestCase):
    def test_majority(self):
        self.assertEqual(majority_word({'101':2,'001':1},3),5)
        with self.assertRaisesRegex(ValueError,'tie'):majority_word({'0':1,'1':1},1)
        with self.assertRaises(ValueError):majority_word({'00':1},1)
    def test_routed_recovery(self):
        try:
            from qiskit import QuantumCircuit
            import qiskit_aer
        except ImportError:self.skipTest('Qiskit Aer unavailable')
        E={(0,1,3)};qc=QuantumCircuit(4);qc.ccz(0,1,3);qc.z(0);qc.cz(1,2)
        for p,shots in ((0,1),(.1,31)):
            backend=AerProbe(qc,shots=shots,readout=p,seed=243)
            for a,b in [(1,2),(3,9),(15,8)]:self.assertEqual(backend(a,b),contract(E,a,b))
            baseline=backend.calls
            r=recover(4,1,1,backend,seed=32)
            self.assertEqual(r.edges,E)
            self.assertEqual(4*(backend.calls-baseline),r.acquisition_queries+r.verification_queries)
            self.assertGreater(backend.metrics()['cx_executions'],0)
