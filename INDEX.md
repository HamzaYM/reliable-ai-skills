# Skill index

All 17 skills, one row each. For the narrative version with quick-start instructions, see [README.md](README.md).

| Category | Skill | What it does |
|---|---|---|
| Review and quality | [multi-model-adversarial-review](skills/adversarial-review/multi-model-adversarial-review/SKILL.md) | Runs a second, independently-vendored model against your own review pass and reconciles the findings, instead of one model reviewing its own work. |
| Review and quality | [tiered-consultancy-review](skills/tiered-review/tiered-consultancy-review/SKILL.md) | A five-tier escalation ladder (analysts, managers, specialists, partners, polish) for taking a deliverable from rough draft to genuinely finished. |
| Review and quality | [pre-merge-validation-gate](skills/validation-gates/pre-merge-validation-gate/SKILL.md) | Defines what "done" actually means for a change and how to report test results without overstating what was checked. |
| Systems and architecture | [architecture-contracts-as-law](skills/architecture-and-contracts/architecture-contracts-as-law/SKILL.md) | Keeps a single, merge-blocking source of truth for system invariants (schema, API shape, module boundaries) in sync with the code. |
| Systems and architecture | [multi-tenant-auth-reference](skills/auth-and-tenancy/multi-tenant-auth-reference/SKILL.md) | A ground-truth reference pattern for token kinds, role checks, and tenant isolation so you stop guessing during auth bugs. |
| Systems and architecture | [llm-eval-harness-and-scoring-pipeline](skills/evals-and-scoring/llm-eval-harness-and-scoring-pipeline/SKILL.md) | Locked aggregation math, partial-failure handling, prompt versioning, and shadow comparison for any pipeline that scores LLM output. |
| Cost and safety | [ai-cost-tracking-and-guardrails](skills/cost-and-safety-guardrails/ai-cost-tracking-and-guardrails/SKILL.md) | Enforced call tracking, safe cross-provider fallover, and fail-closed rate limiting for LLM calls touching money or sensitive data. |
| Cost and safety | [budget-aware-model-allocation](skills/cost-and-safety-guardrails/budget-aware-model-allocation/SKILL.md) | How to work deliberately when a token or rate-limit budget is running low across more than one model or provider. |
| Cost and safety | [config-and-secrets-hygiene](skills/cost-and-safety-guardrails/config-and-secrets-hygiene/SKILL.md) | Picking the right config layer, avoiding precedence traps, and a repeatable recipe for adding a new feature flag safely. |
| Deploy and infrastructure | [staging-to-prod-cutover-campaign](skills/deploy-and-infra/staging-to-prod-cutover-campaign/SKILL.md) | First-apply traps, the do-not-inherit config scrub, and how to separate go-live gates from infra bring-up. |
| Deploy and infrastructure | [environment-and-build-hazards](skills/deploy-and-infra/environment-and-build-hazards/SKILL.md) | The two-role database model, seed-data idempotency, and cloud-auth preflight for local development environments. |
| Debugging | [systematic-debugging-playbook](skills/debugging-playbooks/systematic-debugging-playbook/SKILL.md) | Establishes ground truth before hypothesizing, and the regression rule for multi-round fix loops after a review pass. |
| Debugging | [failure-archaeology](skills/debugging-playbooks/failure-archaeology/SKILL.md) | A "settled battles" reference so nobody re-attempts an approach that was already tried and deliberately abandoned. |
| Process and change management | [git-change-control-for-agents](skills/change-control/git-change-control-for-agents/SKILL.md) | State verification before any git work, the dead-base PR trap, migration collisions, and working-tree discipline. |
| Process and change management | [multi-agent-batch-campaigns](skills/campaign-execution/multi-agent-batch-campaigns/SKILL.md) | Wave planning, file-contention mapping, and checkpoint-to-file discipline for executing a large backlog across parallel agents. |
| Documentation and compliance | [docs-of-record-and-arbitration](skills/docs-and-compliance/docs-of-record-and-arbitration/SKILL.md) | An explicit arbitration order for when project docs disagree, plus a fact-check-first method for business deliverables. |
| Documentation and compliance | [consent-and-regulated-data-reference](skills/docs-and-compliance/consent-and-regulated-data-reference/SKILL.md) | Fail-closed defaults for consent, retention, and audit trails in systems handling regulated personal data. |
