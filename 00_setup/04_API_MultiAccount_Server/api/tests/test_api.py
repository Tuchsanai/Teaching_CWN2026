"""Unit tests with fake CLIs. No real account, network or credential is used.

Run from the api/ folder:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

FAKES = Path(__file__).parent / "fakes"
WRAPPER = Path(__file__).resolve().parent.parent / "wrappers" / "lab04-cli"
TOKEN = "test-token-123"
ORIGIN = "http://127.0.0.1:8005"


def make_settings(root: Path, **over) -> Settings:
    s = Settings(
        api_token_sha256=hashlib.sha256(TOKEN.encode()).hexdigest(),
        cors_origins=(ORIGIN, "http://localhost:8005"),
        accounts={"claude": ("yolo1", "yolo2"), "codex": ("cyolo1",)},
        accounts_root=root / "accounts",
        work_root=root / "work",
        app_home=root / "home",
        wrapper_dir=root / "bin",
        claude_bin=str(FAKES / "fake_claude"),
        codex_bin=str(FAKES / "fake_codex"),
        codex_sandbox="read-only",
        cli_timeout_s=20,
        max_messages=40,
        max_message_chars=8000,
        max_transcript_chars=48000,
        max_output_chars=24000,
        max_stdout_bytes=1_048_576,
        max_body_bytes=262_144,
        per_account_concurrency=1,
        max_concurrency=4,
        queue_wait_s=0,
    )
    return dataclasses.replace(s, **over)


def install_wrappers(root: Path, names=("yolo1", "yolo2", "cyolo1", "yolo9")) -> None:
    """Symlinks like the image's /opt/lab04/bin/yoloN -> lab04-cli."""
    (root / "bin").mkdir(exist_ok=True)
    (root / "home").mkdir(exist_ok=True)
    for n in names:
        (root / "bin" / n).symlink_to(WRAPPER)


def provision(root: Path, provider: str, account: str) -> None:
    d = root / "accounts" / provider / account
    d.mkdir(parents=True)
    name = ".credentials.json" if provider == "claude" else "auth.json"
    (d / name).write_text("{}")  # placeholder, never a real credential


AUTH = {"Authorization": f"Bearer {TOKEN}"}


def chat_body(model="fable", effort="medium", **extra):
    body = {"model": model, "reasoning_effort": effort,
            "messages": [{"role": "user", "content": "สวัสดี ชื่อฉันคือ Mali"},
                         {"role": "assistant", "content": "สวัสดีค่ะ Mali"},
                         {"role": "user", "content": "ฉันชื่ออะไร"}]}
    body.update(extra)
    return body


class APITest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        provision(self.root, "claude", "yolo1")
        provision(self.root, "codex", "cyolo1")
        install_wrappers(self.root)
        self.settings = make_settings(self.root)
        self.client = TestClient(create_app(self.settings))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tmp.cleanup()

    def reply(self, r) -> dict:
        self.assertEqual(r.status_code, 200, r.text)
        return json.loads(r.json()["choices"][0]["message"]["content"])

    # --- health / auth / models -------------------------------------------

    def test_health_is_public_and_has_no_account_info(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertTrue(j["cli"]["claude"]["available"])
        self.assertEqual(j["cli"]["codex"]["version"], "codex-cli 9.9.9")  # via cyolo1 --version
        self.assertNotIn("yolo1", r.text)

    def test_models_requires_token(self):
        self.assertEqual(self.client.get("/v1/models").status_code, 401)
        r = self.client.get("/v1/models", headers={"Authorization": "Bearer wrong"})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json()["error"]["type"], "unauthorized")

    def test_models_capabilities(self):
        j = self.client.get("/v1/models", headers=AUTH).json()
        m = {x["id"]: x for x in j["data"]}
        self.assertEqual(set(m), {"fable", "opus", "gpt-6-astra", "gpt-6-sol", "gpt-6-luna"})
        five = ["low", "medium", "high", "xhigh", "max"]
        for k in ("fable", "opus", "gpt-6-astra"):
            self.assertEqual(m[k]["reasoning_efforts"], five)
        for k in ("gpt-6-sol", "gpt-6-luna"):
            self.assertEqual(m[k]["reasoning_efforts"], ["none"] + five)
        self.assertNotIn("max_completion_tokens", j["supported_parameters"])
        accts = {p["id"]: p["accounts"] for p in j["providers"]}
        self.assertEqual([a["id"] for a in accts["claude"]], ["yolo1", "yolo2"])
        self.assertTrue(accts["claude"][0]["default"])
        self.assertTrue(accts["claude"][0]["credential_file_present"])
        self.assertFalse(accts["claude"][1]["credential_file_present"])

    # --- successful calls ----------------------------------------------------

    def test_claude_call_uses_safe_argv_and_sends_history(self):
        r = self.client.post("/v1/chat/completions", headers=AUTH, json=chat_body("opus", "xhigh"))
        out = self.reply(r)
        argv = out["argv"]
        self.assertEqual(argv[:1], ["-p"])
        self.assertIn("--no-session-persistence", argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--model") + 1], "opus")
        self.assertEqual(argv[argv.index("--effort") + 1], "xhigh")
        self.assertNotIn("--dangerously-skip-permissions", argv)
        self.assertFalse(any("Mali" in a for a in argv), "prompt must go via stdin, not argv")
        self.assertIn("ฉันชื่ออะไร", out["prompt_tail"])
        self.assertIn('"role": "assistant"', out["prompt_tail"])
        self.assertIn("/work/req-", out["cwd"])
        env = out["env"]
        self.assertEqual(env["CLAUDE_CONFIG_DIR"], str(self.root / "accounts" / "claude" / "yolo1"))
        self.assertEqual(env["HOME"], str(self.root / "home"), "HOME must stay the fixed app home")
        self.assertTrue(env["TMPDIR"].startswith(str(self.root / "work" / "req-")))
        self.assertNotIn("API_TOKEN_SHA256", out["env_keys"])
        j = r.json()
        self.assertIsNone(j["usage"])
        self.assertEqual(j["x_backend"]["account"], "yolo1")
        self.assertEqual(j["x_backend"]["history_messages_sent"], 3)
        self.assertEqual(list((self.root / "work").iterdir()), [], "request dir must be removed")

    def test_codex_call_uses_sandbox_and_effort_none(self):
        r = self.client.post("/v1/chat/completions", headers=AUTH,
                             json=chat_body("gpt-6-sol", "none", provider="codex"))
        out = self.reply(r)
        argv = out["argv"]
        self.assertEqual(argv[0], "exec")
        self.assertEqual(out["env"]["CODEX_HOME"], str(self.root / "accounts" / "codex" / "cyolo1"))
        self.assertEqual(out["env"]["HOME"], str(self.root / "home"))
        self.assertTrue(argv[argv.index("-o") + 1].startswith(out["env"]["TMPDIR"] + "/"))
        self.assertEqual(argv[argv.index("-C") + 1], out["cwd"])
        self.assertIn("model_reasoning_effort=none", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertIn("--ephemeral", argv)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)
        self.assertEqual(argv[-1], "-")
        self.assertEqual(r.json()["x_backend"]["provider"], "codex")

    def test_default_effort_and_account(self):
        r = self.client.post("/v1/chat/completions", headers=AUTH,
                             json={"model": "gpt-6-astra", "messages": [{"role": "user", "content": "hi"}]})
        self.assertEqual(r.json()["x_backend"]["reasoning_effort"], "medium")
        self.assertEqual(r.json()["x_backend"]["account"], "cyolo1")

    def test_output_truncation(self):
        body = {"model": "fable", "messages": [{"role": "user", "content": "FAKE_BIG"}]}
        r = self.client.post("/v1/chat/completions", headers=AUTH, json=body)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["choices"][0]["message"]["content"]), 24000)
        self.assertEqual(r.json()["choices"][0]["finish_reason"], "length")

    # --- rejections ------------------------------------------------------------

    def post_err(self, body, status):
        r = self.client.post("/v1/chat/completions", headers=AUTH, json=body)
        self.assertEqual(r.status_code, status, r.text)
        return r.json()["error"]

    def test_invalid_efforts_rejected(self):
        for model, effort in [("gpt-6-astra", "none"), ("fable", "none"), ("opus", "minimal"),
                              ("gpt-6-luna", "minimal"), ("fable", "ultra")]:
            with self.subTest(model=model, effort=effort):
                e = self.post_err(chat_body(model, effort), 400)
                self.assertEqual(e["type"], "unsupported_reasoning_effort")

    def test_unknown_model_rejected(self):
        self.assertEqual(self.post_err(chat_body("sonnet"), 400)["type"], "unsupported_model")

    def test_max_completion_tokens_and_friends_rejected(self):
        for k, v in [("max_completion_tokens", 100), ("max_tokens", 100), ("temperature", 0.2), ("tools", [])]:
            with self.subTest(k=k):
                e = self.post_err(chat_body(**{k: v}), 400)
                self.assertEqual(e["type"], "unsupported_parameter")
                self.assertEqual(e["param"], k)

    def test_stream_true_rejected(self):
        self.assertEqual(self.post_err(chat_body(stream=True), 400)["param"], "stream")

    def test_account_boundaries(self):
        self.assertEqual(self.post_err(chat_body(account="yolo9"), 400)["type"], "unknown_account")
        # a Claude account name is not valid for a Codex model
        self.assertEqual(self.post_err(chat_body("gpt-6-astra", account="yolo1"), 400)["type"], "unknown_account")
        # configured but no credential copy in the volume
        self.assertEqual(self.post_err(chat_body(account="yolo2"), 503)["type"], "account_not_provisioned")

    def test_provider_mismatch(self):
        self.assertEqual(self.post_err(chat_body("fable", provider="codex"), 400)["type"],
                         "provider_model_mismatch")

    def test_message_rules(self):
        e = self.post_err({"model": "fable", "messages": [{"role": "assistant", "content": "x"}]}, 400)
        self.assertEqual(e["type"], "invalid_messages")
        e = self.post_err({"model": "fable", "messages": [
            {"role": "user", "content": "a"}, {"role": "system", "content": "b"},
            {"role": "user", "content": "c"}]}, 400)
        self.assertEqual(e["type"], "invalid_messages")
        e = self.post_err({"model": "fable", "messages": [{"role": "tool", "content": "x"}]}, 400)
        self.assertEqual(e["type"], "invalid_request")
        e = self.post_err({"model": "fable", "messages": [{"role": "user", "content": "x" * 8001}]}, 400)
        self.assertEqual(e["type"], "message_too_long")
        many = [{"role": "user", "content": "y" * 7000} for _ in range(8)]
        self.assertEqual(self.post_err({"model": "fable", "messages": many}, 400)["type"], "transcript_too_long")

    def test_validation_errors_do_not_echo_content(self):
        e = self.post_err({"model": "fable", "messages": [{"role": "user", "content": ["SECRET-ARRAY"]}]}, 400)
        self.assertNotIn("SECRET-ARRAY", json.dumps(e))

    def test_body_limit(self):
        r = self.client.post("/v1/chat/completions", headers={**AUTH, "Content-Type": "application/json"},
                             content=b"{" + b" " * 300_000 + b"}")
        self.assertEqual(r.status_code, 413)

    def test_body_limit_without_content_length(self):
        # A generator body is sent chunked: no Content-Length for the middleware to check.
        sent = []

        def chunks():
            for _ in range(40):                       # 40 x 16 KiB = 640 KiB > 256 KiB cap
                sent.append(1)
                yield b" " * 16384

        r = self.client.post("/v1/chat/completions",
                             headers={**AUTH, "Content-Type": "application/json"}, content=chunks())
        self.assertEqual(r.status_code, 413, r.text)
        self.assertEqual(r.json()["error"]["type"], "request_too_large")
        self.assertIsNone(r.request.headers.get("content-length"))

    def test_small_chunked_body_is_accepted(self):
        body = json.dumps(chat_body()).encode()
        r = self.client.post("/v1/chat/completions", headers={**AUTH, "Content-Type": "application/json"},
                             content=iter([body[:10], body[10:]]))
        self.assertEqual(r.status_code, 200, r.text)

    # --- CLI failures are redacted --------------------------------------------

    def test_claude_auth_failure_redacted(self):
        body = {"model": "fable", "messages": [{"role": "user", "content": "FAKE_AUTH_FAIL"}]}
        e = self.post_err(body, 502)
        self.assertEqual(e["type"], "upstream_auth_error")
        self.assertNotIn("SECRET-ish", json.dumps(e))

    def test_codex_errors_classified_from_error_lines_only(self):
        body = {"model": "gpt-6-astra", "messages": [{"role": "user", "content": "FAKE_RATE"}]}
        self.assertEqual(self.post_err(body, 429)["type"], "upstream_rate_limited")
        body = {"model": "gpt-6-astra", "messages": [{"role": "user", "content": "FAKE_AUTH_FAIL"}]}
        self.assertEqual(self.post_err(body, 502)["type"], "upstream_auth_error")

    def test_timeout(self):
        self.client.__exit__(None, None, None)
        self.client = TestClient(create_app(make_settings(self.root, cli_timeout_s=1)))
        self.client.__enter__()
        body = {"model": "fable", "messages": [{"role": "user", "content": "FAKE_SLEEP"}]}
        self.assertEqual(self.post_err(body, 504)["type"], "cli_timeout")

    def test_logs_never_contain_message_content(self):
        with self.assertLogs("lab04", level="INFO") as cm:
            self.client.post("/v1/chat/completions", headers=AUTH, json=chat_body())
            self.client.post("/v1/chat/completions", headers=AUTH,
                             json={"model": "fable", "messages": [{"role": "user", "content": "FAKE_AUTH_FAIL Mali"}]})
        joined = "\n".join(cm.output)
        self.assertNotIn("Mali", joined)
        self.assertNotIn(TOKEN, joined)
        self.assertIn('"model": "fable"', joined)

    # --- concurrency ------------------------------------------------------------

    def test_per_account_concurrency(self):
        results = {}

        def call(key, content, model="fable"):
            body = {"model": model, "messages": [{"role": "user", "content": content}]}
            results[key] = self.client.post("/v1/chat/completions", headers=AUTH, json=body).status_code

        slow = threading.Thread(target=call, args=("slow", "FAKE_SLEEP"))
        slow.start()
        threading.Event().wait(1.0)
        call("same_account", "hi")                     # claude/yolo1 busy -> 429
        call("other_account", "hi", "gpt-6-astra")     # codex/cyolo1 has its own slot
        slow.join()
        self.assertEqual(results["slow"], 200)
        self.assertEqual(results["same_account"], 429)
        self.assertEqual(results["other_account"], 200)

    # --- CORS ---------------------------------------------------------------------

    def test_cors_explicit_origin_only(self):
        pre = {"Origin": ORIGIN, "Access-Control-Request-Method": "POST",
               "Access-Control-Request-Headers": "authorization,content-type"}
        r = self.client.options("/v1/chat/completions", headers=pre)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["access-control-allow-origin"], ORIGIN)
        self.assertNotIn("access-control-allow-credentials", r.headers)
        bad = dict(pre, Origin="http://evil.example")
        r = self.client.options("/v1/chat/completions", headers=bad)
        self.assertNotEqual(r.headers.get("access-control-allow-origin"), "http://evil.example")
        r = self.client.options("/v1/chat/completions", headers=dict(pre, Origin="null"))
        self.assertNotIn("access-control-allow-origin", r.headers)


class WrapperTest(unittest.TestCase):
    """The container-local yoloN / cyoloN wrapper refuses anything outside its narrow interface."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        provision(self.root, "claude", "yolo1")
        provision(self.root, "codex", "cyolo1")
        install_wrappers(self.root, ("yolo1", "yolo2", "cyolo1", "yolo9"))
        (self.root / "bin" / "claude").symlink_to(WRAPPER)
        (self.root / "t").mkdir()
        self.env = {"PATH": "/usr/bin:/bin", "HOME": str(self.root / "home"), "TMPDIR": str(self.root / "t"),
                    "LAB04_ACCOUNTS_ROOT": str(self.root / "accounts"),
                    "LAB04_CLAUDE_BIN": str(FAKES / "fake_claude"), "LAB04_CODEX_BIN": str(FAKES / "fake_codex")}

    def tearDown(self):
        self.tmp.cleanup()

    def run_w(self, name, *args, env=None):
        return subprocess.run([str(self.root / "bin" / name), *args], input=b"hi", capture_output=True,
                              env={**self.env, **(env or {})}, cwd=self.root / "t", timeout=30)

    def test_ok_and_version(self):
        self.assertEqual(self.run_w("yolo1", "--model", "fable", "--effort", "low").returncode, 0)
        self.assertIn(b"Fake Claude", self.run_w("yolo1", "--version").stdout)

    def test_rejections(self):
        cases = [
            ("yolo1", ["--model", "fable", "--effort", "low", "--dangerously-skip-permissions"], 2),
            ("yolo1", ["--model", "fable", "--effort", "low", "--tools", "Bash"], 2),
            ("yolo1", ["--model", "fable; rm -rf /", "--effort", "low"], 2),
            ("yolo1", ["--model", "fable", "--effort", "minimal"], 2),
            ("yolo9", ["--model", "fable", "--effort", "low"], 2),        # not yolo1..yolo5
            ("claude", ["--version"], 2),                                 # only yoloN / cyoloN names
            ("yolo2", ["--model", "fable", "--effort", "low"], 3),        # allowed name, not provisioned
            ("cyolo1", ["--model", "gpt-6-astra", "--effort", "low", "--output-last-message", "/etc/x"], 2),
            ("cyolo1", ["--model", "gpt-6-astra", "--effort", "low"], 2),  # no output file
        ]
        for name, args, code in cases:
            with self.subTest(name=name, args=args):
                self.assertEqual(self.run_w(name, *args).returncode, code)

    def test_api_allowlist(self):
        r = self.run_w("yolo1", "--model", "fable", "--effort", "low", env={"LAB04_ALLOWED_ACCOUNTS": "yolo2,cyolo1"})
        self.assertEqual(r.returncode, 2)

    def test_auth_env_not_inherited(self):
        r = self.run_w("yolo1", "--model", "fable", "--effort", "low", env={"ANTHROPIC_API_KEY": "x"})
        self.assertNotIn("ANTHROPIC_API_KEY", json.loads(json.loads(r.stdout)["result"])["env_keys"])


class ConfigTest(unittest.TestCase):
    def test_fail_closed(self):
        from app.config import ConfigError, load_settings
        saved = dict(os.environ)
        try:
            os.environ.pop("API_TOKEN_SHA256", None)
            with self.assertRaises(ConfigError):
                load_settings()
            os.environ["API_TOKEN_SHA256"] = "a" * 64
            os.environ["CORS_ORIGINS"] = "*"
            with self.assertRaises(ConfigError):
                load_settings()
            os.environ["CORS_ORIGINS"] = "http://127.0.0.1:8005"
            os.environ["CODEX_SANDBOX"] = "danger-full-access"
            with self.assertRaises(ConfigError):
                load_settings()
            os.environ["CODEX_SANDBOX"] = "read-only"
            os.environ["CLAUDE_ACCOUNTS"] = "yolo1,../etc"
            with self.assertRaises(ConfigError):
                load_settings()
            os.environ["CLAUDE_ACCOUNTS"] = "yolo1"
            os.environ["CODEX_ACCOUNTS"] = "yolo1"          # a Claude name is not a Codex account
            with self.assertRaises(ConfigError):
                load_settings()
            os.environ["CODEX_ACCOUNTS"] = "cyolo1,cyolo2"
            st = load_settings()
            self.assertEqual(st.accounts["claude"], ("yolo1",))
            self.assertEqual(st.accounts["codex"], ("cyolo1", "cyolo2"))
        finally:
            os.environ.clear()
            os.environ.update(saved)


if __name__ == "__main__":
    unittest.main()
