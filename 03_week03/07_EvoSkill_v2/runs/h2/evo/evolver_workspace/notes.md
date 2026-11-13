# Evolver notes (persist across epochs)

## Layout facts (verified)
- Solver cwd in traces: /workspace/evlab/ws/h2/legs/runs/base_train/<task>-r<i>/sandbox (path only; not on this machine)
- Solver checks `./skills` in its cwd at start; in epoch 0 it did not exist.
- Trace jsonl: `assistant` entries carry `tool_use` (Write/Edit/Bash), `user` entries carry `tool_result`, final `result` entry has the answer text.
- Helper scripts: /evo/evolver_workspace/tools/condense.py (readable transcript), tools/writes.py (extract Write/Edit contents).
- Trace does NOT include the original task prompt (brief); only /evo/reference/baankafe/tasks/*.json has the brief text.
- Do NOT use /evo/reference/baankafe/answers/*/solve.py to write skills (train-answer leakage; skills must generalize).

## Epoch 0 results (scores)
- t1-cafe-bill: 0.5, 0.5, 0.6 (s1,s2 per-step half-up rounding; s3 Fraction + single final half-up rounding)
- t2-split-bill: 0.6 (s1 tip half-up), 0.5 (s2 tip floor), 0.6 (s3 tip floor)
- t3-shipping-fee: 0.6 x3 (Decimal, half-up at satang)
- t4-cashback: 0.4 x3 (all: <100 baht -> 0, rate, birthday x2 before cap, cap 200, floor rounding)
- Consistent 0.4 on t4 across 3 different implementations => likely a systematic interpretation mismatch (cap ordering? threshold? rounding?) not yet identified.

## Recurring solver failure modes (epoch 0)
- `python3 -I` used for import from cwd -> ModuleNotFoundError, wasted turns (seen in t1 s1/s2/s3, t3 s1, t4 s3).
- Strict isinstance(int) checks raising TypeError on float inputs (t4 s1, s2, s3) -> risk on hidden tests.
- Per-step rounding vs single final rounding (t1).
- Solvers reported ambiguity honestly in their answers; good.

## Skills written
- epoch 1 staging: money-rule-functions (Thai; keyword->operator table, round once half-up, Fraction, python -I warning).
- Open question for epoch 2: check whether epoch 1 scores moved t1 (single-rounding hypothesis) and whether t4 changed.

## Epoch 1 results (skills_v1 = money-rule-functions)
- t1: 0.5 (s1), 0.6 (s2), 0.6 (s3). t2: 0.6 x3. t3: 0.6 x3. t4: 0.6 x3 (was 0.4)
- Mean: epoch0 0.525 -> epoch1 0.592
- t4 0.4 -> 0.6 after skill: round-once half-up + Fraction + cap after birthday doubling. Confirms rounding was part of the t4 gap.
- All solvers in epoch 1 read ./skills/money-rule-functions/SKILL.md and followed it; no -I import errors seen in epoch 1.
- Plateau at 0.6 across all 4 tasks: remaining 0.4 unidentified. Candidates (unverified): additive vs sequential member discount in t1, tip rounding in t2, signature/edge-input expectations.

## Skills written
- epoch 2 staging (v2): same skill, added default-readings table (threshold base, sequential discounts, cap placement, tip rounded once after combining), signature contract section (no extra defaults, return plain int/list, solve.py in start dir), example-matching rule.

## Epoch 2 results (skills_v2)
- All 12 rollouts 0.6 (t1 x3, t2 x3, t3 x3, t4 x3). Mean 0.6 (epoch1 0.592). Plateau confirmed; no rollout below 0.6.
- Solvers followed v2: sequential discounts, cap after birthday doubling, half-up once, tip combined then rounded once.

## Skills written
- epoch 3 staging (v3): added generic rule-pattern section (tiers vs marginal, clamps, percent-of-percent via Fraction, points floor, negative amounts, date/bool inputs, condition-pair test coverage). Core rules unchanged on purpose: no evidence in traces for an alternative reading of the remaining 0.4.
- Still-unknown gap: candidates remain additive vs sequential member discount (t1), tip rounding (t2), error-handling expectations. Needs grader feedback to resolve.
