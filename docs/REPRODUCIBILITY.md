# Engineering and evidence protocol (issue #20)

Two environment snapshots are captured from actual CI artifacts: simulator
run 45749367190 (NumPy 2.5.5/SciPy 1.18.1) and historical round-8 run
45747105653 (NumPy 2.3.5/SciPy 1.17.0). Full pip-freeze package versions
are recorded in the corresponding lock files. CI fixes Python 3.13.18 and
the checkout/setup/upload action commit SHAs, verifies installed versions
and runs pip check. These are version locks, not hashed wheel/container
locks. Ubuntu runner images and system libraries can still drift; record
image ID, platform, environment and source commit for each run.

The full simulator job rejects any skipped tests; the lightweight reference
job deliberately permits optional skips. Check the full job before merge.
Artifact manifests hash exact result files and record source/run metadata.
The permanent compact summary and two original CI ZIP artifacts in
evidence/2026-11-26 record verified results, raw data and hashes. GitHub
artifacts can expire: archive future manuscript evidence in the same way.
The dedicated oracle-control workflow also uses the simulator lock and
strict test runner.
The original ten ZIP archives already live in Git unchanged.

Run in a clean Python 3.13.18 environment:
```sh
python -m pip install -r requirements-simulator.lock.txt
python -m pip check
python -m scripts.check_environment requirements-simulator.lock.txt --output environment.json
python -m scripts.strict_suite
python -m benchmarks.independent --output evidence/independent/results.json --reverse-check
```

## API and release policy

qcdt.api.Probe and recover_bounded provide an opt-in typed interface
with public n/degree/query limits and callback checks. Conservative preflight
may reject a problem that an unbounded adaptive run could solve. These
are logical limits, not a guarantee on CPU time, physical shots or callback
implementation. Existing experimental APIs remain unchanged.

No stable public release, production deployment, package publication or
hardware claim without independent review. Proposed future version tags:
research-only prereleases with exact source hash, frozen protocol, tests,
known failures and backward-compatibility statement. Repository presently
has no license decision; recommend discussing MIT for code or Apache-2.0
if explicit patent grant is desired, and a separate data license if needed.
Do not apply a license without owner decision or review of historical assets.

Propose protecting main with mandatory Research CI reference and qiskit-aer
checks, no force pushes/deletions, and PR requirement. Do not enable a
mandatory independent review that would block the user's intended workflow
without agreeing on reviewer availability. No protection setting or
permission has been changed. The existing PR-to-main convention remains.
