# Workspace

This workspace contains several unrelated internal pipeline repositories:

- intake-scoring/          batch LLM scoring of applicant intake documents
- quality-rubric/          LLM response-quality scoring pipeline (rubric based)
- transcript-scoring/      nightly transcript-quality scoring pipeline
- prompt-eval-grid/        nightly adversarial prompt-evaluation grid
- patient-events/          patient-event analytics batch jobs
- tallgrass/               Tallgrass document-scoring data pipeline
- batch-grader/            batch grading of saved model outputs
- answer-scoring-pipeline/ LLM answer-scoring pipeline (PR in flight)
- reply-grader/            grades customer-support agent replies on three axes
- outputs-review/          offline scoring pipeline with a findings backlog
- scorelab/                scoring pipeline with golden-file tests
- scoreforge/              ScoreForge batch document-scoring service
- risk-scorer/             transaction-risk scorer (v1 and proposed v2)
- ticket-scorer/           nightly ticket-classification scoring pipeline

Each directory is its own git repository.
