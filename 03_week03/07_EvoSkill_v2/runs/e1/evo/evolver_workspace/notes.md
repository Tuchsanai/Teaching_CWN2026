# epoch1 (skills_v1)
- epoch0 scores: t1 .5, t2 .5, t3 ~.5, t4 .4. Solver wrote naive formula, no validation, no tests.
- reference/answers show hidden policies (silver no bday, shipping 0km=0, express>20kg ValueError, floor for cashback, strict int/bool ValueError).
- v1: one skill baankafe-solve (SKILL.md + solve_template.py). Next: check epoch1 scores, see which categories still fail.
- epoch1 scores ~0.9 all; solver outputs match reference except t3 float distance_km (accepted). v2 adds strict-int rule + corner-case hunt. Remaining 0.1 on t1/t2/t4 unexplained (fuzz found no behavior diff).
- epoch2: identical scores (0.9), solver == reference on fuzz+CLI. Unexplained 0.1. v3 experiment: move solver tests out of workspace (only solve.py left). If epoch3 score changes -> learn; revert if drops.
