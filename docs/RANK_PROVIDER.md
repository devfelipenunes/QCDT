# Certified rank providers for weighted cubic recovery (issue #34)

Status: internal derivation and finite-size experiment, 2026-11-26.
Not a new finite-field multiplication theorem, independent review, or hardware result.

## 1. Literature and scope

Bshouty, *Multilinear Complexity is Equivalent to Optimal Tester Size*,
ECCC TR13-011 (2013), Corollary 3 and the paragraph after Theorem 2,
asserts a deterministic polynomial-in-extension-degree construction of
linear-rank bilinear multiplication, including its symmetric form. See
https://eccc.weizmann.ac.il/report/2013/011/download/ . The construction
uses testers from TR12-011 (2012), especially the polynomial-time
construction sections 3.4–3.6, which in turn use algebraic function fields
and smaller subproblems: https://eccc.weizmann.ac.il/report/2012/011/download/ .
The survey https://doi.org/10.1070/RM9928 corroborates the stated result.
A targeted correction search did not establish any correction invalidating
this corollary, but it is not an independent verification of the papers.
We have NOT implemented the full Bshouty tester construction. The local
Python environment does not have an algebraic-function-field/Riemann–Roch
implementation such as Sage available; porting the full proof is outside
this finite-size implementation.

CRT/evaluation-interpolation and recursive Chudnovsky-type multiplication
are known: Ballet, Bonnecaze and Pacifico (2020),
https://arxiv.org/abs/2007.16082 ; Pacifico (2022),
https://theses.fr/2022AIXM0411.pdf , develops hybrid constructions with
linear rank and polynomial construction time. The present CRT plan is a
specialized engineering alternative, not an originality claim. Cotardo
and Zullo (2026 preprint), https://arxiv.org/abs/2605.12295 , Proposition 2.7
and Table 1, already characterize symmetric rank through spans of
rank-one symmetric matrices and report ranks 3,6,9 for binary fields of
degrees 2,3,4 respectively. Our exact search reproduces these known ranks.

## 2. Uniform exact construction in the QCDT input size

Let m=max(2,ceil(log2(n+1))) and let K be the binary field of degree m.
Take monic irreducible p of degree m. For m>4 choose the smallest positive
k with k I_2(k)>=2m-1, where I_2(k) is the number of monic irreducible
binary polynomials of degree k. Such k=O(log m): among 2^k field elements,
those of proper degree are contained in subfields of degrees at most
floor(k/2), with total size bounded above by sum_{j=1}^{floor(k/2)}2^j.
Hence k I_2(k)>=2^k-2^{floor(k/2)+1}+2. Taking k=ceil(log2(4m))
suffices for m>=5. Select s=ceil((2m-1)/k) distinct degree-k moduli.
Their product has degree >=2m-1. For polynomial inputs of degree <m,
recover their product (degree <=2m-2) exactly by CRT from the s residue
products, then reduce modulo p. Residue maps and output interpolation
are binary linear, so this composes bilinear plans.

For each residue field, use a deterministic exact symmetric rank search.
Represent each linear form by a nonzero k-bit mask and its outer product
by the upper-triangular entries of a symmetric matrix. A set of forms
suffices precisely when their outer-product span contains all k output
coordinate slices of the multiplication tensor. Solve these inclusions
by binary Gaussian elimination and reconstruct output weights. Checking
only upper triangles is sufficient because both the target and rank-one
matrices are symmetric; independent verification uses all ordered basis
pairs. A dependent form is removable and cannot be needed in a minimal
plan. The starting lower bound 2k-1 follows because the first k-1 input
forms share a nonzero kernel vector and multiplication by that vector
has rank k, requiring at least k remaining terms. An independent
symmetric spanning set of size <=k(k+1)/2 exists using coordinate forms
and sums of pairs, so unbounded search terminates. To obtain the linear
rather than quadratic bound, invoke the established symmetric linear-rank
existence theorem above: some sufficient set has size at most C*k for
fixed C. Search increasing subset size, and stop at the first solution.
The number of candidates before success is at most 2^{O(k^2)}; each
linear-system test costs polynomial time in k. For the finitely many
small m<=4 solve directly. The CRT construction therefore has rank
s*O(k)=O(m) with deterministic preprocessing
poly(m)*2^{O((log m)^2)} (apart from finding the initial modulus).
This is NOT a polynomial-in-m construction. It is polynomial in n for
m=O(log n); the existing exhaustive irreducible-modulus search costs at
most 2^{O(m)}=poly(n). No hidden support or oracle is used in preprocessing.

Lift the base plan through the quadratic extension F/K by the three
base products of the tower multiplication formula in general.py. The
resulting rank is O(m). With 2d weighted moments and four phase queries
per contraction, the resulting ideal weighted-link algorithm has
O(d log n) phase queries and deterministic polynomial-in-n preprocessing
and decoding. This supplies a concrete, albeit impractical, uniform
alternative to using Bshouty's fast tester construction as a black-box
provider. It still depends on established symmetric rank existence, not
on an empirical rank extrapolation. The general lower-bound theorem and
its degree range remain as stated in GENERAL_CUBIC_WORD_NOISE.md;
no dense-transition optimality or literature priority is asserted.

## 3. Practical provider and certificates

qcdt/rank_provider.py exposes:
- exact_symmetric(p, max_candidates=None): minimum symmetric rank by
  exhaustive search; an explicit limit raises SearchLimit, not a claim of
  optimality. Exact search is practical here only for very small k.
- exact_rank_plan(g, max_candidates=None): uniform CRT construction from
  section 2. Unbounded mode is the theoretical construction; a finite
  per-residue candidate limit may reject. It is not a scalable default.
- practical_base(p): exact search through degree 4, then recursive CRT
  over mixed irreducible degrees with a degree-coverage knapsack and an
  infinity coefficient; chooses the smaller plan versus base Karatsuba.
  This finite-size heuristic is NOT proved to have O(m) rank.
- direct_tower_plan(g): find a generator of the full field, construct the
  inverse power-basis transformation and pull input forms back to tower
  coordinates; push output weights forward. Worst-case generator search
  is exponential in field degree but polynomial in QCDT input n.
- weights_for_forms(m, product, forms): accepts proposed symmetric forms
  from any external provider and solves their output weights; rejects
  insufficient spans. It is not itself the construction of a tester.
- public_rank_plan(n,d,g): selects among old Karatsuba, tower CRT, and
  direct CRT by the exact number of nontrivial distinct mask pairs
  determined from the public parameters, with rank/name tie breakers.
  No query to the hidden cubic tensor is used in planning. Lower rank
  alone does not imply fewer distinct contractions.

All plans are independently validated by general.check_plan on every
ordered basis pair before acquisition via recover_general. The default
recover_general remains unchanged. Both modes use only the exact oracle
model; no robustness or hardware benefit follows from this algebra.

## 4. Finite-size experiments

Local Python 3.13; four new unit-test methods passed. Minimum symmetric
ranks for all eight irreducible polynomials of degrees 1–4 were 1,3,6,9
by degree. The rank-9 search required 13,032 candidate subsets for each
of the three degree-4 moduli. Every input pair in these small fields was
checked. For tower m=2..16, all three plans passed 17,940 ordered basis
products (45 plans). Exhaustive acquisition with public plan selection
recovered 1,024/1,024 five-vertex hypergraphs; public query counts matched
observed callback counts. The exact CRT mode was separately validated at
m=5,6 with ranks 48,69, a candidate limit of 50,000 per residue; full
reconstruction tested at n=16 and in the benchmark at n=16/32. We do not
claim completion of unbounded exact search on large residue degrees.

Benchmark: six public (n,d) configurations, three seeds 3401/3402/3403
per configuration; 18 instances, 117 method observations, all correct.
Same hidden cubic terms and same ideal callback. The archived original
v0.5 is executed via its existing verified subprocess adapter; current
reference is the v0.10-style asymmetric decoder, not the archived noisy
simplex variant. Both reference and legacy run one holdout, charged
separately and excluded from the following acquisition medians. Degree
and codegree upper bounds supplied (actual codegree used by reference).
Fixture generation is greedy and synthetic, not uniform sampling. Dense
control is balanced fixed pair cover. The exact CRT mode is an additional
comparator where small residue search is feasible; not included in
practical plan selection.

| n | d | practical selected | old Karatsuba / historical v0.5 | current reference | dense | exact CRT if tested |
|---:|---:|---:|---:|---:|---:|---:|
|8|3|436|436|400|48|—|
|8|21|3168|3168|748|48|—|
|16|4|1004|1040|1920|224|1176|
|32|4|1272|1316|1896|960|1688|
|32|8|2700|2960|5148|960|3796|
|64|2|664|664|1148|3968|—|

At m=9, direct CRT rank 80 versus padded tower Karatsuba 186; at m=16,
161 versus 243. These are algebraic rank counts, not native quantum gate
counts. The practical planner improves acquisition on three of the six
configurations relative to Karatsuba, ties the other three. Dense wins
five of six configurations; the best overall method is NOT always the
weighted decoder. The exact CRT construction has larger finite constants
than practical selection in all three compared configurations. Do not
promote it as a faster default. Actual timings include Python and, for
legacy, subprocess overhead; not comparable physical runtime. Initial
full local run exceeded the command time limit, so all six configurations
were rerun in three smaller batches. All batches completed; raw records
retained. CI runs the benchmark as a single command.

## 5. Reproduce and next decision

```
python -m unittest discover -s tests -p test_rank_provider.py -v
python -m benchmarks.rank_provider
```

Requires the existing full simulator/historical Python dependencies for
archived v0.5. Results write rank-provider-results.json. The evidence ZIP
contains local raw results, per-batch records, logs and source snapshot.
Prioritize review of the general weighted reduction and the manuscript
(#6), not further rank micro-optimization without a measured benefit.
If future work specifically needs polynomial time in m, port an established
fast tester/hybrid AG provider, benchmark its constants and use the
existing certificate interface. The slower exact CRT provider is a
justified alternative for the polynomial-in-n requirement. Independent
review, originality, noise tolerance and physical access remain open.
