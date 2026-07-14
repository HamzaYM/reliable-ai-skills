---
name: budget-aware-model-allocation
description: Use when you're working with more than one model or provider with separate rate-limit or token budgets, and one of them is running low. Decide whether to proceed lean, defer non-urgent work, or shift heavy work to whichever provider has headroom, instead of blowing through a limit on autopilot.
---

# Budget-aware model allocation

If you have access to more than one model or vendor, each with its own separate rate-limit or spend budget, treat that as a resource-allocation problem, not just a cost line item. The failure mode this guards against: an offhand, unscoped request (a wide fan-out, a big batch job, ingesting a large corpus) detonates a large fraction of a budget window that was already running low, at the worst possible moment.

## When a budget signal says a window is getting low

1. **Be deliberate before large spends.** If the next action is inherently large (a wide parallel fan-out, ingesting a big corpus, a long agentic loop), say so explicitly before doing it: state the intended scope, either in your own reasoning or to whoever you're working with. If no one is available to check with, default to the smallest scope that actually accomplishes the task rather than blocking entirely.
2. **Shift heavy work to whichever provider has headroom.** If one provider is the constraint and another has budget to spare, route the heavy or parallel execution and review work there. You orchestrate; the other provider spends its own budget. This is the same idea as the multi-model-adversarial-review skill: a second vendor gives you diversity of opinion. It also gives you separate capacity.
3. **Trim before you cut scope.** Lower the effort/reasoning setting, batch requests, and avoid re-reading large context you've already processed, before you resort to skipping work outright.

## When budgets are healthy

Work normally. Don't pre-emptively ration based on a hypothetical future shortage: that just produces worse answers for no real benefit.

## Rules

- **Don't trust a stale signal as current.** If a budget snapshot is flagged as possibly out of date, re-check it or proceed conservatively rather than trusting a number that might be minutes or hours old.
- **This is judgment, not a hard gate.** Never hard-block work because a budget looks low; degrade gracefully instead (smaller scope, lower effort, defer to the other provider).
- **If every available provider is constrained, proceed with the smallest scoped action and say so.** Don't stall waiting for headroom that may not come.

*Evidence: net-new for this library, not part of the original July 2 A/B; tested only in the July 2026 effort lattice, on a single task with 4 must-hits (results/matrix/MATRIX.md; evidence note updated 2026-07-12). Cold already matched loaded in 7 of 15 model/effort cells; the other 8 showed loaded gain from 3/4 to 4/4 must-hits. Single-task scope: directional only, not pre-registered as confirmatory for this skill.*
