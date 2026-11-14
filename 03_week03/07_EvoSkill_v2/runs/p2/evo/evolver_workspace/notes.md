# epoch 0: no skills. scores t1 .5, t2 .5, t3 .4545, t4 .4 (all 3 rollouts identical).
Solver used: t1 half-up final only; t2 half-up tip/grand; t3 half-up final only; t4 floor.
Hidden-test mismatch likely rounding mode / stepwise rounding. No feedback otherwise.
# epoch 1 experiment: skill money-calc-spec assigns A=floor-final(r1), B=ceil-final(r2), C=halfup-each-step(r3) by cwd suffix -rN.
Next: read epoch_1 scores per rollout, find which of A/B/C scores best per task, then replace table with the winning single rule (and generalize).
# epoch 1 results (A floor / B ceil / C step-halfup): t1 .2/.4/.4, t2 .4/.5/.5, t3 .27/.27/.27, t4 .4/.3/.3.
Best so far = halfup-final-only (t1 .5, t2 .5, t3 .4545); t4 halfup-final untested. Test counts: t1 10, t2 10, t3 11, t4 10.
Residual failures not explained by rounding -> hypotheses: ValueError validation of out-of-range inputs, banker's rounding, float-reference style.
# epoch 2 experiment: r1=H (halfup final + ValueError validation), r2=E (banker's final), r3=F (float stepwise round()).
# epoch 2 results: H(halfup final+ValueError) t1 .6 t2 .6 t3 .5455 t4 .5 BEST; E(bankers) .4 .4 .36 .4; F(float round stepwise) .3 .4 .27 .3.
Validation adds ~1 test each. Remaining ~4 fails unknown. Hypothesis: stricter validation (types, empty items, flags).
# epoch 3 experiment: base H fixed; r1=H1 TypeError for wrong types, r2=H2 all ValueError, r3=H3 like H1 + empty list ValueError + non-bool flag TypeError.
