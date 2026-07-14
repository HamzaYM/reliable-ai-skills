# OPS-412 internal timeline (2026-04-08)

- 14:03 checkout failures begin
- 14:50 FIRST ALERT fires (paging)
- 15:05 on-call acknowledges; rollback prepared
- 15:20 mitigation applied (config rolled back)
- 15:41 full recovery confirmed

During the window 1,284 transactions failed and required manual
reprocessing; 37 were unrecoverable and refunded.
