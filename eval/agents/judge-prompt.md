# Grading instructions

Two engineers attempted the same task independently in the same
repository. Below you will find the task they were given, a list of
expectations, and the answers section of each engineer's report.

For each expectation, decide HIT or MISS for each report:

- HIT requires the report to actually state the substance of the
  expectation, grounded in the repository. Quote the exact text from the
  report that satisfies it as evidence.
- A topic mention is not a HIT. Naming the right area without stating the
  specific finding or action the expectation describes is a MISS.
- Judge each report against the expectations only. Do not reward length,
  style, or formatting.

Finish with a one-line comparative verdict saying which report answered
the task better overall, or that they are comparable.

Respond with JSON only, matching the schema you were given: one entry per
expectation, keyed by its id, with a boolean "hit" and a verbatim
"evidence" quote (empty string on MISS) for report_1 and report_2, plus
"comparative_verdict".
