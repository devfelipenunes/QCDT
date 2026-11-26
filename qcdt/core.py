"""Ideal cubic QCDT: linear projection and general asymmetric BCH recovery."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from random import Random
from .field import BCH


def pack(indices):
    return sum(1 << i for i in set(indices))


def contract(edges, a, b):
    out = 0
    for i, j, k in edges:
        for x, y, z in ((i, j, k), (j, i, k), (k, i, j)):
            if ((a >> y & 1) & (b >> z & 1)) ^ ((a >> z & 1) & (b >> y & 1)):
                out ^= 1 << x
    return out


def shadow(edges, n):
    N = [set() for _ in range(n)]
    for e in edges:
        for i, j in combinations(e, 2):
            N[i].add(j)
            N[j].add(i)
    return N


def bounds(edges):
    return (max(Counter(i for e in edges for i in e).values(), default=0),
            max(Counter(p for e in edges for p in combinations(e, 2)).values(), default=0))


def propagate(N, d):
    pairs = {(i, j) for i, ns in enumerate(N) for j in ns if i < j}
    U = {(i, j, k) for i, j in pairs for k in N[i] & N[j] if j < k}
    F = set()
    while True:
        old = len(U), len(F)
        deg = Counter(i for e in F for i in e)
        occupied = Counter(p for e in F for p in combinations(e, 2))
        if max(deg.values(), default=0) > d or max(occupied.values(), default=0) > 1:
            raise ValueError("invalid forced edges")
        U = {e for e in U if e in F or (all(deg[i] < d for i in e)
                                      and all(not occupied[p] for p in combinations(e, 2)))}
        covers = {p: [] for p in pairs}
        for e in U:
            for p in combinations(e, 2):
                covers[p].append(e)
        if any(not c for c in covers.values()):
            raise ValueError("uncovered pair")
        F |= {c[0] for c in covers.values() if len(c) == 1}
        if old == (len(U), len(F)):
            return F, U - F


@dataclass(frozen=True)
class Recovery:
    edges: frozenset
    acquisition_queries: int
    verification_queries: int
    color_bits: int


def recover(n, d, codegree, probe, *, checks=10, seed=None):
    """probe(a,b) returns the n-bit BV output; four logical phase queries per call.

    Exact cubic-oracle promise; no claim for noisy measurements or higher degrees.
    Independent ideal holdout uses fresh uniform masks. ValueError means rejection.
    """
    if n < 3 or not 1 <= codegree <= d or checks < 1:
        raise ValueError("invalid recovery configuration")
    cache = {}
    def query(a, b):
        if not a or not b or a == b:
            return 0
        key = tuple(sorted((a, b)))
        if key not in cache:
            v = probe(a, b)
            if not isinstance(v, int) or not 0 <= v < (1 << n):
                raise ValueError("invalid probe output")
            cache[key] = v
        return cache[key]

    B = BCH(n, 2 * d)
    def acquire(a, F=()):
        raw = [query(a, b) ^ contract(F, a, b) for b in B.masks]
        return [set(B.decode([(v >> i) & 1 for v in raw])) for i in range(n)]

    bits = 0
    if codegree == 1:
        N = acquire((1 << n) - 1)
        if any(i in ns or any(i not in N[j] for j in ns) for i, ns in enumerate(N)):
            raise ValueError("asymmetric projection")
        F, U = propagate(N, d)
        choices = defaultdict(set)
        for e in U:
            for p in combinations(e, 2):
                choices[p].add(next(x for x in e if x not in p))
        conflicts = defaultdict(set)
        for C in choices.values():
            for x in C:
                conflicts[x].update(C - {x})
        colors = {}
        for x in sorted(conflicts, key=lambda j: (-len(conflicts[j]), j)):
            used = {colors[y] for y in conflicts[x] if y in colors}
            colors[x] = next(c for c in range(len(used) + 1) if c not in used)
        bits = max(colors.values(), default=0).bit_length()
        signatures = dict.fromkeys(choices, 0)
        for t in range(bits):
            row = acquire(pack(x for x in colors if colors[x] >> t & 1), F)
            if any(tuple(sorted((i, j))) not in choices for i, ns in enumerate(row) for j in ns):
                raise ValueError("unexpected residual")
            for i, j in choices:
                if (j in row[i]) != (i in row[j]):
                    raise ValueError("asymmetric residual")
                signatures[i, j] |= int(j in row[i]) << t
        found = Counter()
        for p, C in choices.items():
            match = [x for x in C if colors[x] == signatures[p]]
            if len(match) != 1:
                raise ValueError("ambiguous color")
            found[tuple(sorted((*p, match[0])))] += 1
        if any(v != 3 for v in found.values()):
            raise ValueError("inconsistent triangles")
        E = F | set(found)
        if shadow(E, n) != N:
            raise ValueError("projection mismatch")
    else:
        A = BCH(n, codegree)
        rows = [defaultdict(int) for _ in range(n)]
        for t, a in enumerate(A.masks):
            for i, ns in enumerate(acquire(a)):
                for j in ns:
                    rows[i][j] |= 1 << t
        found = Counter()
        for i, row in enumerate(rows):
            for j, v in row.items():
                for k in A.decode([(v >> t) & 1 for t in range(len(A.masks))]):
                    if len({i, j, k}) != 3:
                        raise ValueError("invalid diagonal")
                    found[tuple(sorted((i, j, k)))] += 1
        if any(v != 6 for v in found.values()):
            raise ValueError("inconsistent links")
        E = set(found)
    deg, lam = bounds(E)
    if deg > d or lam > codegree:
        raise ValueError("promise exceeded")
    rng = Random(seed)
    # Do not reuse acquisition data. Seed is for reproducibility, not adversarial security.
    for _ in range(checks):
        a, b = rng.getrandbits(n), rng.getrandbits(n)
        if probe(a, b) != contract(E, a, b):
            raise ValueError("independent verification rejected candidate")
    return Recovery(frozenset(E), 4 * len(cache), 4 * checks, bits)
