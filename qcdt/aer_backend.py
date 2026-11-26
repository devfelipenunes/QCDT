"""Optional Aer shot backend with explicit synthetic noise and resource accounting."""
from .backends import derivative_circuit


def majority_word(counts, n):
    total=sum(counts.values())
    if total<=0 or any(v<0 or len(k)!=n or any(c not in '01' for c in k) for k,v in counts.items()):
        raise ValueError('invalid measurement counts')
    word=0
    for i in range(n):
        ones=sum(v for k,v in counts.items() if k[-1-i]=='1')
        if 2*ones==total: raise ValueError('majority tie')
        if 2*ones>total: word|=1<<i
    return word


class AerProbe:
    def __init__(self, oracle, *, shots=1, seed=42, readout=0., p1=0., p2=0., routed=True):
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
        from qiskit.transpiler import CouplingMap
        if shots<1 or shots%2==0 or not all(0<=p<1 for p in (readout,p1,p2)):
            raise ValueError('use odd shots and valid noise rates')
        self.oracle=oracle;self.n=oracle.num_qubits;self.shots=shots;self.seed=seed
        noise=NoiseModel()
        if readout: noise.add_all_qubit_readout_error(ReadoutError([[1-readout,readout],[readout,1-readout]]))
        if p1: noise.add_all_qubit_quantum_error(depolarizing_error(p1,1),['sx','x'])
        if p2: noise.add_all_qubit_quantum_error(depolarizing_error(p2,2),['cx'])
        self.sim=AerSimulator(noise_model=noise,max_parallel_threads=1)
        self.coupling=CouplingMap.from_line(self.n) if routed else None
        self.compiled={};self.calls=0;self.cx=0;self.depth=0;self.gates=0

    def __call__(self,a,b):
        from qiskit import transpile
        key=(a,b)
        if key not in self.compiled:
            qc=derivative_circuit(self.oracle,a,b);qc.measure_all()
            self.compiled[key]=transpile(qc,basis_gates=['rz','sx','x','cx'],coupling_map=self.coupling,
                                         optimization_level=1,seed_transpiler=self.seed)
        qc=self.compiled[key];self.calls+=1
        self.cx+=int(qc.count_ops().get('cx',0))*self.shots
        self.gates+=qc.size()*self.shots
        self.depth=max(self.depth,qc.depth())
        counts=self.sim.run(qc,shots=self.shots,seed_simulator=self.seed+self.calls).result().get_counts()
        return majority_word(counts,self.n)

    def metrics(self):
        return dict(circuits=self.calls,distinct_compilations=len(self.compiled),shots_per_circuit=self.shots,
                    phase_calls=4*self.calls*self.shots,cx_executions=self.cx,
                    instructions_executed=self.gates,max_transpiled_depth=self.depth)
