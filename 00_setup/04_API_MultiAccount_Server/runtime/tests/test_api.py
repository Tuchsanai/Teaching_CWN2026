import asyncio
import json
import logging

import httpx
import pytest

from conftest import AUTH, TOKEN, chat
from app.config import Settings
from app.main import create_app


# ---------- static page / health / auth ----------

def test_health_needs_no_token(env):
    r = env.client().get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_index_missing_gives_readable_error(env):
    r = env.client().get("/")
    assert r.status_code == 503
    assert "index.html" in r.text and "text/html" in r.headers["content-type"]


def test_index_served_when_present(env):
    (env.web_dir / "index.html").write_text("<h1>chat page</h1>")
    r = env.client().get("/")
    assert r.status_code == 200 and "chat page" in r.text


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong-token-xxxxxxxx"},
                                     {"Authorization": f"Basic {TOKEN}"}])
def test_v1_requires_bearer_token(env, headers):
    c = env.client()
    for r in (c.get("/v1/models", headers=headers),
              c.post("/v1/chat/completions", json={"messages": []}, headers=headers)):
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "invalid_token"


def test_no_token_configured_fails_closed(env):
    r = env.client(API_TOKEN="").get("/v1/models", headers=AUTH)
    assert r.status_code == 503


def test_unknown_route_is_readable(env):
    r = env.client().get("/nope")
    assert r.status_code == 404 and r.json()["error"]["message"] == "Not found."


# ---------- /v1/models ----------

def test_models_catalog(env):
    body = env.client().get("/v1/models", headers=AUTH).json()
    models = {m["id"]: m for m in body["data"]}
    assert set(models) == {"fable", "opus", "gpt-6-astra", "gpt-6-sol", "gpt-6-luna"}
    five = ["low", "medium", "high", "xhigh", "max"]
    assert models["fable"]["reasoning_efforts"] == five
    assert models["opus"]["reasoning_efforts"] == five
    assert models["gpt-6-astra"]["reasoning_efforts"] == five
    assert models["gpt-6-sol"]["reasoning_efforts"] == ["none"] + five
    assert models["gpt-6-luna"]["reasoning_efforts"] == ["none"] + five
    assert models["fable"]["provider"] == "claude" and models["gpt-6-sol"]["provider"] == "codex"
    # only ready accounts of the right provider; cross-provider names in config are dropped
    assert models["opus"]["accounts"] == ["yolo1", "yolo3"]
    assert models["gpt-6-luna"]["accounts"] == ["cyolo1"]
    claude = {a["name"]: a for a in body["accounts"]["claude"]}
    assert set(claude) == {"yolo1", "yolo2", "yolo3"}
    assert claude["yolo1"]["default"] and not claude["yolo2"]["ready"]
    assert [a["name"] for a in body["accounts"]["codex"]] == ["cyolo1"]
    assert str(env.accounts) not in json.dumps(body)  # no internal paths
    assert body["limits"] == {"max_messages": 5, "max_message_chars": 200, "max_total_chars": 600,
                              "max_body_bytes": 4096, "timeout_seconds": 10}


# ---------- chat: happy paths ----------

def test_claude_chat_openai_shape_and_safe_flags(env):
    r = chat(env.client(), "hi there", model="fable", reasoning_effort="high")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"] == {"role": "assistant",
                                             "content": "FAKE-CLAUDE model=fable effort=high n=1 last=hi there"}
    assert body["account"] == "yolo1" and body["provider"] == "claude"
    assert body["usage"] == {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}

    call = env.last_call(".Claude", "yolo1")
    argv = call["argv"]
    assert argv[0] == "-p" and argv[argv.index("--tools") + 1] == ""
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    for flag in ("--strict-mcp-config", "--disable-slash-commands", "--safe-mode", "--no-session-persistence"):
        assert flag in argv
    assert not any("dangerously" in a or a == "bypassPermissions" for a in argv)
    assert call["env"]["CLAUDE_CONFIG_DIR"] == str(env.accounts / ".Claude" / "yolo1")
    assert "ANTHROPIC_API_KEY" not in call["env"] and "API_TOKEN" not in call["env"]
    assert "IS_SANDBOX" not in call["env"]


def test_opus_on_second_claude_account(env):
    r = chat(env.client(), "x", model="opus", reasoning_effort="max", account="yolo3", provider="claude")
    assert r.status_code == 200, r.text
    assert "model=opus effort=max" in r.json()["choices"][0]["message"]["content"]
    assert env.last_call(".Claude", "yolo3")["env"]["CLAUDE_CONFIG_DIR"].endswith("/.Claude/yolo3")


@pytest.mark.parametrize("model,effort", [("gpt-6-sol", "none"), ("gpt-6-luna", "none"),
                                          ("gpt-6-astra", "xhigh"), ("gpt-6-luna", "max")])
def test_codex_chat_and_tools_disabled(env, model, effort):
    r = chat(env.client(), "yo", model=model, reasoning_effort=effort)
    assert r.status_code == 200, r.text
    assert r.json()["choices"][0]["message"]["content"] == f"FAKE-CODEX model={model} effort={effort} n=1 last=yo"
    call = env.last_call(".Codex", "cyolo1")
    argv = call["argv"]
    assert argv[0] == "exec" and argv[-1] == "-"
    assert f'model_reasoning_effort="{effort}"' in argv
    assert argv[argv.index("--sandbox") + 1] == "read-only"
    for f in ("shell_tool", "unified_exec", "apps", "plugins", "browser_use", "computer_use"):
        assert argv[argv.index(f) - 1] == "--disable"
    for flag in ("--strict-config", "--ignore-user-config", "--ephemeral"):
        assert flag in argv
    assert 'web_search="disabled"' in argv
    assert not any("dangerously" in a or a == "danger-full-access" for a in argv)
    assert call["env"]["CODEX_HOME"] == str(env.accounts / ".Codex" / "cyolo1")
    assert "OPENAI_API_KEY" not in call["env"]


def test_full_history_is_sent(env):
    msgs = [{"role": "system", "content": "be brief"},
            {"role": "user", "content": "my name is Nok"},
            {"role": "assistant", "content": "hi Nok"},
            {"role": "user", "content": [{"type": "text", "text": "what is my name?"}]}]
    r = env.client().post("/v1/chat/completions", json={"messages": msgs, "model": "opus"}, headers=AUTH)
    assert r.status_code == 200, r.text
    assert "n=4 last=what is my name?" in r.json()["choices"][0]["message"]["content"]
    stdin = env.last_call(".Claude", "yolo1")["stdin"]
    for text in ("be brief", "my name is Nok", "hi Nok", "what is my name?"):
        assert text in stdin


def test_defaults_apply(env):
    r = chat(env.client())
    assert r.status_code == 200
    assert r.json()["model"] == "fable" and r.json()["reasoning_effort"] == "medium"


def test_extra_openai_fields_ignored(env):
    r = chat(env.client(), "x", model="fable", temperature=0.2, max_tokens=10, stream=False)
    assert r.status_code == 200


# ---------- chat: rejected combinations ----------

@pytest.mark.parametrize("fields,needle", [
    ({"model": "gpt-6-astra", "reasoning_effort": "none"}, "not supported by model 'gpt-6-astra'"),
    ({"model": "fable", "reasoning_effort": "none"}, "not supported by model 'fable'"),
    ({"model": "opus", "reasoning_effort": "ultra"}, "Allowed: low, medium, high, xhigh, max"),
    ({"model": "opus", "account": "cyolo1"}, "is a codex account and cannot be used with claude"),
    ({"model": "gpt-6-luna", "account": "yolo1"}, "is a claude account and cannot be used with codex"),
    ({"model": "fable", "provider": "codex"}, "belongs to provider 'claude'"),
    ({"model": "gpt-6-sol", "provider": "openai"}, "unknown provider"),
    ({"model": "gpt-5.5"}, "unknown model 'gpt-5.5'"),
    ({"model": "fable", "account": "yolo4"}, "not enabled"),
    ({"model": "gpt-6-sol", "account": "cyolo2"}, "not enabled"),
    ({"model": "fable", "account": "yolo2"}, "no login data"),
    ({"model": "fable", "account": "../yolo1"}, "unknown account"),
])
def test_rejected_selection(env, fields, needle):
    r = chat(env.client(), "x", **fields)
    assert r.status_code == 400
    assert needle in r.json()["error"]["message"]


# ---------- chat: request limits and validation ----------

def test_too_many_messages(env):
    msgs = [{"role": "user", "content": "a"}] * 6
    r = env.client().post("/v1/chat/completions", json={"messages": msgs}, headers=AUTH)
    assert r.status_code == 400 and "Too many messages" in r.json()["error"]["message"]


def test_message_too_long(env):
    r = chat(env.client(), "a" * 201)
    assert r.status_code == 400 and "longer than 200" in r.json()["error"]["message"]


def test_conversation_too_long(env):
    msgs = [{"role": "user", "content": "a" * 150}] * 5
    r = env.client().post("/v1/chat/completions", json={"messages": msgs}, headers=AUTH)
    assert r.status_code == 400 and "600 characters in total" in r.json()["error"]["message"]


def test_body_too_large(env):
    r = chat(env.client(), "a" * 5000)
    assert r.status_code == 413 and r.json()["error"]["code"] == "request_too_large"


def test_body_too_large_without_content_length(env):
    def gen():
        yield b'{"messages": [{"role": "user", "content": "'
        for _ in range(10):
            yield b"a" * 1000
        yield b'"}]}'
    r = env.client().post("/v1/chat/completions", content=gen(),
                          headers={**AUTH, "Content-Type": "application/json"})
    assert r.status_code == 413


@pytest.mark.parametrize("body,needle", [
    ({"messages": []}, "messages"),
    ({"messages": [{"role": "tool", "content": "x"}]}, "role"),
    ({"messages": [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "x"}}]}]}, "content"),
    ({"messages": [{"role": "user", "content": "q"}, {"role": "assistant", "content": "a"}]}, "last message"),
    ({"messages": [{"role": "user", "content": "  "}]}, "empty"),
    ({"messages": [{"role": "user", "content": "q"}], "stream": True}, "Streaming is not supported"),
])
def test_invalid_requests_are_readable(env, body, needle):
    r = env.client().post("/v1/chat/completions", json=body, headers=AUTH)
    assert r.status_code == 400
    assert needle in r.json()["error"]["message"]


def test_invalid_json(env):
    r = env.client().post("/v1/chat/completions", content=b"{not json",
                          headers={**AUTH, "Content-Type": "application/json"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "invalid_request"


# ---------- chat: CLI failures never leak internals, never return fake answers ----------

@pytest.mark.parametrize("model", ["fable", "gpt-6-sol"])
def test_auth_failure(env, model):
    r = chat(env.client(), "__AUTH_FAIL__", model=model)
    assert r.status_code == 503 and r.json()["error"]["code"] == "account_auth_failed"
    assert "SECRET-STDERR-DETAIL" not in r.text and "Not logged in" not in r.text
    assert "choices" not in r.json()


def test_rate_limited(env):
    r = chat(env.client(), "__RATE__", model="fable")
    assert r.status_code == 429


@pytest.mark.parametrize("model", ["fable", "gpt-6-luna"])
def test_empty_answer_is_an_error(env, model):
    r = chat(env.client(), "__EMPTY__", model=model)
    assert r.status_code == 502 and "choices" not in r.json()


def test_output_cap(env):
    r = chat(env.client(), "__HUGE__", model="fable")
    assert r.status_code == 502 and r.json()["error"]["code"] == "model_output_too_large"


def test_timeout_kills_cli(env):
    r = chat(env.client(CLI_TIMEOUT_SECONDS="1"), "__SLEEP__", model="fable")
    assert r.status_code == 504 and "within 1 seconds" in r.json()["error"]["message"]
    assert list((env.root / "work").iterdir()) == []  # per-call temp dir cleaned up


def test_cli_missing(env):
    r = chat(env.client(CLAUDE_BIN=str(env.root / "missing-claude")), "x", model="fable")
    assert r.status_code == 502  # launcher exec fails -> no answer, generic message
    assert str(env.root) not in r.text


def test_busy_server(env, monkeypatch):
    for k, v in {"MAX_CONCURRENT_CALLS": "1", "QUEUE_TIMEOUT_SECONDS": "1", "CLI_TIMEOUT_SECONDS": "3"}.items():
        monkeypatch.setenv(k, v)
    app = create_app(Settings.from_env())

    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t", timeout=20) as c:
            body = lambda t: {"messages": [{"role": "user", "content": t}]}  # noqa: E731
            slow = asyncio.create_task(c.post("/v1/chat/completions", json=body("__SLEEP__"), headers=AUTH))
            await asyncio.sleep(0.3)
            fast = await c.post("/v1/chat/completions", json=body("hi"), headers=AUTH)
            return (await slow).status_code, fast

    slow_status, fast = asyncio.run(go())
    assert slow_status == 504
    assert fast.status_code == 429 and fast.json()["error"]["code"] == "server_busy"


def test_logs_have_no_token_or_content(env, caplog):
    caplog.set_level(logging.DEBUG)
    c = env.client()
    chat(c, "very-private-question", model="fable")
    chat(c, "__AUTH_FAIL__", model="gpt-6-sol")
    text = caplog.text
    assert TOKEN not in text and "very-private-question" not in text and "SECRET-STDERR-DETAIL" not in text
    assert "yolo1" in text  # but the call itself is logged
