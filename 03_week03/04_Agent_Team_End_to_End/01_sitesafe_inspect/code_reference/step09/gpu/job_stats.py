#!/usr/bin/env python3
"""Per-image processing time on the GPU from the gateway's jobs.db (read-only).
infer_ms = time inside the model call (measured by the worker) · proc_ms = STARTED→DONE seen by the gateway."""
import json, sqlite3, statistics as st
db = sqlite3.connect("file:/workspace/e2e_sitesafe/deploy/data/jobs.db?mode=ro", uri=True)
rows = db.execute("SELECT result_json, proc_ms, delivery_count FROM jobs WHERE status='DONE' ORDER BY finished_at").fetchall()
infer = [json.loads(r[0])["infer_ms"] for r in rows]; proc = [r[1] for r in rows if r[1] is not None]
def s(x):
    x = sorted(x); return {"n": len(x), "min": x[0], "median": st.median(x), "mean": round(st.mean(x), 1), "p95": x[max(0, int(len(x) * 0.95) - 1)], "max": x[-1]}
print(json.dumps({"jobs_done": len(rows), "jobs_total": db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
                  "infer_ms": s(infer), "proc_ms_started_to_done": s(proc),
                  "delivered_twice": sum(1 for r in rows if r[2] > 1)}, indent=1))
