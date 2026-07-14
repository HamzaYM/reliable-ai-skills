# Postmortem: cache evictions (2026-03-18)

A Redis instance under memory pressure evicted keys. Large numbers of users
were logged out and in-progress work was dropped.

Timeline: memory headroom eroded over two weeks; when the instance hit its
limit, the eviction policy removed live keys.

Remediation: configure an explicit eviction policy suitable for the data,
and alert on memory headroom before the limit is reached.
