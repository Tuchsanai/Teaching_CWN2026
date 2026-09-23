# Setup report: multi-account Claude Code / Codex CLI

Date: 2026-09-23 · User: `root` · Container: Linux (WSL2 kernel), JupyterLab terminal

## 1. Versions checked (nothing reinstalled)

| Tool | Command | Result | Location |
|---|---|---|---|
| Claude Code | `claude --version` | **command not found** because `~/.local/bin` isn't in `PATH` | binary exists at `/root/.local/bin/claude` → `~/.local/share/claude/versions/2.1.280` |
| Claude Code | `/root/.local/bin/claude --version` | `2.1.280 (Claude Code)` | — |
| Codex CLI | `codex --version` | `codex-cli 0.156.1` | `/usr/bin/codex` |

The user chose not to edit `.bashrc` or PATH, so the wrappers call Claude by its **absolute path** `/root/.local/bin/claude`.
This is a stable symlink that Claude Code's own updater keeps current. It isn't a versioned path.
**Plain `claude` still doesn't work in a new shell.** That's a leftover from the earlier setup step; the learner should fix it there.

## 2. Where files were placed and why

| File | Location | Why |
|---|---|---|
| Installer | `/workspace/install-ai-accounts.sh` | Sits in the working folder, so it's easy to open, edit `BASE_PATH` and re-run. **`BASE_PATH` is defined only here.** |
| Launcher | `/usr/local/bin/ai-account-launch` | `/usr/local/bin` is already on PATH, so no PATH edit is needed. The installer generates this file; its `BASE_PATH` comes from the installer. |
| `yolo1..5`, `cyolo1..5` | `/usr/local/bin/<name>` → symlink to the launcher | One file handles everything. The launcher picks the tool and account from the name it was called by (`$0`). |

To change `BASE_PATH`, edit line 13 of `install-ai-accounts.sh` and re-run it. The launcher is regenerated to point at the new path.

## 3. Config root structure

```
$BASE_PATH = /root/ai-accounts            (mode 700)
├── .Claude/
│   ├── yolo1/ … yolo5/                    CLAUDE_CONFIG_DIR per account (mode 700)
│   │   ├── .claude.json                   account state/onboarding/user-scope MCP (created by Claude)
│   │   ├── .credentials.json              ← created on /login (0600) — not there yet
│   │   ├── backups/  (plus sessions/, projects/, history.jsonl, cache/ … created as used)
│   │   └── skills/<name> → ../../shared/skills/<name>   (symlink per skill, created by the launcher)
│   └── shared/
│       ├── skills/                        source for skills used by every yoloN
│       └── mcp/mcp.json                   source for MCP servers used by every yoloN (passed via --mcp-config)
└── .Codex/
    ├── cyolo1/ … cyolo5/                  CODEX_HOME per account (mode 700)
    │   ├── config.toml                    cli_auth_credentials_store="file", mcp_oauth_credentials_store="file"
    │   ├── auth.json                      ← created on login — not there yet
    │   ├── tmp/ (plus sessions/, log/, shell_snapshots/ … created as used)
    │   └── skills/<name> → shared/skills/<name>   (symlink per skill)
    └── shared/
        ├── skills/
        └── mcp/config.toml                [mcp_servers.<name>] tables, passed via -c
```

## 4. Credential storage (checked in official docs and in real behavior)

| CLI | Mechanism | Credential location | Evidence |
|---|---|---|---|
| Claude Code | `CLAUDE_CONFIG_DIR` | `<root>/.credentials.json`, mode 0600 (Linux has no keychain) | Docs (authentication): "If you've set `CLAUDE_CONFIG_DIR`… keeps the `.credentials.json` file under that directory". Tested: `.claude.json` is written inside `<root>` and not in `~` |
| Codex CLI | `CODEX_HOME` + `cli_auth_credentials_store = "file"` | `<root>/auth.json` | Docs (auth/config-reference): the `file` option stores `auth.json` under `CODEX_HOME`. Set to `file` explicitly so it never uses a shared OS keyring (`auto` would try the keyring first) |

Environment variables that **override every account** (the launcher warns with the **variable name only**, never the value):

| CLI | Variables checked | Status on this machine now |
|---|---|---|
| Claude | `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_PROFILE`, `CLAUDE_CODE_USE_BEDROCK/VERTEX/FOUNDRY` | none set |
| Codex | `OPENAI_API_KEY`, `CODEX_API_KEY` | none set |

## 5. Wrapper behavior

| Item | yoloN | cyoloN |
|---|---|---|
| env | `CLAUDE_CONFIG_DIR=<root>`; `IS_SANDBOX=1` only when running as root | `CODEX_HOME=<root>` |
| flag | `--dangerously-skip-permissions` (checked in `claude --help` 2.1.280) | `--dangerously-bypass-approvals-and-sandbox` (checked in `codex --help` 0.156.1) |
| arguments | pass `"$@"` through unchanged | pass `"$@"` through unchanged |
| shared MCP | `--mcp-config shared/mcp/mcp.json`, only when `mcpServers` has entries and the JSON is valid | `-c mcp_servers.<name>={…}` for each server in `shared/mcp/config.toml` |
| shared skills | links `shared/skills/*` into `<root>/skills/` on every launch | same |
| missing account folder | prints `account folder not found: <path>` and exits with code 3 | same |
| debug | `AI_ACCOUNTS_DRYRUN=1 yolo1 …` prints the env vars and final command without running it | same |

`HOME`, `.bashrc`, PATH, Git and SSH config are unchanged.

## 6. Notes from the earlier lab (rechecked on this version)

| Note | Result on this machine |
|---|---|
| Running as root needs `IS_SANDBOX=1` | **Still true**: without it you get `--dangerously-skip-permissions cannot be used with root/sudo privileges`. The launcher sets it automatically. |
| `CODEX_HOME` must exist before running codex | **Still true**: you get `CODEX_HOME points to "…", but that path does not exist`. The installer creates it with `mkdir -p`. |
| `codex login status` doesn't check that the token still works | Can't test without a login. The login guide uses `cyoloN exec` to confirm. |

## 7. Things still shared (this is not OS isolation)

- **Linux user**: every account runs as `root`. Every process can read every account's credentials; the 700/600 permissions only block other users.
- **Project config** in the working folder: `.claude/`, `CLAUDE.md`, `.mcp.json`, `AGENTS.md`, `.agents/skills`, `.codex/`. Every account sees these.
- **Codex user/admin skill scopes**: `$HOME/.agents/skills` and `/etc/codex/skills` are read by every cyoloN and by plain `codex` (neither exists right now).
- **Anthropic profiles**: `~/.config/anthropic` (`ant auth login`) isn't split per `CLAUDE_CONFIG_DIR` (doesn't exist right now).
- **Everything else in the environment**: environment variables, Git identity and credential helper, SSH keys and known_hosts, network, `/tmp`, and the binaries themselves (updating Claude or Codex affects every account).
- The Codex help text mentions a "shared local app-server daemon". **Not checked** whether it's split per `CODEX_HOME`.
- The default `claude` (`~/.claude`) and `codex` (`~/.codex`) are **separate from every account** and unchanged.

## 8. Limitations and what's partially supported

| Topic | Details |
|---|---|
| Claude shared MCP | Uses `--mcp-config`, which applies only to the current session. The servers **don't show in `yoloN mcp list`** (that lists user/local/project scopes only). `--mcp-config` takes multiple values, so the launcher puts it before `--dangerously-skip-permissions`. Tested: otherwise it swallows the first prompt argument. |
| Claude shared skills | Docs support one symlink per skill folder. Can't confirm skills are loaded without a login → SKIP |
| Codex shared skills | Tested with `codex debug prompt-input`: a symlinked skill under `$CODEX_HOME/skills` shows up, and disappears when the link is removed |
| Codex shared MCP | Codex has no include/extends for `config.toml`, so the launcher uses `-c`. It **adds to** the account's own servers (tested: `mcp list` shows both). Values passed with `-c` are visible in `ps`, **so don't put secrets in shared/mcp**; use `bearer_token_env_var` / `env_vars` instead. |
| Skills added later | Links are created the next time that account is launched. A session already running has to be restarted. A per-account skill with the same name wins over the shared one. |
| Claude settings.json | Separate per account; nothing shared (not requested). |

## 9. Incident during testing (reported honestly)

The SSH test used `ssh -o StrictHostKeyChecking=accept-new git@github.com`, which **added 1 line to `~/.ssh/known_hosts`**.
I found it right away and removed that line; the file's SHA-256 **matches the pre-install baseline again** (`sha256sum -c` → OK).
The test was then redone with `StrictHostKeyChecking=yes -o UpdateHostKeys=no`, which writes nothing.
