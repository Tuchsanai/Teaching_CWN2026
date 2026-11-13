# epoch 0 -> v1
scores e0: t1 0.5x3 (half-up end), t2 0.5x3, t3 0.5,0.5,0.6 (s3 added ValueError range validation => +0.1), t4 0.3x3 (floor).
Solver never saw tests; rollouts r1/r2/r3 differ by cwd suffix -rN. v1 skill: r1=half-up end, r2=round each step half-up, r3=floor end -> compare scores in epoch 1 per rollout index, then fix the winning policy in v2. Also validation ValueError.
# epoch1 results
r1(half-up end): t1 .7 t2 .7 t3 .6 t4 .7; r2(round each step): .5 .7 .5 .6; r3(floor): .3 .6 .5 .5. => half-up once at end fixed in v2.
validation added gave ~+0.2 (e0 vs e1 r1). Remaining ~0.3 unknown. v2 explores validation strictness: r1 strict ValueError+empty err; r2 ranges only/no types/empty ok; r3 TypeError for wrong types.
# epoch2 results
validation r1 strict ValueError: .7 .7 .6 .7 ; r2 no types/empty ok: .6 all; r3 TypeError: .6 all. => strict ValueError fixed in v3.
t3 stuck .6 regardless. v3 explores final rounding: r1 half-up, r2 ceil, r3 banker's. remaining 0.3 unexplained (ideas: t3 float weight rejection, empty items, ties).
