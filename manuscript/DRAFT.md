# Sparse cubic phase-oracle reconstruction by derivative sketching

**Working manuscript — internal review only.** Author list and affiliations
not assigned. No submission, peer review, or claim of priority.

## Abstract

We study recovery of the cubic support of an unknown Boolean polynomial
from coherent phase-oracle access, under bounded vertex degree and pair
codegree one. Combining finite-difference Bernstein–Vazirani measurements,
binary sparse row sketches, projection constraints and known-support
linear systems yields an O(d log n) ideal query bound. A greedy counting
argument combined with a quantum final-state dimension bound gives a
candidate matching lower bound throughout the admissible degree range.
Classical binary value queries require Omega(nd log n), and a sparse
third-derivative algorithm attains the corresponding order at bounded
error. We distinguish query complexity from hardware resources and
report negative results under historical device-snapshot noise. All
claims remain subject to independent review and prior-art clearance.

## 1. Model and contribution

Recover cubic coefficients, not lower-degree coefficients, original
gate ordering or global phase. See docs/LINEAR_QUERY_COMPLEXITY.md for
the complete candidate theorem and proof; docs/MODEL.md for the broader
oracle model. The specific review target is the matching complexity
on the linear bounded-degree class. The finite-difference primitive,
BCH decoding, known-support graph learning, and counting methods are
known techniques. Do not present their combination as automatically novel.

## 2. Related work

Montanaro (2012), The quantum query complexity of learning multilinear
polynomials, https://arxiv.org/abs/1105.3310.
Montanaro and Shao (2022), Quantum algorithms for learning a hidden graph,
https://doi.org/10.4230/LIPIcs.TQC.2022.1.
Arunachalam et al. (2023), Optimal algorithms for learning quantum phase
states, https://doi.org/10.4230/LIPIcs.TQC.2023.3.
See docs/PRIOR_ART.md and docs/PRIOR_ART_DECISION.md for access-model
distinctions and prior-art caveats. Systematic forward/backward citation
review and a search for the exact linear cubic promise are outstanding.

## 3. Methods and evidence

The implementation uses the reference and known-support decoders,
certified balanced dense baseline, label-bit baseline, and classical
sparse comparator. Fifty generated instances (five public configurations,
ten seeds) give 230 method observations, all correct; reverse-order
execution agrees on explicit scientific fields. These are synthetic ideal
contractions, not 230 independent hardware trials. Median phase queries
including holdout at n=64,d=4,codegree=1: 264 QCDT, 4008 dense.
For n=32,d=4,codegree bound 3: 2668 QCDT, 1000 dense. The latter is
outside the linear theorem and is retained as a negative comparator.
Raw evidence is stored in evidence/2026-11-26, run 45749367190.

The corrected historical-device benchmark (run 45748250183) used public
shot caps and certification in both algorithms: QCDT 4/18 exact and
14 rejected; dense 11/18 exact and 7 rejected; zero wrong observed in
both. Actual shots 8130 versus 27655, not equal consumption. The
compiler-boundary controls (run 45749584325) recovered all 12 ideal
cases; noisy QCDT full/boundary 2/6 exact each, dense full 4/6 and
boundary 3/6. Ideal two-qubit gate totals are greater for QCDT than
dense in these small fixtures. Historical snapshots are not live QPU
calibrations. No physical speedup or general robustness is established.

## 4. Limitations and review questions

1. Is the greedy family-count argument uniform in d, and are all
   counted tensors linear? Is the final-state-span argument sound for
   adaptive controlled oracle access?
2. Does existing literature imply the exact Theta(d log n) result
   for this promise, or a stronger result? Check the models explicitly.
3. Does the known-support decoder require any hidden information?
   Are expected classical runtime and deterministic query bounds separate?
4. Can a physically defensible coherent access model be identified?
   A transparent synthesized gate list is not such evidence.
5. Do all experimental figures retain negative results and use the
   correct denominator and access model?

## 5. Disposition

Request independent mathematical and literature review before deciding
on a preprint. No reviewer has been contacted and no endorsement is
claimed. Hardware is a separate feasibility gate (#5/#21). Prepare
only a synthetic validation pilot if no opaque physical oracle is
available, with explicit cost accounting and no advantage claim.
A useful physical candidate is a commuting three-local diagonal
Hamiltonian with unknown quantized phases at a known evolution time;
this is a hypothesis, not a demonstrated application, and generic
continuous phases violate the current Boolean sign model.
