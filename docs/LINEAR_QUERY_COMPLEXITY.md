# Candidate tight query complexity for linear cubic tensors

Status: internal proof candidate, 2026-11-26. Independent proof review and
novelty review pending. This is a new result within this project's research
history, not a claim of priority in the literature.

## Theorem candidate

Let n >= 96 and 1 <= d <= floor((n-1)/2). A Boolean multilinear
polynomial f has degree at most three, and its cubic monomials form a
3-uniform linear hypergraph (each pair lies in at most one edge) with
maximum vertex degree at most d. Given coherent phase queries
U_f|x> = (-1)^f(x)|x>, output its cubic support.

The bounded-error quantum query complexity (worst-case success >=2/3)
is Theta(d log n), uniformly over the stated range. The upper bound is
an exact-query construction with expected polynomial classical runtime;
the lower bound allows arbitrary quantum workspaces and adaptive
algorithms. Classical binary value-query complexity is Theta(nd log n)
with bounded error. Query counts do not measure circuit depth, oracle
synthesis, gate noise or physical wall-clock cost. Lower-degree terms
are arbitrary for the upper bounds; pure cubics suffice for lower bounds.
The global constant is not identifiable with phase-only access and is
not part of the output.

## 1. Counting linear bounded-degree hypergraphs

Take m=floor(nd/48). Build an ordered sequence of m triples, each
maintaining maximum degree <=d and pair codegree <=1. At t<m edges,
there are at most floor(3t/d) saturated vertices. At least
n-3t/d >= 15n/16 vertices are available. There are 3t previously
used unordered pairs. For each pair at most n-2 triples contain it.
A union bound therefore gives at least

    C(n-floor(3t/d),3) - 3t(n-2)

legal choices. This overcounts forbidden triples and is a lower bound.
Since n>=96, available-2 >= 7n/8. The binomial term is >=
(7n/8)^3/6 = 343n^3/3072. The forbidden term is <=
3(nd/48)n <= n^3/32. The difference is > n^3/20.
Thus there are at least (n^3/20)^m ordered sequences. A final
hypergraph has exactly m! legal orders (the constraints are hereditary).
The number M of labeled distinct outputs satisfies

    M >= (n^3/20)^m / m! >= (n^3/(20m))^m.

Here m>=nd/96 and n^3/(20m)>= (48/20)n^2/d >= n.
Consequently log_2 M >= (nd/96) log_2 n.
All counted inputs satisfy codegree one. The earlier lower bound
using a family of codegree d cannot be substituted for this proof.

## 2. Query lower bounds

Classical: fix random coins. A q-query binary decision tree has <=2^q
leaves, each naming at most one correct output. Averaging over uniform
inputs and the coins, success <=2^q/M. Worst-case success >=2/3 implies
q >= log_2 M + log_2(2/3) = Omega(nd log n).

Quantum: write z_x=(-1)^f(x) for the 2^n oracle signs. After q calls,
purified final states are linear combinations of monomials in z_x of
degree <=q, with input-independent vector coefficients. This follows
by induction since a query is diagonal in x (controlled/no-op queries
can add the constant monomial); interleaved operations independent of
f preserve the expansion. Deferred measurements and coherent classical
control give the same bound for adaptive algorithms with worst-case q.
At most (2^n+1)^q monomials suffice, allowing repetitions and padding.
All final states therefore lie in a common subspace of dimension
D <= (2^n+1)^q. For the POVM element P_H guessing hypergraph H and
projection Pi onto the subspace, each state rho_H <= Pi, so

    (1/M) sum_H Tr(P_H rho_H) <= Tr(Pi)/M = D/M.

If success >=2/3 on every input, D >= 2M/3. It follows that
q >= log_2(2M/3)/log_2(2^n+1) = Omega(d log n).
This is a dimension-counting argument; it is not a gate lower bound.

## 3. Upper bounds and comparison

For masks a,b, four calls and BV recover the full vector D(a,b)
whose i-th bit is b^T L_i a, where L_i is the alternating link
matrix with entries T_ijk. This finite-difference primitive is known.

Under codegree one, L_i 1 is the neighbor indicator of vertex i.
BCH odd-moment row sketches recover all neighborhoods in O(d log n)
queries. Each true triple is a triangle of the resulting projection;
propagate uniquely forced triangles and saturated pair/degree constraints.
For each remaining pair, the true third vertex belongs to its candidate
set. The conflict graph connects alternative third vertices; it is
contained in the square of the projection, of degree <=(2d)^2.
Greedy coloring thus needs O(log(d+1)) binary color directions.

For each color direction, the residual adjacency row is supported on
the known neighborhood N_i, of size <=Delta=2d. Choose labels of
width r=Delta+ceil(log_2 Delta)+1, avoiding previously assigned spans
in each incident neighborhood. At most Delta forbidden spans of size
<=2^(Delta-1) exclude fewer than half the labels. Independent random
resampling is Las Vegas with expected constant trials per label and
polynomial linear-algebra work. For an empty projection no labels are
needed. Unit masks can replace labels when r>=n. The local independent
labels determine each row by a full-column-rank system. Decode the
third-vertex colors and validate the triangle witnesses. The ambiguity
stage uses O(d log(d+1)) additional phase queries. Total
O(d log n+d log(d+1))=O(d log n). This is implemented in
qcdt/known_support.py. An optional constant number of ideal holdout
probes does not change the asymptotic bound.

Classical upper: qcdt/matched.py::classical_sparse uses third finite
differences, cancellation of recovered triples and binary splitting.
A nonzero residual trilinear form is detected with probability >=1/8
on three independent uniform masks: a nonzero multilinear form has
at least half its contractions nonzero in each successive argument.
At most floor(nd/3) triples can be recovered; O(log(nd/delta)) random
trials per stopping attempt and O(log n) splitting steps per triple
(each costs <=8 value queries) give O(nd log n) at constant delta.
The union bound includes all stopping attempts. Hence both models
match the counting lower bounds in their respective access models.

## 4. Scope, checks and falsification

Local finite checks: 63,071 (n,d) pairs for 96<=n<=512;
explicit ordered-path enumeration for five configurations gives
0, 10, 120, 1470, 9240 distinct families, each with exactly k! orders.
These are sanity checks of the combinatorial argument, not empirical
verification of asymptotic quantum optimality. The proof would fail
if the greedy bound, heredity, monomial span, or upper-bound decoder
assumptions fail. A prior theorem in the same model may preempt
novelty even if the mathematics is correct.

Related work: Montanaro, https://arxiv.org/abs/1105.3310
(finite-difference polynomial learning); Montanaro and Shao,
https://doi.org/10.4230/LIPIcs.TQC.2022.1 (graph parity queries and
known-support graph-state learning); Arunachalam et al.,
https://doi.org/10.4230/LIPIcs.TQC.2023.3 (phase-state-copy learning).
These are antecedents, not direct evidence that the specific tight
linear-hypergraph result is new. The proof uses standard counting and
quantum query dimension techniques. Independent literature and proof
review are required before any publication claim.
