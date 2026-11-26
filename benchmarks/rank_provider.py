"""Predeclared ideal experiment, no hardware or historical timing comparison."""
import itertools
import json
import random
from pathlib import Path
from statistics import median
from time import perf_counter
from qcdt import contract,bounds,recover
from qcdt.general import Tower,check_plan,recover_general
from qcdt.matched import balanced_dense
from qcdt.legacy import recover_legacy
from qcdt.rank_provider import (candidate_plans,exact_symmetric,irreducibles,
    exact_rank_plan,public_mask_count)


def fixture(n,d,seed):
    rng=random.Random(seed);E=set();degree=[0]*n
    for _ in range(20*n*d):
        e=tuple(sorted(rng.sample(range(n),3)))
        if e not in E and all(degree[v]<d for v in e):
            E.add(e)
            for v in e:degree[v]+=1
    return E


def run(configs=None):
    ranks=[];small=[];rows=[];exact=[]
    for k in range(1,5):
        for p in irreducibles(k):
            start=perf_counter();plan,attempts=exact_symmetric(p)
            small.append(dict(degree=k,modulus=p,rank=len(plan),attempts=attempts,host_seconds=perf_counter()-start))
    for m in range(2,17):
        g=Tower(m);start=perf_counter();plans=candidate_plans(g);setup=perf_counter()-start
        for name,plan in plans.items():
            start=perf_counter();check_plan(g,plan)
            ranks.append(dict(m=m,width=g.width,method=name,rank=len(plan),
                all_plans_setup_seconds=setup,validation_seconds=perf_counter()-start))
    for m in (5,6):
        g=Tower(m);start=perf_counter();plan=exact_rank_plan(g,max_candidates=50000);check_plan(g,plan)
        exact.append(dict(m=m,rank=len(plan),host_seconds=perf_counter()-start))
    # Same public promises and common instances; no holdout cost for any method.
    # Reference performs one holdout internally, excluded and reported separately.
    for n,d in (configs if configs is not None else ((8,3),(16,4),(32,4),(32,8),(64,2),(8,21))):
        g=Tower(n.bit_length());plans=candidate_plans(g)
        predicted={name:4*public_mask_count(n,d,g,p) for name,p in plans.items()}
        chosen=min(plans,key=lambda name:(predicted[name],len(plans[name]),name))
        if g.m in (5,6):
            plans['exact-crt']=exact_rank_plan(g,max_candidates=50000)
            predicted['exact-crt']=4*public_mask_count(n,d,g,plans['exact-crt'])
        for seed in (3401,3402,3403):
            E=fixture(n,d,seed);lam=max(1,bounds(E)[1]);row=dict(n=n,d=d,seed=seed,codegree=lam,edges=len(E),chosen=chosen,methods={})
            for name,plan in plans.items():
                start=perf_counter();got,q,r=recover_general(n,d,lambda a,b:contract(E,a,b),plan_factory=lambda _:plan)
                if got!=E or q!=predicted[name]:raise RuntimeError('acquisition or recovery mismatch')
                row['methods'][name]=dict(queries=q,rank=r,host_seconds=perf_counter()-start)
            start=perf_counter();r=recover(n,d,lam,lambda a,b:contract(E,a,b),checks=1,seed=seed)
            if r.edges!=E:raise RuntimeError('reference mismatch')
            row['methods']['reference']=dict(queries=r.acquisition_queries,holdout=r.verification_queries,host_seconds=perf_counter()-start)
            start=perf_counter();got,q=balanced_dense(n,lambda a,b:contract(E,a,b))
            if got!=E:raise RuntimeError('dense mismatch')
            row['methods']['dense']=dict(queries=q,host_seconds=perf_counter()-start)
            start=perf_counter();v=recover_legacy('v0.5',n,d,lam,lambda a,b:contract(E,a,b),checks=1,seed=seed)
            if v.edges!=E:raise RuntimeError('historical v0.5 mismatch: '+str(v.reason))
            row['methods']['historical-v0.5']=dict(queries=v.acquisition_queries,holdout=v.verification_queries,host_seconds=perf_counter()-start)
            rows.append(row)
        print(n,d,chosen,predicted,flush=True)
    summary=[]
    for n,d in sorted({(x['n'],x['d']) for x in rows}):
        a=[x for x in rows if (x['n'],x['d'])==(n,d)]
        summary.append(dict(n=n,d=d,count=len(a),chosen=a[0]['chosen'],median_queries={k:median(x['methods'][k]['queries'] for x in a) for k in a[0]['methods']}))
    return dict(schema='rank-provider-v1',small=small,rank_rows=ranks,exact_crt=exact,rows=rows,summary=summary)
if __name__=='__main__':
    result=run();Path('rank-provider-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary']),flush=True)
