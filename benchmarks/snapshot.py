"""Predefined exploratory matched total-shot-cap benchmark; no QPU access."""
import json
from pathlib import Path
from qcdt import recover,bounds
from qcdt.backends import truth_table_probe
from qcdt.matched import balanced_dense
from qcdt.snapshot_backend import SnapshotProbe,snapshot_metadata

BUDGET=2048
SEEDS=(101,202,303)
FIXTURES=(('single',4,{(0,1,3)}),('overlap',5,{(0,1,2),(0,1,4)}),
          ('pasch',6,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)}))

def run():
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2,FakeLagosV2
    devices=(FakeManilaV2(),FakeLagosV2())
    rows=[];metadata=[snapshot_metadata(device) for device in devices]
    for device in devices:
        for name,n,E in FIXTURES:
            if n>device.num_qubits:continue
            qc=QuantumCircuit(n);qc.z(0);qc.cz(1,2)
            for e in sorted(E):qc.ccz(*e)
            exact=truth_table_probe(n,E|{(0,),(1,2)})
            d,lam=bounds(E);cache={}
            methods={'qcdt':lambda p:recover(n,d,lam,p,seed=32).edges,
                     'dense':lambda p:balanced_dense(n,p)[0]}
            for method,fn in methods.items():
                count=[0]
                def planned(a,b):
                    count[0]+=1;return exact(a,b)
                if fn(planned)!=E:raise RuntimeError('ideal plan failed')
                shots=BUDGET//count[0];shots-=int(shots%2==0)
                for seed in SEEDS:
                    p=SnapshotProbe(qc,device,shots=shots,budget=BUDGET,seed=seed,cache=cache)
                    try:
                        got=fn(p);outcome='exact' if got==E else 'wrong';reason=None
                    except ValueError as ex:
                        got=None;outcome='rejected';reason=str(ex)
                    row=dict(device=device.name,fixture=name,n=n,method=method,seed=seed,
                             outcome=outcome,reason=reason,planned_circuits=count[0],
                             edges=sorted(E),recovered=sorted(got) if got is not None else None,
                             **p.metrics())
                    print(json.dumps(row),flush=True)
                    rows.append({**row,'measurements':p.records})
    return dict(model='historical device calibration snapshot; Aer density matrix; fixed fixtures, three seeds; not live hardware',
                shot_cap=BUDGET,seeds=SEEDS,devices=metadata,rows=rows)
if __name__=='__main__':
    Path('snapshot-results.json').write_text(json.dumps(run(),indent=2,default=str)+'\n')
