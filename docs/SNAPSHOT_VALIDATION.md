# M15: historical calibration snapshot validation protocol

Predefined before the benchmark run. The optional IBM Runtime dependency
is pinned to 0.43.1, in addition to Qiskit 2.2.3 and Aer 0.17.2.
Use FakeManilaV2 (5 qubits) and FakeLagosV2 (7 qubits), with historical
IBM device calibration snapshots packaged by IBM. AerSimulator.from_backend
constructs local noise models from these properties. No IBM service
credentials, live calibration, job submission, or QPU are used.
Sources: https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/0.43/fake-provider
and https://quantum.cloud.ibm.com/docs/en/guides/local-simulators.
Snapshot noise is an approximation to historical hardware behavior, not
a prediction of its current performance.

Five device/fixture combinations: single cubic edge (4 qubits) and
overlap (5) on both; Pasch (6) on Lagos only. All include linear/quadratic
terms. Three fixed shot-sampling seeds for each method. The same total
shot cap 2048 per method and trial; derive odd per-circuit shots from
the ideal truth-table plan, enforce the cap in the noisy execution.
Actual consumed shots may differ due to rounding and rejection. QCDT
includes ten holdout checks, dense comparator has no holdout. No tuning
of the budget or seeds after observing results. Compare exact, wrong
and rejected separately; retain rejection reason, raw counts, layout,
depth, two-qubit gate count, total shots and logical phase calls.
Archive backend gate parameters, coupling, qubit relaxation values,
calibration properties when exposed, and dependency versions.
Repeated seeds on a fixed fixture are not independent random circuits.

Acceptance for simulator stage: exact ideal statevector/FWHT and routed
layout checks, reproducible CI logs and raw simulator artifacts. A noisy
failure is a valid scientific outcome rather than CI failure. Hardware
and live calibration validation belong to issue #5, not this gate.
Independent review, claims of practical advantage and robustness remain
out of scope. Historical noisy decoder migration is tracked in #2.

Run:
```sh
python -m pip install -r requirements-qiskit.txt
python -m unittest discover -s tests -v
python -m benchmarks.known_support
python -m benchmarks.snapshot
```
