# clinic-notes

Multi-tenant clinic-notes SaaS (FastAPI + Postgres). LLM subsystem lives
under backend/app/ai/. Tickets use the CLIN-N scheme.

Team rule: all LLM calls must go through TrackedLLMClient
(backend/app/ai/tracked_client.py) so usage and cost are recorded.
