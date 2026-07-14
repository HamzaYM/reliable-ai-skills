# transcript-scoring

Nightly transcript-quality scoring pipeline. Only a few sample transcripts
are committed for reference; the full dataset is fetched at run time from
the internal transcript store `s3://ts-internal/nightly-manifest/`.
Budget/usage telemetry is captured to `.cache/usage_snapshot.json`.
