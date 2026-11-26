"""Predeclared multi-seed ideal-oracle study; no quantum wall-clock claims."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import platform
import statistics
from qcdt import bounds,contract,recover
from qcdt.known_support import recover_linear
from qcdt.matched import classical_sparse,label_bits
from qcdt.budget import dense_certified
from benchmarks.provenance import SCHEMA,digest,seed_for,rng_for,compare

MASTER=20261126
SEEDS=(11,23,37,53,71,89,107,131,149,167)
CONFIGS=((6,2,1),(16,2,1),(32,4,1),(64,4,1),(32,4,3))

def cases():
    return [dict(n=n,d=d,codegree=lam,rep=rep) for n,d,lam in CONFIGS for rep in SEEDS]

def instance(case):
    n,d,lam=(case[k] for k in ('n','d','codegree'))
    rng=rng_for(MASTER,case,'instance');E=set();deg=[0]*n;ps={}
    for _ in range(n*d*20):
        e=tuple(sorted(rng.sample(range(n),3)));pairs=list(combinations(e,2))
        if e in E or any(deg[i]>=d for i in e) or any(ps.get(p,0)>=lam for p in pairs):continue
        E.add(e)
        for i in e:deg[i]+=1
        for p in pairs:ps[p]=ps.get(p,0)+1
    terms=sorted(E|{(),(0,),(1,2)})
    return E,terms

def run_case(case):
    n,d,lam=(case[k] for k in ('n','d','codegree'))
    E,terms=instance(case)
    masks=[sum(1<<i for i in t) for t in terms]
    ih=digest(dict(n=n,terms=terms))
    common=dict(schema=SCHEMA,case=case,instance_sha256=ih,terms=terms)
    rows=[]
    methods=['qcdt','dense-certified','classical-sparse']
    if lam==1:methods+=['known-support','label-bits']
    for method in methods:
        seed=seed_for(MASTER,case,'holdout')
        cseed=seed_for(MASTER,case,'classical-sparse')
        lseed=seed_for(MASTER,case,'known-support')
        calls=[0]
        def probe(a,b):
            calls[0]+=4
            return contract(E,a,b)
        def evaluate(x):
            calls[0]+=1
            return sum((x&m)==m for m in masks)&1
        got=None;acq=None;ver=None;reason=None
        try:
            if method=='qcdt':
                r=recover(n,d,lam,probe,seed=seed);got=r.edges
                acq,ver=r.acquisition_queries,r.verification_queries
            elif method=='dense-certified':
                got=dense_certified(n,d,lam,probe,seed=seed)
                acq,ver=calls[0]-40,40
            elif method=='known-support':
                got,acq,ver=recover_linear(n,d,probe,seed=lseed)
            elif method=='label-bits':
                got,acq=label_bits(n,d,probe);ver=0
            else:
                got,acq=classical_sparse(n,d,evaluate,seed=cseed);ver=0
            if acq+ver!=calls[0]:raise RuntimeError('query accounting mismatch')
            outcome='exact' if got==E else 'wrong'
        except ValueError as exc:
            outcome='rejected';reason=str(exc)
        rows.append(dict(**common,method=method,seeds=dict(master=MASTER,instance=seed_for(MASTER,case,'instance'),
            holdout=seed,classical=cseed,known_support=lseed),outcome=outcome,
            recovered=sorted(got) if got is not None else None,reason=reason,
            query_model='value' if method=='classical-sparse' else 'phase',
            acquisition_queries=acq,verification_queries=ver,queries=calls[0]))
    return rows

def run(order=None):
    return [row for case in (cases() if order is None else order) for row in run_case(case)]

def summary(rows):
    groups={}
    for r in rows:
        c=r['case'];key=(c['n'],c['d'],c['codegree'],r['method'])
        groups.setdefault(key,[]).append(r)
    return [dict(n=k[0],d=k[1],codegree=k[2],method=k[3],count=len(v),
                 exact=sum(x['outcome']=='exact' for x in v),rejected=sum(x['outcome']=='rejected' for x in v),
                 wrong=sum(x['outcome']=='wrong' for x in v),median_queries=statistics.median(x['queries'] for x in v))
            for k,v in sorted(groups.items())]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--reverse-check',action='store_true')
    a=p.parse_args();rows=run();reverse=None
    if a.reverse_check:
        reverse=compare(rows,run(list(reversed(cases()))))
        if not reverse:raise RuntimeError('order-dependent results')
    result=dict(schema=SCHEMA,python=platform.python_version(),master=MASTER,
                reverse_order_match=reverse,rows=rows,summary=summary(rows))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(reverse_order_match=reverse,instances=len(cases()),observations=len(rows),
                          summary=result['summary'])),flush=True)
