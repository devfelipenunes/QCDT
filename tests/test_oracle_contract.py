import unittest
from qcdt.oracle_contract import boundary_derivative
from qcdt.backends import derivative_circuit,truth_table_probe

class OracleContractTests(unittest.TestCase):
    def test_boundary_semantics(self):
        try:
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import Statevector,Operator
        except ImportError:self.skipTest('Qiskit unavailable')
        E={(0,1,3),(0,2,3)}
        qc=QuantumCircuit(4);qc.z(0);qc.cz(1,2)
        for e in sorted(E):qc.ccz(*e)
        p=truth_table_probe(4,E|{(0,),(1,2)})
        for a,b in [(0,0),(1,2),(3,9),(15,8),(5,5)]:
            f=derivative_circuit(qc,a,b);g=boundary_derivative(qc,a,b)
            self.assertEqual(g.count_ops().get('barrier'),8)
            # Remove directives only for unitary comparison, not resource compilation.
            clean=QuantumCircuit(4)
            for ins in g.data:
                if ins.operation.name!='barrier':
                    clean.append(ins.operation,[g.find_bit(q).index for q in ins.qubits])
            self.assertTrue(Operator(f).equiv(Operator(clean)))
            prob=Statevector.from_instruction(clean).probabilities()
            self.assertAlmostEqual(float(prob[p(a,b)]),1.)
