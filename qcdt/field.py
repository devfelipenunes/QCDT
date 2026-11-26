"""Binary finite fields and BCH sparse-vector decoding (reference implementation)."""
from functools import lru_cache


def remainder(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    return a


def mul(a, b, poly):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a.bit_length() == poly.bit_length():
            a ^= poly
    return result


@lru_cache(maxsize=None)
def modulus(m):
    # Deterministic small-field search; not an asymptotic field construction.
    for p in range((1 << m) | 1, 1 << (m + 1), 2):
        x = 2
        for i in range(1, m + 1):
            x = mul(x, x, p)
            if i <= m // 2 and gcd(x ^ 2, p) != 1:
                break
        else:
            if x == 2:
                return p
    raise ValueError("no irreducible polynomial found")


class BCH:
    def __init__(self, n, k):
        self.n, self.k = n, min(n, k)
        self.m = max(2, n.bit_length())
        self.poly = modulus(self.m)
        self.masks = []
        for t in range(1, 2 * self.k, 2):
            labels = [self.power(j + 1, t) for j in range(n)]
            self.masks.extend(sum(((x >> b) & 1) << j for j, x in enumerate(labels))
                              for b in range(self.m))

    def mul(self, a, b):
        return mul(a, b, self.poly)

    def power(self, a, t):
        r = 1
        while t:
            if t & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            t >>= 1
        return r

    def decode(self, bits):
        if len(bits) != len(self.masks) or any(b not in (0, 1) for b in bits):
            raise ValueError("invalid syndrome")
        k, m = self.k, self.m
        odd = [sum(bits[j + b] << b for b in range(m))
               for j in range(0, len(bits), m)]
        s = [0] * (2 * k + 1)
        for t in range(1, 2 * k + 1):
            s[t] = odd[t // 2] if t % 2 else self.mul(s[t // 2], s[t // 2])
        seq = s[1:]
        c = [1] + [0] * (2 * k)
        b = c.copy()
        L, shift, last = 0, 1, 1
        for i, x in enumerate(seq):
            for j in range(1, L + 1):
                x ^= self.mul(c[j], seq[i - j])
            if not x:
                shift += 1
                continue
            old = c.copy()
            coef = self.mul(x, self.power(last, (1 << m) - 2))
            for j in range(2 * k + 1 - shift):
                c[j + shift] ^= self.mul(coef, b[j])
            if 2 * L <= i:
                L, b, last, shift = i + 1 - L, old, x, 1
            else:
                shift += 1
        if L > k:
            raise ValueError("sparsity exceeded")
        # Scan only the n admissible labels, not the entire field or all pairs.
        roots = []
        for j in range(self.n):
            v = 0
            for x in c[:L + 1]:
                v = self.mul(v, j + 1) ^ x
            if not v:
                roots.append(j)
        word = sum(1 << j for j in roots)
        if len(roots) != L or any((word & a).bit_count() % 2 != y
                                  for a, y in zip(self.masks, bits)):
            raise ValueError("inconsistent BCH syndrome")
        return roots
