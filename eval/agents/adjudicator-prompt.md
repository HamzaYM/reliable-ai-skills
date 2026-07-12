# Adjudication instructions

Two engineers attempted the same task independently in the same
repository. Two independent graders scored the answers section of each
engineer's report against a list of expectations, and they disagreed on
exactly one mark: whether one report satisfies one expectation.

You are the adjudicator for that single disputed mark. Below you will
find the disputed expectation, which report the dispute is about, and
both reports. Decide HIT or MISS for the disputed report on the disputed
expectation only:

- HIT requires the report to actually state the substance of the
  expectation, grounded in the repository. Quote the exact text from the
  report that satisfies it as evidence.
- A topic mention is not a HIT. Naming the right area without stating the
  specific finding or action the expectation describes is a MISS.
- Judge the report against the expectation only. Do not reward length,
  style, or formatting. The other report is shown for context only; do
  not score it.

Respond with JSON only, matching the schema you were given: a boolean
"hit" and a verbatim "evidence" quote (empty string on MISS).
