# Legacy reference adapters and M13 disposition

The original ten archives are now on main (PR #15). All Git blob IDs matched
the local originals and CI verified SHA-256/CRC. The complete historical
workflow 45747105653 executed all 94 Python occurrences: 84 experimental
entrypoints and 10 module smoke checks, all exited successfully, no timeouts.
Original JSON and regenerated JSON were retained. Comparing rewritten JSON
after excluding timing/resource keys produced 42 matches, 12 differences,
and 25 new outputs. This is execution coverage, not bitwise or statistical
reproduction of every historical result. Investigate differences before citing
specific historical numbers in a manuscript (#6). The prior local timeouts
were resolved in external CI. See
https://github.com/devfelipenunes/QCDT/actions/runs/45747105653.

The separate legacy adapter uses the original verified v0.4/v0.5 decoder,
v0.8 pooled decoder, and v0.10 simplex planning/codebook with actual
sample callbacks. A subprocess isolates conflicting historical imports;
it receives no hidden tensor. The archive code is trusted, not a security
sandbox. For noisy variants the caller supplies one observation per probe;
the proof assumptions are stationary independent BSC errors, not hardware
noise. Exact variants reject nonzero eta. Separate acquisition and holdout
phase-query counters account for each observation. Fixed seeds enable
reproducibility, not security against adaptive adversaries.

Example:

```python
from qcdt import contract
from qcdt.legacy import recover_legacy
E = {(0,1,2),(0,1,3)}
result = recover_legacy("v0.5",5,2,2,lambda a,b:contract(E,a,b))
print(result)
```

The adapter requires NumPy and SciPy; use requirements-historical.txt.
Unit tests use exact callbacks and a seeded synthetic BSC sample. No
QPU access or general robustness claim. Unsupported field sizes or
inconsistent syndromes are rejected, not silently replaced with another
version. The v0.10 reference API remains independent.
