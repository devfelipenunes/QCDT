# Model and candidate guarantees

Let f be a Boolean multilinear polynomial of degree at most three over F2.
The phase oracle is U_f|x> = (-1)^f(x)|x>. We recover its cubic coefficients
T_ijk. Local degree d bounds triples containing a vertex; codegree lambda
bounds triples containing a pair. Both bounds are supplied, not learned here.

The second finite difference D_a D_b f is affine. Its coefficient of x_i is
b^T L_i a, where L_i[j,k]=T_ijk is alternating. A four-call derivative circuit
followed by Bernstein–Vazirani gives all coefficients simultaneously. This
primitive follows known polynomial-learning techniques.

For binary sparse vectors of weight <=k, odd power sums of distinct nonzero
GF(2^m) labels determine even power sums by squaring. The first 2k moments
uniquely determine a vector by Vandermonde; Berlekamp–Massey plus a root scan
recovers it in polynomial time. For general codegree use asymmetric sketches
H_(2d) L_i H_lambda^T; first decode the support of L_i a, then each sparse row.
Cost before verification O(d lambda log^2 n) logical phase queries.

For lambda=1, L_i 1 equals the adjacency indicator of the pair projection.
All triples are triangles of that projection. Propagate forced triangles and
saturated pairs/degrees. If ambiguity remains, assign different colors to
alternative third vertices for each pair. The conflict graph is a subgraph
of the square of the projection, degree <= (2d)^2. For each color bit use a
BCH sketch to identify the residual third vertex. The ideal acquisition bound
is O(d log n log(d+1)), or O(d log n) when propagation suffices. These are
candidate bounds, not measured physical runtimes.

Independent verification: for an incorrect cubic reconstruction, some
residual link is a nonzero alternating matrix of rank >=2. Uniform independent
a,b detect a discrepancy at that output bit with probability at least 3/8.
With r independent checks, false acceptance <=(5/8)^r in the ideal cubic
model. Fixed seeds are only for reproducibility. This does not certify
arbitrary noncubic or systematically corrupted oracles.

For fixed degree, the family of partitions into disjoint triples has
n!/(6^(n/3)(n/3)!) possibilities (n divisible by 3), giving an Omega(n log n)
classical bit-query lower bound by counting. The oracle-query quantum lower
bound from the dimension of the span of degree-q oracle-sign monomials is
Omega(log n). Independent review is required.

## Related work to compare formally

- Montanaro, [Learning multilinear polynomials](https://arxiv.org/abs/1105.3310).
- Montanaro and Shao, [Quantum algorithms for learning a hidden graph](https://doi.org/10.4230/LIPIcs.TQC.2022.1).
- Arunachalam et al., [Learning quantum phase states](https://arxiv.org/abs/2208.07851).
- [Learning bounded-degree graphs](https://arxiv.org/abs/2402.18714).
- [Hypergraph reconstruction thresholds](https://proceedings.mlr.press/v247/bresler24a.html)
  and [partial and exact recovery](https://proceedings.mlr.press/v291/bresler25a.html).
- [Sketching sparse matrices](https://arxiv.org/abs/1303.6544).

Access models differ. Query separation is not gate or wall-clock advantage.
The public gate list trivializes recovery; a realistic application requires
an opaque, coherently callable oracle. This is a preliminary literature map,
not an exhaustive novelty search.
