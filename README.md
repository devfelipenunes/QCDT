# QCDT — Quantum Coded Derivative Tomography

Experimental research into sparse cubic Boolean phase-oracle reconstruction.
**Research candidate, not a peer-reviewed discovery.** Novelty, physical quantum
advantage and general noise robustness are not established.

## Implementations and reproducibility

- Ideal reference: BCH, projection/colouring and asymmetric recovery.
- Known-support refinement: codegree-one recovery using local linear systems.
- Legacy adapters: verified historical v0.4, v0.5, v0.8 and simplex acquisition.
- Exact truth-table and Qiskit backends; Aer shot and historical device snapshots.
- Ten original archives under historical/archives, with integrity manifest and
  complete historical replay workflow. All 94 Python occurrences executed in
  the historical replay; module smoke checks and output discrepancies are
  recorded separately from scientific correctness.

## Run (Python 3.13)

```bash
python -m unittest discover -s tests -v
python -m pip install -r requirements-historical.txt
python -m unittest discover -s tests -v
python scripts/verify_archives.py historical/archives
```

Without optional dependencies, simulator and legacy tests may be skipped.
See CI for actual executed checks.

```python
from qcdt import recover, contract
hidden = {(0, 1, 2), (3, 4, 5)}
# Algebraic contraction backend: not a quantum execution.
result = recover(6, 1, 1, lambda a,b: contract(hidden,a,b), seed=42)
print(result)
```

The learner receives only a probe callback. For an exact cubic Boolean phase
oracle, each probe corresponds to four coherent calls and a Bernstein–Vazirani
measurement. The reference recovers cubic coefficients, not original gate order,
global phase or arbitrary quantum circuits. The ideal holdout is probabilistic
under explicit assumptions. A public gate list makes the problem trivial
classically; synthesized benchmarks do not establish physical advantage.

## Scientific status

See [model](docs/MODEL.md), [pre-hardware audit](docs/PRE_HARDWARE_AUDIT.md),
[prior-art decision](docs/PRIOR_ART_DECISION.md), [historical adapters](docs/LEGACY_ADAPTERS.md),
[roadmap](docs/ROADMAP.md) and [archive manifest](docs/ARCHIVES.sha256).
The audited matched-cap benchmark uses only public promise parameters for
planning and applies holdout to both quantum methods. Historical snapshot
results remain available with their methodological limitations.

No physical QPU has been used. Publication requires independent review.
