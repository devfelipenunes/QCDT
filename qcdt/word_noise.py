"""Amplification under a conditional per-observation whole-word error bound."""
import math
from random import Random
from .core import contract

def repetitions(cap,eta,delta):
    if type(cap) is not int or cap<1 or not 0<=eta<.5 or not 0<delta<1:raise ValueError('invalid guarantee')
    if eta==0:return 1
    r=math.ceil(math.log(cap/delta)/(2*(.5-eta)**2))
    return r if r%2 else r+1

class Majority:
    """Bitwise majority; early stop only when the planned result is irreversible."""
    def __init__(self,n,sample,r,*,cost=4,budget=None,early=True):
        if type(n) is not int or n<1 or type(r) is not int or r<1 or r%2==0 or cost<1:raise ValueError('invalid majority')
        self.n=n;self.sample=sample;self.r=r;self.cost=cost;self.budget=budget;self.early=early;self.calls=0;self.shots=0
    def __call__(self,*args):
        self.calls+=1;ones=[0]*self.n;h=self.r//2+1
        for t in range(1,self.r+1):
            if self.budget is not None and (self.shots+1)*self.cost>self.budget:raise ValueError('budget exhausted')
            v=self.sample(*args);self.shots+=1
            if type(v) is not int or not 0<=v<1<<self.n:raise ValueError('invalid sample')
            for j in range(self.n):ones[j]+=v>>j&1
            if self.early and all(x>=h or t-x>=h for x in ones):break
        return sum((x>=h)<<j for j,x in enumerate(ones))

def holdout_count(eta,delta):
    """Unamplified full-word test: valid for eta < 21/53."""
    gap=(21/32)*(1-eta)-eta
    if not 0<=eta<21/53 or not 0<delta<1:raise ValueError('invalid certification promise')
    return math.ceil(2*math.log(1/delta)/gap**2)

def certify(n,edges,sample,eta,delta,*,seed=None):
    """Fresh mask randomness assumed independent of candidate and prior history."""
    r=holdout_count(eta,delta);threshold=(eta+(21/32)*(1-eta))/2
    rng=Random(seed);errors=0
    for _ in range(r):
        a,b=rng.getrandbits(n),rng.getrandbits(n);v=sample(a,b)
        if type(v) is not int or not 0<=v<1<<n:raise ValueError('invalid sample')
        errors+=v!=contract(edges,a,b)
    return errors/r<=threshold,r,errors
