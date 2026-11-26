# Research contribution workflow

All substantive work follows an issue and a pull request into main.

1. Select or create an issue with a hypothesis, acceptance criteria and scope.
2. Branch from current main; use an issue-linked branch name.
3. Implement, test, and record commands, versions, seeds and failures.
4. Open a PR referencing the issue. Report new tests, comparisons, assumptions and limitations. Use "Refs #N" for partial work; "Closes #N" only when all acceptance criteria are met.
5. Inspect the diff and require the reference and Qiskit/Aer CI jobs to pass on the exact PR head. Do not bypass failed checks, required reviews or branch rules.
6. Merge passing, scoped PRs into main; use a merge commit to preserve research history. Verify the merge. Keep incomplete issues open.
7. Update issue progress and research records. Continue with the next prioritized issue.

This policy is a workflow convention, not a configured branch protection rule. No claim of peer review, novelty or hardware advantage follows from a successful CI run.

## Historical artifacts

Run `python scripts/verify_archives.py /path/to/QCDT_historical_archives.zip` from the repository root, or pass a directory holding the original ZIPs. The verifier compares each archive with docs/ARCHIVES.sha256 and tests the inner ZIP's CRC without extracting or executing files. The historical bundle is currently external to the repository; this check does not reproduce the experiments. Never commit credentials, personal data or unreviewed historical files to this public repository.

## Validation

```bash
python -m unittest discover -s tests -v
python -m pip install -r requirements-qiskit.txt
python -m unittest discover -s tests -v
python -m benchmarks.resources resources.json
```

Record independently reproduced results separately from legacy observations.
