import json
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

FAKE_BIN = Path(__file__).parent / "fake_bin"
TOKEN = "test-token-0123456789abcdef"
IMAGE_LAUNCHER = Path("/usr/local/bin/ai-account-launch")
LAUNCHER = IMAGE_LAUNCHER if IMAGE_LAUNCHER.exists() else ROOT / "docker" / "ai-account-launch"


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Isolated accounts volume, launcher dir and web dir; CLIs replaced by fakes."""
    base = tmp_path / "accounts"
    for provider, name, login in [(".Claude", "yolo1", ".credentials.json"),
                                  (".Claude", "yolo3", ".credentials.json"),
                                  (".Codex", "cyolo1", "auth.json")]:
        (base / provider / name).mkdir(parents=True)
        (base / provider / name / login).write_text("{}")
    (base / ".Claude" / "yolo2").mkdir(parents=True)  # enabled but never logged in

    launchers = tmp_path / "bin"
    launchers.mkdir()
    for n in range(1, 6):
        (launchers / f"yolo{n}").symlink_to(LAUNCHER)
        (launchers / f"cyolo{n}").symlink_to(LAUNCHER)

    web = tmp_path / "web"
    web.mkdir()
    values = {
        "API_TOKEN": TOKEN, "API_TOKEN_FILE": str(tmp_path / "no-such-secret"),
        "AI_ACCOUNTS_BASE": str(base), "LAUNCHER_DIR": str(launchers), "WEB_DIR": str(web),
        "WORK_ROOT": str(tmp_path / "work"),
        "CLAUDE_ACCOUNTS": "yolo1,yolo2,yolo3,cyolo2", "CODEX_ACCOUNTS": "cyolo1,yolo4",
        "CLAUDE_BIN": str(FAKE_BIN / "claude"), "CODEX_BIN": str(FAKE_BIN / "codex"),
        "CLI_TIMEOUT_SECONDS": "10", "MAX_MESSAGES": "5", "MAX_MESSAGE_CHARS": "200",
        "MAX_TOTAL_CHARS": "600", "MAX_BODY_BYTES": "4096",
        # must never reach the CLI: the launcher unsets it
        "ANTHROPIC_API_KEY": "should-not-leak", "OPENAI_API_KEY": "should-not-leak",
    }
    for k, v in values.items():
        monkeypatch.setenv(k, v)

    class Env:
        root = tmp_path
        accounts = base
        web_dir = web

        @staticmethod
        def client(**overrides):
            for k, v in overrides.items():
                monkeypatch.setenv(k, v)
            return TestClient(create_app(Settings.from_env()), raise_server_exceptions=False)

        @staticmethod
        def last_call(provider, account):
            return json.loads((base / provider / account / "last_call.json").read_text())

    return Env


AUTH = {"Authorization": f"Bearer {TOKEN}"}


def chat(client, content="hello", **fields):
    body = {"messages": [{"role": "user", "content": content}], **fields}
    return client.post("/v1/chat/completions", json=body, headers=AUTH)
