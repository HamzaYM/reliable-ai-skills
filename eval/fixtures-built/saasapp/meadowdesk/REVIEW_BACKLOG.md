# Review remediation backlog

| ID | Status | Location | Finding |
| --- | --- | --- | --- |
| F-01 | done | backend/app/services/tenants.py:5 | N+1 tenant query when listing bookings |
| F-02 | todo | backend/app/routers/bookings.py:12 | overlapping-booking validation missing on create |
| F-03 | todo | backend/app/routers/bookings.py:142 | timezone handling in the availability window ignores tenant tz |
| F-04 | in progress | backend/migrations/0001_init.sql:3 | missing index on bookings(tenant_id, day) |
| F-05 | done | backend/app/services/tenants.py:1 | tenant-subdomain sanitization absent |
| F-06 | todo | backend/app/routers/bookings.py:9 | booking endpoints lack rate limiting |
| F-07 | todo | backend/app/routers/desks.py:8 | 404 error schema inconsistent with the rest of the API |
| F-08 | todo | backend/app/routers/bookings.py:60 | DST transitions skew reminder normalization |
| F-09 | todo | backend/app/routers/bookings.py:10 | bookings list pagination unbounded page size |
| F-10 | todo | infra/main.tf:3 | over-permissive security group ingress |
