# Targeted literature review — reviewer aid, 26 November 2026

Not a systematic review or proof of originality. Search scope: quantum
exact learning, sparse Boolean cubic polynomials, parity hypergraph
oracles, sparse interpolation, finite-field rank, graph learning, and
oracle identification. Queries included "quantum query learning sparse
multilinear Boolean polynomials bounded degree hypergraph parity oracle",
"quantum exact learning sparse Boolean functions polynomial GF(2)
membership queries", "learning hypergraphs parity queries classical
sparse hypergraph reconstruction polynomial mod 2", and
"sparse interpolation finite fields Ben Or Tiwari". Primary paper pages
and available full-text sections were preferred. No exhaustive citation
graph or subscription database coverage is claimed.

| Source | Model / result | Relation and review risk |
|---|---|---|
| [Montanaro 2012](https://arxiv.org/html/1105.3310), Theorem 1, Lemma 4 and Algorithm 1 | coherent value oracle, arbitrary bounded total degree; O(n²) quantum queries for degree three | Direct antecedent for derivative-BV and counting. Our shared sparse moments must supply the distinction. |
| [Montanaro–Shao](https://arxiv.org/html/2011.08611), Theorems 14/15, Lemma 16 | graph states and graph parity; adjacency-vector multiplication with two coherent calls; bounded-degree support learning | Direct antecedent for sparse row sketches. Theorem 15 specifically uses graph-state copies with known containing graph. A cubic link reduction is not by itself novel. |
| [Arunachalam et al. TQC 2023](https://arxiv.org/html/2208.07851), §4.1 | phase-state copies; sparse F₂ monomial representations | Closest sparse phase-state direction; their sample access and total sparsity differ from our local cubic incidence/coherent oracle. Check whether their derivative samples can be upgraded or composed to reproduce our result. |
| [Bshouty 2013](https://eccc.weizmann.ac.il/report/2013/011/download/), Corollary 3 p.9 and after Theorem 2 p.10 | uniform linear-rank finite-field bilinear multiplication, symmetric version | Known theorem required for efficient upper. Full tester construction is not our implementation. |
| [Ben-Or–Tiwari 1988](https://doi.org/10.1145/62212.62241) | deterministic sparse polynomial interpolation | Moment recurrence/interpolation is established. Review whether multiplicative Sidon labels and shared contractions are already combined in prior work. Abstract/metadata checked. |
| [Roth–Benedek](https://www.cs.columbia.edu/~atw12/downloads/Roth.Benedek.interpolation.GF2.pdf) | classical sparse GF(2) interpolation via a critical set | Distinct value-query model and total monomial sparsity. Do not compare without normalizing promises. Abstract retrieved; full theorem comparison pending. |
| [Schapire–Sellie 1996](https://doi.org/10.1006/jcss.1996.0017) | membership and equivalence queries | Counterexample oracle is additional access. Polynomial-time sparse learning is established. Abstract checked. |
| [Sparse polynomial learning and graph sketching 2014](https://proceedings.neurips.cc/paper_files/paper/2014/hash/78812290b46192ce379f0349a4ef0758-Abstract.html) | real coefficients, random examples and cut sketches | Different field and identifiability conditions, not a direct comparator. |
| [Quantum exact learning 2019](https://doi.org/10.4230/LIPIcs.ICALP.2019.16) | Fourier-sparse Boolean functions, uniform quantum examples | Fourier sparsity is not algebraic-normal-form sparsity; cannot transfer exponents directly. |
| [Hypergraph CUT learnability 2026](https://doi.org/10.4230/LIPIcs.ESA.2026.150) | cut counts, sometimes edge-existence access | Different oracle and identifiability constraints. Linear hypergraphs in that model are relevant context, not a direct query lower bound. |

The rank-provider prior-art notes in docs/RANK_PROVIDER.md remain relevant
for CRT, symmetric rank and finite-size implementations. The manuscript
does not claim to invent finite differences, Prony/Berlekamp–Massey,
bilinear rank, conditional counting, CRT, or graph parity learning.

## Candidate delta versus known work

The specific question for review is whether the combination of a four-call
full cubic contraction, injective multiplicative labels for unordered link
pairs, nonzero weights, and shared bilinear finite-field moments yields a
previously unreported efficient exact learner under a maximum cubic
incidence bound. Query-only optimality is much less distinctive: random
binary contractions and a union bound already provide separating sketches
if arbitrary decoding time is allowed. This is now explicit in the draft.

## Outstanding independent search

Trace citations of [1–4] in both directions, search quantum learning
of sparse Reed–Muller codes, tensor/alternating-form reconstruction,
compressed sparse graph/hypergraph sketches and bilinear rank reductions.
Search synonyms for weighted pair-label interpolation and sparse tensor
slice recovery. Require a proof-level comparison on any candidate overlap.
Record source, exact theorem and model, whether it subsumes our statement,
and whether it makes the result incremental or redundant. An unsuccessful
search is not evidence of priority. Current status: no directly matching
result established by this targeted audit; equivalence remains possible.
