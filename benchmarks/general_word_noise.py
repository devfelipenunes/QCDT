import itertools as it, math, random, json, cmath, statistics
from pathlib import Path
from qcdt import contract,recover,bounds
from qcdt.general import recover_general,Tower,karatsuba_plan,check_plan
from qcdt.word_noise import Majority,repetitions,certify,holdout_count
from qcdt.matched import balanced_dense

def cap(n,d,lam,r):
    m=max(2,n.bit_length());B=min(n,2*d)*m
    return B*(1+(min(n,min(n-1,2*d)**2+1)-1).bit_length())+r if lam==1 else B*min(n,lam)*m+r

def phase(n,terms,offsets):
    ms=[sum(1<<i for i in t) for t in terms]
    return [(-1)**sum(x&m==m for m in ms)*cmath.exp(-1j*sum(t for t,m in zip(offsets,ms) if x&m==m)) for x in range(1<<n)]

def probs(V,a,b):
    w=[V[x]*V[x^a]*V[x^b]*V[x^a^b] for x in range(len(V))];s=1
    while s<len(w):
        for i in range(0,len(w),2*s):
            for j in range(i,i+s):u,v=w[j],w[j+s];w[j],w[j+s]=u+v,u-v
        s*=2
    return [abs(x/len(w))**2 for x in w]

def onebit(V,x):return min(1,max(0,(1-(V[x]*V[0].conjugate()).real)/2))

def dense_value(n,evaluate):
    values={0:0};E=set()
    for r in range(1,4):
        for t in it.combinations(range(n),r):
            x=sum(1<<j for j in t);values[x]=evaluate(x)
            if r==3:
                coeff=0;s=x
                while True:
                    coeff^=values[s]
                    if not s:break
                    s=(s-1)&x
                if coeff:E.add(t)
    return frozenset(E)

def experiment():
    fixtures=[('single',4,{(0,1,3)}),('overlap',5,{(0,1,2),(0,1,4)}),('pasch',6,{(0,1,2),(0,3,4),(1,3,5),(2,4,5)})]
    rows=[];budget=4096;checks=5
    for name,n,E in fixtures:
        d,lam=bounds(E);terms=[(0,),(1,2)]+sorted(E)
        for scale in (0.,.1,.25,.5):
            for rep in range(8):
                offsets=[random.Random(f'offset:{name}:{scale}:{rep}:{i}').uniform(-scale,scale) for i in range(len(terms))];V=phase(n,terms,offsets);cache={}
                for method in ('qcdt','dense','onebit'):
                    planned=(4*cap(n,d,lam,checks) if method=='qcdt' else 4*(n//2*(n//2-1)//2+((n+1)//2)*(((n+1)//2)-1)//2+checks) if method=='dense' else sum(math.comb(n,k) for k in range(1,4))+4*checks)
                    r=budget//planned;r-=int(r%2==0);rng=random.Random(f'sample:{name}:{scale}:{rep}:{method}');controls={'cx':0,'h':0}
                    def sample(a,b):
                        key=(a,b)
                        if key not in cache:cache[key]=probs(V,a,b)
                        controls['h']+=2*n
                        return rng.choices(range(1<<n),weights=cache[key],k=1)[0]
                    def bit(x):
                        controls['h']+=2;controls['cx']+=2*(x.bit_count()-1)
                        return int(rng.random()<onebit(V,x))
                    P=Majority(n,sample,r,cost=4,early=True);B=Majority(1,bit,r,cost=1,early=True)
                    reason=None;got=None
                    try:
                        if method=='qcdt':got=recover(n,d,lam,P,seed=32,checks=checks).edges
                        else:
                            got=balanced_dense(n,P)[0] if method=='dense' else dense_value(n,B)
                            rr=random.Random(32)
                            for _ in range(checks):
                                a,b=rr.getrandbits(n),rr.getrandbits(n)
                                if P(a,b)!=contract(got,a,b):raise ValueError('holdout rejected')
                        if bounds(got)[0]>d or bounds(got)[1]>lam:raise ValueError('promise exceeded')
                        outcome='exact' if got==E else 'wrong'
                    except ValueError as exc:outcome='rejected';reason=str(exc)
                    calls=4*P.shots+B.shots;fixed=r*(4*P.calls+B.calls)
                    if calls>budget or fixed>budget:raise RuntimeError('cap violation')
                    if scale==0 and outcome!='exact':raise RuntimeError('ideal failure')
                    rows.append(dict(fixture=name,n=n,d=d,codegree=lam,scale=scale,rep=rep,method=method,offsets=offsets,planned=planned,reps=r,phase_calls=calls,fixed_calls_same_path=fixed,outcome=outcome,reason=reason,control=controls))
    return rows

def run():
    checks=0
    for m in range(2,10):
        g=Tower(m);check_plan(g,karatsuba_plan(g));checks+=g.width**2
    T=list(it.combinations(range(5),3));count=0
    for word in range(1<<len(T)):
        E={e for j,e in enumerate(T) if word>>j&1};d=max(1,bounds(E)[0]);got,q,rank=recover_general(5,d,lambda a,b:contract(E,a,b));assert got==E;count+=1
    print('general exhaustive',count,'bilinear basis checks',checks,flush=True)
    rng=random.Random(32);examples=[]
    for n,d in [(8,3),(16,4),(32,4),(32,8),(64,2)]:
        E=set();deg=[0]*n
        for _ in range(n*d*20):
            e=tuple(sorted(rng.sample(range(n),3)))
            if e not in E and all(deg[i]<d for i in e):
                E.add(e)
                for i in e:deg[i]+=1
        got,q,rank=recover_general(n,d,lambda a,b:contract(E,a,b));assert got==E
        old=recover(n,d,max(1,bounds(E)[1]),lambda a,b:contract(E,a,b),seed=32,checks=1)
        examples.append(dict(n=n,d=d,codegree=bounds(E)[1],weighted=q,reference=old.acquisition_queries,rank=rank))
    print('examples',examples,flush=True)
    # For any finite sequence, early majority is identical to full majority.
    early=0;used=0;full=0
    for _ in range(500):
        seq=[rng.randrange(32) for i in range(15)]
        a=Majority(5,lambda:next(i1),15);b=Majority(5,lambda:next(i2),15,early=False);i1=iter(seq);i2=iter(seq)
        assert a()==b();early+=1;used+=a.shots;full+=b.shots
    # Word corruption can flip an arbitrary subset, with history-dependent distribution.
    E={(0,1,2),(0,1,3)};bad={(0,1,2)};n=5;out=[]
    for eta in (.05,.15,.25):
        r=repetitions(40,eta,.01);counts=[0,0];cert=[0,0];s=0
        for rep in range(40):
            rg=random.Random(f'noise:{eta}:{rep}');last=0
            def sample(a,b):
                nonlocal last
                v=contract(E,a,b)
                if rg.random()<eta:v^=(last or 31)
                last=(v+1)%32
                return v
            P=Majority(n,sample,r)
            for j in range(40):
                a,b=rg.randrange(32),rg.randrange(32);counts[0]+=P(a,b)==contract(E,a,b);counts[1]+=1
            s+=P.shots
            cert[0]+=certify(n,E,sample,eta,.01,seed=rep)[0]
            cert[1]+=certify(n,bad,sample,eta,.01,seed=rep)[0]
        out.append(dict(eta=eta,repetitions=r,correct=counts[0],total=counts[1],shots=s,certify_true=cert[0],certify_wrong=cert[1],holdout=holdout_count(eta,.01)))
    rows=experiment();groups={}
    for row in rows:
        key=(row['scale'],row['method']);g=groups.setdefault(key,dict(exact=0,rejected=0,wrong=0,phase_calls=0,fixed=0));g[row['outcome']]+=1;g['phase_calls']+=row['phase_calls'];g['fixed']+=row['fixed_calls_same_path']
    summary=[dict(scale=k[0],method=k[1],**v) for k,v in sorted(groups.items())];print('noise',out,'early',used,full,'summary',summary,flush=True)
    result=dict(exhaustive=count,bilinear_checks=checks,examples=examples,early=dict(trials=early,shots=used,fixed=full),noise=out,rows=rows,summary=summary)
    Path('general-word-noise-results.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
