# Immutable evidence from 26 November 2026

The two ZIPs are byte-identical downloads of the GitHub Actions artifacts:
- Run 45749367190, artifact 15085290685: independent experiment (50 cases,
  230 observations, reverse-order check), plus prior benchmark families.
- Run 45749584325, artifact 15084898356: 36 compiler-boundary control
  runs, including 12 ideal and 24 snapshot-noise observations.

The files contain raw results, measurement counts where available,
device properties and pip-freeze records. Source run IDs are part of
their filenames. SHA-256 and Git blob hashes were computed locally
before transferring via Base64; the resulting Git blobs matched exactly.
The archives are never regenerated or replaced. The regression test
checks ZIP CRC, SHA-256 and salient reported observations. It does
not re-run the experiments or certify their scientific interpretation.
The historical calibration snapshots and synthetic oracles are not
physical hardware execution. Preserve negative results and rejection
records; do not cherry-pick runs.
