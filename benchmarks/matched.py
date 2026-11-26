"""Fixed-seed ideal query benchmark. No quantum timing or physical advantage claim."""
import itertools
import json
import random
import statistics
from pathlib import Path
from qcdt import bounds, contract, recover
from qcdt.matched import balanced_dense, label_bits, classical_sparse


def graph(n,d,rng,linear):
    E=set(); deg=[0]*n; pairs=set()
    # Random candidate draws avoid constructing n choose 3 triples at scale.
    for _ in range(n*d*20):
        e=tuple(sorted(rng.sample(range(n),3)))
        ps=set(itertools.combinations(e,2))
        if e in E or any(deg[i]>=d for i in e) or (linear and ps & pairs): continue
        E.add(e);pairs|=ps
        for i in e:deg[i]+=1
    return E


def run():
    rng=random.Random(1403); rows=[]
    for n,d,linear in [(6,2,True),(16,2,True),(32,4,True),(64,4,True),(128,2,True),(32,4,False)]:
        cases=[]
        for trial in range(5):
            E=graph(n,d,rng,linear); dg,lam=bounds(E);dg=max(1,dg);lam=max(1,lam)
            p=lambda a,b:contract(E,a,b)
            terms=[sum(1<<i for i in e) for e in E]+[0,1,3]
            f=lambda x:sum((x&m)==m for m in terms)&1
            q=recover(n,dg,lam,p,seed=trial)
            D,dc=balanced_dense(n,p);C,cc=classical_sparse(n,dg,f,seed=trial)
            item=dict(exact_q=q.edges==E,exact_dense=D==E,exact_classical=C==E,qcdt=q.acquisition_queries,verification=q.verification_queries,dense=dc,classical=cc,codegree=lam,degree=dg)
            if lam==1:
                L,lc=label_bits(n,dg,p);item.update(exact_label=L==E,label=lc)
            cases.append(item)
        keys=['qcdt','verification','dense','classical']+(['label'] if all('label' in x for x in cases) else [])
        row=dict(n=n,d=d,linear=linear,cases=cases,median={k:statistics.median(x[k] for x in cases) for k in keys},success={k:sum(x[k] for x in cases) for k in cases[0] if k.startswith('exact') and all(k in x for x in cases)})
        rows.append(row);print(n,d,linear,row['median'],row['success'],flush=True)
    return rows

if __name__=='__main__':
    Path('matched-results.json').write_text(json.dumps(run(),indent=2)+'\n')
