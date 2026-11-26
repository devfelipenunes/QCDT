"""Small-instance independent simulator and optional Qiskit circuit backend."""
import math


def truth_table_probe(n, terms):
    masks = [sum(1 << i for i in e) for e in terms]
    f = [sum((x & m) == m for m in masks) % 2 for x in range(1 << n)]
    def probe(a, b):
        w = [(-1) ** (f[x] ^ f[x ^ a] ^ f[x ^ b] ^ f[x ^ a ^ b]) for x in range(1 << n)]
        step = 1
        while step < len(w):
            for off in range(0, len(w), 2 * step):
                for j in range(off, off + step):
                    u, v = w[j], w[j + step]
                    w[j], w[j + step] = u + v, u - v
            step *= 2
        out = max(range(len(w)), key=lambda j: abs(w[j]))
        if abs(w[out]) != len(w):
            raise ValueError("non-affine derivative")
        return out
    return probe


def derivative_circuit(oracle, a, b):
    from qiskit import QuantumCircuit
    n = oracle.num_qubits
    if oracle.num_clbits or not 0 <= a < 1 << n or not 0 <= b < 1 << n:
        raise ValueError("invalid oracle or mask")
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for mask in (a, b, a, b):
        qc.compose(oracle, inplace=True)
        for j in range(n):
            if mask >> j & 1:
                qc.x(j)
    qc.h(range(n))
    return qc


def qiskit_probe(oracle):
    from qiskit.quantum_info import Statevector
    def probe(a, b):
        probs = Statevector.from_instruction(derivative_circuit(oracle, a, b)).probabilities()
        out = int(probs.argmax())
        if not math.isclose(float(probs[out]), 1.0, abs_tol=1e-9):
            raise ValueError("non-affine derivative")
        return out
    return probe
