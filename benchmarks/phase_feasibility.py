"""Predeclared phase offsets, 60 mask pairs per configuration, no QPU."""
import argparse
import json
from pathlib import Path
from random import Random
from statistics import mean
from qcdt import contract
from qcdt.phase_feasibility import phase_diagonal,derivative_distribution,word_error_bound

def run():
    rng=Random(271);rows=[]
    for n,E in [(4,[(0,1,2)]),(6,[(0,1,2),(0,3,4),(1,3,5),(2,4,5)])]:
        terms=[(0,),(1,2)]+E
        ideal=phase_diagonal(n,terms)
        masks=[(rng.randrange(1<<n),rng.randrange(1<<n)) for _ in range(60)]
        for scale in (0.,.005,.02,.05,.1,.25,.5):
            offsets=[rng.uniform(-scale,scale) for _ in terms]
            actual=phase_diagonal(n,terms,offsets)
            eps,bound=word_error_bound(ideal,actual)
            observations=[]
            for a,b in masks:
                target=contract(E,a,b)
                p0=derivative_distribution(ideal,a,b)
                p=derivative_distribution(actual,a,b)
                if abs(p0[target]-1)>1e-10 or abs(sum(p)-1)>1e-10:
                    raise RuntimeError('ideal mismatch or normalization failure')
                error=max(0.,1-p[target])
                if error>bound+1e-10:raise RuntimeError('norm bound violation')
                observations.append(dict(a=a,b=b,target=target,word_error=error))
            errors=[x['word_error'] for x in observations]
            rows.append(dict(n=n,terms=terms,phase_offset_max=scale,offsets=offsets,
                             operator_norm_distance=eps,bound=bound,max_word_error=max(errors),
                             mean_word_error=mean(errors),observations=observations))
    return dict(model='fixed-time diagonal phase offsets, exact probability calculation; not hardware',seed=271,rows=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    result=run();out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([ {k:v for k,v in r.items() if k!='observations'} for r in result['rows'] ]))
