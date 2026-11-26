import unittest
from qcdt import contract
from qcdt.backends import derivative_circuit

class AerTests(unittest.TestCase):
    def test_ideal_and_readout_noise(self):
        try:
            from qiskit import QuantumCircuit, transpile
            from qiskit_aer import AerSimulator
            from qiskit_aer.noise import NoiseModel, ReadoutError
        except ImportError:
            self.skipTest('Qiskit Aer not installed')
        E = {(0, 1, 2), (0, 2, 3)}
        n = 4
        oracle = QuantumCircuit(n)
        oracle.z(0); oracle.cz(1, 2)
        for i,j,k in sorted(E): oracle.ccz(i,j,k)
        sim = AerSimulator()
        masks = [(1,2),(3,6),(15,5),(0,9),(9,9)]
        circuits = []
        for a,b in masks:
            qc = derivative_circuit(oracle,a,b)
            qc.measure_all(); circuits.append(qc)
        compiled = transpile(circuits,sim,seed_transpiler=92)
        ideal = sim.run(compiled,shots=32,seed_simulator=92).result()
        for j,(a,b) in enumerate(masks):
            key = format(contract(E,a,b),f'0{n}b')
            self.assertEqual(ideal.get_counts(j),{key:32})
        noise = NoiseModel()
        noise.add_all_qubit_readout_error(ReadoutError([[0,1],[1,0]]))
        flipped = sim.run(compiled,noise_model=noise,shots=32,seed_simulator=92).result()
        for j,(a,b) in enumerate(masks):
            key = format(contract(E,a,b)^((1<<n)-1),f'0{n}b')
            self.assertEqual(flipped.get_counts(j),{key:32})
        # Synthetic stationary BSC, not a calibrated hardware model.
        noise = NoiseModel()
        noise.add_all_qubit_readout_error(ReadoutError([[.9,.1],[.1,.9]]))
        shots = 2048
        sample = sim.run(compiled,noise_model=noise,shots=shots,seed_simulator=92).result()
        for j,(a,b) in enumerate(masks):
            expected = contract(E,a,b)
            errors = sum((int(k,2)^expected).bit_count()*v for k,v in sample.get_counts(j).items())
            self.assertTrue(.07 < errors/(n*shots) < .13)
