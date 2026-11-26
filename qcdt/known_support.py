"""Ideal codegree-one comparator using known-support linear equations.

The matrix-vector sketch is a direct adaptation of known graph-learning
methods. Classical randomness chooses a valid encoding before any queries.
"""
from collections import Counter, defaultdict
from itertools import combinations
from random import Random
from .core import bounds, contract, propagate, shadow, pack
from .field import BCH


def reduce_word(word, basis):
    while word and word.bit_length()-1 in basis:
        word ^= basis[word.bit_length()-1]
    return word


def local_codes(N, seed=42):
    """Labels linearly independent on every known neighborhood.

    For each vertex, exclude the spans of previously assigned neighbors
    in each incident neighborhood. A width Delta+ceil(log2 Delta)+1
    guarantees a random label succeeds with probability at least 1/2.
    No oracle calls are made here.
    """
    n=len(N); delta=max(map(len,N),default=0)
    if not delta:return [],[0]*n
    width=delta+(delta-1).bit_length()+1
    if width>=n:return [1<<i for i in range(n)],[1<<i for i in range(n)]
    rng=Random(seed);basis=[{} for _ in N];labels=[0]*n
    for j in range(n):
        while True:
            v=rng.getrandbits(width)
            if all(reduce_word(v,basis[i]) for i in N[j]):break
        labels[j]=v
        for i in N[j]:
            z=reduce_word(v,basis[i]);basis[i][z.bit_length()-1]=z
    masks=[pack(j for j in range(n) if labels[j]>>t&1) for t in range(width)]
    return masks,labels


def solve_local(labels, neighbors, word):
    """Solve a full-column-rank system over F2 on a known support."""
    basis={}
    ns=sorted(neighbors)
    for j,v in enumerate(ns):
        x=labels[v];coef=1<<j
        while x and x.bit_length()-1 in basis:
            a,b=basis[x.bit_length()-1];x^=a;coef^=b
        if not x:raise ValueError('dependent neighborhood labels')
        basis[x.bit_length()-1]=(x,coef)
    coef=0
    while word:
        pivot=word.bit_length()-1
        if pivot not in basis:raise ValueError('inconsistent local sketch')
        a,b=basis[pivot];word^=a;coef^=b
    return {v for j,v in enumerate(ns) if coef>>j&1}


def recover_linear(n,d,probe,*,seed=42,checks=10):
    """Reconstruct cubic triples under the ideal codegree-one promise."""
    if n<3 or d<1 or checks<1:raise ValueError('invalid configuration')
    cache={}
    def query(a,b):
        if not a or not b or a==b:return 0
        key=tuple(sorted((a,b)))
        if key not in cache:
            v=probe(a,b)
            if not isinstance(v,int) or not 0<=v<1<<n:raise ValueError('invalid probe')
            cache[key]=v
        return cache[key]
    H=BCH(n,2*d);a=(1<<n)-1
    words=[query(a,b) for b in H.masks]
    N=[set(H.decode([v>>i&1 for v in words])) for i in range(n)]
    if any(i in ns or len(ns)>2*d or any(i not in N[j] for j in ns) for i,ns in enumerate(N)):
        raise ValueError('invalid projection')
    F,U=propagate(N,d)
    choices=defaultdict(set)
    for e in U:
        for p in combinations(e,2):choices[p].add(next(v for v in e if v not in p))
    conflicts=defaultdict(set)
    for C in choices.values():
        for v in C:conflicts[v].update(C-{v})
    colors={}
    for v in sorted(conflicts,key=lambda x:(-len(conflicts[x]),x)):
        used={colors[w] for w in conflicts[v] if w in colors}
        colors[v]=next(c for c in range(len(used)+1) if c not in used)
    bits=max(colors.values(),default=0).bit_length()
    signature=dict.fromkeys(choices,0)
    masks,labels=local_codes(N,seed=seed) if bits else ([],[])
    for t in range(bits):
        a=pack(v for v in colors if colors[v]>>t&1)
        words=[query(a,b)^contract(F,a,b) for b in masks]
        residual=[solve_local(labels,ns,sum(((v>>i)&1)<<j for j,v in enumerate(words)))
                  for i,ns in enumerate(N)]
        for i,ns in enumerate(residual):
            if any(i not in residual[j] or tuple(sorted((i,j))) not in choices for j in ns):
                raise ValueError('invalid residual')
        for i,j in choices:signature[i,j]|=int(j in residual[i])<<t
    votes=Counter()
    for p,C in choices.items():
        match=[v for v in C if colors[v]==signature[p]]
        if len(match)!=1:raise ValueError('invalid color')
        votes[tuple(sorted((*p,match[0])))]+=1
    if any(x!=3 for x in votes.values()):raise ValueError('invalid triangle')
    E=F|set(votes)
    if shadow(E,n)!=N or bounds(E)[0]>d or bounds(E)[1]>1:raise ValueError('invalid candidate')
    rng=Random(seed+1)
    for _ in range(checks):
        a,b=rng.getrandbits(n),rng.getrandbits(n)
        if probe(a,b)!=contract(E,a,b):raise ValueError('holdout rejected')
    return frozenset(E),4*len(cache),4*checks
