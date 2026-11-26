# Historical reproduction — selected battery

Original archive bytes are identified by the ten SHA-256 entries in
ARCHIVES.sha256. The combined ZIP remains external to this repository:
the local execution environment cannot resolve github.com and the GitHub
connector accepts text or explicit encoded blobs, not local file paths.
This PR does not claim full binary migration. Retain the original ZIPs.

Run from the repository root with trusted archives and Python 3.13.5,
NumPy 2.3.5, SciPy 1.17.0:

```sh
python scripts/verify_archives.py /path/to/QCDT_historical_archives.zip
python -m scripts.replay_history /path/to/QCDT_historical_archives.zip --output replay-output --timeout 120
```

The replay driver verifies hashes/CRC, extracts per job into disposable
directories, records stdout/stderr, status and log hashes. It does not
extract or alter original files in the repository. Execute only the trusted
archive versions. It does not test arbitrary malicious archives.

## Actual local reproduction, 2026-11-25 (BRT)

Executed the original archived scripts with fixed seeds, Python 3.13.5,
NumPy 2.3.5 and SciPy 1.17.0, single-threaded BLAS. Initial eight-worker
run used a 12-second per-script budget: 10 passed, four timed out.
Four-worker retry with a 45-second budget: all four passed.
All fourteen selected entrypoints completed successfully. This was a local
parallel replay of extracted archives before the reusable driver was added;
not a new independent statistical sample and not a full historical replay.

| Archive | Entrypoint | Evidence |
|---|---|---|
| bundle | qcdt.py | 50/50 recoveries, 112 phase calls/trial |
| round4 | validation.py | 7776 collision checks, MILP and differential benchmarks |
| round5 | graph_validation.py | 320 synthetic agreements, 2046 OR restrictions |
| round6 | lower_bound.py | 1830 distinct enumerated hypergraphs |
| round6 | graph_dynamic.py | 50000 updates, 12200 scans, 200 pair checks |
| round7 | run_circuit.py | circuit and Pauli-noise reproduction |
| round7 | crt.py | 505 basis products and 6 recoveries; retry |
| round8 | structural_tests.py | 26624 derivative identities, 200 channel checks |
| round9 | certification.py | certification and conservative-bound cases |
| round9 | crosscheck.py | 960 probes, 6 end-to-end |
| round10 | noise_audit.py | 540 calibrated pairs; 100 adversarial false accepts; retry |
| round11 | audit.py | paired budgets, 192 explicit probes; retry |
| round12 | audit.py | 1024 + 271 exhaustive graphs, 324 probes, 16 circuits, 27 scale observations, 85 rejections; retry |
| round12 | outer_code.py | 2667 code distances, 64/64 outer-code recoveries, 63/64 repetition |

A zero process exit is not proof of every scientific assertion; some legacy
scripts print metrics rather than asserting them. All legacy failures and
timeouts are retained in historical records. Remaining: migration of all
original archive bytes and raw results, full script inventory/coverage,
comparison of regenerated JSON against archival values excluding timing,
and migration of noisy variants into the reference API.

## Archive inventory

| Bundle | Files | Python | JSON | Logs |
|---|---:|---:|---:|---:|
| initial | 3 | 2 | 1 | 0 |
| round4 | 7 | 3 | 2 | 0 |
| round5 | 14 | 6 | 4 | 3 |
| round6 | 16 | 8 | 4 | 3 |
| round7 | 21 | 11 | 4 | 4 |
| round8 | 55 | 17 | 17 | 17 |
| round9 | 29 | 13 | 7 | 6 |
| round10 | 18 | 9 | 4 | 3 |
| round11 | 20 | 11 | 4 | 3 |
| round12 | 24 | 14 | 4 | 4 |
