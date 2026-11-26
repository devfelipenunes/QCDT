# Independent experiment protocol (issue #17)

The immutable historical archives remain unchanged. The previous round-8
discrepancy is explained by shared RNG consumption order, not a numerical
regression of current code. Run scripts/audit_round8.py for the historical
comparison. Do not replace either historical sample.

New benchmark: benchmarks.independent. Five public configurations and ten
predeclared instance seeds each (50 generated instances); separate SHA-256
derived streams for instance generation, verification, local-code generation,
and classical search. Generator is a bounded greedy sampler, not uniform over
hypergraphs. It can produce degree/codegree below the public upper bounds.
Store complete terms, public bounds, instance hash, seed provenance, outcomes,
candidate, query counts and explicit schema. Each method sees only its callback
and public bounds. All methods share fixtures; QCDT/dense use the same seeded
holdout masks, known-support uses its own documented seed. Label-bit baseline
does not certify; classical has its own stopping guarantee. Do not compare
these as equal physical resources. No physical execution or hardware advantage.

Re-run the full experiment in reversed order and compare explicit scientific
fields, not CPU times or heuristic key-name filtering. Reject duplicate keys.
Use namespaced output under evidence/independent/; preserve old raw outputs.
This is an internal multi-seed study, not a statistically representative
hardware population or an independent peer review.

Command:
```sh
python -m benchmarks.independent --output evidence/independent/results.json --reverse-check
```
