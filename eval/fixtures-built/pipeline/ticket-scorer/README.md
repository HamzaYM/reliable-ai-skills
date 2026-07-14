# ticket-scorer

Nightly LLM ticket-classification pipeline: it classifies incoming support
tickets and scores its predictions against a labeled evaluation set. Tickets
use the SCORE-N scheme. The classifier is a deterministic offline keyword stub
so batch and single-item runs are reproducible without network access.
