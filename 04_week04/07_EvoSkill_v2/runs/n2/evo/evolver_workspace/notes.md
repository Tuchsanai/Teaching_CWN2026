# epoch1 notes
- epoch0 scores 0.4-0.6: solver lacked input validation (Reject tests) + hidden policies (S1 dist0->0, S2 express>20000 reject, C1 silver no birthday x2, C2 cashback floor).
- v1 staging: baankafe-solve-playbook (+template), baankafe-house-rules. Next: check epoch1 scores, see which test groups still fail.
- epoch2: scores ep1 0.6-0.9; v2 adds mandatory main() CLI, comprehensive test_solve template, forces silver C1 policy. no-test-file/main hypothesis from t2_s1 (main) 0.9 vs 0.7.
- epoch3: ep2 scores all 1.0 (12/12). staging left unchanged (skills_v2 kept as v3) to avoid regression; unseen-task generalization relies on house-rules section 4.
