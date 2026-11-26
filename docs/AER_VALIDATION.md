# Routed Aer end-to-end validation

This extends the ideal derivative and isolated readout tests with full
reconstruction from sampled measurements. Optional AerProbe transpires
the actual derivative circuit to rz/sx/x/cx on a bidirectional line
coupling map. Every requested shot is counted as four logical phase-oracle
calls; CNOT executions count the compiled CNOT gates times shots, including
routing. A transpiled circuit is cached, never a noisy measured result.
Classical processing and transpilation time are not quantum execution time.

The benchmark covers one cubic edge (4 qubits), overlapping edges (5),
and Pasch ambiguity (6), with lower-degree terms in all oracles. Both
QCDT (including holdout) and the balanced dense comparator receive the
same per-circuit shot budget, not necessarily the same total budget.
Noise conditions: ideal, 10% independent readout, mild synthetic gate
depolarization (1q .001, 2q .005, readout .02), and stronger synthetic
depolarization (1q .005, 2q .02, readout .05). These are not fitted to
any physical device. Seeded exploratory runs are not population estimates.
Wrong accepted, rejected and exact reconstructions must remain separate.
No guarantee for gate noise follows from the independent BSC analysis.

Reproduce in Python 3.13 with pinned Qiskit/Aer:
```sh
python -m pip install -r requirements-qiskit.txt
python -m unittest discover -s tests -v
python -m benchmarks.aer_recovery
```
CI stores aer-recovery.json alongside environment and resource artifacts.
Do not infer a speedup or calibrated hardware fidelity. Actual device
calibration, larger independent samples, statistical intervals, and
migration of the historical simplex/noisy decoders remain open.
