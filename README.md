# QCDT — Quantum Coded Derivative Tomography

Experimental research into reconstruction of sparse cubic Boolean phase oracles.
**Research candidate, not a peer-reviewed discovery.** Novelty, physical quantum
advantage and general noise robustness are not established.

This first consolidation PR freezes a readable ideal-oracle reference
implementation of the round-12 v0.10 construction (linear projection and coloring,
plus asymmetric BCH recovery for general codegree). It is not a byte-for-byte
import of the twelve historical rounds. The coded acquisition, noisy recovery
and historical comparators still require migration. Root decoding uses a scan
over admissible labels instead of the earlier trace-factorization routine.

## Run (Python 3.13)

```bash
python -m unittest discover -s tests -v
```

No third-party packages are required for the reference tests. Optional Qiskit
validation uses the circuit adapter and the separate CI job.

```python
from qcdt import recover, contract
hidden = {(0, 1, 2), (3, 4, 5)}
# Algebraic contraction backend: not a quantum execution.
result = recover(6, 1, 1, lambda a,b: contract(hidden,a,b), seed=42)
print(result)
```

The learner receives only a probe callback. For a cubic phase oracle, each
probe corresponds to four coherent oracle calls and a Bernstein–Vazirani
measurement. The reference also contains an independent truth-table Fourier
backend and an optional Qiskit circuit backend. It reconstructs cubic terms,
not the original gate ordering or global phase.

## Scientific status

- Reference tests: exhaustive small hypergraphs, Pasch ambiguity, all 256
  mask pairs for a mixed-degree polynomial, a quartic counterexample, and
  algebraic scaling.
- Separate acquisition and verification query counters.
- Ideal model only in the reference API; out-of-promise recovery is not certified
  universally. The independent holdout is probabilistic.
- Local execution: Python 3.13.5, 6 test methods passed, 1 optional Qiskit method
  skipped. CI and hardware execution must be verified separately.
- See [specification](docs/MODEL.md), [roadmap](docs/ROADMAP.md) and
  [historical archive manifest](docs/ARCHIVES.sha256).
