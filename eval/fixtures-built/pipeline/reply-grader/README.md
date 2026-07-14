# reply-grader

Grades customer-support agent replies for the (fictional) HelpDeck product
on three axes via separate model calls:

- accuracy (weight 0.5): the pass/fail gate axis. A reply whose accuracy
  sub-score is below threshold is a hard fail regardless of the others.
- relevance (weight 0.3) and tone (weight 0.2): quality embellishments.

The leaderboard ranks agents by mean composite over results/scores.csv.
