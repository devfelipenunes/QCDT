# M14 decision: reposition as a research refinement

The original derivative primitive is already implied by Montanaro (2012)
and Montanaro–Shao (2022), Lemma 16. Their Theorem 15 also explicitly learns
a graph of known bounded-degree support from random linear systems. Source:
https://arxiv.org/html/2011.08611 (section 3, theorem 15; section 4, lemma 16).
The earlier prior-art audit documents phase, value, graph-state, CUT and OR
models. Additional focused searches on 2026-11-26: "hypergraph parity queries
quantum learning", "learning hypergraph phase oracle cubic Boolean",
"quantum sparse multilinear polynomial learning queries". No directly
matching primary result surfaced in these searches; absence is not evidence
of novelty. This remains a targeted audit, not a systematic review of all
citations and databases.

## Stronger known-support reduction

Given exact projection N of a linear 3-uniform hypergraph, all rows of
each derivative adjacency matrix have support in N. A known-support
linear sketch (as in Theorem 15) replaces repeated sparse BCH decoding
in the ambiguity-resolution stage.

Let Delta=max |N(i)| <= 2d. Assign each vertex a binary label of width
r=Delta+ceil(log2 Delta)+1. When assigning vertex j, at most Delta spans
are forbidden: for every i adjacent to j, avoid the span of labels
already assigned in N(i). Each such span has dimension at most Delta-1.
Their union has size <=Delta*2^(Delta-1)<2^r/2. Uniform resampling thus
has expected constant trials; check membership by Gaussian elimination.
Labels in every N(i) are independent by induction. No oracle calls are
used during label selection. For small n one can instead use n unit masks.
This is a Las Vegas classical construction (expected polynomial time),
not a deterministic worst-case runtime claim.

For each ambiguity color bit, use r fixed masks b rather than BCH sketches
and solve a local full-rank linear system at each i. Same projection,
propagation and independent ideal holdout as the reference. Conflict
colors still require O(log(d+1)) direction bits. Query cost:
O(d log n + d log(d+1)) = O(d log n), since d <= (n-1)/2 for linear
hypergraphs. This bound is a derivation for a composition of known
techniques; it is not a novelty claim. No extension to general codegree
or gate noise is proved. Greedy span construction and reconstruction
are internally tested; independent proof review still required.

## Gate decision

Do not market QCDT as a newly discovered fundamental quantum algorithm.
Retain it as a candidate refinement and empirical study of sparse cubic
phase-oracle characterization. The graph-learning derivative/known-support
sketch, coding and projection methods are antecedents; possible original
contribution must be separately substantiated. The concrete M14 decision
is to reposition rather than certify novelty. Track independent proof
review and manuscript decisions under #6; actual oracle and hardware
feasibility under #5/#7. A successful CI run cannot certify originality.
