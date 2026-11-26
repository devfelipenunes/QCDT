"""Matched ideal-oracle baselines and a sparse classical value-query comparator."""
from collections import Counter, defaultdict
from itertools import combinations
from math import ceil, log
from random import Random
from .core import bounds, contract
from .field import BCH


def balanced_dense(n, probe):
    """Every triple has a pair within one of two balanced parts (Mantel cover)."""
    result = set()
    calls = 0
    for part in (range(n//2), range(n//2,n)):
        for i,j in combinations(part,2):
            word = probe(1<<i,1<<j)
            calls += 4
            for k in range(n):
                if k not in (i,j) and word>>k&1:
                    result.add(tuple(sorted((i,j,k))))
    return frozenset(result), calls


def label_bits(n,d,probe):
    """Graph derivative + sparse row sketches, no projection/poda/coloring.

    Under codegree 1, each pair's unique third vertex has a nonzero binary
    label. This is a derived comparator, not a verbatim published algorithm.
    """
    B=BCH(n,2*d); labels=[defaultdict(int) for _ in range(n)];cache={}
    for t in range(n.bit_length()):
        a=sum(1<<j for j in range(n) if (j+1)>>t&1)
        words=[]
        for b in B.masks:
            if not a or not b or a==b: v=0
            else:
                key=tuple(sorted((a,b)))
                if key not in cache: cache[key]=probe(a,b)
                v=cache[key]
            words.append(v)
        for i in range(n):
            for j in B.decode([v>>i&1 for v in words]): labels[i][j]|=1<<t
    votes=Counter()
    for i,row in enumerate(labels):
        for j,label in row.items():
            k=label-1
            if not 0<=k<n or len({i,j,k})!=3: raise ValueError('invalid label')
            votes[tuple(sorted((i,j,k)))]+=1
    if any(v!=6 for v in votes.values()) or bounds(votes)[0]>d or bounds(votes)[1]>1:
        raise ValueError('inconsistent linear hypergraph')
    return frozenset(votes),4*len(cache)


def classical_sparse(n,d,evaluate,*,delta=.01,seed=0):
    """Third derivative and binary splitting; from the round-8 comparator.

    The residual trilinear contraction is nonzero on uniform independent
    masks with probability at least 1/8 if a cubic term remains. Union
    bound over at most floor(nd/3)+1 stopping attempts.
    """
    if not 0<delta<1 or d<1: raise ValueError('invalid bound')
    rng=Random(seed); max_edges=n*d//3
    trials=ceil(log(delta/(max_edges+1))/log(7/8)); cache={}; found=set()
    def r(x):
        if x not in cache: cache[x]=evaluate(x)
        return cache[x] ^ (sum((x&e)==e for e in found)&1)
    def T(a,b,c): return r(0)^r(a)^r(b)^r(c)^r(a^b)^r(a^c)^r(b^c)^r(a^b^c)
    for _ in range(max_edges+1):
        for _ in range(trials):
            masks=[rng.getrandbits(n) for _ in range(3)]
            if T(*masks): break
        else:
            return frozenset(tuple(i for i in range(n) if e>>i&1) for e in found),len(cache)
        for j in range(3):
            while masks[j].bit_count()>1:
                bits=[i for i in range(n) if masks[j]>>i&1]
                lo=sum(1<<i for i in bits[:len(bits)//2]);hi=masks[j]^lo
                masks[j]=lo
                if not T(*masks): masks[j]=hi
        edge=masks[0]|masks[1]|masks[2]
        if edge.bit_count()!=3 or edge in found or not T(*masks): raise ValueError('inconsistent derivative')
        found.add(edge)
    raise ValueError('degree promise exceeded')
