# Independent review packet

Status: internal draft, no reviewer contacted. Request reviewers with
expertise in quantum query complexity and finite-field/sparse interpolation.
Do not imply endorsement from reviewing or citing an author's work.

| Gate | Review question | Reject or revise if |
|---|---|---|
| Model | Is one coherent sign query well-defined and repeatable? Are lower terms truly irrelevant? | Any step uses extra hidden data, copies interchangeably with queries, or controlled access without charging it. |
| Lower count | Does the unsaturated-vertex greedy count hold uniformly including d near maximal? | Count includes duplicate or out-of-promise supports, or constants fail. |
| Span lower bound | Does purification with no-op padding cover adaptive bounded-query protocols? | Span dimension or POVM inequality is wrong. |
| Universal separation | Does every possible difference link lie in the matrix family, and does the union bound give the full degree range? | A nonzero difference can survive the proposed existence argument or decoder needs additional queries. |
| Pair labels | Are labels nonzero and unique, weights nonzero over characteristic 2? | Collision or cancellation on distinct pairs. |
| Weighted acquisition | Does bilinear expansion exactly yield all moments with only R contractions per moment? | Missing cross term, wrong orientation, or hidden input in planning. |
| Decoder | Does the leading Hankel rank identify r, and do 2d moments suffice? | Singular leading system for a legitimate support or ambiguity in admissible roots. |
| Uniformity | Is field setup, exact rank-provider search and all reconstruction polynomial in n? | Bound relies only on finite-size ranks, or exponential-in-n computation. |
| Literature | Does an existing result imply the same efficient reconstruction bound under the same promise? | If yes, reposition as reproduction/refinement and cite it. |
| Noise | Are conditional full-word bounds and fresh holdouts kept separate from physical claims? | Any blanket robustness claim or uncharged extra oracle access. |
| Evidence | Are negatives, differing verification policies, source hashes, and timeouts disclosed? | Any cherry-picking, unequal budget presented as equal consumption, or unsupported empirical claim. |

Suggested response format: section/lemma, verdict (correct / needs repair /
subsumed by prior work / insufficient evidence), counterexample or source,
and proposed correction. Prioritize mathematical correctness and originality
over hardware. Before any submission: agree author list and affiliations,
resolve licensing and branch governance with owner, verify references and
raw artifacts, incorporate reviewer feedback, and decide venue. Do not
automatically submit or contact anyone on behalf of the user.
