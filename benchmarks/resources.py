"""Resource accounting after basis transpilation; no hardware routing or timings."""
import json
import sys
from pathlib import Path
from qcdt import recover, contract, bounds
from qcdt.baselines import dense_cubic, classical_cubic
from qcdt.backends import derivative_circuit


def report():
    from qiskit import QuantumCircuit, transpile
    fixtures = [(4,set()), (6,{(0,1,2),(3,4,5)}),
                (6,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)}),
                (6,{(0,1,2),(0,1,3),(0,1,4)}),
                (8,{(0,1,2),(3,4,5),(0,6,7)})]
    result = []
    for n,E in fixtures:
        oracle = QuantumCircuit(n)
        oracle.z(0); oracle.cz(1,2)
        for i,j,k in sorted(E): oracle.ccz(i,j,k)
        terms = E | {(0,), (1,2)}
        masks = [sum(1<<i for i in e) for e in terms]
        f = lambda x: sum((x&m)==m for m in masks)%2
        counts = {}
        def tracked(name):
            calls = []
            counts[name] = calls
            def probe(a,b):
                qc = derivative_circuit(oracle,a,b)
                tr = transpile(qc,basis_gates=['rz','sx','x','cx'],optimization_level=1,seed_transpiler=92)
                calls.append(dict(depth=tr.depth(),cx=int(tr.count_ops().get('cx',0)),gates=tr.size()))
                return contract(E,a,b)
            return probe
        d,lam = bounds(E)
        r = recover(n,max(1,d),max(1,lam),tracked('qcdt'),seed=92)
        D,q = dense_cubic(n,tracked('dense'))
        C,c = classical_cubic(n,f)
        if not (r.edges == D == C == E): raise RuntimeError('reconstruction mismatch')
        row = dict(n=n,d=d,codegree=lam,edges=sorted(E),classical_value_queries=c,
                   qcdt_acquisition=r.acquisition_queries,qcdt_verification=r.verification_queries,dense_phase_queries=q)
        for name, data in counts.items():
            row[name] = dict(circuits=len(data),phase_queries=4*len(data),
                             total_cx=sum(x['cx'] for x in data),total_gates=sum(x['gates'] for x in data),
                             max_depth=max((x['depth'] for x in data),default=0))
        result.append(row)
    return dict(model='ideal algebraic outputs; Qiskit transpiled basis; no device coupling or measurement gates',rows=result)

if __name__ == '__main__':
    out = json.dumps(report(),indent=2)
    print(out)
    if len(sys.argv)>1: Path(sys.argv[1]).write_text(out+'\n')
