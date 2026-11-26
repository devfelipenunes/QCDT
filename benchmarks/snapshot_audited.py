"""Matched total-shot caps from public promises, no hidden-truth query planning.

Predefined follow-up to historical snapshot.py. Results are exploratory;
historical calibration snapshots are not live hardware. Both algorithms
get the same promised n,d,codegree and ten independent-in-model holdout
masks (fixed seeds for reproducibility), not necessarily equal realized shots.
"""
import json
from pathlib import Path
from qcdt import recover
from qcdt.budget import circuit_cap,odd_shots,dense_certified
from qcdt.snapshot_backend import SnapshotProbe,snapshot_metadata

BUDGET=2048
SEEDS=(101,202,303)
FIXTURES=(('single',4,1,1,{(0,1,3)}),
          ('overlap',5,2,2,{(0,1,2),(0,1,4)}),
          ('linear',6,2,1,{(0,1,2),(0,3,4)}),
          ('pasch',6,2,1,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)}))

def run():
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2,FakeLagosV2
    devices=(FakeManilaV2(),FakeLagosV2())
    rows=[];metadata=[snapshot_metadata(device) for device in devices]
    for device in devices:
        for name,n,d,lam,E in FIXTURES:
            if n>device.num_qubits:continue
            qc=QuantumCircuit(n);qc.z(0);qc.cz(1,2)
            for e in sorted(E):qc.ccz(*e)
            cache={}
            methods={'qcdt':lambda p:recover(n,d,lam,p,seed=32).edges,
                     'dense-certified':lambda p:dense_certified(n,d,lam,p,seed=32)}
            for method,fn in methods.items():
                cap=circuit_cap(n,d,lam,method)
                shots=odd_shots(BUDGET,cap)
                for seed in SEEDS:
                    p=SnapshotProbe(qc,device,shots=shots,budget=BUDGET,seed=seed,cache=cache)
                    try:
                        got=fn(p);outcome='exact' if got==E else 'wrong';reason=None
                    except ValueError as exc:
                        got=None;outcome='rejected';reason=str(exc)
                    row=dict(device=device.name,fixture=name,n=n,d=d,codegree=lam,method=method,seed=seed,
                             outcome=outcome,reason=reason,public_circuit_cap=cap,
                             edges=sorted(E),recovered=sorted(got) if got is not None else None,**p.metrics())
                    if row['circuits']>cap or row['shots_used']>BUDGET:
                        raise RuntimeError('public budget violation')
                    print(json.dumps(row),flush=True)
                    rows.append({**row,'measurements':p.records})
    return dict(model='historical calibration snapshot, public promises and caps, same holdout policy; no live hardware',
                shot_cap=BUDGET,seeds=SEEDS,devices=metadata,rows=rows)

if __name__=='__main__':
    Path('snapshot-audited-results.json').write_text(json.dumps(run(),indent=2,default=str)+'\n')
