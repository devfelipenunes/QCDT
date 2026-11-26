"""Local Aer simulation from packaged historical IBM device snapshots."""
from .backends import derivative_circuit
from .aer_backend import majority_word


def snapshot_metadata(backend):
    target=backend.target
    gates=[]
    for name in sorted(target.operation_names):
        for qargs,props in target[name].items():
            if props is not None:
                gates.append(dict(name=name,qubits=list(qargs) if qargs is not None else None,
                                  error=props.error,duration=props.duration))
    qp=target.qubit_properties or []
    properties=backend.properties() if hasattr(backend,'properties') else None
    return dict(name=backend.name,num_qubits=backend.num_qubits,
                backend_version=backend.backend_version,
                coupling=list(backend.coupling_map.get_edges()),
                dt=backend.dt,qubits=[dict(t1=p.t1,t2=p.t2,frequency=p.frequency) if p else None for p in qp],
                gates=gates,properties=properties.to_dict() if properties is not None else None)


class SnapshotProbe:
    """Bounded total shots, actual transpiled circuits and raw measured counts."""
    def __init__(self, oracle, backend, *, shots, budget, seed=42, noisy=True, cache=None):
        from qiskit_aer import AerSimulator
        if shots<1 or shots%2==0 or budget<shots:raise ValueError('invalid shots/budget')
        if oracle.num_qubits>backend.num_qubits:raise ValueError('device too small')
        self.oracle,self.backend,self.shots,self.budget,self.seed=oracle,backend,shots,budget,seed
        self.sim=(AerSimulator.from_backend(backend,method='density_matrix',max_parallel_threads=1)
                  if noisy else AerSimulator(max_parallel_threads=1))
        # Only reuse this cache within the same oracle, backend and transpiler settings.
        self.cache={} if cache is None else cache
        self.records=[];self.used=0;self.twoq=0;self.instructions=0;self.depth=0

    def __call__(self,a,b):
        from qiskit import transpile
        if self.used+self.shots>self.budget:raise ValueError('total shot budget exhausted')
        key=(a,b)
        if key not in self.cache:
            qc=derivative_circuit(self.oracle,a,b);qc.measure_all()
            self.cache[key]=transpile(qc,backend=self.backend,optimization_level=1,seed_transpiler=1729)
        tr=self.cache[key]
        count2=sum(len(x.qubits)==2 and x.operation.name!='barrier' for x in tr.data)
        self.used+=self.shots;self.twoq+=count2*self.shots
        self.instructions+=tr.size()*self.shots;self.depth=max(self.depth,tr.depth())
        counts=self.sim.run(tr,shots=self.shots,seed_simulator=self.seed+len(self.records)).result().get_counts()
        self.records.append(dict(a=a,b=b,counts=dict(counts),depth=tr.depth(),twoq_gates=count2,
                                 instructions=tr.size(),layout=str(tr.layout)))
        return majority_word(counts,self.oracle.num_qubits)

    def metrics(self):
        return dict(budget=self.budget,shots_used=self.used,shots_per_circuit=self.shots,
                    phase_calls=4*self.used,circuits=len(self.records),
                    twoq_executions=self.twoq,instructions_executed=self.instructions,
                    max_depth=self.depth)
