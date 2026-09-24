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
