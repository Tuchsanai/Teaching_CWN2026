#!/usr/bin/env python3
"""Basic HTTP check of the web side in the test profile (AI_MODE=mock, BUG_MODE=0).

    cp .env.test.example .env.test
    docker compose --env-file .env.test --profile test up -d --build
    python3 scripts/smoke_test.py --base http://127.0.0.1:3000 --test-key "$(grep ^TEST_RESET_KEY .env.test | cut -d= -f2)"

Python standard library only.  Every check prints PASS/FAIL; the exit code is the number
of failed checks.  The script resets the test data first (POST /api/test/reset), so never
point it at a production system (the reset route answers 404 there anyway).
Expected values come from docs/TEST-DATA.md (§1–§4) and docs/DESIGN.md (§5.2, §7).
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

# 32×24 JPEG used for every upload; mock-gateway takes H and V from the file name.
JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19i"
    "Z2hnPk1xeXBkeFxlZ2P/2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2Nj"
    "Y2NjY2NjY2P/wAARCAAYACADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUF"
    "BAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVW"
    "V1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi"
    "4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAEC"
    "AxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVm"
    "Z2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq"
    "8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCSiiivGPWCiiigAooooAKKKKAP/9k="
)

USERS = {
    "manager": ("manager@sitesafe.test", "Test-Manager-01", "manager", None),
    "sup.a": ("sup.a@sitesafe.test", "Test-SupA-01", "supervisor", "SITE-A"),
    "sup.b": ("sup.b@sitesafe.test", "Test-SupB-01", "supervisor", "SITE-B"),
    "sup.c": ("sup.c@sitesafe.test", "Test-SupC-01", "supervisor", "SITE-C"),
    "exec": ("exec@sitesafe.test", "Test-Exec-01", "executive", None),
}

# TEST-DATA §4 rows used here: file → (H, V, expected result)
UPLOADS = {
    "h1_v0.jpg": (1, 0, "FAIL"),
    "h0_v2.jpg": (0, 2, "FAIL"),
    "h0_v1.jpg": (0, 1, "WARN"),
    "h0_v0.jpg": (0, 0, "PASS"),
}

# TEST-DATA §3: (date, site) → taken, with result, pass, fail, sum H, rate text, red, edited, failed
REPORT = {
    ("2026-11-16", "SITE-A"): (300, 300, 269, 20, 15, "89.67", True, 0, 0),
    ("2026-11-16", "SITE-B"): (300, 300, 270, 20, 20, "90.00", False, 0, 0),
    ("2026-11-16", "SITE-C"): (300, 300, 271, 20, 20, "90.33", False, 0, 0),
    ("2026-11-17", "SITE-A"): (0, 0, 0, 0, 0, "ไม่มีข้อมูล", False, 0, 0),
    ("2026-11-17", "SITE-B"): (10, 10, 9, 0, 0, "90.00", False, 0, 0),
    ("2026-11-17", "SITE-C"): (10, 9, 9, 0, 0, "100.00", False, 0, 1),
    ("2026-11-18", "SITE-A"): (300, 300, 270, 19, 15, "90.00", False, 1, 0),
    ("2026-11-18", "SITE-B"): (12, 10, 8, 1, 1, "80.00", True, 0, 0),
    ("2026-11-18", "SITE-C"): (1, 1, 0, 1, 2, "0.00", True, 0, 0),
}
REPORT_FIELDS = ("taken", "with_result", "pass", "fail", "h_total", "pass_rate_text", "red", "edited", "failed")

failures = 0


def check(name: str, ok: bool, detail: str = "") -> bool:
    global failures
    if not ok:
        failures += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  · ' + detail) if detail else ''}")
    return ok


class Response:
    def __init__(self, status: int, headers, body: bytes):
        self.status, self.headers, self.body = status, headers, body

    def json(self):
        try:
            return json.loads(self.body.decode("utf-8"))
        except ValueError:
            return None


def request(base, method, path, *, body=None, headers=None, cookie=None, timeout=30) -> Response:
    headers = dict(headers or {})
    if cookie:
        headers["Cookie"] = cookie
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode()
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(base + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return Response(res.status, res.headers, res.read())
    except urllib.error.HTTPError as err:
        return Response(err.code, err.headers, err.read())


def multipart(filename: str, data: bytes, mime="image/jpeg"):
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    return body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}


def login(base, key) -> str | None:
    email, password, _, _ = USERS[key]
    res = request(base, "POST", "/api/auth/login", body={"email": email, "password": password})
    if res.status != 200:
        return None
    cookie = res.headers.get("Set-Cookie", "")
    return cookie.split(";", 1)[0] if cookie.startswith("sitesafe_session=") else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="http://127.0.0.1:3000")
    parser.add_argument("--test-key", required=True, help="TEST_RESET_KEY of the test profile")
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds to wait for mock results")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    # 1 · health
    res = request(base, "GET", "/api/health")
    health = res.json() or {}
    check("GET /api/health → 200 status ok", res.status == 200 and health.get("status") == "ok", json.dumps(health, ensure_ascii=False))
    check("health: ai_mode mock · dispatcher ok · gateway ok",
          health.get("ai_mode") == "mock" and health.get("dispatcher") == "ok" and health.get("gateway") == "ok")

    # 2 · reset
    check("reset with a wrong X-Test-Key → 401",
          request(base, "POST", "/api/test/reset", body={}, headers={"X-Test-Key": "wrong"}).status == 401)
    res = request(base, "POST", "/api/test/reset", body={}, headers={"X-Test-Key": args.test_key}, timeout=120)
    reset = res.json() or {}
    check("POST /api/test/reset → 200 · 3 sites · 5 users · 1233 photos · 1 override",
          res.status == 200 and (reset.get("sites"), reset.get("users"), reset.get("photos"), reset.get("overrides")) == (3, 5, 1233, 1),
          json.dumps(reset, ensure_ascii=False))

    # 3 · login of every account (3 roles)
    cookies = {}
    for key, (email, _, role, site) in USERS.items():
        cookie = login(base, key)
        me = request(base, "GET", "/api/auth/me", cookie=cookie).json() if cookie else None
        user = (me or {}).get("user", me or {})
        got_role = user.get("role")
        got_site = (user.get("site") or {}).get("code") if isinstance(user.get("site"), dict) else user.get("site_code")
        check(f"login {email} → role {role}" + (f" · site {site}" if site else ""),
              cookie is not None and got_role == role and (site is None or got_site == site),
              f"role={got_role} site={got_site}")
        cookies[key] = cookie
    res = request(base, "POST", "/api/auth/login", body={"email": "sup.a@sitesafe.test", "password": "wrong-password"})
    check("login with a wrong password → 401 without cookie (A-3)", res.status == 401 and not res.headers.get("Set-Cookie"))

    # 4 · uploads judged through dispatcher + mock-gateway (BR-01 … BR-03)
    sup = cookies["sup.a"]
    res = request(base, "POST", "/api/uploads", body={"count": len(UPLOADS)}, cookie=sup)
    batch_id = (res.json() or {}).get("batch_id")
    check("POST /api/uploads {count: 4} as sup.a → 201", res.status == 201 and bool(batch_id))
    photo_ids = {}
    for name in UPLOADS:
        body, headers = multipart(name, JPEG)
        res = request(base, "POST", f"/api/uploads/{batch_id}/photos", body=body, headers=headers, cookie=sup)
        check(f"upload {name} → 201", res.status == 201, f"HTTP {res.status}")
        photo_ids[name] = (res.json() or {}).get("id")

    deadline = time.monotonic() + args.timeout
    batch = {}
    while time.monotonic() < deadline:
        batch = request(base, "GET", f"/api/uploads/{batch_id}", cookie=sup).json() or {}
        counts = batch.get("counts", {})
        if counts.get("done", 0) + counts.get("failed", 0) >= len(UPLOADS):
            break
        time.sleep(0.5)
    by_name = {p.get("original_filename"): p for p in batch.get("photos", [])}
    for name, (h, v, expected) in UPLOADS.items():
        p = by_name.get(name, {})
        check(f"{name} → {expected}", p.get("status") == "DONE" and p.get("current_result") == expected
              and p.get("model_result") == expected and (p.get("h"), p.get("v")) == (h, v),
              f"status={p.get('status')} result={p.get('current_result')} H={p.get('h')} V={p.get('v')}")
        detail = (request(base, "GET", f"/api/photos/{photo_ids.get(name)}", cookie=sup).json() or {}).get("photo", {})
        boxes = detail.get("detections") or []
        check(f"{name}: detail shows {h + v} boxes ({h} NO_HARDHAT, {v} NO_VEST)",
              len(boxes) == h + v and sum(b.get("cls") == "NO_HARDHAT" for b in boxes) == h)

    # 5 · daily report (TEST-DATA §3) as manager, and as executive
    for date in ("2026-11-16", "2026-11-17", "2026-11-18"):
        rep = request(base, "GET", f"/api/reports/daily?date={date}", cookie=cookies["manager"]).json() or {}
        sites = {s["site"]["code"]: s for s in rep.get("sites", [])}
        check(f"report {date}: 3 sites · ready label", len(sites) == 3 and rep.get("ready") is True
              and rep.get("ready_label") == "รายงานประจำวันพร้อมแล้ว", rep.get("ready_label", ""))
        for code in ("SITE-A", "SITE-B", "SITE-C"):
            got = tuple(sites.get(code, {}).get(f) for f in REPORT_FIELDS)
            want = REPORT[(date, code)]
            check(f"report {date} {code} = TEST-DATA §3", got == want, f"got {got}")
    res = request(base, "GET", "/api/reports/daily?date=2026-11-16", cookie=cookies["exec"])
    check("executive opens the report → 200 with 3 sites (A-9)", res.status == 200 and len((res.json() or {}).get("sites", [])) == 3)
    res = request(base, "GET", "/api/reports/daily?date=2026-11-16", cookie=sup)
    sites = (res.json() or {}).get("sites", [])
    check("sup.a sees only SITE-A in the report (A-5)", res.status == 200 and [s["site"]["code"] for s in sites] == ["SITE-A"])

    # 6 · photo links are not public (FR-22)
    own = photo_ids.get("h0_v0.jpg")
    res = request(base, "GET", f"/api/photos/{own}/image")
    check("GET /api/photos/{id}/image without login → 401, no image bytes (A-2)",
          res.status == 401 and not res.body.startswith(b"\xff\xd8") and not res.headers.get("Content-Type", "").startswith("image/"),
          f"HTTP {res.status} {res.headers.get('Content-Type')}")
    res = request(base, "GET", f"/api/photos/{own}/image", cookie="sitesafe_session=forged-token")
    check("… with a forged session cookie → 401", res.status == 401 and not res.body.startswith(b"\xff\xd8"))
    res = request(base, "GET", f"/api/photos/{own}/image", cookie=sup)
    check("… as the owner supervisor → 200 image/jpeg · Cache-Control private, no-store",
          res.status == 200 and res.body == JPEG and res.headers.get("Content-Type") == "image/jpeg"
          and res.headers.get("Cache-Control") == "private, no-store")
    res = request(base, "GET", f"/api/photos/{own}/image", cookie=cookies["sup.b"])
    check("… as the supervisor of another site → 404 (A-4)", res.status == 404 and not res.body.startswith(b"\xff\xd8"))
    res = request(base, "GET", "/api/photos")
    check("GET /api/photos without login → 401 (A-1)", res.status == 401)
    res = request(base, "POST", "/api/uploads", body={"count": 1}, cookie=cookies["exec"])
    check("executive POST /api/uploads → 403 (A-7)", res.status == 403)
    res = request(base, "GET", "/logo.png")
    check("GET /logo.png → 200 image/png", res.status == 200 and res.body.startswith(b"\x89PNG"))

    print(f"\n{'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
