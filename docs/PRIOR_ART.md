# Prior-art audit — targeted search, not a novelty certificate

Search date: 2026-11-25 BRT. Queries included "quantum query complexity learning
multilinear polynomials", "quantum learning hidden hypergraph parity oracle sparse
multilinear polynomial", "quantum graph learning parity bounded degree",
"quantum phase states sparse diagonal circuits", "hypergraph projection
reconstruction", and "learning sparse multivariate polynomials membership
queries". Include primary sources on exact learning, graph/hypergraph
reconstruction, oracles, and sparse Boolean phases. Exclude unrelated classical
simulation and approximate Fourier learning from direct complexity comparisons.
This is a targeted search, not an exhaustive bibliometric review.

## Access-model matrix

| Source | Access | Relevant result / distinction |
|---|---|---|
| Montanaro (2012), [arXiv:1105.3310](https://arxiv.org/abs/1105.3310), Lemma 4 and Algorithm 1 | coherent value oracle | Finite differences and BV already learn highest-degree coefficients; cubic dense unit-pair method costs 4 binom(n,2). QCDT does not invent the derivative primitive. |
| Montanaro & Shao (TQC 2022), [paper](https://arxiv.org/html/2011.08611), Lemma 16 and Theorem 14 | graph parity queries / graph-state copies | Two graph parity queries return adjacency-matrix times a mask. Sparse rows recover from shared random linear sketches, O(d log m) queries/copies in stated bounded-degree regime. |
| Arunachalam et al. (TQC 2023), [paper](https://arxiv.org/html/2208.07851), Sec. 4.1 | copies of phase states | Sparse phase-state learning via derivative samples and sparse linear systems; coherent repeatable oracle is stronger than copy access. Cannot compare sample counts directly. |
| Ferber & Hardiman (2024), [paper](https://arxiv.org/html/2402.18714v1) | quantum OR queries | Bounded-degree graph learning, different oracle; no direct query-count comparison. |
| Bresler et al. [COLT 2024](https://proceedings.mlr.press/v247/bresler24a.html), [COLT 2025](https://proceedings.mlr.press/v291/bresler25a.html) | observed graph projection | Reconstruction thresholds for random hypergraphs. Projection ambiguity and recovery from it are known. QCDT can ask extra coherent queries to disambiguate. |
| Schapire & Sellie (1996), [paper](https://doi.org/10.1006/jcss.1996.0017) | membership and equivalence queries | Classical sparse polynomial learning; equivalence counterexamples are not available in our value-query model. |
| [ESA 2026 CUT-oracle learnability](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESA.2026.150) | cut queries | Identifiability barriers, different oracle; not a direct comparator. |

## Stronger reduction and baseline

A directional derivative of a cubic polynomial is quadratic. Its alternating
adjacency matrix A_a has entries sum_k T_ijk a_k. Applying the graph parity
primitive of Montanaro–Shao to this derivative yields A_a b in four cubic
phase calls. Thus this central QCDT operation is a direct composition of
known methods, not an independent novelty claim. The linear terms of the
quadratic derivative do not affect the measured coefficients.

For codegree one, give vertex k the nonzero binary label k+1. For each label
bit choose a mask a. Recover all sparse rows of A_a with BCH sketches;
each pair's recovered bit vector is its unique third vertex's label.
Requires O(d log^2 n) ideal phase queries; no projection ambiguity or
coloring. Implemented in qcdt/matched.py as label_bits, a derived comparator
using known graph sketch ideas rather than a verbatim published algorithm.
QCDT's projection/propagation/coloring can reduce the number of directions.
For general codegree the asymmetric BCH scheme is likewise a composition
of derivative and row-sketch methods. Novelty must be evaluated at the
specific improvement, not at the component algorithms.

Dense comparator: query only unit pairs internal to a balanced partition
of vertices into two parts. Each triple contains at least one such pair.
Cost 4[binom(floor(n/2),2)+binom(ceil(n/2),2)]. Among fixed unit-pair-only
schemes it is optimal: the complement of any covering pair set must
be triangle-free, and Mantel's theorem bounds its size by floor(n^2/4).
This is not a lower bound for arbitrary coherent algorithms.

Classical comparator: third derivative with independent masks, binary
splitting and cancellation (round 8). At most floor(nd/3) cubic terms,
a nonzero residual trilinear form is detected with probability at least
1/8. A union bound sets the number of negative attempts for delta=.01.
Counts distinct cached value queries; not claimed to be best possible.

## Fixed-seed comparison

30 generated hypergraphs (five per configuration), local Python 3.13.5.
Same oracle polynomial, including lower terms. True d and codegree supplied
to QCDT; label method only under codegree 1. QCDT uses 40 holdout calls
in addition to acquisition. Label and dense methods use ideal promise,
no independent holdout. Classical includes probabilistic stopping.
All applicable reconstructions were correct, but these are small,
exploratory samples, not independent confirmations of theoretical optimality.

| n,d; family | QCDT acquisition | QCDT holdout | balanced dense | label bits | classical value |
|---|---:|---:|---:|---:|---:|
| 6,2 linear | 60 | 40 | 24 | 72 | 64 |
| 16,2 linear | 80 | 40 | 224 | 340 | 839 |
| 32,4 linear | 184 | 40 | 960 | 1020 | 2769 |
| 64,4 linear | 224 | 40 | 3968 | 1456 | 6557 |
| 128,2 linear | 128 | 40 | 16128 | 880 | 7317 |
| 32,4 overlapping | 1896 | 40 | 960 | n/a | 2872 |

Median logical calls; different oracle models are explicitly labeled.
No physical timing or gate advantage inferred. QCDT loses to the stronger
dense comparator on the small and overlapping examples. Tests: 1024
five-vertex hypergraphs for dense coverage, 26 linear cases for label bits,
mixed-degree and Pasch checks. Reproduce with python -m benchmarks.matched.

## Decision

Continue only as a candidate refinement of known sparse graph/polynomial
learning. The derivative, sparse row sketch and projection are individually
known. The deterministic ambiguity resolution using fewer directions under
codegree one is a specific candidate contribution. Need independent proof
review, broader search including citations forward/backward, comparison
against more published implementations and a realistic oracle cost model.
No novelty or quantum advantage claim; issue #3 remains open.
