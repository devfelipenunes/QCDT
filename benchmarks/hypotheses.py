"""Predeclared small phase controls and ideal phase-access query comparators."""
import json
import statistics
from pathlib import Path
from random import Random
from qcdt import contract
from qcdt.known_support import recover_linear
from qcdt.matched import classical_sparse
from qcdt.phase_feasibility import phase_diagonal
from qcdt.phase_cycling import distribution,sector_variances,relative_bit_probability,relative_cost

def run():
    rng=Random(301);phase=[];cost=[]
    for n,E in [(4,{(0,1,2)}),(6,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)})]:
        terms=[(0,),(1,2)]+sorted(E)
        for scale in (.02,.1,.25,.5):
            for rep in range(8):
                offsets=[rng.uniform(-scale,scale) for _ in terms]
                V=phase_diagonal(n,terms,offsets);U=phase_diagonal(n,terms)
                theta=[sum(t for e,t in zip(terms,offsets) if all(x>>i&1 for i in e)) for x in range(1<<n)]
                for _ in range(16):
                    a,b=rng.randrange(1<<n),rng.randrange(1<<n)
                    target=contract(E,a,b)
                    errors=[max(0,1-distribution(V,a,b,s)[target]) for s in ((0,0),(0,1),(1,0),(1,1))]
                    bound=sum(sector_variances(theta,a,b).values())/4
                    if sum(errors)/4>bound+1e-10:raise RuntimeError('bound violation')
                    phase.append(dict(n=n,scale=scale,rep=rep,a=a,b=b,offsets=offsets,forward=errors[0],
                                      sectors=errors,mixed=sum(errors)/4,bound=bound))
    for n in (6,24,48,96,192):
        E={tuple(i+x for x in e) for i in range(0,n,6)
           for e in ((0,1,2),(0,3,4),(1,3,5),(2,4,5))}
        results={}
        for det in (False,True):
            got,acq,holdout=recover_linear(n,2,lambda a,b:contract(E,a,b),deterministic=det)
            if got!=E:raise RuntimeError('recovery mismatch')
            results['deterministic' if det else 'randomized']=acq+holdout
        terms=[sum(1<<i for i in e) for e in E]+[1,3]
        resource=dict(oracle_calls=0,cx=0,h=0)
        def bit(x):
            for k,v in relative_cost(x).items():resource[k]+=v
            return sum((x&m)==m for m in terms)&1
        got,q=classical_sparse(n,2,bit,seed=301)
        if got!=E:raise RuntimeError('value comparator mismatch')
        cost.append(dict(n=n,edges=len(E),**results,value_queries=q,relative_phase_control=resource))
    summary=[]
    for n in (4,6):
        for scale in (.02,.1,.25,.5):
            rows=[r for r in phase if r['n']==n and r['scale']==scale]
            summary.append(dict(n=n,scale=scale,count=len(rows),
               mean_forward=statistics.mean(x['forward'] for x in rows),
               mean_mixed=statistics.mean(x['mixed'] for x in rows),
               mixed_worse=sum(x['mixed']>x['forward']+1e-10 for x in rows)))
    return dict(phase=phase,summary=summary,cost=cost,
        limitations='exact probabilities; 8 offset vectors per size/scale, 16 masks each; inverse access assumed; ideal query counts and control gates only')
if __name__=='__main__':
    result=run()
    Path('hypotheses-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(summary=result['summary'],cost=result['cost'])),flush=True)
