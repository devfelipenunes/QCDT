# Pre-hardware technical and scientific audit

Audited baseline: main at 14a2acb78c81f1dff5703d257865dcf0683239d4.
Date: 2026-11-26 BRT. Internal audit, not independent peer review.
Ten prior PRs merged. Issues #2–#4 closed for engineering, scoped positioning
and simulator delivery respectively, not universal reproducibility or novelty.
The audit deliberately separates theorem assumptions, empirical evidence,
software correctness, and readiness to submit jobs or a manuscript.

## Evidence and scope

- Repository tree and ten archive hashes inspected; all ten original ZIPs
  passed SHA-256 and CRC verification locally. Eight locally available core
  Python file blob hashes matched main. Other files were reviewed through
  GitHub. The earlier full historical replay covers 94 occurrences, including
  10 module smoke checks; process success is not proof of every printed claim.
- Main workflow run 45747590348 passed both jobs. Partial local checkout
  ran 17 methods: 14 passed and 3 optional Qiskit tests skipped. External
  CI is the simulator evidence.
- New independent fixtures: 162 random hypergraphs (n=3–32) with supplied
  bounds sometimes larger than actual degree/codegree; all reconstructed,
  with callback count checked in regression tests. 5,101 exhaustive BCH
  sparse-vector decodes (n=3–9, all k from 1 to n), all correct.
- Rechecked degree-four counterexample: the monomial x0*x1*x2*x3 has
  210 non-affine second derivatives out of 256 mask pairs; 46 affine.
  Consequently a successful affine test is not a certificate of degree <=3.
- Prior-art sources rechecked: Montanaro 2012 (arXiv:1105.3310);
  Montanaro–Shao (arXiv:2011.08611), Theorem 15 is a graph-state-copy
  result and Lemma 16 gives adjacency-vector multiplication with two
  coherent parity calls; Arunachalam et al. (arXiv:2208.07851) is a
  phase-state-copy problem, including sparse diagonal circuits. Different
  models must not be treated as equal sample budgets.

## Claim matrix

| Claim | Disposition |
|---|---|
| Four-call second derivative followed by BV identifies all cubic contractions | Valid under exact repeatable Boolean phase oracle, degree <=3; known primitive |
| BCH recovery from odd moments | Valid under sparsity promise, independently tested; polynomial scan over admissible labels, not constant CPU |
| Asymmetric BCH recovery O(d lambda log^2 n) | Candidate query bound follows from row weights <=2d and <=lambda; ideal only |
| Linear projection/colouring O(d log n log(d+1)) | Valid internal derivation under codegree one; no extrapolation to overlapping pairs |
| Known-support refinement O(d log n) | Internal bound under codegree one; classical expected-polynomial label selection under randomized labels, not deterministic runtime. Theorem 15 is an antecedent, not our theorem |
| Quantum Omega(log n) for fixed d | Counting/dimension lower bound using disjoint triples; equivalent coherent value oracle provides phase kickback. Not a physical speedup |
| Variable-d lower bound from round 6 | Constructed family has pair codegree d (A_a,C_a reused); cannot claim it proves tightness for all increasing-d linear hypergraphs |
| Ideal holdout false accept <=(5/8)^r | Correct for fixed wrong cubic candidate and independent uniform masks; fixed public reproducibility seeds are not adversarial security |
| v0.8/outer simplex noisy guarantees | Conditional on specified stationary independent BSC; not arbitrary gate noise or systematic errors |
| General full circuit tomography | Not established. Current reference returns cubic coefficients, not Z/CZ terms, original ordering, phase, arbitrary unitaries |
| Physical advantage, novelty, blockchain utility | Not established |

## Findings, ordered by risk

**A1 high — hidden-truth-dependent shot allocation.** The previous
benchmarks/snapshot.py calls an ideal truth-table oracle to learn how many
adaptive probes QCDT will use and allocates shots accordingly. This is
not available free in a real black-box experiment. Concrete counterexample:
two linear graphs at n=6,d=2,lambda=1, with 2 versus 4 edges (Pasch), use
17 versus 23 probes including holdout. Prior cap 2048 gives 119 versus 89
odd shots per probe from hidden-dependent plans. The old numbers remain
historical; they cannot establish fair end-to-end superiority.

Correction: qcdt/budget.py derives conservative upper bounds from public
n,d,lambda and holdout count only. For codegree 1, let B=min(n,2d)*m,
Delta=min(n-1,2d), c=ceil(log2(min(n,Delta^2+1))). Bound B(1+c)+r probes.
For general codegree, B*min(n,lambda)*m+r. Balanced dense count is
binom(floor(n/2),2)+binom(ceil(n/2),2)+r. Both methods receive the same
promise and holdout policy, with odd shots from cap/bound, no oracle
planning. Unused budget is reported, not silently redistributed.
This is a matched-cap comparison, not necessarily matched consumed shots.
New snapshot_audited benchmark retains old snapshot.py and raw outcomes.

**A2 high — physical access and resource interpretation.** Synthesized
Z/CZ/CCZ oracles are transparent to the transpiler, which may cancel or
reorder gates across query boundaries. Gate counts are valid for the
compiled synthetic circuit, not evidence of an opaque oracle cost.
An exposed gate list is classically trivial to read; a QPU pilot tests
feasibility rather than quantum advantage. Define what oracle access
means, preserve boundaries where relevant, account for synthesis,
routing, reset, shots and classical decoding, and compare certified dense
and classical baselines before any hardware efficiency claim.

**A3 high — real noise.** Previous snapshots: QCDT 5/15 exact, 10 rejected,
0 wrong; dense 9/15 exact, 6 wrong. These reused fixtures with three seeds,
not independent randomly sampled circuits, and dense lacked holdout.
Zero observed errors is not a zero error rate. Snapshot properties are
historical, not today's calibration. Strong coherent errors and adversarial
mask-dependent corruption already refuted general robustness. Do not
select favourable seeds or discard rejected instances.

**A4 high — novelty and bounds.** Keep the scoped M14 decision: a
candidate refinement/empirical study, not a new fundamental primitive.
The fixed-degree separation is in query complexity only. Independent
proof review, systematic citation tracing and publication decision remain
open. No blockchain application is validated.

**A5 high — historical reproducibility.** Issue #17's apparent stochastic
regression has a reproduced explanation. The global Random(20261126) in
round8 scientific_tests.py is consumed by independent_full() before compare()
when running the default script. Local isolated invocation
python scientific_tests.py compare reproduced all original raw correctness
and query fields (excluding time). Local sequential invocation
python scientific_tests.py independent_full compare reproduced all
corresponding fields of external CI 45747105653. n=9,d=2 v0.1 20/20 vs
19/20; n=128,d=2 classical 7777 vs 7858 median value calls. Neither sample
is fabricated or discarded; they are distinct seeded streams. Eight other
JSON discrepancies were filename collisions by older scripts, three were
resource-only; prior evidence retained. Use independent per-case RNG
streams, instance hashes, explicit argv and schemas for scientific fields.
The new scripts/audit_round8.py recreates both paths in disposable dirs.
The publication-grade multi-seed and namespace audit still belongs to #17.

**A6 medium — reproducibility and repository governance.** Main is not
protected (GitHub branch metadata protected=false); green CI was checked
by workflow convention, not enforced repository rule. Direct pushes remain
possible. No LICENSE or packaging metadata in the audited tree. Historical
data are intact, but workflow artifacts can expire; pin transitive versions
and action SHAs, record platform/CPU and checksums, preserve compact evidence
in Git, and decide license with owner. Do not change branch permissions or
license without approval. README/roadmap updated to remove stale first-PR status.

**A7 medium — scope and API.** This is a research library, not a supported
SDK. No release policy, typed backend protocol, maximum input/budget policy
or independent installation CI. Legacy worker is process isolation, not a
security sandbox; run only verified trusted archives. Seeded fixed masks
and synthetic inputs cannot establish adversarial certification. Test
missing/invalid bounds, timeouts, repeated seeds and archive integrity;
do not promise arbitrary n or arbitrary noise.

## Gate decision

GO: further simulator experiments with public shot planning, reproducible
ideal-oracle research, manuscript outline and external reviewer request.
NO-GO: claim of novelty, physical advantage, general noise tolerance,
production integration, or publication based on unreviewed historical
numbers. Hardware pilot may be prepared, not submitted until #5 defines
a credible access model, budget, live calibration and predeclared success/
rejection metrics. Maintain #17 for publication-grade audit and separate
readiness follow-up for engineering. A passing internal audit is not peer review.
