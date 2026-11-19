# ReceiptDesk model evaluation (NFR-01)

- model: `/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct + no adapter`  backend: `hf`  at 2026-11-19 06:28:32
- Test Set: 95 readable + 20 unreadable receipts
- flags = web rules: confidence < 0.90 · |items − total| > 1.00 baht

| Metric | Value | Count | Rule | Result |
|---|---|---|---|---|
| M1 Total Accuracy | 46.32% | 44/95 | >= 95.0% | FAIL |
| M2 Silent Error Rate | 20.0% | 19/95 | <= 1.0% | FAIL |
| M3 Flag Recall | 62.75% | 32/51 | >= 80.0% (no wrong totals = pass) | FAIL |
| M4 Flag Rate | 63.16% | 60/95 | <= 20.0% | FAIL |
| M5 Abstention (unreadable set) | 4 | 4/20 | == 0 receipts | FAIL |
| M6 JSON Validity | 89.47% | 85/95 | >= 99.0% | FAIL |
| M7 Item F1 (report only) | 76.45% | 185/235 | not a gate | — |

**Verdict: NOT deployable**

Silent errors (wrong total, no flag): te0000, te0002, te0015, te0021, te0024, te0032, te0044, te0045, te0052, te0062, te0063, te0065, te0067, te0068, te0073, te0078, te0079, te0080, te0091
Flagged (valid answer): 50 · failed reads → pile: 10

## Threshold sweep (informational, DESIGN D-02 — the gate above always uses 0.90)

| conf threshold | M2 silent | M3 recall | M4 flag rate | M5 |
|---|---|---|---|---|
| 0.50 | 22.11% | 58.82% | 60.0% | 4 |
| 0.70 | 20.0% | 62.75% | 63.16% | 4 |
| 0.80 | 20.0% | 62.75% | 63.16% | 4 |
| 0.85 | 20.0% | 62.75% | 63.16% | 4 |
| 0.90 | 20.0% | 62.75% | 63.16% | 4 |
| 0.95 | 20.0% | 62.75% | 63.16% | 4 |
| 0.99 | 20.0% | 62.75% | 65.26% | 4 |
