# Timing (monotonic /proc/uptime, UTC from `date -u`)

| Phase | UTC start | UTC end | mono start | mono end | Seconds | Status | Note |
|---|---|---|---|---|---|---|---|
| setup (session + first evidence) | 12:01:12Z | 12:01:22Z | 351683.25 | 351693.22 | 9.97 | PASS | includes writing pw.sh |
| search | 12:01:22Z | 12:02:15Z | 351693.22 | 351746.51 | 53.29 | BLOCKED | includes waits 8.01 + 6.00 s, retry 1, trace, and AI thinking time between commands |
| flight | — | — | — | — | 0 | BLOCKED | form not reached |
| hotels | — | — | — | — | 0 | BLOCKED | form not reached |
| report | 12:02:15Z | 12:02:44Z | 351746.51 | 351774.83 | 28.32 | PASS | close + steps.md + blocker.md |
| **total** | 12:01:12Z | 12:02:44Z | 351683.25 | 351774.83 | **91.58** | BLOCKED | = sum of phases (no double counting) |
