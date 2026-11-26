"""Boundary-preserved vs fully compiled synthetic oracle controls.

Fixed fixtures and public shot allocation. No QPU, no claim of oracle opacity.
"""
import json
from pathlib import Path
from time import perf_counter
from qcdt import recover
from qcdt.budget import circuit_cap,odd_shots,dense_certified
from qcdt.backends import derivative_circuit
from qcdt.oracle_contract import boundary_derivative
from qcdt.snapshot_backend import SnapshotProbe,snapshot_metadata

FIXTURES=(('single',4,1,1,{(0,1,3)}),('overlap',5,2,2,{(0,1,2),(0,1,4)}),
          ('pasch',6,2,1,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)}))
BUDGET=2048
def run():
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2,FakeLagosV2
    devices=(FakeManilaV2(),FakeLagosV2())
    rows=[]
    for name,n,d,lam,E in FIXTURES:
        device=devices[int(n>5)]
        start=perf_counter()
        oracle=QuantumCircuit(n);oracle.z(0);oracle.cz(1,2)
        for e in sorted(E):oracle.ccz(*e)
        build=perf_counter()-start
        for method in ('qcdt','dense-certified'):
            fn=(lambda p:recover(n,d,lam,p,seed=32).edges) if method=='qcdt' else (lambda p:dense_certified(n,d,lam,p,seed=32))
            cap=circuit_cap(n,d,lam,method)
            for mode,builder in [('full',derivative_circuit),('boundary',boundary_derivative)]:
                for condition,seed in [('ideal',101),('snapshot',101),('snapshot',202)]:
                    shots=1 if condition=='ideal' else odd_shots(BUDGET,cap)
                    p=SnapshotProbe(oracle,device,shots=shots,budget=BUDGET,seed=seed,
                       noisy=condition!='ideal',circuit_builder=builder)
                    start=perf_counter();reason=None
                    try:
                        got=fn(p);outcome='exact' if got==E else 'wrong'
                    except ValueError as exc:
                        got=None;outcome='rejected';reason=str(exc)
                    elapsed=perf_counter()-start
                    row=dict(fixture=name,n=n,d=d,codegree=lam,device=device.name,method=method,
                             compilation=mode,condition=condition,seed=seed,outcome=outcome,reason=reason,
                             expected=sorted(E),recovered=sorted(got) if got is not None else None,
                             public_circuit_cap=cap,oracle_source='known synthetic Z/CZ/CCZ list',
                             oracle_build_seconds=build,oracle_logical_gates=oracle.size(),
                             host_elapsed_seconds=elapsed,**p.metrics())
                    row['host_other_seconds']=max(0,elapsed-row['compile_seconds']-row['simulation_seconds'])
                    if row['circuits']>cap or row['shots_used']>BUDGET:raise RuntimeError('budget violation')
                    if condition=='ideal' and outcome!='exact':raise RuntimeError('ideal control failed')
                    print(json.dumps(row),flush=True)
                    rows.append({**row,'measurements':p.records})
    return dict(model='synthetic visible oracle, boundary directives, historical snapshots; no hardware',
                shot_cap=BUDGET,devices=[snapshot_metadata(x) for x in devices],rows=rows)
if __name__=='__main__':
    Path('oracle-boundary-results.json').write_text(json.dumps(run(),indent=2,default=str)+'\n')
