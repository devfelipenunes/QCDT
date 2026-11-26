# Quantized diagonal evolution: a physical hypothesis, not a validated application

Refs #21 and #7. Do not claim a general Hamiltonian-learning result.
Let P_i=(I-Z_i)/2 and let a device repeatedly implement the unknown
diagonal evolution at a known time T, with hbar=1,

    H = (pi/T) sum_S c_S prod_{i in S} P_i, c_S integers, |S|<=3.

Then exp(-iHT)|x> = (-1)^{sum_S c_S prod x_i}|x>.
QCDT can recover the parity of the cubic coefficients under its degree
and codegree promises. It cannot recover the integer coefficients, T,
or the Hamiltonian itself from one evolution time. Adding 2pi/T to
any coefficient leaves the unitary unchanged. The structure of a
generic real-valued Hamiltonian is not identifiable by this reduction.
The commuting projectors are a mathematical model; no experimental
device with opaque unknown quantized interactions has been identified.

## Coherent phase mismatch

Suppose the actual fixed-time diagonal unitary V has distance
epsilon=||V-U_f||_op from the ideal sign oracle (a fixed global phase
can also be removed). A derivative circuit uses four calls. Replacing
them one at a time and applying the triangle inequality, all other
operations unitary, gives output state distance <=4 epsilon.
Projection onto the complement of the correct ideal BV word therefore
has squared norm <=min(1,16 epsilon^2). This holds even with coherent
repeatable errors, not merely independent BSC readout. It is a
conservative one-probe bound. If epsilon<1/(4 sqrt(2)), the bound is
strictly below 1/2. Independent executions under a stationary unitary
could then be amplified by majority, but this does not give a general
hardware noise guarantee, especially with correlated executions,
calibration drift, or unknown epsilon. For term phase deviations
delta_S, epsilon<=sum_S |delta_S|, which can scale poorly with size.

Test predeclared configurations: one edge at n=4 and Pasch at n=6,
plus one linear and one quadratic term each; seven offset scales from
0 to 0.5 radians; 60 seeded mask pairs per fixture reused at each scale.
Compute exact probabilities by a complex Walsh transform of the four
shifted phases, compare with the ideal contraction, and check the bound.
This is 840 observations, not 840 independent randomly sampled physical
instances. Offsets are drawn once per fixture/scale. No gate noise,
readout, synthesis, coupling, or hardware experiment is modeled here.
A negative control confirms phase aliases and failure at strong offsets.
Keep all outcomes. Reproduce via
python -m benchmarks.phase_feasibility --output evidence/phase/results.json.

## Relevance to the research direction

General Hamiltonian learning is established and covers broader access
models; see Practical Hamiltonian learning with unitary dynamics and
Gibbs states (2024), https://doi.org/10.1038/s41467-023-44008-1;
Learning the structure of any Hamiltonian from minimal assumptions
(STOC 2025), https://doi.org/10.1145/3717823.3718115;
Testing and learning structured quantum Hamiltonians,
https://arxiv.org/abs/2411.00082.
A possible niche is recovery of Boolean/quantized cubic phase support
when an opaque repeatable evolution is available. A known gate list
is only a synthetic feasibility control. No superiority to general
Hamiltonian learners, hardware resource improvement, or commercial
application is established. Keep issue #21 open until a physical
access model, calibration, costs and authorization are demonstrated.

## Important query-complexity scope

Even without codegree one, a brute-force link decoder can achieve
O(d log n + log(1/delta)) ideal probes by uniform random contractions:
for each vertex there are at most (1+binom(n-1,2))^d possible links;
two distinct links differ by a nonzero alternating matrix of rank >=2.
For uniform a,b the probability of a matching bit is <=5/8.
Union-bound over alternative links and vertices, then exhaustively
search each link and check symmetry. This is the earlier random-sketch
construction, with n^O(d) classical decoding rather than efficient
runtime in d. Thus the new tight linear result should emphasize
efficient classical decoding at the optimal query scale, not imply
that O(d log n) query complexity alone requires codegree one.
Novelty remains a question for independent review.
