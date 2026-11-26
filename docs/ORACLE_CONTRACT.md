# Hardware-readiness contract (issue #21)

The learner's mathematical access is to the same coherent, repeatable
unitary U_f |x> = (-1)^f(x)|x>, with f a Boolean cubic polynomial.
A probe consumes four calls. Bounds n,d,codegree are public upper bounds.
The learner cannot inspect f, a circuit gate list, coefficients, or an
ideal answer for shot planning. Measurement results can be noisy.
An actual device implementation would additionally require a defensible
way to invoke U_f coherently at each boundary. Reset, control, routing,
oracle synthesis/access, acquisition, holdout and classical decoding must
be counted. If the source gate list is available, reading its cubic terms
classically is trivial; no practical quantum advantage can follow from
this synthetic characterization alone.

## Controls fixed before execution

Compare ordinary fully transpiled derivative circuits with barriers on
all logical wires immediately before and after each of the four oracle
calls. Barriers are compiler directives, not security or hardware black-box
enforcement. A barrier does not prove the implementation opaque, and the
oracle is still expanded and routed. Both controls implement the same
ideal unitary. No extra oracle calls are implied by barriers.

Three fixtures: single (4 qubits), overlapping (5), Pasch (6); public
promises as in audited snapshot experiment. Manila/Lagos historical
snapshots, ideal sampled circuits and two fixed noise seeds; QCDT and
balanced dense both independently checked using ten holdout probes.
Use public circuit caps and odd shots from cap 2048; ideal uses one shot.
Report actual calls, shots, native two-qubit gates, layout, depth,
rejections/wrong answers, host oracle construction, compilation, simulation
and residual host processing times. The last quantity includes Python
overhead and is NOT isolated decoding time. All time measurements are
local simulator host measurements, not QPU wall-clock. Compare resource
counts for ideal runs (same acquired masks); noisy adaptive paths may
differ. Historical calibration is approximate and not current.

## Real execution gate

Before #5, a proposed pilot must specify device availability, live
calibration, coherent call/access implementation, hardware budget,
shot/circuit cap, independently seeded validation, and permission for
execution. Record job IDs, timestamps, compiled circuits, layout and raw
counts. Use both full and boundary-preserved controls if available.
No submission or live credentials used here. Actual oracle access and
cost, device-specific timing, and superiority remain unknown. This closes
only the synthetic control portion of hardware readiness.
