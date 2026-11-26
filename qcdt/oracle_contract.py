"""Synthetic controls for coherent Boolean phase-oracle access.

Barriers preserve compiler scheduling boundaries; they do not hide a gate
list, enforce an external device API, or establish physical oracle cost.
"""
def boundary_derivative(oracle,a,b):
    from qiskit import QuantumCircuit
    n=oracle.num_qubits
    if oracle.num_clbits or not 0<=a<1<<n or not 0<=b<1<<n:
        raise ValueError('invalid oracle or mask')
    qc=QuantumCircuit(n)
    qc.h(range(n))
    for mask in (a,b,a,b):
        qc.barrier(range(n))
        qc.compose(oracle,inplace=True)
        qc.barrier(range(n))
        for j in range(n):
            if mask>>j&1:qc.x(j)
    qc.h(range(n))
    return qc
