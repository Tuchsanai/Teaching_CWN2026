#!/usr/bin/env python3
"""Real API checks against the deployed app (no mocks). URL from .env APP_TEST_URL, token from
the owner-only token file; the token is never printed. Usage: python3 tests/e2e/api_check.py"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
env = {k: v for k, _, v in (l.partition("=") for l in (ROOT / ".env").read_text().splitlines() if "=" in l)}
BASE = env["APP_TEST_URL"].rstrip("/")
TOKEN = (ROOT / env.get("API_TOKEN_FILE", "secrets/api_token")).read_text().strip()
results = []


def call(path, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"} if body is not None else {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, method=method, headers=headers,
                                 data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, r.headers.get("content-type", ""), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("content-type", ""), e.read().decode()


def check(name, cond, detail=""):
    results.append(cond)
    print(f"{'PASS' if cond else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))


print(f"target: {BASE}")
s, ct, html = call("/")
ext = sorted(set(re.findall(r'(?:src|href)\s*=\s*"(https?:)?//[^"]+"', html) +
                 re.findall(r'@import|url\(\s*["\']?https?://', html)))
check("GET / returns HTML", s == 200 and "text/html" in ct and "<title>Multi-Account Chat</title>" in html, f"{s} {ct} {len(html)} bytes")
check("GET / has no external src/href/@import/url()", not re.search(r'(?:src|href)\s*=\s*"(?:https?:)?//', html)
      and not re.search(r'@import|url\(\s*["\']?(?:https?:)?//', html))
check("GET / CSP blocks external loads", "default-src 'none'" in html)
s, _, b = call("/health"); check("GET /health without token", s == 200 and json.loads(b) == {"status": "ok"}, b)
s, _, b = call("/v1/models"); check("GET /v1/models without token -> 401", s == 401, json.loads(b)["error"]["message"])
s, _, b = call("/v1/models", token="wrong-token-0000000000000"); check("GET /v1/models wrong token -> 401", s == 401, json.loads(b)["error"]["message"])
s, _, b = call("/v1/models", token=TOKEN)
m = json.loads(b) if s == 200 else {}
check("GET /v1/models with token", s == 200 and [x["id"] for x in m["data"]] == ["fable", "opus", "gpt-6-astra", "gpt-6-sol", "gpt-6-luna"],
      "accounts=" + json.dumps({p: [a["name"] for a in v] for p, v in m.get("accounts", {}).items()}))
body = {"messages": [{"role": "user", "content": "hi"}], "model": "gpt-6-astra", "reasoning_effort": "none"}
s, _, b = call("/v1/chat/completions", "POST", body, TOKEN)
check("unsupported effort -> readable 400", s == 400, json.loads(b)["error"]["message"])
body = {"messages": [{"role": "user", "content": "hi"}], "model": "gpt-9"}
s, _, b = call("/v1/chat/completions", "POST", body, TOKEN)
check("unsupported model -> readable 400", s == 400, json.loads(b)["error"]["message"])
body = {"messages": [{"role": "user", "content": "hi"}], "model": "opus", "account": "cyolo1"}
s, _, b = call("/v1/chat/completions", "POST", body, TOKEN)
check("cross-provider account -> readable 400", s == 400, json.loads(b)["error"]["message"])
print(f"{results.count(True)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
