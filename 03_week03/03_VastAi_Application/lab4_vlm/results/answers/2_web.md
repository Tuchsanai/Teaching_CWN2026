I started the expense-book website from Docker on this machine and opened http://localhost:3404. `/api/status` returns `{"ok":true,"base":true,"ft":true}`. The very first status check failed (`fetch failed`) because the container had only just started; it passed on the next check without any change.

## Results for the first 3 receipts (`POST /api/read`)

| Receipt | Model | Items correct | Total correct? | Time (s) |
|---|---|---|---|---|
| test_092 | base | 0 / 1 | ❌ (read 250,000, answer 240,000) | 1.44 |
| test_092 | ft | **1 / 1** | ✅ 240,000 | 0.68 |
| test_051 | base | 0 / 4 | ❌ (read 334,011, answer 334,000) | 1.40 |
| test_051 | ft | **3 / 4** | ❌ (read 334,011, answer 334,000) | 1.02 |
| test_020 | base | 4 / 5 | ❌ (read 377,059, answer 377,859) | 1.28 |
| test_020 | ft | **5 / 5** | ✅ 377,859 | 0.95 |

**Combined:** base got 4/10 items right and 0/3 totals. ft got 9/10 items right and 2/3 totals. ft was also faster on every receipt (0.7–1.0 s vs. 1.3–1.4 s).

I counted an item as correct only when both its name and price match the answer in `samples.json`, ignoring case and symbols. This is the same rule `eval.py` uses. The times are the `seconds` field the website's API reports.

What went wrong on each receipt:
- **test_092, base:** It read the wrong line, giving price 60,000 when the answer is 240,000.
- **test_051, base:** All 4 prices are correct, but every name is missing the "(TA)" prefix, so none of them count as correct.
- **test_051, ft:** "GRG" was read as "ORG", so one item is wrong. Both models read the total as 334,011, but the answer is 334,000.
- **test_020, base:** "chkn" was read as "chkm", and one digit of the total is wrong (377,059).

The website is still running. To shut it down when you're finished, run `docker compose down -v` in `lab4_vlm/web/` (step 4 of RECIPE). The Vast.ai machine is also still running and costing money until it is deleted with the third prompt.