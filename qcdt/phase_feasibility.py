"""Synthetic fixed-time diagonal evolution: ideal signs and phase perturbations.

Not a Hamiltonian-learning algorithm for arbitrary coefficients. This models
only coherent, repeatable access at a specified evolution time.
"""
import cmath
import math

def phase_diagonal(n,terms,offsets=None):
    if n<1:raise ValueError('invalid n')
    masks=[]
    for term in terms:
        if len(set(term))!=len(term) or any(not 0<=i<n for i in term):
            raise ValueError('invalid term')
        masks.append(sum(1<<i for i in term))
    offsets=[0.]*len(masks) if offsets is None else list(offsets)
    if len(offsets)!=len(masks) or not all(math.isfinite(v) for v in offsets):
        raise ValueError('invalid phase offsets')
    return [(-1 if sum((x&m)==m for m in masks)%2 else 1)
            *cmath.exp(-1j*sum(v for m,v in zip(masks,offsets) if (x&m)==m))
            for x in range(1<<n)]

def derivative_distribution(diagonal,a,b):
    """Four forward calls to a diagonal unitary, with the usual XOR masks."""
    size=len(diagonal)
    if size<2 or size&(size-1) or not 0<=a<size or not 0<=b<size:
        raise ValueError('invalid diagonal or masks')
    if any(abs(abs(v)-1)>1e-10 for v in diagonal):
        raise ValueError('diagonal must be unitary')
    w=[diagonal[x]*diagonal[x^a]*diagonal[x^b]*diagonal[x^a^b] for x in range(size)]
    step=1
    while step<size:
        for off in range(0,size,2*step):
            for i in range(off,off+step):
                u,v=w[i],w[i+step]
                w[i],w[i+step]=u+v,u-v
        step*=2
    return [abs(v/size)**2 for v in w]

def word_error_bound(ideal,actual):
    if len(ideal)!=len(actual) or not ideal:raise ValueError('dimension mismatch')
    eps=max(abs(x-y) for x,y in zip(ideal,actual))
    return eps,min(1.,16*eps**2)
