# ReceiptDesk model evaluation (NFR-01)

- model: `/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct + no adapter`  backend: `hf`  at 2026-11-19 06:33:07
- Test Set: 98 readable + 0 unreadable receipts
- flags = web rules: confidence < 0.90 · |items − total| > 1.00 baht

| Metric | Value | Count | Rule | Result |
|---|---|---|---|---|
| M1 Total Accuracy | 45.92% | 45/98 | >= 95.0% | FAIL |
| M2 Silent Error Rate | 24.49% | 24/98 | <= 1.0% | FAIL |
| M3 Flag Recall | 54.72% | 29/53 | >= 80.0% (no wrong totals = pass) | FAIL |
| M4 Flag Rate | 56.12% | 55/98 | <= 20.0% | FAIL |
| M5 Abstention (unreadable set) | 0 | 0/0 | == 0 receipts | FAIL |
| M6 JSON Validity | 90.82% | 89/98 | >= 99.0% | FAIL |
| M7 Item F1 (report only) | 76.09% | 175/217 | not a gate | — |

**Verdict: NOT deployable**

Silent errors (wrong total, no flag): va0009, va0010, va0012, va0017, va0026, va0032, va0047, va0052, va0053, va0054, va0056, va0058, va0065, va0066, va0071, va0072, va0074, va0076, va0079, va0082, va0089, va0097, va0098, va0099
Flagged (valid answer): 46 · failed reads → pile: 9

## Threshold sweep (informational, DESIGN D-02 — the gate above always uses 0.90)

| conf threshold | M2 silent | M3 recall | M4 flag rate | M5 |
|---|---|---|---|---|
| 0.50 | 27.55% | 49.06% | 53.06% | 0 |
| 0.70 | 25.51% | 52.83% | 55.1% | 0 |
| 0.80 | 25.51% | 52.83% | 55.1% | 0 |
| 0.85 | 25.51% | 52.83% | 55.1% | 0 |
| 0.90 | 24.49% | 54.72% | 56.12% | 0 |
| 0.95 | 24.49% | 54.72% | 56.12% | 0 |
| 0.99 | 21.43% | 60.38% | 59.18% | 0 |
