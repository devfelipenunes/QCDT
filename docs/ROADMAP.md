# Scientific consolidation gates

- [ ] M13: migrate the complete historical source, raw results and logs; preserve archive hashes; consolidate reproducibility scripts. Ideal reference port and local tests are the first step.
- [ ] M14: systematic prior-art search, formal model comparison, published baselines and independent proof review; reject or reposition the contribution if already known.
- [ ] M15: execute independent Qiskit and Aer tests, check bit order, transpilation, gate counts and calibrated noise. No hardware claims from simulator data.
- [ ] M16: preregister a 4–8 qubit pilot, verify device access and shot budget, collect calibration metadata and all failures.
- [ ] M17: English manuscript, independent researcher review, decision on submission/preprint. No originality or authorship endorsements assumed.
- [ ] M18: investigate opaque diagonal circuit characterization; blockchain only with a defensible coherent access model and strong classical comparator.

Version v0.10 is the provisional research candidate, not an API stability promise.
Preserve v0.4/v0.5 as high-codegree comparators and v0.8 as a noisy-model comparator.
Do not merge experimental variants merely because they add features.
