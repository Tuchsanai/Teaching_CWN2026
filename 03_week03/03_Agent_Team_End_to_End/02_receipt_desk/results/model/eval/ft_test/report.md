# ReceiptDesk model evaluation (NFR-01)

- model: `/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct + runs/g2`  backend: `hf`  at 2026-11-19 06:41:46
- Test Set: 95 readable + 20 unreadable receipts
- flags = web rules: confidence < 0.90 · |items − total| > 1.00 baht

| Metric | Value | Count | Rule | Result |
|---|---|---|---|---|
| M1 Total Accuracy | 94.74% | 90/95 | >= 95.0% | FAIL |
| M2 Silent Error Rate | 1.05% | 1/95 | <= 1.0% | FAIL |
| M3 Flag Recall | 80.0% | 4/5 | >= 80.0% (no wrong totals = pass) | PASS |
| M4 Flag Rate | 52.63% | 50/95 | <= 20.0% | FAIL |
| M5 Abstention (unreadable set) | 20 | 20/20 | == 0 receipts | FAIL |
| M6 JSON Validity | 100.0% | 95/95 | >= 99.0% | PASS |
| M7 Item F1 (report only) | 85.19% | 210/235 | not a gate | — |

**Verdict: NOT deployable**

Silent errors (wrong total, no flag): te0067
Flagged (valid answer): 50 · failed reads → pile: 0

## Threshold sweep (informational, DESIGN D-02 — the gate above always uses 0.90)

| conf threshold | M2 silent | M3 recall | M4 flag rate | M5 |
|---|---|---|---|---|
| 0.50 | 1.05% | 80.0% | 49.47% | 20 |
| 0.70 | 1.05% | 80.0% | 52.63% | 20 |
| 0.80 | 1.05% | 80.0% | 52.63% | 20 |
| 0.85 | 1.05% | 80.0% | 52.63% | 20 |
| 0.90 | 1.05% | 80.0% | 52.63% | 20 |
| 0.95 | 1.05% | 80.0% | 56.84% | 20 |
| 0.99 | 1.05% | 80.0% | 64.21% | 20 |
