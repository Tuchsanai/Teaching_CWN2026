#!/usr/bin/env python3
"""Step 09 · end-to-end test through the web's own API (real HTTP, no browser).

  python code_step09/e2e_upload.py --images results/deploy/test_images --count 5  --out results/deploy/e2e_5photos.json
  python code_step09/e2e_upload.py --images results/deploy/test_images --count 20 --out results/deploy/queue_20jobs_web.json

What it does (run from the lesson folder):
  1. logs in as a seeded supervisor (docs/TEST-DATA.md), opens an upload of N photos, sends N files
  2. polls GET /api/uploads/{batchId} until no photo is QUEUED/PROCESSING, keeping a timeline
  3. reads the rows of those photos from PostgreSQL (photos + detections)
  4. asks the gateway (GET /v1/jobs?ids=, HTTPS + X-API-Key) for the same job ids
  5. compares every field (h, v, model_version, conf_threshold, image size, every box)

The gateway key is read from ./.env and is never printed or written to the output.
"""
from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USERS = {"sup.a": ("sup.a@sitesafe.test", "Test-SupA-01"), "sup.b": ("sup.b@sitesafe.test", "Test-SupB-01"),
         "sup.c": ("sup.c@sitesafe.test", "Test-SupC-01")}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def http(method, url, *, body=None, headers=None, context=None, timeout=30):
    headers = dict(headers or {})
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode()
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as res:
            return res.status, res.headers, res.read()
    except urllib.error.HTTPError as err:
        return err.code, err.headers, err.read()


def multipart(filename: str, data: bytes):
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            "Content-Type: image/jpeg\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    return body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}


def env_value(path: Path, name: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{name} not found in {path}")


def psql_json(sql: str):
    cmd = ["docker", "compose", "-p", "sitesafe-e2e", "exec", "-T", "db",
           "psql", "-U", "sitesafe", "-d", "sitesafe", "-At", "-c", sql]
    out = subprocess.run(cmd, cwd=ROOT / "app", capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(out) if out.strip() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3410")
    ap.add_argument("--images", required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--user", default="sup.a", choices=sorted(USERS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=float, default=300)
    args = ap.parse_args()

    files = sorted(Path(args.images).glob("*.jpg"))[: args.count]
    if len(files) < args.count:
        raise SystemExit(f"need {args.count} images, found {len(files)}")
    email, password = USERS[args.user]

    status, headers, _ = http("POST", args.base + "/api/auth/login", body={"email": email, "password": password})
    cookie = (headers.get("Set-Cookie") or "").split(";", 1)[0]
    if status != 200 or not cookie:
        raise SystemExit(f"login failed: HTTP {status}")
    auth = {"Cookie": cookie}

    status, _, raw = http("POST", args.base + "/api/uploads", body={"count": args.count}, headers=auth)
    if status != 201:
        raise SystemExit(f"open upload failed: HTTP {status} {raw[:200]!r}")
    batch_id = json.loads(raw)["batch_id"]

    t0 = time.perf_counter()
    started_at = now_iso()
    photos = []
    for path in files:
        body, extra = multipart(path.name, path.read_bytes())
        t = time.perf_counter()
        status, _, raw = http("POST", f"{args.base}/api/uploads/{batch_id}/photos", body=body, headers={**auth, **extra})
        if status != 201:
            raise SystemExit(f"upload {path.name} failed: HTTP {status} {raw[:200]!r}")
        photos.append({"file": path.name, "id": json.loads(raw)["id"],
                       "accepted_after_s": round(time.perf_counter() - t0, 3),
                       "upload_http_s": round(time.perf_counter() - t, 3)})
    all_uploaded_s = round(time.perf_counter() - t0, 3)
    print(f"uploaded {len(photos)} photos in {all_uploaded_s} s (batch {batch_id})", flush=True)

    # poll the web until nothing is waiting
    timeline, last = [], None
    done_seen: dict[str, float] = {}
    while True:
        status, _, raw = http("GET", f"{args.base}/api/uploads/{batch_id}", headers=auth)
        data = json.loads(raw) if status == 200 else {}
        rows = data.get("photos", [])
        counts = {}
        for p in rows:
            counts[p["status"]] = counts.get(p["status"], 0) + 1
            if p["status"] in ("DONE", "FAILED") and p["id"] not in done_seen:
                done_seen[p["id"]] = round(time.perf_counter() - t0, 3)
        elapsed = round(time.perf_counter() - t0, 2)
        if counts != last:
            timeline.append({"t_s": elapsed, "utc": now_iso(), **counts})
            print(f"  t={elapsed:7.2f}s {counts}", flush=True)
            last = counts
        if rows and not (counts.get("QUEUED", 0) + counts.get("PROCESSING", 0)):
            break
        if elapsed > args.timeout:
            print("TIMEOUT waiting for results", flush=True)
            break
        time.sleep(0.25)
    all_finished_s = max(done_seen.values()) if done_seen else None

    ids = [p["id"] for p in photos]
    id_list = ",".join(f"'{i}'" for i in ids)
    db_rows = psql_json(
        "SELECT json_agg(t) FROM (SELECT p.id, p.status, p.dispatch_state, p.model_h, p.model_v, p.model_result,"
        " p.current_result, p.model_version, p.conf_threshold::float8 AS conf_threshold, p.image_w, p.image_h,"
        " p.submit_attempts, p.fail_reason,"
        " round(extract(epoch FROM (p.submitted_at - p.accepted_at))::numeric, 3)::float8 AS accept_to_submit_s,"
        " round(extract(epoch FROM (p.finished_at - p.accepted_at))::numeric, 3)::float8 AS accept_to_finish_s,"
        " (SELECT coalesce(json_agg(json_build_object('cls', d.cls, 'confidence', d.confidence::float8,"
        "   'box', json_build_array(d.x1, d.y1, d.x2, d.y2)) ORDER BY d.id), '[]'::json)"
        "    FROM detections d WHERE d.photo_id = p.id) AS detections"
        f" FROM photos p WHERE p.id IN ({id_list})) t") or []
    db = {r["id"]: r for r in db_rows}

    key = env_value(ROOT / ".env", "GATEWAY_API_KEY")
    gw_url = env_value(ROOT / "app" / ".env", "GATEWAY_URL")
    ctx = ssl.create_default_context(cafile=str(ROOT / "results" / "deploy" / "gateway_ca.crt"))
    gw = {}
    for start in range(0, len(ids), 50):
        status, _, raw = http("GET", f"{gw_url}/v1/jobs?ids={','.join(ids[start:start + 50])}",
                              headers={"X-API-Key": key}, context=ctx)
        if status != 200:
            raise SystemExit(f"gateway GET /v1/jobs failed: HTTP {status}")
        for job in json.loads(raw)["jobs"]:
            gw[job["job_id"]] = job

    def sig(dets):
        return sorted((d["cls"], round(float(d["confidence"]), 6), tuple(d["box"])) for d in dets)

    mismatches, table = [], []
    for p in photos:
        row, job = db.get(p["id"]), gw.get(p["id"])
        res = (job or {}).get("result") or {}
        entry = {"file": p["file"], "id": p["id"],
                 "web_status": row and row["status"], "gateway_status": job and job["status"],
                 "db": row and {k: row[k] for k in ("model_h", "model_v", "model_result", "model_version",
                                                    "conf_threshold", "image_w", "image_h")},
                 "db_boxes": row and len(row["detections"]),
                 "gateway": {k: res.get(k) for k in ("h", "v", "model_version", "conf_threshold", "image_w", "image_h", "infer_ms")},
                 "gateway_boxes": len(res.get("detections", [])),
                 "accept_to_submit_s": row and row["accept_to_submit_s"],
                 "accept_to_finish_s": row and row["accept_to_finish_s"],
                 "submit_attempts": row and row["submit_attempts"],
                 "seen_done_by_client_s": done_seen.get(p["id"])}
        problems = []
        if not row or not job:
            problems.append("missing in db or gateway")
        elif row["status"] != "DONE" or job["status"] != "DONE":
            problems.append(f"status web={row['status']} gateway={job['status']}")
        else:
            pairs = [("model_h", "h"), ("model_v", "v"), ("model_version", "model_version"),
                     ("image_w", "image_w"), ("image_h", "image_h")]
            problems += [f"{a}: db={row[a]} gateway={res.get(b)}" for a, b in pairs if row[a] != res.get(b)]
            if abs(float(row["conf_threshold"]) - float(res.get("conf_threshold", -1))) > 1e-9:
                problems.append("conf_threshold differs")
            if sig(row["detections"]) != sig(res.get("detections", [])):
                problems.append("detections differ")
            if len(row["detections"]) != row["model_h"] + row["model_v"]:
                problems.append("box count != H + V")
        entry["match"] = not problems
        entry["problems"] = problems
        mismatches += problems
        table.append(entry)

    infer = [e["gateway"]["infer_ms"] for e in table if e["gateway"].get("infer_ms") is not None]
    waits = [e["accept_to_finish_s"] for e in table if e["accept_to_finish_s"] is not None]
    summary = {
        "test": f"{args.count} photos through the web API", "started_utc": started_at, "base": args.base,
        "user": email, "batch_id": batch_id, "photos": len(photos),
        "done_in_web": sum(1 for e in table if e["web_status"] == "DONE"),
        "done_in_gateway": sum(1 for e in table if e["gateway_status"] == "DONE"),
        "matching_db_vs_gateway": sum(1 for e in table if e["match"]),
        "all_uploaded_s": all_uploaded_s,
        "first_upload_to_last_result_s": all_finished_s,
        "per_photo_accept_to_finish_s": {"min": min(waits), "max": max(waits), "mean": round(sum(waits) / len(waits), 3)} if waits else None,
        "gpu_infer_ms": {"min": min(infer), "max": max(infer), "mean": round(sum(infer) / len(infer), 1)} if infer else None,
        "timeline": timeline, "items": table,
    }
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("items", "timeline")}, ensure_ascii=False, indent=1))
    for e in table:
        print(f"  {'OK ' if e['match'] else 'BAD'} {e['file'][:28]:28} db H={e['db'] and e['db']['model_h']} V={e['db'] and e['db']['model_v']}"
              f" {e['db'] and e['db']['model_result']} boxes={e['db_boxes']} | gw H={e['gateway']['h']} V={e['gateway']['v']}"
              f" boxes={e['gateway_boxes']} infer={e['gateway']['infer_ms']}ms | wait={e['accept_to_finish_s']}s {e['problems'] or ''}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
