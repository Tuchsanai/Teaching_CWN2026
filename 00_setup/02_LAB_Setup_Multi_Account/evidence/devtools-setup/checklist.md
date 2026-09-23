# Checklist: multi-account setup (2026-09-23)

| # | Item | Evidence | Result | Reason |
|---|---|---|---|---|
| 1 | `codex --version` before setup | `codex-cli 0.156.1` at `/usr/bin/codex` | PASS | — |
| 2 | `claude --version` before setup | `claude: command not found`; `/root/.local/bin/claude --version` → `2.1.280 (Claude Code)` | FAIL (PATH) | `~/.local/bin` isn't in PATH (earlier setup step). The user chose the absolute path and no reinstall |
| 3 | Flags checked against the installed version's `--help` | claude: `--dangerously-skip-permissions`; codex: `--dangerously-bypass-approvals-and-sandbox` | PASS | — |
| 4 | `yolo1..yolo5 --version` | 5/5 `2.1.280 (Claude Code)`, rc=0 (all run in parallel) | PASS | — |
| 5 | `cyolo1..cyolo5 --version` | 5/5 `codex-cli 0.156.1`, rc=0 (all run in parallel) | PASS | — |
| 6 | Each command uses its own config root | dry-run: `CLAUDE_CONFIG_DIR=…/.Claude/yoloN`, `CODEX_HOME=…/.Codex/cyoloN`; `find` after `auth status` / `login status` shows each account's `.claude.json` / `tmp/` in its own folder | PASS | — |
| 7 | Default `~/.codex` not touched | `ls -A ~/.codex` → `tmp`, same as before | PASS | — |
| 8 | Codex stores credentials in a file under CODEX_HOME | `config.toml` has `cli_auth_credentials_store = "file"` | PASS (config) | Location of `auth.json` after a real login → see #23 (Codex login) |
| 9 | `IS_SANDBOX=1` needed as root | Without it: `cannot be used with root/sudo privileges`; with it: `Not logged in` | PASS | The launcher sets it automatically |
| 10 | CODEX_HOME must exist beforehand | Error `CODEX_HOME … does not exist` when missing | PASS | The installer runs `mkdir -p` |
| 11 | `"$@"` passed through unchanged, including spaces | dry-run: `-p hello\ world` / `prompt\ as\ first\ arg` stay whole | PASS | — |
| 12 | Clear message when an account folder is missing | `[yolo2] account folder not found: <path>` rc=3 (and cyolo2 too) | PASS | Tested with a copy of the launcher pointed at a fake BASE_PATH |
| 13 | Secrets never printed | The launcher only prints paths and variable names; no env vars are set right now | PASS | — |
| 14 | Installer second run doesn't damage anything | Run 2: 0 create/update lines, 46 keep lines; sha256 of every file and the file list identical before/after, including a test edit in `config.toml` and a test `settings.json` | PASS | Test files were removed afterwards |
| 15 | Codex shared skills | `cyolo4 debug prompt-input` shows `zz-probe: shared probe skill`; the negative control (link removed) shows 0 | PASS | Probe removed |
| 16 | Codex shared MCP | `cyolo2 mcp list` shows `zzprobe` from shared alongside its own servers; an arg with a space is kept | PASS | Probe removed |
| 17 | Claude shared MCP | dry-run adds `--mcp-config …/shared/mcp/mcp.json` before the flag; a real run reaches `Not logged in` (config parsed); bad JSON → warning and skipped | PASS (wiring) | Actually starting the MCP server needs a login → SKIP |
| 18 | Claude shared skills loaded in a session | symlink `yoloN/skills/zz-probe → shared/skills/zz-probe` created and cleaned up correctly | SKIP | Showing skills in a session needs a login |
| 19 | Git works normally | `git --version` 2.55.0; `~/.gitconfig` sha256 unchanged; init + commit in a scratch repo works | PASS | — |
| 20 | SSH works normally | `ssh -V` OK; `ssh -G github.com` OK; `known_hosts` sha256 = baseline | PASS | The test accidentally added 1 line to known_hosts; it was removed and the hash matches again (see setup-report §9). GitHub's host key wasn't in the baseline to begin with |
| 21 | `.bashrc` / `.profile` not modified | sha256 = baseline | PASS | — |
| 22 | Claude login for each account (yolo1..5) | — | SKIP | The account owner will do this (login-guide §1) |
| 23 | Codex login for each account + `cyoloN exec` confirmation | — | SKIP | The account owner will do this (login-guide §2) |
| 24 | Logged-in accounts are actually separate (different emails, running at once) | — | SKIP | Needs real credentials |
