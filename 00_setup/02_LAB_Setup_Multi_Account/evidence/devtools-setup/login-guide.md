# Login guide: do each account yourself in the Terminal

> Run these yourself in the JupyterLab Terminal. Don't paste tokens, codes or anything from `auth.json` / `.credentials.json` into chat or into files.
> Replace `N` with 1–5. Do one account at a time. Before switching to the next account, **sign out in the browser** or use a private window, so the next account doesn't get the previous account's session.

## 0. Before you start (once)

```bash
# These variables must not be set, or they override the per-account login (this checks names only)
for v in ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_PROFILE OPENAI_API_KEY CODEX_API_KEY; do
  [ -n "${!v:-}" ] && echo "SET: $v (run: unset $v)"; done; echo checked
```

If a wrapper says `account folder not found`, run `bash /workspace/install-ai-accounts.sh` (it doesn't delete anything that exists).

## 1. Claude Code: yolo1 … yolo5 (a different Anthropic account for each)

| Step | Command / action | Expected result |
|---|---|---|
| 1 | `yoloN auth status` | `"loggedIn": false` |
| 2 | `yoloN` (opens the interactive session) → at the first launch or `/login`, choose the account type | A login URL is shown |
| 3 | Open the URL in a browser and sign in to **the Anthropic account for this N** | The browser shows a code (common in containers/WSL) |
| 4 | Paste the code at `Paste code here if prompted` → `Enter` | `Login successful` |
| 5 | `/status` in the session, then `/exit` | Shows the email/organization for this account |
| 6 | `yoloN auth status` | `"loggedIn": true` (don't share its output if it shows anything sensitive) |
| 7 | `ls -l ~/ai-accounts/.Claude/yoloN/.credentials.json` (**`ls` only, never `cat`**) | The file exists, `-rw-------` |
| 8 | Confirm it really works: `yoloN -p "reply with the word OK"` | Replies OK |

Alternative for step 2: `yoloN auth login` (a subcommand in 2.1.280).

## 2. Codex CLI: cyolo1 … cyolo5 (a different OpenAI/ChatGPT account for each)

| Step | Command / action | Expected result |
|---|---|---|
| 1 | `cyoloN login status` | `Not logged in` |
| 2 | `cyoloN login --device-auth` (recommended in a container because the localhost callback may not work). If your account says device code isn't enabled, turn it on in the ChatGPT security settings first, or use `cyoloN login` instead. | A URL and a one-time code are shown |
| 3 | Open the URL and sign in to **the OpenAI account for this N** → enter the code | The terminal says the login succeeded |
| 4 | `ls -l ~/ai-accounts/.Codex/cyoloN/auth.json` (**`ls` only**) | The file exists |
| 5 | `cyoloN login status` | Says you're logged in. **Not enough on its own** (it doesn't check whether the token works) |
| 6 | Confirm it really works: `cyoloN exec "reply with the word OK"` | Replies OK. If you get 401/expired, log in again |

## 3. Checking the accounts are separate (after logging in to 2+ accounts)

```bash
for n in 1 2 3 4 5; do printf "yolo$n: "; yolo$n auth status 2>/dev/null | grep -o '"email": *"[^"]*"' || echo "-"; done
ls -l ~/ai-accounts/.Claude/yolo*/.credentials.json ~/ai-accounts/.Codex/cyolo*/auth.json 2>/dev/null
```

Each account should show a different email and credentials in its own folder. (The email field in `auth status` hasn't been checked before a login; if the command shows nothing, use `/status` inside each account's session instead.) You can open several accounts at once in separate Terminal tabs.

## 4. Logging out or removing an account

- Claude: `/logout` inside `yoloN`, or `yoloN auth logout`
- Codex: `cyoloN logout`
