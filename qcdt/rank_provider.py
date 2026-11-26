"""Certified symmetric rank search and CRT rank providers (ideal algebra only).

The exact CRT mode uses a known O(k) symmetric-rank existence theorem for
small residue fields, not Bshouty's polynomial-in-field-degree algorithm.
Practical mode uses exact search only through degree four, then recursive CRT.
"""
from functools import lru_cache
from itertools import combinations
from .field import gcd, mul, remainder
from .general import polynomial_plan, karatsuba_plan

class SearchLimit(ValueError):
    """Exact search exceeded its explicit candidate limit; no result certified."""


def pmul(a, b):
    out = 0
    while b:
        if b & 1: out ^= a
        a <<= 1; b >>= 1
    return out


def quotient(a, p):
    out = 0
    while a and a.bit_length() >= p.bit_length():
        s = a.bit_length() - p.bit_length()
        out ^= 1 << s; a ^= p << s
    if a: raise ValueError('nonexact polynomial division')
    return out


def power(a, k, p):
    out = 1
    while k:
        if k & 1: out = mul(out, a, p)
        a = mul(a, a, p); k >>= 1
    return out


def irreducible(p):
    if type(p) is not int or p < 2: return False
    m = p.bit_length()-1
    x = remainder(2, p); z = x
    for i in range(1, m+1):
        z = mul(z, z, p)
        if i <= m//2 and gcd(z^x, p) != 1: return False
    return z == x


@lru_cache(None)
def irreducibles(k):
    return tuple(p for p in range(1<<k, 1<<(k+1)) if irreducible(p))


def linear_basis(columns):
    """Gaussian elimination, including a witness in the original columns."""
    basis = {}
    for i, v in enumerate(columns):
        c = 1<<i
        while v and v.bit_length()-1 in basis:
            w, b = basis[v.bit_length()-1]; v ^= w; c ^= b
        if v: basis[v.bit_length()-1] = (v,c)
    return basis


def coordinates(basis, word):
    c = 0
    while word:
        pivot = word.bit_length()-1
        if pivot not in basis: return None
        w,b = basis[pivot]; word ^= w; c ^= b
    return c


def xor_columns(columns, word):
    v = 0
    while word:
        low=word&-word; v ^= columns[low.bit_length()-1]; word ^= low
    return v


def _outer(mask, pairs):
    return sum(1<<t for t,(i,j) in enumerate(pairs) if mask>>i&1 and mask>>j&1)


def _targets(m, product):
    pairs=[(i,j) for i in range(m) for j in range(i,m)]
    values=[product(1<<i,1<<j) for i,j in pairs]
    return pairs,[sum(((v>>k)&1)<<t for t,v in enumerate(values)) for k in range(m)]


def weights_for_forms(m, product, forms):
    """Convert symmetric binary linear forms into a multiplication plan.

    Solve for each output coordinate in the span of outer products. A
    claimed external tester is not trusted until the span contains the
    multiplication tensor. Raises ValueError if the forms are insufficient.
    """
    forms=tuple(forms)
    if any(type(a) is not int or not 0<a<1<<m for a in forms):
        raise ValueError('invalid form')
    pairs,targets=_targets(m,product)
    basis=linear_basis(_outer(a,pairs) for a in forms)
    weights=[0]*len(forms)
    for k,target in enumerate(targets):
        c=coordinates(basis,target)
        if c is None: raise ValueError('forms do not span multiplication')
        while c:
            low=c&-c;weights[low.bit_length()-1]|=1<<k;c^=low
    return tuple((a,a,w) for a,w in zip(forms,weights) if w)


@lru_cache(None)
def exact_symmetric(p, max_candidates=None):
    """Exhaustive minimum symmetric rank, no precomputed decomposition.

    Without a budget this terminates, but is exponential in field degree.
    With a budget it raises SearchLimit rather than claiming optimality.
    """
    if not irreducible(p): raise ValueError('irreducible modulus required')
    if max_candidates is not None and max_candidates<1: raise ValueError('invalid search limit')
    m=p.bit_length()-1
    pairs,targets=_targets(m,lambda a,b:mul(a,b,p))
    vectors=[0]+[_outer(a,pairs) for a in range(1,1<<m)]
    attempts=0
    # Rank >=2m-1: choose m-1 input forms with a nonzero common kernel;
    # multiplication by that nonzero element still has rank m.
    for r in range(2*m-1,min((1<<m)-1,len(pairs))+1):
        for forms in combinations(range(1,1<<m),r):
            if max_candidates is not None and attempts>=max_candidates:
                raise SearchLimit('exact symmetric rank search budget exhausted')
            attempts+=1
            basis=linear_basis(vectors[a] for a in forms)
            if len(basis)<r: continue
            if all(coordinates(basis,t) is not None for t in targets):
                return weights_for_forms(m,lambda a,b:mul(a,b,p),forms),attempts
    raise RuntimeError('symmetric forms must span all symmetric matrices')


def _combine(plan):
    out={}
    for a,b,w in plan:
        if a and b and w: out[a,b]=out.get((a,b),0)^w
    return tuple((a,b,w) for (a,b),w in sorted(out.items()) if w)


def karatsuba_base(p):
    m=p.bit_length()-1; size=1<<(m-1).bit_length()
    bits=[1<<i if i<m else 0 for i in range(size)]
    return _combine((a,b,remainder(w,p)) for a,b,w in polynomial_plan(bits,bits))


def crt_lift(p, parts, *, infinity=False):
    """Interpolate product polynomial from residues, optionally leading term."""
    m=p.bit_length()-1; parts=tuple(parts)
    moduli=[q for q,_ in parts]
    if len(set(moduli))!=len(moduli) or not all(irreducible(q) for q in moduli):
        raise ValueError('distinct irreducible moduli required')
    P=1
    for q in moduli: P=pmul(P,q)
    if P.bit_length()-1<2*m-1-int(infinity): raise ValueError('insufficient CRT degree')
    out=[]
    for q,plan in parts:
        k=q.bit_length()-1; M=quotient(P,q)
        E=pmul(M,power(remainder(M,q),(1<<k)-2,q))
        images=[remainder(1<<i,q) for i in range(m)]
        def pull(a): return sum(((a&v).bit_count()%2)<<i for i,v in enumerate(images))
        out.extend((pull(a),pull(b),remainder(remainder(pmul(E,w),P),p)) for a,b,w in plan)
    if infinity:
        w=(1<<(2*m-2))^remainder(1<<(2*m-2),P)
        out.append((1<<(m-1),1<<(m-1),remainder(w,p)))
    return _combine(out)


@lru_cache(None)
def exact_crt(p, max_candidates=None):
    """Uniform linear-rank construction with slow exact small-field search.

    For m>4 choose a degree k=O(log m) with enough distinct irreducibles.
    Exact residue searches have time 2^O(k^2) by known linear-rank existence.
    Rank O(m) holds for the unbounded mode; not a fast field-degree algorithm.
    """
    if not irreducible(p): raise ValueError('irreducible modulus required')
    m=p.bit_length()-1
    if m<=4:return exact_symmetric(p,max_candidates)[0]
    k=1
    while len(irreducibles(k))*k<2*m-1:k+=1
    count=(2*m-1+k-1)//k
    return crt_lift(p,[(q,exact_symmetric(q,max_candidates)[0]) for q in irreducibles(k)[:count]])


@lru_cache(None)
def practical_base(p):
    """Finite-size hybrid: certified exact small ranks, recursive mixed CRT.

    No assertion that this bounded practical mode has linear asymptotic rank.
    """
    if not irreducible(p): raise ValueError('irreducible modulus required')
    m=p.bit_length()-1
    if m<=4:return exact_symmetric(p)[0]
    target=2*m-2;k=1
    while sum(j*len(irreducibles(j)) for j in range(1,k+1))<target:k+=1
    if k>=m:return karatsuba_base(p)
    # Knapsack: minimize residue rank before lifting and cancelling duplicates.
    dp={0:(0,())}
    for j in range(1,k+1):
        for q in irreducibles(j):
            plan=practical_base(q)
            for deg,(cost,parts) in list(dp.items()):
                nd=min(target,deg+j);nc=cost+len(plan)
                if nd not in dp or nc<dp[nd][0]:dp[nd]=(nc,parts+((q,plan),))
    candidate=crt_lift(p,dp[target][1],infinity=True)
    old=karatsuba_base(p)
    return candidate if len(candidate)<len(old) else old


def tower_lift(g, base):
    m=g.m;out=[]
    for a,b,w in base:
        out.extend([(a,b,w|(w<<m)),(a<<m,b<<m,g.base(g.beta,w)),(a|(a<<m),b|(b<<m),w<<m)])
    return _combine(out)


def exact_rank_plan(g, *, max_candidates=None):
    return tower_lift(g,exact_crt(g.mod,max_candidates))


def power_basis(g):
    """Find a generator outside the base field; worst-case polynomial in n.

    Width 2m=O(log n); exhaustive generator search is not polynomial in m.
    """
    for z in range(1<<g.m,1<<g.width):
        powers=[1]
        for _ in range(g.width):powers.append(g.mul(powers[-1],z))
        basis=linear_basis(powers[:-1])
        if len(basis)==g.width:
            p=(1<<g.width)|coordinates(basis,powers[-1])
            return p,tuple(powers[:-1]),basis
    raise RuntimeError('no generator found')


def direct_tower_plan(g, factory=practical_base):
    p,columns,basis=power_basis(g)
    images=[coordinates(basis,1<<i) for i in range(g.width)]
    def pull(a):return sum(((a&v).bit_count()%2)<<i for i,v in enumerate(images))
    return _combine((pull(a),pull(b),xor_columns(columns,w)) for a,b,w in factory(p))


def practical_rank_plan(g):
    """Choose smallest certified rank of the three public algebraic plans."""
    plans=(karatsuba_plan(g),tower_lift(g,practical_base(g.mod)),direct_tower_plan(g))
    return min(plans,key=len)


def candidate_plans(g):
    return {'karatsuba':karatsuba_plan(g),'tower-crt':tower_lift(g,practical_base(g.mod)),
            'direct-crt':direct_tower_plan(g)}


def public_mask_count(n,d,g,plan):
    """Exact number of distinct nontrivial masks under the weighted plan.

    Uses public parameters only; no callback or hidden support. This is
    not the truth-dependent adaptive planning rejected in the audit.
    """
    if n<3 or d<1 or n>=1<<g.m:raise ValueError('invalid parameters')
    d=min(d,(n-1)*(n-2)//2)
    xs=list(range(1,n+1));labels=[(1<<g.m)|x for x in xs];powers=[1]*n
    cache=set()
    def mask(values,form):return sum(((v&form).bit_count()%2)<<j for j,v in enumerate(values))
    for _ in range(2*d):
        A=[g.mul(x,p) for x,p in zip(xs,powers)]
        left={a:mask(A,a) for a in {t[0] for t in plan}}
        right={b:mask(powers,b) for b in {t[1] for t in plan}}
        for a,b,_ in plan:
            x,y=left[a],right[b]
            if x and y and x!=y:cache.add(tuple(sorted((x,y))))
        powers=[g.mul(p,L) for p,L in zip(powers,labels)]
    return len(cache)


def public_rank_plan(n,d,g):
    plans=candidate_plans(g)
    name=min(plans,key=lambda name:(public_mask_count(n,d,g,plans[name]),len(plans[name]),name))
    return name,plans[name]
