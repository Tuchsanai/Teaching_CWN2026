# LAB 05 — Validation (revision, 2026-09-24)

yolo3 wrote and edited every file in this revision inside devtools. It did **not** rerun the Trip.com website and did **not** rerun the setup. It did not change or overwrite any file under `evidence/`: the sha256 hashes of every evidence PNG are the same before and after the edits.

## What changed

| # | Requirement | Where | Result |
|---|---|---|---|
| 1 | Create one `LAB_DIR` under `…/05_Playwright_CLI_Trip/runs`, calling `date` once, with `mktemp -d`, the variable quoted, and `cd` running only if `mktemp` succeeds. Explain that Remote and devtools are separate filesystems with no shared mount, and that the teacher exports files deliberately | README step 2 | Done |
| 2 | Both complete Thai prompts appear in the README in ```` ```text ```` fences labeled "💬 AI chat". The fences are byte-identical to the `.txt` files | README steps 4 and 6 | Done (checked by script) |
| 3 | Dates come from `DEPART_OFFSET` and `NIGHTS`, with no hardcoded `3+4` | `prompt-trip.txt` step 0, README §4 | Done |
| 4 | Setup prompt: global npm install and a browser cache outside the project are allowed, existing `.playwright/cli.config.json` is never overwritten, the run stops if Node/npm is missing, recovered failures are recorded, and Overall is PASS when the 4 final checks pass | `prompt-install.txt` | Done |
| 5 | No `close-all`/`kill-all`. Only the lab's own named session (`lab05`/`trip`) is closed, and only that session must be absent from `playwright-cli list` | Both prompts, README steps 5 and 9, §10 | Done |
| 6 | `MAX_ITEMS`, `HOTEL_TARGET`, `NIGHTS`, `DESTINATION` and others are labeled classroom assumptions | `prompt-trip.txt` parameter box, README §4 | Done |
| 7 | `assets/lab05-workflow.png` sits near the intro. The Thai caption says it is AI-generated with ChatGPT's built-in ImageGen, not by yolo3, and is not evidence | README top | Done |
| 8 | Combined measured time 85.53 + 91.58 = 177.11 s (~2m57s), excluding the gap between runs, README writing and image generation. Component timings kept. Stated explicitly that this is not successful-search time | README §7.1 | Done |
| 9 | Teaching-time estimate (55–85 min), labeled as an estimate and kept separate from measured time | README §7.2 | Done |
| 10 | Says "yolo3 ran inside devtools via JupyterLab", with no "teacher ran" claims. States that the final Thai prompts were **not** rerun verbatim and lists the known differences | README §6 | Done |
| 11 | Safety section cut to 3 short rules (stop before booking, no CAPTCHA bypass → BLOCKED, unknown instead of invented data) | README §3 | Done |
| 12 | Real screenshots placed at each stage with source-relative links: setup `evidence/setup/lab05-example.png` (step 4); trip `01-home.png` (step 6), `02-verify-after-wait.png` and `03-retry-blocked.png` (§6) | README | Done |

## Automated checks (actual output of the validation script run on the final files)

```
PASS | AI chat fences found: 2 (['Prompt ที่ 1 (ติดตั้ง)', 'Prompt ที่ 2 (Trip.com)'])
PASS | prompt-install.txt: fence "Prompt ที่ 1 (ติดตั้ง)" byte-equal (8147 bytes, sha256 7986887a6ce8)
PASS | prompt-trip.txt: fence "Prompt ที่ 2 (Trip.com)" byte-equal (13659 bytes, sha256 3ea690860cef)
PASS | local markdown links: 24 checked, missing=[]
PASS | in-page anchors: 14 links -> ['s1', 's10', 's11', 's12', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9'] all defined
PASS | embedded images: ['assets/lab05-workflow.png', 'evidence/setup/lab05-example.png', 'evidence/trip/01-home.png', 'evidence/trip/02-verify-after-wait.png', 'evidence/trip/03-retry-blocked.png']
PASS | absent: close-all guidance / kill-all guidance / ~/lab05 path / hardcoded 3+4 / "teacher ran" / "teacher's run" / "personally" / TODO / TBD / template placeholder / "(no browsers)" requirement  (0 hits in README.md, prompt-install.txt, prompt-trip.txt)
PASS | LAB_DIR snippet: date once, mktemp -d, quoted, rooted at .../runs
PASS | prompt-trip.txt: dates use DEPART_OFFSET and NIGHTS
PASS | README.md: dates use DEPART_OFFSET and NIGHTS
PASS | setup mono 351539.96→351625.49 = 85.53 s
PASS | trip mono 351683.25→351774.83 = 91.58 s
PASS | trip phases 9.97+53.29+0+0+28.32 = 91.58
PASS | phase boundaries from timing.md match phase seconds
PASS | combined 85.53+91.58 = 177.11 s
PASS | 177.11 s = 2 min 57.11 s (~2m57s)
PASS | excluded gap between runs = 57.76 s
PASS | README states combined time and that it is not successful-search time
PASS | teaching estimate labeled as estimate, separate section 7.2
PASS | README says final Thai prompts were not rerun verbatim
PASS | workflow image caption: AI-generated with ChatGPT, not by yolo3, not evidence
PASS | prompt-trip: MAX_ITEMS/HOTEL_TARGET/NIGHTS/DESTINATION labeled classroom assumptions
PASS | prompt-install: global npm + cache allowed, config preserved, stop w/o Node/npm, recovered failures + final-check PASS
PASS | evidence PNG hashes unchanged
```

### PNG references

The first pass used a broad regex and reported 6 false "missing" results. These were bare filenames in the artifact tree and output paths inside the prompts. A second pass checked each group in its own context:

```
PASS | README prose/image PNG ref exists: assets/lab05-workflow.png            (1536×1024, valid PNG signature)
PASS | README prose/image PNG ref exists: evidence/setup/lab05-example.png     (1280×720)
PASS | README prose/image PNG ref exists: evidence/trip/01-home.png            (1280×720)
PASS | README prose/image PNG ref exists: evidence/trip/02-verify-after-wait.png (1280×720)
PASS | README prose/image PNG ref exists: evidence/trip/03-retry-blocked.png   (1280×720)
PASS | artifact-tree PNG 01-home.png / 02-verify-after-wait.png / 03-retry-blocked.png / 04-reload-still-blocked.png -> evidence/trip/
PASS | artifact-tree PNG lab05-example.png -> evidence/setup/ ; lab05-workflow.png -> assets/
INFO | prompt-install.txt names output path evidence/setup/lab05-example.png (created by a future run, relative to the run folder)
INFO | prompt-trip.txt names output path evidence/trip/05-flight-results.png (example name for a future run; intentionally not present)
```

`04-reload-still-blocked.png` has the same sha256 as `01-home.png` (b4bdf8e2…). It was captured before the widget rendered. The README notes this in the artifact tree and does not embed it.

### Shell snippets executed

- **Date block** (from `prompt-trip.txt` step 0): output was `RUN_DATE=2026-09-24 DEPART=2026-09-27 RETURN_SEARCH=2026-10-01`. With `DEPART_OFFSET=10 NIGHTS=2` it gave `2026-10-04 2026-10-06`, so editing the variables changes the result.
- **LAB_DIR snippet:** ran twice in the same second with `RUNS_DIR` pointed at a temp directory, so no `runs/` folder was created here. It produced two distinct directories, `lab05-20260924-191045-uNHZd6` and `…-HbhvkZ`. The temp directory was then removed.

## No fabricated results

- **Results match the evidence.** The README reports BLOCKED, 0 flights, 0 hotels and no recommendation. Every number (4.57, 9.97, 53.29, 28.32, 91.58, 85.53, 8.01/6.00 s waits, versions) comes from `setup-report.md`, `evidence/trip/timing.md`, `commands.log` and `phases.log`.
- **Screenshots viewed this session:** `assets/lab05-workflow.png` (a concept diagram captioned "Concept illustration") and `evidence/trip/01-home.png` (Trip.com verification page). Both match their captions. The other evidence screenshots were verified in the earlier session and are unchanged (same hashes).

## Known limitations

- **Prompts not rerun.** The final Thai prompts were not rerun verbatim. The setup (11:58:49Z–12:00:14Z) and Trip (12:01:12Z–12:02:44Z) evidence comes from earlier tasks that ran before these prompt texts were finalized. The new rules (date variables, owned-session close, config preservation, final-check PASS logic) have not been tested against the live site.
- **Historical wording kept.** The header of `evidence/trip/steps.md` still says "actual run by the instructor/AI". That is the original wording, left untouched to preserve the evidence. README §6 gives the accurate description.
- **Timing includes AI thinking time.** The Trip timings include the AI's thinking time between commands, as `timing.md` notes.
- **Remote folder not changed.** yolo3 edited only the devtools copy of this folder. The Remote authoring folder is a separate filesystem, so the teacher has to export these files deliberately.

---

# Human-assistance revision (2026-09-24, later edit)

This edit was a targeted patch (`/tmp/lab05bak/patch.py`, exact-match replacements that each had to match once) to `README.md`, `prompt-trip.txt`, `prompt-install.txt` and this file. **No Trip.com experiment and no setup were rerun.** Nothing under `evidence/` and `setup-report.md` changed: all 64 evidence file hashes and the `setup-report.md` hash match the pre-edit snapshot.

## What changed

| # | Change | Where |
|---|---|---|
| 1 | On CAPTCHA/verification the AI no longer terminates BLOCKED on first hit. It waits 5–10 s, takes one fresh snapshot (no goto/reload), then sets **WAITING_FOR_HUMAN**, writes `human-help.md`, logs WAIT_START, asks the human and pauses. While waiting it keeps the same `trip` session, browser context and current tab (no close/reload/goto/new browser/tab switch). The AI never solves or bypasses verification | `prompt-trip.txt` rule 2 (ก–ซ), README §3 |
| 2 | Resume only after explicit human confirmation **and** a fresh snapshot showing the real page. It resumes from the interrupted step without repeating steps 0–1 or recomputing dates. If still blocked: back to WAITING, or BLOCKED with reasons if the human can't help. Never invent success | rule 2 จ–ฉ, step 2 |
| 3 | Login walls: ask the human, recommend stopping as BLOCKED (login required), never request, type or record credentials. Generic Access Denied/server unavailable may not be solvable by a human; the status is recorded truthfully | rule 2 ช–ซ, README §10 |
| 4 | Timing: `human-wait.log` WAIT_START/WAIT_END; report `human_wait`, `active_automation = end_to_end − human_wait`, `end_to_end`. The wait counts once, inside its phase | prompt timing section, step 6, README §7.1 |
| 5 | New README **ขั้นที่ 6.1** (`#s5-human`): second Jupyter Terminal `playwright-cli show --host 127.0.0.1 --port 9230` (blocking, keep running). Local PowerShell `ssh -N -L 127.0.0.1:9230:127.0.0.1:9230 -p 2222 root@localhost` (port must match devtools setup, student authenticates, no credentials embedded). Open `http://localhost:9230`, select session `trip`, complete the challenge manually, tell AI. Stop both with Ctrl+C after the lab. No `0.0.0.0`, no disabling auth, pick a free consistent port | README step 6.1 |
| 6 | Step 6.1 is labeled **documented/manual path, not end-to-end tested**. Verified only: `playwright-cli --help show` (v0.1.21) lists `--port` "start as a blocking http server on this port" and `--host`. The installed official README says Session detail gives "full remote control". devtools has no `jupyter_server_proxy` | README step 6.1, §6 |
| 7 | §6 now says explicitly the BLOCKED run is **historical**, from before this revision. It used goto-retry, and no human was asked or completed verification. The historical result and all timings (4.57, 9.97, 53.29, 28.32, 91.58, 85.53, 177.11, 57.76 s) are unchanged. `human_wait` for that run = 0 | README §6, §7.1 |
| 8 | Dates: step 0 no longer hardcodes `DEPART_OFFSET=3`/`NIGHTS=4`. The AI assigns the shell vars from the parameter box (edit once). The README no longer tells students to edit step 0 too | `prompt-trip.txt` step 0, README step 6 item 1, §4 note |
| 9 | Setup prompt: an existing `.playwright/cli.config.json` is inspected with secrets redacted (keys and non-secret browser values only, `[REDACTED]` for token/password/secret/key/auth/cookie/header/proxy/storageState/credential URLs). It never dumps the whole file | `prompt-install.txt` step 5 |
| 10 | Vocabulary (WAITING_FOR_HUMAN, Dashboard), TOC link, step 7 checks, file-tree note, checklist, recovery rows (CAPTCHA, login, Access Denied, port busy, tunnel down, session not visible), and an official reference row | README |

## Automated checks (actual output)

```
PASS | AI chat fences found: 2
PASS | prompt-install.txt: fence "Prompt ที่ 1 (ติดตั้ง)" byte-equal (8668 bytes, sha256 abe59a3ab781)
PASS | prompt-trip.txt: fence "Prompt ที่ 2 (Trip.com)" byte-equal (19162 bytes, sha256 1899547215b5)
PASS | local markdown links: 24 checked, missing=[]
PASS | in-page anchors: 21 links -> ['s1', 's10', 's11', 's12', 's2', 's3', 's4', 's5', 's5-human', 's6', 's7', 's8', 's9'] all defined=['s1', 's10', 's11', 's12', 's2', 's3', 's4', 's5', 's5-human', 's6', 's7', 's8', 's9']
PASS | prompt-trip step 0: no hardcoded DEPART_OFFSET=<n>/NIGHTS=<n>
PASS | prompt-trip: DEPART_OFFSET/NIGHTS values appear once (parameter box)
PASS | prompt-trip step 0 tells AI to assign shell vars from parameter box
PASS | no "edit step 0 too" instruction left
PASS | no mandatory BLOCKED on first CAPTCHA: old phrases hits=[]
PASS | prompt-trip rule 2 forbids immediate BLOCKED
PASS | prompt-trip contains: WAITING_FOR_HUMAN
PASS | prompt-trip contains: ห้าม close/reload/goto
PASS | prompt-trip contains: ห้ามเปิด browser/session ใหม่
PASS | prompt-trip contains: ห้ามทำขั้น 0-1 ซ้ำ
PASS | prompt-trip contains: ยืนยันชัดเจน
PASS | prompt-trip contains: snapshot + screenshot ใหม่
PASS | prompt-trip contains: human-wait.log
PASS | prompt-trip contains: active_automation
PASS | prompt-trip contains: end_to_end
PASS | prompt-trip contains: เพียงครั้งเดียว
PASS | prompt-trip contains: ห้ามขอ ห้ามพิมพ์ และห้ามบันทึกชื่อผู้ใช้
PASS | prompt-trip contains: Access Denied
PASS | prompt-trip contains: ห้ามแต่งว่าสำเร็จ
PASS | README contains: playwright-cli show --host 127.0.0.1 --port 9230
PASS | README contains: ssh -N -L 127.0.0.1:9230:127.0.0.1:9230 -p 2222 root@localhost
PASS | README contains: http://localhost:9230
PASS | README contains: ยังไม่ได้ทดสอบครบวงจร
PASS | README contains: jupyter_server_proxy
PASS | README contains: 0.0.0.0
PASS | README contains: Ctrl+C
PASS | README contains: ไม่มีมนุษย์คนใดทำ verification
PASS | README contains: รอบประวัติศาสตร์
PASS | README never instructs --host 0.0.0.0
PASS | no credentials embedded in ssh command
PASS | prompt-install: config inspected with secrets redacted, no full dump
PASS | historical value kept: BLOCKED ⛔
PASS | historical value kept: 4.57
PASS | historical value kept: 9.97
PASS | historical value kept: 53.29
PASS | historical value kept: 28.32
PASS | historical value kept: 91.58
PASS | historical value kept: 85.53
PASS | historical value kept: 177.11
PASS | historical value kept: 57.76
PASS | historical value kept: 8.01 + 6.00
FAILS: 0
PASS | evidence hashes unchanged (64 files); setup-report.md: OK
```

Step-0 block executed with vars assigned from the box: `3 4` → `DEPART=2026-09-27 RETURN_SEARCH=2026-10-01`; `10 2` → `2026-10-04 2026-10-06`.

## Known limitations (this edit)

- **Dashboard/tunnel handoff untested.** The WAITING_FOR_HUMAN flow and the dashboard/SSH-tunnel handoff have **not** been tested end to end or against the live site. Only the CLI help was checked. Whether a headless session's dashboard view accepts the challenge input is unconfirmed.
- **Default SSH port is an assumption.** `-p 2222` is the classroom default. Students must use the port from their own devtools setup.
- **Earlier checks are stale.** The earlier "Automated checks" block above shows the prompt sizes and hashes from before this edit (8147/13659 bytes). The current values are in this section.
