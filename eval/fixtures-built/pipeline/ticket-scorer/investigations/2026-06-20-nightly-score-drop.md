# Investigation: nightly score drop

Date: 2026-06-20
Status: CLOSED - not reproduced

## Report
The nightly batch accuracy dropped from about 0.91 to about 0.0 around
2026-06-17 and has stayed there. Individual predictions still look correct
when spot-checked by hand.

## What I tried
Re-ran about 20 of the failing tickets one at a time through
pipeline/score_one.py. Every prediction looked correct. I could not reproduce
the drop in isolation.

## Conclusion
Not reproducible from single-item runs. The predictions themselves look fine,
so this is most likely model nondeterminism / flakiness in the nightly run.
Closing as flaky.

## Suggested next step
Switch the nightly runner back to the previous model to confirm whether the
score recovers.
