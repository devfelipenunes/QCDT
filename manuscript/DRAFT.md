# Sparse cubic Boolean phase-oracle reconstruction by weighted derivative sketches

**Working manuscript, revision 2 — internal review draft, 26 November 2026.**
Authorship and affiliations to be confirmed by the contributors. No submission,
external endorsement, or claim of literature priority.

## Abstract

We study identification of the cubic support of an unknown Boolean polynomial
with maximum cubic incidence degree d on n variables, given repeatable coherent
phase-oracle access. Lower-degree coefficients are unrestricted nuisance terms.
A four-call finite-difference measurement returns all contractions of a cubic
coefficient tensor with two binary masks. We combine these measurements with
weighted multiplicative pair labels, finite-field bilinear multiplication,
and sparse interpolation to obtain a candidate exact algorithm with
O(min(d log n,n²)) queries and deterministic polynomial-in-n classical
processing. A counting argument gives an Ω(d log(n²/d)) quantum lower bound.
A separate universal-mask argument achieves the matching query order throughout
the degree range, without an efficient decoding guarantee. The corresponding
binary classical value-query order is Θ(nd log(n²/d)). In particular, the
efficient weighted construction attains optimal query order for
d≤n^(2−ε), for fixed ε>0. We explicitly distinguish this query theorem from
finite-size performance and physical resource advantages. Synthetic experiments
show reductions on some sparse instances and losses on small or overlapping
instances, including under approximate device-snapshot noise. The specific
combination of weighted pair labels and shared derivative sketches is the
candidate contribution to be assessed against earlier work.

## 1. Problem and results

All arithmetic on Boolean variables is over F₂ unless specified otherwise.
Let [n]={1,...,n}, n≥3, and write

$$
f(x)=g(x)+\sum_{i<j<k} T_{ijk}x_ix_jx_k,\qquad \deg g\le 2.
$$

The unknown support E consists of unordered triples with T=1. Define
d_i=|{e∈E:i∈e}| and assume max_i d_i≤d, where
1≤d≤N=binom(n−1,2) is a public upper bound. The promise is on cubic incidence,
not polynomial degree (which is at most three) and not total monomial
sparsity. Pair codegree is unrestricted except when explicitly considering
the linear subclass. The output is E, not g, global phase, the original
gate sequence, or an arbitrary Hamiltonian.

One quantum query is an invocation of U_f|x⟩=(-1)^f(x)|x⟩, with the same
unknown exact unitary available repeatedly. The upper construction does not
require controlled-U, an independently accessible inverse, or any ideal
answers during planning. One classical value query returns one bit f(x).
We do not equate these access models physically. Counting lower bounds allow
arbitrary computation, adaptive queries, and worst-case success ≥2/3.

**Theorem 1 (candidate, query complexity).** For n≥96 and the full admissible
range of d, ignoring computational runtime, the bounded-error query complexities
are

$$
Q(n,d)=\Theta\!\left(d\log_2(n^2/d)\right),\quad
C(n,d)=\Theta\!\left(nd\log_2(n^2/d)\right).
$$

The upper bounds can in fact be achieved by exact nonadaptive queries using
a finite deterministic search for universal masks and exhaustive decoding.
Their computation may be exponential; this is not an efficient algorithm.

**Theorem 2 (candidate, efficient recovery).** In the same model there is
an exact, nonadaptive quantum algorithm using O(min(d log n,n²)) phase
queries and deterministic classical work polynomial in n. For every fixed
ε>0, this matches Theorem 1 in the range d≤n^(2−ε). Classical value access
can simulate its sketches in O(min(nd log n,n³)) queries with polynomial
classical work. The dense-transition gap is an efficient-computation gap,
not a query-only gap. We do not prove hardness of efficient decoding there.

The proof uses standard finite differences [1,2], known linear-rank
multiplication [4,5], and known sparse interpolation principles [6,7].
Their combination below is the subject of independent review; no novelty
claim follows merely from stating a theorem.

## 2. Shared derivative measurements

For a∈F₂^n define Δ_a f(x)=f(x+a)+f(x). Since deg f≤3,
Δ_bΔ_a f is affine, with linear coefficients

$$
D_i(a,b)=\sum_{\{j,k\}:\{i,j,k\}\in E}(a_jb_k+a_kb_j).
$$

Indeed, expand each cubic monomial and keep the terms linear in x; all
quadratic and lower monomials contribute only constants or zero. Define
L_i as the symmetric zero-diagonal matrix with an entry 1 at (j,k) iff
{i,j,k}∈E. Then D_i=a^T L_i b. This is the four-call cubic specialization
of finite-difference Bernstein–Vazirani learning [1]; the corresponding
two-call graph adjacency measurement is explicit in [2, Lemma 16].

Prepare |+⟩^n, apply U_f then X_a, U_f then X_b, U_f then X_a, U_f then X_b.
The total shifts cancel and the phases multiply to
(-1)^{f(x)+f(x+a)+f(x+b)+f(x+a+b)}. A final H on every wire and measurement
returns D(a,b) with probability one. The constant disappears as a global
phase. Masks are classical public bitstrings; no oracle is used to choose
them. For ideal f, zero masks and equal masks imply D=0; unordered mask
pairs are interchangeable. Such omissions and caching are optional exact
optimizations, not additional oracle information.

A classical simulation of one output bit uses the third difference
Δ_cΔ_bΔ_a f(0) with c=e_i, expanded into at most eight evaluations. Hence a
full vector costs at most 8n classical value calls, even with unrestricted g.
This identity avoids assuming access to the lower-degree coefficients.

## 3. Query lower bounds (all degrees)

For n≥96, let m=floor(nd/48). Greedily form an ordered sequence of m
distinct triples while maintaining each vertex degree at most d. After
t<m steps, at most floor(3t/d) vertices are saturated. Restrict to unsaturated
vertices and exclude already used triples. At least

$$
\binom{n-\lfloor3t/d\rfloor}{3}-t
$$

legal choices remain. There are ≥15n/16 unsaturated vertices, their number
minus two is ≥7n/8, and t≤n³/96. Thus this expression exceeds n³/20.
Every resulting graph has exactly m! orders because the degree constraint
is hereditary. The number M of distinguishable supports satisfies

$$
M\ge (n^3/20)^m/m!\ge(n^3/(20m))^m,\qquad
\log_2 M\ge (nd/96)\log_2(n^2/d).
$$

Here m≥nd/96 and n³/(20m)≥(48/20)n²/d. These pure cubic examples belong
to the promised class. For the linear subclass the count also works with
d≤floor((n−1)/2): exclude all triples containing any of the 3t used pairs.
The extra exclusion is at most 3t(n−2)≤n³/32, which still leaves n³/20
choices. This separately proves the linear lower bound.

A depth-q binary decision tree has at most 2^q leaves. Fix its random
coins; under a uniform support, success is ≤2^q/M. Averaging the coins,
worst-case success ≥2/3 requires q≥log₂(2M/3).

For quantum queries, denote the 2^n oracle signs by z_x. After q queries,
purified final states are sums of monomials of degree ≤q in the z_x, each
times an input-independent vector. This follows inductively by expanding
each query as a sum of z_x times input-independent projectors; between-query
operations preserve the expansion. Deferred measurement and coherent
control include adaptive protocols of worst-case length q; granting
controlled/no-op access for padding cannot weaken the resulting lower
bound. At most (2^n+1)^q monomials suffice (allow repetitions and padding
with the constant 1). All final states lie in a common subspace S of
dimension at most that number. For the POVM element P_E corresponding to
guess E and the projector Π_S, ρ_E≤Π_S. Hence average success is at most

$$
M^{-1}\sum_E\operatorname{Tr}(P_E\rho_E)
\le \dim(S)/M.
$$

Consequently q≥log₂(2M/3)/log₂(2^n+1)=Ω(d log(n²/d)).
This standard dimension/counting method bounds queries, not gate cost.

## 4. Universal masks: matching query bounds without a runtime guarantee

This section closes the query-only dense-transition gap left open in the
earlier internal report GENERAL_CUBIC_WORD_NOISE.md.

Set B=binom(n,2), s=min(2d,B). Consider every nonzero alternating binary
n-by-n matrix having at most s unordered nonzero pairs. There are
H=Σ_{j=1}^s binom(B,j) such matrices. Every difference of two possible link
matrices belongs to this set if nonzero. A nonzero alternating matrix has
rank at least two. For independent uniform a,b, conditioning on a gives
Pr[a^T L b=0]=(1+2^{-rank L})/2≤5/8.

Take k independent mask pairs. The union bound gives probability at most
H(5/8)^k that some nonzero matrix in the set is undetected by all pairs.
Thus for any k with H(5/8)^k<1 a universal separating list exists. It depends
only on n,d. The estimate Σ_{j=0}^s binom(B,j)≤(eB/s)^s follows by bounding
the sum using (1+s/B)^B (B/s)^s. This also covers s=B. Therefore
k=O(d log(n²/d)) throughout the admissible range (n²/d≥2).

A deterministic algorithm can enumerate all lists of length k until it
finds one detecting every matrix in the set, using no oracle calls. Query
the corresponding D vectors. For each i, enumerate candidate links of
size at most d on [n]\{i}, retaining the one matching all bits. The true
link is present; separation ensures uniqueness. Validate three-way
consistency and output the triples. The query cost is at most 4k; the
search and decoder are not polynomial-time algorithms in general. This
proves exact nonadaptive query existence, and finite uniform computation
without a useful runtime guarantee. By the classical simulation of D,
at most 8nk classical value queries suffice for the same method. The
lower bounds of Section 3 now prove Theorem 1. They also show why simply
exhibiting sparse random sketches is not the distinctive efficient result.

## 5. Weighted derivative sketches: efficient recovery

Choose m=max(2,ceil(log₂(n+1))), K=GF(2^m). Pick β∈K of absolute trace one,
and form the quadratic extension F=K[u]/(u²+u+β). The trace is surjective:
the trace polynomial is nonzero of degree <|K|, so some element has trace
one. The map x↦x²+x has kernel {0,1} and image the trace-zero subspace;
therefore u²+u+β is irreducible. Exhaustive modulus/trace search costs
polynomial in n as m=O(log n).

Take distinct nonzero x_j∈K for each vertex, L_j=u+x_j. Assign each unordered
pair a label and weight

$$
z_{jk}=L_j L_k=(\beta+x_jx_k)+(1+x_j+x_k)u,\quad
w_{jk}=x_j+x_k.
$$

Both are nonzero. Labels are injective on unordered distinct pairs: the
u-coordinate determines their sum, the constant determines their product,
and these determine the unordered roots of X²+(x_j+x_k)X+x_jx_k. This
property is crucial; it does not rely on pair codegree.

For t=0,...,2d−1, define moments
M_i(t)=Σ_{jk∈link(i)} w_jk z_jk^t. With A_j=x_j L_j^t and B_j=L_j^t, this is
Σ_{jk∈link(i)} (A_jB_k+A_kB_j). Let a fixed binary bilinear multiplication
algorithm in F be

$$
xy=\sum_{\ell=1}^{R} c_\ell \alpha_\ell(x)\gamma_\ell(y),
$$

where c_ℓ∈F and α_ℓ,γ_ℓ are F₂-linear forms. Form masks a_ℓ,j=α_ℓ(A_j)
and b_ℓ,j=γ_ℓ(B_j). Expanding both products gives

$$
M_i(t)=\sum_{\ell=1}^{R}c_\ell D_i(a_\ell,b_\ell).
$$

Each of 2d moments therefore uses R shared contractions, obtaining all n
link moments simultaneously. The cost is ≤8dR phase calls, and the mask
list is determined by public parameters. The essential reduction is from
sparse unknown cubic interactions to weighted univariate moment problems,
without paying separately for each vertex.

### 5.1. Bilinear plan and uniform construction

Known results provide R=O(m) over a fixed finite base field [4,5]. Bshouty
[4, Corollary 3] supplies deterministic polynomial construction in extension
degree, including the symmetric version (statement after Theorem 2).
Our proof can invoke this result as a black-box mathematical theorem. The
implementation does not port its full tester construction.

For a concrete alternative, choose k=O(log m) such that degree-k irreducibles
over F₂ have total degree at least 2m−1. Such k exists because the number
of degree-k field elements is ≥2^k−Σ_{j≤floor(k/2)}2^j. Choose
ceil((2m−1)/k) distinct moduli. Multiply polynomial residues, interpolate
by CRT, and reduce modulo the desired degree-m modulus. Input and output
maps are linear. Each residue field has a symmetric multiplication plan
of rank O(k) by [4,5]. A uniform algorithm searches subsets of the
2^k−1 nonzero linear forms by increasing cardinality and tests whether
the span of their outer-product matrices contains all multiplication
coordinate slices. If so, binary elimination gives the output weights.
A symmetric plan of rank O(k) ensures success after 2^{O(k²)} tests;
this is a proof using the established existence result, not empirical
rank extrapolation. Total rank is O(m). Preprocessing is
poly(m)2^{O((log m)²)} plus initial modulus search, hence poly(n), but
not necessarily poly(m).

Lift the plan to F by three K products:
(x+yu)(z+wu)=(xz+βyw)+((x+y)(z+w)+xz)u. Both fixed β multiplication and
coordinate maps are binary linear. Thus R=O(m). This CRT variant uses
known interpolation and symmetric-rank methods [8,9]; no independent
finite-field multiplication contribution is claimed. It is uniform but
potentially impractical. The executable unbounded exact mode implements
this strategy; finite search limits explicitly reject. Practical mixed CRT
and Karatsuba providers do not inherit its linear-rank theorem. In
particular, padded Karatsuba yields R=O(m^{log₂3}).

### 5.2. Reconstruction from moments

Fix link i of size r≤d. For r>0 the leading r-by-r Hankel matrix
H_r=(M_i(a+b))_{0≤a,b<r} factors as V diag(w)V^T, with V the square
Vandermonde on the r distinct labels. All weights are nonzero; hence H_r
is invertible. The leading d-by-d Hankel matrix has rank r since it has
the analogous d-by-r full-column-rank Vandermonde factor and its
transpose has full row rank. Thus the rank recovers r; r=0 means the
link is empty. This is an alternative elementary proof of recoverability
to the Berlekamp–Massey decoder used in code.

The monic polynomial P(Z)=∏_{jk∈link(i)}(Z+z_jk)=Z^r+Σ_{j<r}p_j Z^j
gives a recurrence Σ_{j<r}p_j M_i(t+j)=M_i(t+r). The first r such equations
have invertible coefficient matrix H_r, uniquely determining P with
the available 2d moments. Evaluate P at the O(n²) admissible pair labels
not containing i, keep the roots, and check re-encoded moments. The
true r labels are all roots; a degree-r nonzero polynomial cannot have
more. Each recovered triple must occur in all three links. This
recovers E without a discrete logarithm or exponential search over supports.

Classical cost is polynomial in n: field elements have O(log n) bits,
d=O(n²), all finite-field operations, mask formation, moment storage,
Gaussian elimination (or Berlekamp–Massey), admissible root scanning and
consistency checks use polynomially many such operations. The exact
query cost is O(d log n). Choose the smaller of its public upper bound
and balanced dense unit-pair acquisition, costing
4[binom(floor(n/2),2)+binom(ceil(n/2),2)] phase calls: any triple contains
a pair inside one of two parts. Classical simulation or ordinary Möbius
interpolation gives the stated classical efficient upper bound. For
d≤n^(2−ε), log(n²/d)≥ε log n, proving the claimed query optimality
with polynomial-time processing in this range.

## 6. Verification and conditional noise (not part of the exact theorem)

For a nonzero residual alternating trilinear form T, its radical has
codimension at least three: choose u,v,w with T(u,v,w)=1, and evaluate
against the other two to show the three classes are independent.
Outside the radical, the alternating contraction in the remaining two
arguments has rank≥2. Thus Pr[D_T(a,b)=0]≤1/8+(7/8)/4=11/32,
with equality for a single triple. For a fixed incorrect cubic candidate,
r independent fresh holdouts have false acceptance at most (11/32)^r.
Five probes suffice for failure≤0.01. Fixed reproducibility seeds are
not adversarial security; the cubic promise is essential.

With conditional full-word error probability ≤η<1/2 for every requested
mask pair and past history, repeating an ideal contraction R odd times
and taking bit majorities fails with probability at most
exp(−2R(1/2−η)²), by conditional Hoeffding on incorrect-word indicators.
A majority of correct words guarantees all bit majorities correct.
Union-bound over a public bound K on adaptive probes. The implementation
can stop early when the fixed-R majority is irreversible. It may save
queries but does not increase the mathematical guarantee. The uniform
conditional bound is an assumption, not a measured physical property.
Coherent perturbation estimates and phase-cycling experiments are
documented in docs/QUANTIZED_PHASE_FEASIBILITY.md, docs/H1_H4.md and
docs/GENERAL_CUBIC_WORD_NOISE.md. The phase cycle requires adjoint
access and did not reliably improve measured probabilities. Do not
promote these conditions to general hardware robustness.

## 7. Evidence and negative results

All counts below are selected, previously executed synthetic experiments,
not statistically representative hardware trials. The two main ideal
benchmarks have different instances and verification policies; do not
combine their counts as a single independent sample. Exact CRT construction
is tested at small degrees only; finite-size practical plan selection is
not evidence of asymptotic constants.

| n,d | weighted practical | archived v0.5 / Karatsuba | reference | balanced dense |
|---|---:|---:|---:|---:|
| 8,3 | 436 | 436 | 400 | 48 |
| 16,4 | 1004 | 1040 | 1920 | 224 |
| 32,4 | 1272 | 1316 | 1896 | 960 |
| 32,8 | 2700 | 2960 | 5148 | 960 |
| 64,2 | 664 | 664 | 1148 | 3968 |
| 8,21 | 3168 | 3168 | 748 | 48 |

Table 1: 18 generated instances, 117 method observations, all reconstructed.
Acquisition medians exclude holdout. Reference receives true codegree as
a bound; the weighted algorithm does not need it. Dense wins five of six
configurations. Exact CRT had worse acquisition counts than practical
selection in all three configurations where compared. Raw data and
source: evidence/2026-11-26/rank-provider-local.zip, PR #35 and run
45756400085. See docs/RANK_PROVIDER.md for setup and caveats.

The independent-order benchmark (50 instances, 230 method observations)
reproduced all explicit scientific fields in reverse order. In a distinct
linear n=64,d=4 configuration, median QCDT/dense-certified phase calls
including holdout were 264/4008; at n=32,d=4 with codegree bound 3 the
counts were 2668/1000. Source: run 45749367190, immutable artifact archive
in evidence/2026-11-26. These are logical phase calls, not runtime or
two-qubit gates. The earlier deterministic linear decoder remains a useful
alternative, not needed for the general theorem.

| Perturbed diagonal phase scale | QCDT exact | dense exact | one-bit exact |
|---|---:|---:|---:|
| 0 | 24/24 | 24/24 | 24/24 |
| 0.1 rad | 24/24 | 24/24 | 24/24 |
| 0.25 rad | 24/24 | 24/24 | 24/24 |
| 0.5 rad | 15/24 | 16/24 | 21/24 |

Table 2: 288 exact-probability sampled method observations, three fixed
fixtures, common phase oracle, public 4096-call cap, same five holdouts;
no wrong accepted observed, remaining rejected. Actual consumption varies.
Not gate noise, readout, or real hardware. Source run 45754890684 and
general-word-noise-local.zip.

In the corrected historical-device-snapshot benchmark, QCDT had 4/18
exact and 14 rejected; dense-certified had 11/18 exact and 7 rejected.
No incorrect acceptance was observed in this finite sample. Total shots
8130/27655 differ, although the public cap was equal. Synthetic oracle
gates were visible to the compiler; boundary controls preserve semantics,
not opacity. Small fixtures showed greater two-qubit gate cost for QCDT.
Original hidden-truth-dependent shot allocation was superseded, not erased.
Source run 45748250183, docs/PRE_HARDWARE_AUDIT.md. No QPU was executed.

## 8. Access models, limitations and conclusion

A phase oracle on a basis state alone does not reveal f(x). Interference
of |0⟩ and |x⟩ obtains f(x)+f(0) with one coherent call; this provides
a matched-access single-bit evaluation, not purely classical hardware.
Conversely one standard coherent binary value query can implement a phase
query by kickback. State copies alone do not permit arbitrary shifted
coherent calls to U_f. Real Fourier sparsity, total F₂ monomial sparsity,
and bounded cubic incidence are different promises. Equivalence-query
learning has an additional counterexample oracle. CUT/OR hypergraph
oracles are not the parity-of-contained-edges oracle considered here.

The ideal result may be useful when repeated opaque coherent access to
a sign-valued cubic evolution is justified. Known synthetic gate lists
are classically readable; they test implementation feasibility only.
Fixed-time diagonal evolutions with integer multiples of π have a
restricted Boolean interpretation, and continuous Hamiltonian coefficients
are not identifiable from parity alone. No actual opaque physical access,
cost advantage, general hardware noise tolerance, or commercial application
is established.

We recommend independent assessment of (i) the weighted shared-moment
reduction and its proof dependencies, (ii) priority relative to quantum
polynomial learning, graph parity learning and sparse interpolation, and
(iii) the separation between query-only and efficient algorithms.
Theorem statements are internal proof candidates; finite tests are not
proofs, and no reviewer has yet endorsed them. The full-range query theorem
does not establish efficient recovery near dense-transition degrees.
The paper should not be submitted until the authors approve the text,
the evidence and citations are checked, and external feedback is sought.

## References

[1] A. Montanaro, The quantum query complexity of learning multilinear
polynomials, Information Processing Letters (2012).
https://doi.org/10.1016/j.ipl.2012.03.002 — https://arxiv.org/abs/1105.3310

[2] A. Montanaro and C. Shao, Quantum algorithms for learning a hidden
graph, TQC 2022. https://doi.org/10.4230/LIPIcs.TQC.2022.1 —
https://arxiv.org/abs/2011.08611

[3] S. Arunachalam et al., Optimal algorithms for learning quantum phase
states, TQC 2023. https://doi.org/10.4230/LIPIcs.TQC.2023.3 —
https://arxiv.org/abs/2208.07851

[4] N. H. Bshouty, Multilinear complexity is equivalent to optimal tester
size, ECCC TR13-011 (2013), Corollary 3 and paragraph after Theorem 2.
https://eccc.weizmann.ac.il/report/2013/011/

[5] S. Ballet et al., On the tensor rank of multiplication in finite
extensions of finite fields (survey). https://doi.org/10.1070/RM9928

[6] M. Ben-Or and P. Tiwari, A deterministic algorithm for sparse
multivariate polynomial interpolation, STOC 1988.
https://doi.org/10.1145/62212.62241

[7] R. M. Roth and G. M. Benedek, Interpolation and approximation of
sparse multivariate polynomials over GF(2).
https://doi.org/10.1137/0220019

[8] S. Ballet, A. Bonnecaze and B. Pacifico, recursive projective-line
multiplication construction. https://arxiv.org/abs/2007.16082

[9] G. Cotardo and F. Zullo, preprint on symmetric multiplication rank
(2026), Proposition 2.7 and Table 1. https://arxiv.org/abs/2605.12295

[10] R. E. Schapire and L. M. Sellie, Learning sparse multivariate
polynomials over a field with queries and counterexamples, JCSS (1996).
https://doi.org/10.1006/jcss.1996.0017

See LITERATURE_REVIEW.md for comparison and source-check coverage.
