"""Same ideal oracle, same 10 holdout checks, deterministic fixtures."""
import json
from pathlib import Path
from qcdt import contract,recover
from qcdt.known_support import recover_linear
from qcdt.matched import label_bits,balanced_dense

def run():
    rows=[]
    for n in (6,24,48,96,192):
        E={tuple(i+x for x in e) for i in range(0,n,6)
           for e in ((0,1,2),(0,3,4),(1,3,5),(2,4,5))}
        p=lambda a,b:contract(E,a,b)
        new,acq,holdout=recover_linear(n,2,p)
        old=recover(n,2,1,p)
        label,lc=label_bits(n,2,p)
        if not new==old.edges==label==E:raise RuntimeError('recovery failure')
        row=dict(n=n,edges=len(E),known_support_acquisition=acq,
                 old_acquisition=old.acquisition_queries,verification=holdout,label_acquisition=lc,
                 balanced_dense=4*((n//2)*(n//2-1)//2+((n+1)//2)*((n+1)//2-1)//2))
        rows.append(row);print(json.dumps(row),flush=True)
    return rows
if __name__=='__main__':
    Path('known-support.json').write_text(json.dumps(run(),indent=2)+'\n')
