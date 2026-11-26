"""Public-promise-only circuit planning for fair oracle benchmarks."""
def circuit_cap(n, d, codegree, method, *, checks=10):
    if n<3 or not 1<=codegree<=d or checks<1:
        raise ValueError('invalid public promise')
    if method=='dense-certified':
        lo=n//2; hi=n-lo
        return lo*(lo-1)//2+hi*(hi-1)//2+checks
    if method!='qcdt':
        raise ValueError('unknown method')
    m=max(2,n.bit_length())
    b=min(n,2*d)*m
    if codegree==1:
        # Conflicts lie in the square of the projection, of max degree Delta^2.
        delta=min(n-1,2*d)
        colors=min(n,delta*delta+1)
        bits=(colors-1).bit_length()
        return b*(1+bits)+checks
    return b*min(n,codegree)*m+checks


def odd_shots(budget, circuits):
    if circuits<1 or budget<circuits:
        raise ValueError('budget below one shot per planned circuit')
    shots=budget//circuits
    return shots if shots%2 else shots-1


def dense_certified(n,d,codegree,probe,*,seed=32,checks=10):
    from random import Random
    from .matched import balanced_dense
    from .core import bounds,contract
    E,_=balanced_dense(n,probe)
    deg,lam=bounds(E)
    if deg>d or lam>codegree:
        raise ValueError('dense candidate exceeds promise')
    rng=Random(seed)
    for _ in range(checks):
        a,b=rng.getrandbits(n),rng.getrandbits(n)
        if probe(a,b)!=contract(E,a,b):
            raise ValueError('dense holdout rejected')
    return E
