"""Exploratory end-to-end Aer benchmark with synthetic noise, not hardware calibration."""
import json
from pathlib import Path
from qcdt import recover,bounds,contract
from qcdt.matched import balanced_dense
from qcdt.aer_backend import AerProbe


def run():
    from qiskit import QuantumCircuit
    fixtures=[('single',4,{(0,1,3)}),('overlap',5,{(0,1,2),(0,1,4)}),
              ('pasch',6,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)})]
    conditions=[('ideal',1,0.,0.,0.),('readout',31,.1,0.,0.),
                ('mild',31,.02,.001,.005),('strong',127,.05,.005,.02)]
    rows=[]
    for name,n,E in fixtures:
        d,lam=bounds(E);qc=QuantumCircuit(n);qc.z(0);qc.cz(1,2)
        for e in sorted(E):qc.ccz(*e)
        for noise,shots,ro,p1,p2 in conditions:
            for method in ('qcdt','dense'):
                p=AerProbe(qc,shots=shots,seed=2403,readout=ro,p1=p1,p2=p2)
                try:
                    if method=='qcdt': got=recover(n,d,lam,p,seed=32).edges
                    else: got=balanced_dense(n,p)[0]
                    outcome='exact' if got==E else 'wrong'
                except ValueError:
                    outcome='rejected';got=None
                row=dict(fixture=name,n=n,d=d,codegree=lam,method=method,noise=noise,readout=ro,p1=p1,p2=p2,
                         outcome=outcome,edges=sorted(E),recovered=sorted(got) if got is not None else None,**p.metrics())
                rows.append(row);print(json.dumps(row),flush=True)
                if noise=='ideal' and outcome!='exact':raise RuntimeError('ideal reconstruction failed')
    return dict(model='synthetic depolarizing and readout, line coupling, one seed per case; not calibrated',rows=rows)
if __name__=='__main__':
    Path('aer-recovery.json').write_text(json.dumps(run(),indent=2)+'\n')
