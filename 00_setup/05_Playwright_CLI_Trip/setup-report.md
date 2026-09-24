# Lab 05 — Playwright CLI Setup Report

- Start (UTC): 2026-09-24T11:58:49Z
- End (UTC): 2026-09-24T12:00:14Z
- Elapsed (monotonic, /proc/uptime): **85.53 s** (351539.96 → 351625.49)
- Host: Ubuntu 24.04.5 LTS on WSL2 (kernel 6.6.87.2-microsoft-standard-WSL2), devtools container, user root
- Mode: headless (Playwright CLI default; confirmed by `playwright-cli list` → `headed: false`)
- **Overall result: PASS**

## Versions

| Component | Version |
|---|---|
| Node.js | v22.23.2 |
| npm | 12.0.2 |
| @playwright/cli (`playwright-cli --version`) | 0.1.21 |
| Bundled playwright-core | 1.64.0-alpha-1789764292000 |
| Chromium (Chrome for Testing) | 154.0.8037.0 (playwright chromium v1246) |
| Chrome Headless Shell | 154.0.8037.0 (chromium-headless-shell v1246) |
| FFmpeg | playwright ffmpeg v1011 |

## Steps

| # | Step | Command | Result |
|---|---|---|---|
| 1 | Check Node | `node --version` | PASS (v22.23.2) |
| 2 | Check npm | `npm --version` | PASS (12.0.2) |
| 3 | Check CLI | `which playwright-cli` | FAIL → not installed (exit 127) |
| 4 | Verify package is official | `npm view @playwright/cli name version repository.url maintainers` | PASS (repo `github.com/microsoft/playwright-cli`, Microsoft maintainers) |
| 5 | Install CLI | `npm install -g @playwright/cli@latest` | PASS (/usr/bin/playwright-cli, 0.1.21) |
| 6 | Read help | `playwright-cli --help`; `playwright-cli --help open\|install-browser\|screenshot\|snapshot\|close` | PASS |
| 7 | Read official docs | README from https://github.com/microsoft/playwright-cli (raw main) + bundled SKILL.md | PASS — CLI is headless by default; sessions via `-s=`; config at `.playwright/cli.config.json` |
| 8 | Check browsers | `playwright-cli install-browser --list` / `--dry-run` | Browsers missing |
| 9 | Install browser | `playwright-cli install-browser chromium` | PASS (~28 s; no `--with-deps` needed) |
| 10 | Open page (1st try) | `playwright-cli -s=lab05 open https://example.com` | FAIL — see error 1 |
| 11 | Local config | wrote `./.playwright/cli.config.json` (browserName `chromium`, `headless: true`) | PASS |
| 12 | Open page (retry) | `playwright-cli -s=lab05 open https://example.com` | PASS — URL `https://example.com/`, title "Example Domain" |
| 13 | Inspect snapshot | `playwright-cli -s=lab05 snapshot --filename=evidence/setup/lab05-snapshot.yml` | PASS — heading "Example Domain", paragraph, link "Learn more" → iana.org |
| 14 | Screenshot | `playwright-cli -s=lab05 screenshot --filename=evidence/setup/lab05-example.png` | PASS — valid PNG, 1280x720, 15909 bytes, visually verified |
| 15 | Close session | `playwright-cli -s=lab05 close` | PASS — "Browser 'lab05' closed"; `playwright-cli list` → no browsers |
| — | `playwright-cli install --skills` | not run (not required for this lab) | SKIP |
| — | `install-browser --with-deps` | not needed | SKIP |

## Errors encountered

1. First `open` failed because the CLI's default browser channel is `chrome` (Google Chrome), which was not installed:
   ```
   PlaywrightError: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
   Run "npx playwright install chrome"
   ```
   Resolution: instead of installing Google Chrome system-wide, created the documented config file
   `.playwright/cli.config.json` in the lab directory selecting the already-installed bundled Chromium:
   ```json
   { "browser": { "browserName": "chromium", "launchOptions": { "headless": true } } }
   ```
   (Alternative for students: `playwright-cli install-browser chrome`.)

## Evidence

- `evidence/setup/lab05-example.png` — screenshot of https://example.com (1280x720)
- `evidence/setup/lab05-snapshot.yml` — accessibility snapshot
- `evidence/setup/open.log` — output of successful `open`
- `.playwright-cli/` — CLI auto-saved snapshot from `open`

## Safety notes

- No MCP browser or external browser tool used; only `playwright-cli`.
- No security protections disabled (no `--no-sandbox` etc.); no account/global settings edited.
- No `.env` or credential files read. No secrets in this report.
- Only changes outside this directory: global npm package `@playwright/cli` and browser cache `/root/.cache/ms-playwright/`.
