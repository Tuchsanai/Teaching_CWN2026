epoch1: wrote skills_v1 money-func-solver. Diagnosis: epoch0 scores 0.3-0.6; no validation (Reject tests), floor rounding in cashback, no test_solve.py.
epoch2: all rollouts 0.9, behavior identical to reference (fuzzed). residual 0.1 unknown; likely test_solve quality (t4 tests missed 10000..10099 boundary). Added template_test.py + stronger test guidance.
epoch3: epoch2 scores all 1.0 with skills_v2; no changes made (skills_v3 = v2).
