# Recommendation: ship scorer v2 (ML-88)

v2 raises overall accuracy from 91.2% to 94.8% on our evaluation set.

v2 is a clear improvement across the board. The new ensemble captures
interaction features v1 could not represent, and error analysis shows the
remaining misses are concentrated in ambiguous cases.

We recommend replacing v1 with v2 in production at the next release window.

## Evaluation

Overall accuracy on the evaluation set:

| version | accuracy |
| --- | --- |
| v1 | 91.2% |
| v2 | 94.8% |
