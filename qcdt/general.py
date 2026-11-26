"""Weighted moments for arbitrary cubic links; elementary Karatsuba rank.
External bilinear plans are validated, not assumed correct. No QPU access.
"""
from itertools import combinations
from collections import Counter
from .field import modulus,mul,remainder

class Tower:
    def __init__(self,m):
        self.m=m;self.width=2*m;self.mask=(1<<m)-1;self.mod=modulus(m)
        def trace(x):
            z=x
            for _ in range(m-1):x=self.base(x,x);z^=x
            return z
        self.beta=next(1<<i for i in range(m) if trace(1<<i)==1)
    def base(self,a,b):return mul(a,b,self.mod)
    def mul(self,a,b):
        x,y=a&self.mask,a>>self.m;z,w=b&self.mask,b>>self.m
        p=self.base(x,z);q=self.base(y,w);r=self.base(x^y,z^w)
        return (p^self.base(self.beta,q))|((r^p)<<self.m)
    def power(self,a,t):
        r=1
        while t:
            if t&1:r=self.mul(r,a)
            a=self.mul(a,a);t>>=1
        return r
    def inv(self,a):
        if not a:raise ValueError('zero inverse')
        return self.power(a,(1<<self.width)-2)

def polynomial_plan(a,b):
    if len(a)==1:
        if a[0] and b[0]:yield a[0],b[0],1
        return
    h=len(a)//2
    for x,y,w in polynomial_plan(a[:h],b[:h]):yield x,y,w^(w<<h)
    for x,y,w in polynomial_plan(a[h:],b[h:]):yield x,y,(w<<h)^(w<<(2*h))
    for x,y,w in polynomial_plan([x^y for x,y in zip(a[:h],a[h:])],[x^y for x,y in zip(b[:h],b[h:])]):yield x,y,w<<h

def karatsuba_plan(g):
    m=g.m;size=1<<(m-1).bit_length();bits=[1<<i if i<m else 0 for i in range(size)]
    out=[]
    for a,b,w in polynomial_plan(bits,bits):
        w=remainder(w,g.mod)
        if w:
            out.extend([(a,b,w|(w<<m)),(a<<m,b<<m,g.base(g.beta,w)),(a|(a<<m),b|(b<<m),w<<m)])
    return tuple(out)

def check_plan(g,plan):
    plan=tuple(plan);limit=1<<g.width
    if not plan or any(not all(type(x) is int and 0<x<limit for x in term) or len(term)!=3 for term in plan):raise ValueError('invalid plan')
    for i in range(g.width):
        for j in range(g.width):
            v=0
            for a,b,w in plan:
                if (a>>i&1) and (b>>j&1):v^=w
            if v!=g.mul(1<<i,1<<j):raise ValueError('incorrect bilinear plan')
    return plan

def locator(seq,g,d):
    C=[1]+[0]*len(seq);B=C.copy();L=0;shift=1;last=1
    for i,s in enumerate(seq):
        delta=s
        for j in range(1,L+1):delta^=g.mul(C[j],seq[i-j])
        if not delta:shift+=1;continue
        old=C.copy();coef=g.mul(delta,g.inv(last))
        for j in range(len(C)-shift):C[j+shift]^=g.mul(coef,B[j])
        if 2*L<=i:L=i+1-L;B=old;last=delta;shift=1
        else:shift+=1
    if L>d:raise ValueError('degree promise exceeded')
    return C[:L+1]

def recover_general(n,d,probe,*,plan_factory=karatsuba_plan):
    """Return edges, phase calls, rank. Exact cubic promise; no holdout."""
    if type(n) is not int or type(d) is not int or n<3 or d<1:raise ValueError('invalid bounds')
    d=min(d,(n-1)*(n-2)//2);g=Tower(max(2,n.bit_length()));plan=check_plan(g,plan_factory(g))
    xs=list(range(1,n+1));labels=[(1<<g.m)|x for x in xs];powers=[1]*n
    pairs=[(j,k,g.mul(labels[j],labels[k])) for j,k in combinations(range(n),2)]
    if len({z for j,k,z in pairs})!=len(pairs) or any(not z for j,k,z in pairs):raise RuntimeError('label collision')
    cache={};moments=[[] for _ in xs]
    def query(a,b):
        if not a or not b or a==b:return 0
        key=tuple(sorted((a,b)))
        if key not in cache:
            v=probe(*key)
            if type(v) is not int or not 0<=v<1<<n:raise ValueError('invalid observation')
            cache[key]=v
        return cache[key]
    def mask(vectors,a):return sum(((v&a).bit_count()%2)<<j for j,v in enumerate(vectors))
    for t in range(2*d):
        A=[g.mul(x,p) for x,p in zip(xs,powers)];out=[0]*n
        for a,b,w in plan:
            v=query(mask(A,a),mask(powers,b))
            while v:
                low=v&-v;out[low.bit_length()-1]^=w;v^=low
        for i,x in enumerate(out):moments[i].append(x)
        powers=[g.mul(p,L) for p,L in zip(powers,labels)]
    votes=Counter()
    for i,seq in enumerate(moments):
        C=locator(seq,g,d);found=[]
        if len(C)>1:
            for j,k,z in pairs:
                if i in (j,k):continue
                v=0
                for c in C:v=g.mul(v,z)^c
                if not v:found.append((j,k,z))
        if len(found)!=len(C)-1:raise ValueError('locator mismatch')
        for t,expected in enumerate(seq):
            value=0
            for j,k,z in found:value^=g.mul(xs[j]^xs[k],g.power(z,t))
            if value!=expected:raise ValueError('moment mismatch')
        for j,k,_ in found:votes[tuple(sorted((i,j,k)))]+=1
    if any(v!=3 for v in votes.values()):raise ValueError('asymmetric links')
    return frozenset(votes),4*len(cache),len(plan)
