epoch0 scores ~0.4-0.6. Cause: solver skipped input validation (Reject tests) + hidden policies (C1 silver no birthday, S1 dist0->0, S2 express>20000 ValueError). Rounding: half-up charge, floor payout.
v1: staging/baankafe-solve (SKILL.md + template_solve.py). Next: check epoch1 scores, see whether policies applied & what generalises.
v2 (epoch2 turn): epoch1 scores ~0.9 (t3s2/t4s2 0.7: left my_function in main). Remaining loss: float distance_km accepted (ref rejects) + unknown 0.1 on t1/t2/t4 (code identical to ref on fuzz). Added TARGET in template + check_solve.py + int-only rule.
v3 (epoch3 turn): epoch2 all 0.9, code identical to ref; remaining 0.1 unknown (likely non-code). Added step 6.1 full reject test + honest final report. Don't churn further.
