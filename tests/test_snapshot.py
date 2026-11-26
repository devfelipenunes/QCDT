import unittest
from qcdt import contract
from qcdt.snapshot_backend import SnapshotProbe,snapshot_metadata

class SnapshotTests(unittest.TestCase):
    def test_layout_and_budget(self):
        try:
            from qiskit import QuantumCircuit
            from qiskit_ibm_runtime.fake_provider import FakeManilaV2
            import qiskit_aer
        except ImportError:self.skipTest('snapshot dependencies unavailable')
        device=FakeManilaV2();meta=snapshot_metadata(device)
        self.assertEqual(meta['num_qubits'],5);self.assertTrue(meta['gates'])
        E={(0,1,3)};qc=QuantumCircuit(4);qc.ccz(0,1,3);qc.z(0);qc.cz(1,2)
        p=SnapshotProbe(qc,device,shots=3,budget=9,noisy=False)
        for a,b in [(1,2),(3,9),(15,8)]:
            self.assertEqual(p(a,b),contract(E,a,b))
        self.assertEqual(p.metrics()['phase_calls'],36)
        with self.assertRaisesRegex(ValueError,'budget'):p(2,4)
        noisy=SnapshotProbe(qc,device,shots=3,budget=3,seed=243,noisy=True)
        self.assertTrue(0<=noisy(3,9)<16)
        self.assertEqual(sum(noisy.records[0]['counts'].values()),3)
