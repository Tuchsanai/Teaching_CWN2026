# ReceiptDesk model evaluation (NFR-01)

- model: `/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct + runs/g2`  backend: `hf`  at 2026-11-19 06:32:11
- Test Set: 98 readable + 0 unreadable receipts
- flags = web rules: confidence < 0.90 · |items − total| > 1.00 baht

| Metric | Value | Count | Rule | Result |
|---|---|---|---|---|
| M1 Total Accuracy | 95.92% | 94/98 | >= 95.0% | PASS |
| M2 Silent Error Rate | 0.0% | 0/98 | <= 1.0% | PASS |
| M3 Flag Recall | 100.0% | 4/4 | >= 80.0% (no wrong totals = pass) | PASS |
| M4 Flag Rate | 51.02% | 50/98 | <= 20.0% | FAIL |
| M5 Abstention (unreadable set) | 0 | 0/0 | == 0 receipts | FAIL |
| M6 JSON Validity | 100.0% | 98/98 | >= 99.0% | PASS |
| M7 Item F1 (report only) | 84.26% | 190/217 | not a gate | — |

**Verdict: NOT deployable**

Silent errors (wrong total, no flag): none
Flagged (valid answer): 50 · failed reads → pile: 0

## Threshold sweep (informational, DESIGN D-02 — the gate above always uses 0.90)

| conf threshold | M2 silent | M3 recall | M4 flag rate | M5 |
|---|---|---|---|---|
| 0.50 | 0.0% | 100.0% | 48.98% | 0 |
| 0.70 | 0.0% | 100.0% | 50.0% | 0 |
| 0.80 | 0.0% | 100.0% | 50.0% | 0 |
| 0.85 | 0.0% | 100.0% | 51.02% | 0 |
| 0.90 | 0.0% | 100.0% | 51.02% | 0 |
| 0.95 | 0.0% | 100.0% | 52.04% | 0 |
| 0.99 | 0.0% | 100.0% | 68.37% | 0 |
