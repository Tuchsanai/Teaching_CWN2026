"""Step 11 ยท compare totals saved in PostgreSQL (web) with what the gateway answered (watch_gateway.py),
plus the CORD ground truth. usage: python compare_db_gateway.py <batch_id> -> results/deploy/e2e_check.json"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; D = ROOT / "results/deploy"
batch = sys.argv[1]
gw = json.loads((D / "gateway_answers.json").read_text(encoding="utf-8"))
gt = {g["file"]: g["total"] for g in json.loads((D / "test_images/ground_truth.json").read_text())}
sql = ("select r.id, r.file_name, r.status, r.total, r.total_confidence, r.result_at - r.accepted_at "
       f"from receipts r where r.batch_id='{batch}' order by r.file_name")
out = subprocess.run(["docker", "compose", "-p", "receiptdesk-e2e", "exec", "-T", "db", "psql", "-U", "receiptdesk",
                      "-d", "receiptdesk", "-A", "-t", "-F", "|", "-c", sql],
                     capture_output=True, text=True).stdout
rows = []
for line in out.strip().splitlines():
    rid, fn, st, tot, conf, took = line.split("|")
    g = gw.get(rid, {}); res = g.get("result") or {}
    q, f = g.get("queued_at"), g.get("finished_at")
    rows.append({"file": fn, "db_status": st, "db_total": tot, "db_conf": round(float(conf), 4) if conf else None, "upload_to_review": took,
                 "gw_status": g.get("status"), "gw_total": res.get("total"),
                 "gw_conf": round(res["total_confidence"], 4) if "total_confidence" in res else None,
                 "match": tot == res.get("total"), "truth": gt.get(fn), "correct": tot == gt.get(fn)})
json.dump(rows, open(D / "e2e_check.json", "w"), indent=1)
for r in rows: print(r)
print("match", sum(r["match"] for r in rows), "/", len(rows), "ยท correct vs truth", sum(r["correct"] for r in rows))
