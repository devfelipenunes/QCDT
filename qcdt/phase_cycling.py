"""Exact probability controls; inverse-oracle access is an extra physical assumption."""
import cmath
import math
from .phase_feasibility import phase_diagonal
from .core import contract

def fwht(values):
    v=list(values);s=1
    while s<len(v):
        for j in range(0,len(v),2*s):
            for k in range(j,j+s):
                a,b=v[k],v[k+s];v[k],v[k+s]=a+b,a-b
        s*=2
    return v

def distribution(diagonal,a,b,sector):
    """Sector (p,q): sign (-1)^(p*i+q*j) on shift i*a XOR j*b."""
    size=len(diagonal);p,q=sector
    if size<2 or size&(size-1) or not 0<=a<size or not 0<=b<size or p not in (0,1) or q not in (0,1):
        raise ValueError('invalid parameters')
    w=[]
    for x in range(size):
        value=1+0j
        for i in (0,1):
            for j in (0,1):
                z=diagonal[x^(a if i else 0)^(b if j else 0)]
                value*=z.conjugate() if (p*i+q*j)&1 else z
        w.append(value)
    return [abs(z/size)**2 for z in fwht(w)]

def sector_variances(theta,a,b):
    """Real unwrapped phase theta; Parseval on Boolean Fourier characters."""
    size=len(theta)
    if size<2 or size&(size-1):raise ValueError('invalid length')
    variances={(p,q):0. for p in (0,1) for q in (0,1)}
    for s,v in enumerate(fwht(theta)):
        if s:
            key=((a&s).bit_count()%2,(b&s).bit_count()%2)
            variances[key]+=16*(v/size)**2
    return variances

def relative_bit_probability(diagonal,x):
    """One forward U on (|0>+|x>)/sqrt(2), unprepare, measure in X."""
    if not 0<=x<len(diagonal):raise ValueError('invalid word')
    if not x:return 0.
    return min(1.,max(0.,(1-(diagonal[x]*diagonal[0].conjugate()).real)/2))

def relative_cost(x):
    """Ideal all-to-all control only, excludes oracle synthesis, measurement, routing."""
    w=x.bit_count()
    return dict(oracle_calls=int(w>0),cx=2*max(0,w-1),h=2*int(w>0))
