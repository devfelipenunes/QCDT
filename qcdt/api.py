"""Explicit opt-in bounded ideal research API; not production or adversarial safety."""
from dataclasses import dataclass
from typing import Protocol
from .budget import circuit_cap
from .core import Recovery,recover

class Probe(Protocol):
    def __call__(self,a:int,b:int,/) -> int: ...

@dataclass(frozen=True)
class ResourcePolicy:
    max_n:int=512
    max_degree:int=32
    max_phase_queries:int=100000

def recover_bounded(n:int,d:int,codegree:int,probe:Probe,*,policy:ResourcePolicy=ResourcePolicy(),
                    checks:int=10,seed:int|None=None)->Recovery:
    """Preflight a conservative logical query cap. No time/memory guarantee.

    The callback must implement an exact cubic oracle contraction. A policy
    limit is not a proof of the cubic promise. Counts logical phase calls,
    not physical shots, native gates or costs inside the caller's callback.
    """
    for x in (n,d,codegree,checks,policy.max_n,policy.max_degree,policy.max_phase_queries):
        if type(x) is not int or x<1:raise ValueError('positive integer required')
    if n<3 or n>policy.max_n or d>policy.max_degree or codegree>d:
        raise ValueError('resource policy or promise exceeded')
    if 4*circuit_cap(n,d,codegree,'qcdt',checks=checks)>policy.max_phase_queries:
        raise ValueError('conservative phase query cap exceeded')
    used=0
    def limited(a,b):
        nonlocal used
        if used+4>policy.max_phase_queries:raise ValueError('phase query cap exhausted')
        used+=4
        word=probe(a,b)
        if type(word) is not int or not 0<=word<1<<n:raise ValueError('invalid callback word')
        return word
    result=recover(n,d,codegree,limited,checks=checks,seed=seed)
    if used!=result.acquisition_queries+result.verification_queries:
        raise RuntimeError('inconsistent logical query count')
    return result
