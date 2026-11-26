"""Elementary exact comparators; not claimed to be best published algorithms."""
from itertools import combinations
from functools import lru_cache


def dense_cubic(n, probe):
    """Unit-vector second derivatives, each exposing all third coefficients."""
    edges = set()
    count = 0
    for i, j in combinations(range(n), 2):
        v = probe(1 << i, 1 << j)
        count += 4
        for k in range(j + 1, n):
            if v >> k & 1:
                edges.add((i, j, k))
    return frozenset(edges), count


def classical_cubic(n, evaluate):
    """Exact Mobius interpolation of cubic coefficients via value queries."""
    @lru_cache(None)
    def f(x):
        return evaluate(x)
    edges = set()
    for e in combinations(range(n), 3):
        value = 0
        for r in range(4):
            for subset in combinations(e, r):
                value ^= f(sum(1 << i for i in subset))
        if value:
            edges.add(e)
    return frozenset(edges), f.cache_info().misses
