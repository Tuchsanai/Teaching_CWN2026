"""The in-container yoloN/cyoloN launcher, and the flags we rely on in the installed CLIs."""

import os
import shutil
import subprocess

import pytest

from conftest import FAKE_BIN, LAUNCHER
from app.runner import CODEX_DISABLED_FEATURES


def run_launcher(tmp_path, name, *args, base=None):
    link = tmp_path / name
    if not link.exists():
        link.symlink_to(LAUNCHER)
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "AI_ACCOUNTS_BASE": str(base or tmp_path / "acc"),
           "CLAUDE_BIN": str(FAKE_BIN / "claude"), "CODEX_BIN": str(FAKE_BIN / "codex"),
           "ANTHROPIC_API_KEY": "leak"}
    return subprocess.run([str(link), *args], env=env, input="", capture_output=True, text=True, timeout=20)


@pytest.mark.parametrize("flag", ["--dangerously-skip-permissions", "--allow-dangerously-skip-permissions",
                                  "--dangerously-bypass-approvals-and-sandbox", "bypassPermissions",
                                  "danger-full-access"])
def test_launcher_refuses_bypass_flags(tmp_path, flag):
    (tmp_path / "acc" / ".Claude" / "yolo1").mkdir(parents=True)
    (tmp_path / "acc" / ".Codex" / "cyolo1").mkdir(parents=True)
    for name in ("yolo1", "cyolo1"):
        r = run_launcher(tmp_path, name, "-p", flag)
        assert r.returncode == 2 and "refusing" in r.stderr


def test_launcher_needs_account_folder(tmp_path):
    r = run_launcher(tmp_path, "yolo2", "-p")
    assert r.returncode == 3 and "account folder not found" in r.stderr


def test_launcher_rejects_other_names(tmp_path):
    r = run_launcher(tmp_path, "yolo9", "-p")
    assert r.returncode == 2


def test_launcher_uses_own_config_folder(tmp_path):
    for p in (".Claude/yolo3", ".Codex/cyolo1"):
        (tmp_path / "acc" / p).mkdir(parents=True)
    assert run_launcher(tmp_path, "yolo3", "-p", "--model", "opus").returncode == 0
    import json
    call = json.loads((tmp_path / "acc/.Claude/yolo3/last_call.json").read_text())
    assert call["env"]["CLAUDE_CONFIG_DIR"] == str(tmp_path / "acc/.Claude/yolo3")
    assert "ANTHROPIC_API_KEY" not in call["env"]
    assert call["argv"] == ["-p", "--model", "opus"]  # model/effort flags pass through unchanged


# ---- flags used by app/runner.py exist in the CLIs actually installed (skipped outside the image)

def _installed(name):
    path = shutil.which(name, path="/usr/local/bin")
    if not path:
        pytest.skip(f"{name} CLI not installed here (runs inside the app image)")
    return path


def test_installed_versions_match_devtools():
    assert "2.1.281" in subprocess.run([_installed("claude"), "--version"], capture_output=True, text=True).stdout
    assert "0.156.1" in subprocess.run([_installed("codex"), "--version"], capture_output=True, text=True).stdout


def test_installed_claude_help_has_our_flags():
    out = subprocess.run([_installed("claude"), "--help"], capture_output=True, text=True).stdout
    for flag in ("--print", "--output-format", "--model", "--effort", "--tools", "--strict-mcp-config",
                 "--disable-slash-commands", "--setting-sources", "--safe-mode", "--permission-mode",
                 "--permission-prompts", "--no-session-persistence", "--system-prompt", "dontAsk", "xhigh"):
        assert flag in out, flag


def test_installed_codex_help_and_features(tmp_path):
    codex = _installed("codex")
    out = subprocess.run([codex, "exec", "--help"], capture_output=True, text=True).stdout
    for flag in ("--strict-config", "--ignore-user-config", "--ignore-rules", "--ephemeral",
                 "--skip-git-repo-check", "--sandbox", "read-only", "--output-last-message", "--disable"):
        assert flag in out, flag
    home = tmp_path / "codex-home"
    home.mkdir()
    feats = subprocess.run([codex, "features", "list"], capture_output=True, text=True,
                           env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(tmp_path),
                                "CODEX_HOME": str(home)}).stdout
    names = {line.split()[0] for line in feats.splitlines() if line.strip()}
    missing = [f for f in CODEX_DISABLED_FEATURES if f not in names]
    assert not missing, missing
