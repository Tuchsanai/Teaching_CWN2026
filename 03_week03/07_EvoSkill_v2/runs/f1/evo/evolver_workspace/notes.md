# notes
- epoch1 (skills_v1) scores: t1/t2 0.9, t3 0.818, t4 0.8. Solver code == reference except: t3 missed S2 (express>20000 reject) & accepted float distance; t4 gave silver birthday x2 (C1 missing). t1/t2 lose 0.1 unknown (code matches reference).
- v2: made policies mandatory in SKILL.md section 3 (answers in /evo/reference/baankafe/answers).
- epoch2 (skills_v2): t1/t2/t4 0.9, t3 0.909. Re-ran reference test_solve.py against epoch_2 solver code: all 12/12 pass for all 4 tasks -> residual loss is hidden/unknowable, no fix identifiable. epoch3: no traces/scores existed at my turn; kept staging unchanged (v3 == v2).
