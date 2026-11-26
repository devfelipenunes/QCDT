# Historical artifact import status

All ten archives exist in the external combined bundle. They are not yet in
Git: the local execution sandbox cannot resolve GitHub, and the connector
does not provide a local-file-to-blob transfer path. Do not treat the
manifest as equivalent to the original bytes.

Local inventory (2026-11-26): 213 archive members including directory
entries, 94 Python file occurrences, 42 distinct Python file contents.
All 94 compiled successfully. The previous selected replay completed 14
entrypoints. A further exploratory 12-second run: six completed
(compact_validation, stress, compare, checked_recovery, field_extension,
paired), four timed out (round6 benchmark, round10 codegree, round11 pruning,
round12 benchmark). Timeouts are not passes. Historical scripts may print
metrics instead of asserting every claim.

To import, download the original combined ZIP from the research conversation,
then in a local clone with GitHub access:

```sh
git switch main
git pull --ff-only
git switch -c research/2-import-original-archives
python -m scripts.import_archives /path/to/QCDT_historical_archives.zip
python scripts/verify_archives.py historical/archives
git add historical/archives
git commit -m "research: import original historical archives without modification"
git push -u origin research/2-import-original-archives
gh pr create --base main --title "M13: import verified original archives" --body "Refs #2. Original bytes verified against historical SHA-256 manifest."
```

Review the diff and CI before merging; don't overwrite source archives or
execute them on an untrusted machine. Remaining #2 criteria include the
actual import, complete replay including timeout resolution, and migration
of the historical alternative/noisy algorithms into the reference API.
