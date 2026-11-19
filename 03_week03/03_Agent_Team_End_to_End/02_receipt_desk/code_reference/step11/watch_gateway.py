"""Step 11 · record what the gateway answers for a web batch, before the dispatcher deletes it (G7).
Polls G4 GET /v1/jobs/{batch_id} every 0.5 s (same call the dispatcher makes) and keeps the last
result of each receipt. The API key is read from ../.env and never printed.
usage: python watch_gateway.py <batch_id> <out.json> [timeout_s]"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
key = next(l.split("=", 1)[1].strip() for l in open(ROOT / ".env") if l.startswith("GATEWAY_API_KEY="))
env = dict(l.strip().split("=", 1) for l in open(ROOT / "app" / ".env") if "=" in l)
base = env["GATEWAY_URL"].rstrip("/")
batch, out = sys.argv[1], Path(sys.argv[2]); limit = float(sys.argv[3]) if len(sys.argv) > 3 else 900
seen, t0 = {}, time.time()
while time.time() - t0 < limit:
    try:
        req = urllib.request.Request(f"{base}/v1/jobs/{batch}", headers={"X-API-Key": key})
        job = json.load(urllib.request.urlopen(req, timeout=10))
        for r in job.get("receipts", []):
            prev = seen.get(r["receipt_ref"], {})
            if r.get("status") != prev.get("status"):
                r["_seen_at_s"] = round(time.time() - t0, 1)
                print(f"{r['_seen_at_s']:7.1f}s {r['receipt_ref'][:8]} {r.get('status')}", flush=True)
            if r.get("status") in ("done", "unreadable", "failed") or "result" in r:
                r.setdefault("_seen_at_s", prev.get("_seen_at_s"))
            seen[r["receipt_ref"]] = {**prev, **r}
        out.write_text(json.dumps(seen, indent=1, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        if e.code == 404 and seen: break      # job gone = dispatcher cleaned everything up
    except Exception as e:
        print("poll error", type(e).__name__, flush=True)
    time.sleep(0.5)
print("watch finished", len(seen), "receipts")
