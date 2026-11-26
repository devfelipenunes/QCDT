# Original historical research artifacts

The ten ZIPs under archives/ are the byte-identical originals transferred
from the research conversation. Their Git blob IDs were checked against
the original local files before constructing the commit. SHA-256 and
internal CRC are verified again in CI using docs/ARCHIVES.sha256.
The archive members include all available original scripts, results, logs
and the original experimental limitations; no archived byte was altered.

Inventory at import: 213 ZIP entries (including six directory entries),
207 files, 94 Python occurrences, 42 distinct Python contents. All 94
compiled locally. The selected local replay completed 21 entrypoints; three
additional scripts reached a time limit after retries. Those timeouts are
not passes.

Run the full archive-context replay:

```sh
python -m pip install -r requirements-historical.txt
python scripts/verify_archives.py historical/archives
python -m scripts.import_archives historical/archives --destination /tmp/qcdt-verified
python -m scripts.replay_all historical/archives quantum_research_round12.zip --output replay-round12 --timeout 240 --workers 3
```

The historical CI workflow covers all ten archives with isolated temporary
directories per script, including repeated file contents in different
archive contexts. Module-only scripts count as module smoke checks.
Reconstructed JSON is compared with archived output when rewritten,
excluding explicitly identified timing/resource fields. Every failure,
timeout, changed JSON and new output is retained as a diagnostic artifact;
default exit status covers integrity/harness, not scientific agreement.
Use --strict to reject any nonzero script exit or timeout. Do not equate
CI green with all legacy claims being reproduced.

The reference API remains separate from archival code. Version migration
and independent validation of the legacy/noisy decoders are distinct tasks.
