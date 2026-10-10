import type { Reporter, FullConfig, Suite, TestCase, TestResult, FullResult } from '@playwright/test/reporter';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import ffmpegStatic from 'ffmpeg-static';

/**
 * Builds e2e/index.html: a clickable test summary report (double-click to open, no server needed).
 * GIF/MP4/screenshots and data.json go to test-report/.
 *  - summary: exit criteria from TEST-PLAN.md, results by module/priority, defects, all test cases
 *  - one detail view per test case: steps + checkpoints, % passed, what went wrong, GIF/MP4, screenshots
 * Test-plan data (module, technique, priority, expected result, source [D]/[R]/[O]) is read from ../TEST-PLAN.md (หัวข้อ 5).
 * Pass/fail is judged with the exit criteria of OUR plan (หัวข้อ 6.2): per browser, P1 100% and ≥ 95% overall,
 * every failed test classified (triage.json: เว็บผิด / แผนผิด / test เขียนผิด) and has evidence.
 */

type Check = { step: string; name: string; ok: boolean; expected?: string; received?: string };
type Evidence = { steps: string[]; checks: Check[]; stoppedAt?: { step: string; message: string } };
type Run = {
  browser: string; status: string; duration: number; evidence: Evidence; error?: string;
  shots: { name: string; file: string }[]; video?: string;
};
type PlanRow = { module: string; what: string; technique: string; priority: string; expected: string; source: string };
type Triage = { cause: string; note?: string };

const BROWSERS = ['chromium', 'firefox', 'webkit'];
// ffmpeg-static's binary (downloaded by "postinstall"), or an ffmpeg already on PATH
const FFMPEG = ffmpegStatic && fs.existsSync(ffmpegStatic as unknown as string) ? (ffmpegStatic as unknown as string) : 'ffmpeg';
const stripAnsi = (s = '') => s.replace(/\u001b\[[0-9;]*m/g, '');

function run(cmd: string, args: string[]) {
  return new Promise<void>((resolve) => {
    const p = spawn(cmd, args, { stdio: 'ignore' });
    p.on('close', () => resolve());
    p.on('error', () => resolve());
  });
}

async function pool<T>(items: T[], size: number, fn: (x: T) => Promise<void>) {
  const queue = [...items];
  await Promise.all(Array.from({ length: size }, async () => { for (let x; (x = queue.shift()); ) await fn(x); }));
}

function readPlan(file: string) {
  const plan = new Map<string, PlanRow>();
  if (!fs.existsSync(file)) return plan;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    if (!/^\| TC-/.test(line)) continue;
    const c = line.split('|').slice(1, -1).map((x) => x.trim().replace(/\*\*/g, ''));
    // ID | โมดูล | สิ่งที่ทดสอบ | เทคนิค | ระดับ | ผลที่คาดหวัง | ที่มา
    if (c.length >= 6) plan.set(c[0], { module: c[1], what: c[2], technique: c[3], priority: c[4], expected: c[5], source: c[6] ?? '-' });
    else if (c.length === 5) plan.set(c[0], { module: c[1], what: c[2], technique: '-', priority: c[3], expected: c[4], source: '-' });
  }
  return plan;
}

export default class HtmlReport implements Reporter {
  private out: string;
  private indexFile: string;
  private rootDir = process.cwd();
  private baseURL = 'http://localhost:3000';
  private started = new Date();
  private tests = new Map<string, { title: string; tags: string[]; expected: string; source: string; file: string; runs: Run[] }>();
  private jobs: (() => Promise<void>)[] = [];

  constructor(options: { outputFolder?: string; indexFile?: string } = {}) {
    this.out = options.outputFolder ?? 'test-report';
    this.indexFile = options.indexFile ?? 'index.html';
  }

  onBegin(config: FullConfig, _suite: Suite) {
    this.rootDir = config.configFile ? path.dirname(config.configFile) : config.rootDir;
    this.out = path.resolve(this.rootDir, this.out);
    this.indexFile = path.resolve(this.rootDir, this.indexFile);
    this.baseURL = (config.projects[0]?.use?.baseURL as string) ?? this.baseURL;
    fs.rmSync(this.out, { recursive: true, force: true });
    fs.mkdirSync(path.join(this.out, 'media'), { recursive: true });
  }

  onTestEnd(test: TestCase, result: TestResult) {
    const browser = test.parent.project()?.name ?? 'chromium';
    const id = test.title.match(/^(TC-[A-Z]+-\d+)/)?.[1] ?? test.title;
    const entry = this.tests.get(id) ?? {
      title: test.title.replace(id, '').trim(),
      tags: test.tags,
      expected: test.annotations.find((a) => a.type === 'expected')?.description ?? '',
      source: test.annotations.find((a) => a.type === 'source')?.description ?? '-',
      file: path.basename(test.location.file),
      runs: [],
    };
    this.tests.set(id, entry);

    let evidence: Evidence = { steps: [], checks: [] };
    const shots: Run['shots'] = [];
    let video: string | undefined;
    for (const a of result.attachments) {
      if (a.name === 'evidence.json' && a.body) evidence = JSON.parse(a.body.toString());
      else if (a.name === 'video' && a.path) video = a.path;
      else if (a.contentType === 'image/png' && (a.body || a.path)) {
        const circled = a.name.startsWith('วงจุดที่ผิด');
        if (!circled && shots.length) continue; // prefer our circled screenshots over the automatic one
        const file = `media/${id}-${browser}-${shots.length + 1}.png`;
        if (a.body) fs.writeFileSync(path.join(this.out, file), a.body);
        else fs.copyFileSync(a.path!, path.join(this.out, file));
        shots.push({ name: circled ? a.name.replace(/^วงจุดที่ผิด:?\s*/, '') || 'หยุดกลางทาง' : 'ภาพตอนล้ม', file });
      }
    }
    // the automatic screenshot only matters when we have no circled one
    const circledShots = shots.filter((s) => s.name !== 'ภาพตอนล้ม');
    const run: Run = {
      browser, status: result.status, duration: result.duration, evidence,
      error: result.errors.length ? stripAnsi(result.errors[0].message).split('\n')[0] : undefined,
      shots: circledShots.length ? circledShots : shots,
    };
    entry.runs.push(run);

    // queue the video conversion; it runs in onEnd, 3 at a time
    if (video && fs.existsSync(video)) {
      const evidenceVideo = browser === 'chromium';
      if (evidenceVideo || result.status !== 'passed') {
        const base = evidenceVideo ? id : `${id}-${browser}`;
        const src = path.join(this.out, 'media', `${base}.webm`);
        fs.copyFileSync(video, src);
        run.video = base;
        this.jobs.push(() => this.convert(src, base, evidenceVideo));
      }
    }
  }

  private convert(src: string, base: string, gif: boolean) {
    const media = path.join(this.out, 'media');
    return (async () => {
      await run(FFMPEG, ['-y', '-loglevel', 'error', '-i', src, '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '30', '-preset', 'veryfast', '-movflags', '+faststart',
        path.join(media, `${base}.mp4`)]);
      if (gif) {
        await run(FFMPEG, ['-y', '-loglevel', 'error', '-i', src, '-vf',
          'fps=7,scale=760:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
          path.join(media, `${base}.gif`)]);
      }
      if (fs.existsSync(path.join(media, `${base}.mp4`))) fs.rmSync(src, { force: true });
    })();
  }

  async onEnd(result: FullResult) {
    process.stdout.write('\nกำลังสร้างรายงานและแปลงวิดีโอเป็น GIF/MP4 ...\n');
    await pool(this.jobs, 3, (job) => job());

    // e2e/ sits next to TEST-PLAN.md; the copy in _solution/e2e is one level deeper
    const planFile = ['..', '../..'].map((up) => path.resolve(this.rootDir, up, 'TEST-PLAN.md')).find((f) => fs.existsSync(f)) ?? '';
    const plan = readPlan(planFile);
    // การจำแนกข้อที่ล้ม (EX4) — เขียนเองหลังดูผล: { "TC-…": { "cause": "เว็บผิด" | "แผนผิด" | "test เขียนผิด", "note": "…" } }
    const triageFile = path.join(this.rootDir, 'triage.json');
    const triage: Record<string, Triage> = fs.existsSync(triageFile) ? JSON.parse(fs.readFileSync(triageFile, 'utf8')) : {};
    const bugMode = await fetch(this.baseURL).then((r) => r.text()).then((h) => /data-bug-mode="1"/.test(h)).catch(() => false);
    const media = path.join(this.out, 'media');
    const has = (f: string) => fs.existsSync(path.join(media, f));
    // links in index.html are relative to where index.html lives (e2e/ → test-report/media/...)
    const rel = path.relative(path.dirname(this.indexFile), this.out).replace(/\\/g, '/');
    const url = (f: string) => (rel ? rel + '/' : '') + f;

    const cases = [...this.tests.entries()].map(([id, t]) => {
      const p = plan.get(id);
      const runs = BROWSERS.map((b) => t.runs.find((r) => r.browser === b)).filter(Boolean) as Run[];
      // checkpoints a full run should have: the largest count from a run that was not stopped halfway
      const full = Math.max(0, ...runs.filter((r) => !r.evidence.stoppedAt).map((r) => r.evidence.checks.length));
      const perBrowser = runs.map((r) => {
        const passed = r.evidence.checks.filter((c) => c.ok).length;
        const total = Math.max(r.evidence.checks.length, r.evidence.stoppedAt ? full : 0);
        return {
          browser: r.browser, status: r.status, duration: r.duration, passed, total,
          steps: r.evidence.steps, checks: r.evidence.checks, stoppedAt: r.evidence.stoppedAt, error: r.error,
          shots: r.shots.map((s) => ({ ...s, file: url(s.file) })),
          mp4: r.video && has(`${r.video}.mp4`) ? url(`media/${r.video}.mp4`) : undefined,
        };
      });
      const passed = perBrowser.reduce((n, b) => n + b.passed, 0);
      const total = perBrowser.reduce((n, b) => n + b.total, 0);
      const status = perBrowser.length && perBrowser.every((b) => b.status === 'passed') ? 'passed'
        : perBrowser.every((b) => b.status === 'skipped') ? 'skipped' : 'failed';
      return {
        id, title: t.title, file: t.file,
        module: p?.module ?? (t.tags.find((x) => !/^@P\d$/.test(x)) ?? '').replace('@', ''),
        priority: p?.priority ?? (t.tags.find((x) => /^@P\d$/.test(x)) ?? '@P3').replace('@', ''),
        technique: p?.technique ?? '-',
        expected: p?.expected ?? t.expected,
        source: p?.source ?? t.source,
        triage: triage[id],
        inPlan: !!p,
        status, passed, total, pct: total ? Math.round((passed / total) * 100) : status === 'passed' ? 100 : 0,
        gif: has(`${id}.gif`) ? url(`media/${id}.gif`) : undefined,
        mp4: has(`${id}.mp4`) ? url(`media/${id}.mp4`) : undefined,
        browsers: perBrowser,
      };
    });
    // test cases in TEST-PLAN.md that this run did not execute (e.g. only one file was run)
    for (const [id, p] of plan) {
      if (cases.some((c) => c.id === id)) continue;
      cases.push({
        id, title: p.what, file: '-', module: p.module, priority: p.priority, technique: p.technique, expected: p.expected, source: p.source, triage: triage[id],
        inPlan: true, status: 'notrun', passed: 0, total: 0, pct: 0, gif: undefined, mp4: undefined, browsers: [],
      });
    }
    const order = [...plan.keys()];
    cases.sort((a, b) => (order.indexOf(a.id) + 1 || 999) - (order.indexOf(b.id) + 1 || 999) || a.id.localeCompare(b.id));

    let n = 0;
    for (const c of cases) if (c.status === 'failed') (c as any).defect = `DEF-${String(++n).padStart(3, '0')}`;

    const data = {
      project: 'PawPantry',
      started: this.started.toISOString(),
      duration: result.duration,
      baseURL: this.baseURL,
      bugMode,
      browsers: BROWSERS.filter((b) => cases.some((c) => c.browsers.some((x) => x.browser === b))),
      runs: cases.reduce((s, c) => s + c.browsers.length, 0),
      planTotal: plan.size,
      cases,
    };
    fs.writeFileSync(path.join(this.out, 'data.json'), JSON.stringify(data, null, 2));
    fs.writeFileSync(this.indexFile, renderHtml(data));

    if (this.jobs.length && !fs.readdirSync(media).some((f) => f.endsWith('.mp4'))) {
      process.stdout.write('\n⚠️  แปลงวิดีโอไม่สำเร็จ: ไม่พบ ffmpeg — รัน "node node_modules/ffmpeg-static/install.js" ในโฟลเดอร์ e2e แล้วรันใหม่\n');
    }
    const count = (s: string) => cases.filter((c) => c.status === s).length;
    const notrun = count('notrun');
    process.stdout.write(`\n📊 รายงาน: ${this.indexFile}  (ดับเบิลคลิกเปิดได้เลย)\n` +
      `   test case ${cases.length} ข้อ · ผ่าน ${count('passed')} · ไม่ผ่าน ${count('failed')}` +
      (notrun ? ` · ยังไม่ได้รัน ${notrun}` : '') + ` · BUG_MODE=${bugMode ? 1 : 0}\n`);
  }

  printsToStdio() { return false; }
}

export function renderHtml(data: unknown) {
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return `<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>รายงานผลการทดสอบ · PawPantry</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;600;700&display=swap" rel="stylesheet">
<style>${CSS}</style></head>
<body><div id="app"></div>
<script id="data" type="application/json">${json}</script>
<script>${JS}</script></body></html>`;
}

const CSS = `
:root{--bg:#f4f6fa;--card:#fff;--ink:#1e2a3a;--muted:#64748b;--line:#e2e8f0;--pass:#16a34a;--pass-bg:#e8f7ee;
--fail:#dc2626;--fail-bg:#fdecec;--warn:#d97706;--accent:#ff6b4a;--p1:#dc2626;--p2:#d97706;--p3:#0d9488}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "IBM Plex Sans Thai","Leelawadee UI",Tahoma,sans-serif}
a{color:inherit}.wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}
header.top{background:#1e2a3a;color:#fff}header.top .wrap{padding:18px 20px;display:flex;flex-wrap:wrap;gap:8px 24px;align-items:center;justify-content:space-between}
header.top h1{margin:0;font-size:22px}header.top .meta{color:#cbd5e1;font-size:13.5px;display:flex;flex-wrap:wrap;gap:6px 18px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:999px;font-size:12.5px;font-weight:600;background:#eef2f7;color:#334155;white-space:nowrap}
.chip.bug{background:#fde68a;color:#78350f}.chip.ok{background:var(--pass-bg);color:var(--pass)}.chip.no{background:var(--fail-bg);color:var(--fail)}
.chip.P1{background:#fde2e2;color:var(--p1)}.chip.P2{background:#fdf0dc;color:var(--p2)}.chip.P3{background:#dcf3f0;color:var(--p3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:0 0 18px}
h2{font-size:18px;margin:0 0 12px}h3{font-size:16px;margin:0 0 10px}
.verdict{display:flex;gap:16px;align-items:center;border-radius:14px;padding:18px 22px;margin:0 0 18px;border:2px solid}
.verdict.ok{background:var(--pass-bg);border-color:#86efac}.verdict.no{background:var(--fail-bg);border-color:#fca5a5}
.verdict.wait{background:#f1f5f9;border-color:#cbd5e1}.kpi.wait .v{color:var(--muted)}
.res.notrun{color:var(--muted)}.status.notrun{background:#f1f5f9;color:#475569}
.verdict .big{font-size:40px;line-height:1}.verdict b{font-size:20px}.verdict ul{margin:6px 0 0;padding-left:20px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.kpi .v{font-size:28px;font-weight:700;line-height:1.2}.kpi .l{color:var(--muted);font-size:13px}
.kpi.pass .v{color:var(--pass)}.kpi.fail .v{color:var(--fail)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:860px){.grid2{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12.5px;color:var(--muted);font-weight:600;background:#f8fafc}
tbody tr.click{cursor:pointer}tbody tr.click:hover{background:#fff7f4}
.bar{height:8px;background:#eef2f7;border-radius:99px;overflow:hidden;min-width:70px}.bar>i{display:block;height:100%;background:var(--pass)}
.bar.low>i{background:var(--fail)}.bar.mid>i{background:var(--warn)}
.pct{display:flex;align-items:center;gap:8px}.pct span{min-width:38px;font-weight:600;font-size:13px}
.res{font-weight:700}.res.passed{color:var(--pass)}.res.failed{color:var(--fail)}
.br{display:inline-block;width:26px;height:26px;border-radius:7px;text-align:center;line-height:26px;font-weight:700;font-size:13px;margin-right:4px}
.br.passed{background:var(--pass-bg);color:var(--pass)}.br.failed,.br.timedOut,.br.interrupted{background:var(--fail-bg);color:var(--fail)}.br.none{background:#f1f5f9;color:#94a3b8}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px;align-items:center}
.filters button{border:1px solid var(--line);background:#fff;border-radius:999px;padding:5px 13px;font:inherit;font-size:13px;cursor:pointer}
.filters button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.filters input{border:1px solid var(--line);border-radius:999px;padding:6px 14px;font:inherit;font-size:13px;min-width:200px;margin-left:auto}
.scroll{overflow-x:auto}
.back{display:inline-block;margin:0 0 14px;text-decoration:none;color:var(--muted)}.back:hover{color:var(--ink)}
.tc-head{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 6px}.tc-head h1{font-size:24px;margin:0}
.status{padding:4px 14px;border-radius:999px;font-weight:700;font-size:14px}.status.passed{background:var(--pass-bg);color:var(--pass)}.status.failed{background:var(--fail-bg);color:var(--fail)}
.ring{--p:0;width:110px;height:110px;border-radius:50%;background:conic-gradient(var(--c) calc(var(--p)*1%),#eef2f7 0);display:grid;place-items:center;flex:none}
.ring>div{width:84px;height:84px;border-radius:50%;background:#fff;display:grid;place-items:center;text-align:center;line-height:1.1}
.ring b{font-size:24px}.ring small{color:var(--muted);font-size:11.5px}
.sumrow{display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.errbox{background:var(--fail-bg);border:1px solid #fca5a5;border-radius:12px;padding:14px 16px;margin:0 0 18px}
.errbox h3{color:var(--fail)}.errbox table td,.errbox table th{background:transparent;border-color:#f8c4c4}
.steps{list-style:none;margin:0;padding:0}.steps>li{border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:0 0 8px}
.steps>li.bad{border-color:#fca5a5;background:#fffafa}.steps .st{font-weight:600}
.steps ul{list-style:none;margin:6px 0 0;padding:0}.steps ul li{padding:3px 0 3px 26px;position:relative;font-size:14px}
.steps ul li:before{position:absolute;left:0;font-weight:700}.steps ul li.ok:before{content:"✓";color:var(--pass)}.steps ul li.no:before{content:"✗";color:var(--fail)}
.steps ul li.no{color:var(--fail)}.steps .detail{display:block;color:#7f1d1d;font-size:13px}
.media img,.media video{width:100%;border-radius:10px;border:1px solid var(--line);background:#000;display:block}
.tabs{display:flex;gap:6px;margin:0 0 10px}.tabs button{border:1px solid var(--line);background:#fff;border-radius:8px;padding:5px 12px;font:inherit;font-size:13px;cursor:pointer}.tabs button.on{background:var(--ink);color:#fff}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}.shots figure{margin:0}.shots img{width:100%;border-radius:8px;border:2px solid #fca5a5;cursor:zoom-in}
.shots figcaption{font-size:12.5px;color:var(--muted)}
.nav{display:flex;justify-content:space-between;margin-top:10px}.nav a{text-decoration:none;color:var(--muted)}
.nw,td b{white-space:nowrap}.muted{color:var(--muted)}.small{font-size:13px}
#zoom{position:fixed;inset:0;background:rgba(15,23,42,.85);display:none;place-items:center;z-index:9;cursor:zoom-out}#zoom img{max-width:94vw;max-height:92vh;border-radius:8px}
footer{color:var(--muted);font-size:12.5px;text-align:center;margin-top:24px}
`;

const JS = String.raw`
const D = JSON.parse(document.getElementById('data').textContent);
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const BR = { chromium: 'C', firefox: 'F', webkit: 'W' };
const BRN = { chromium: 'Chromium', firefox: 'Firefox', webkit: 'WebKit (Safari)' };
const TH = { passed: 'ผ่าน', failed: 'ไม่ผ่าน', timedOut: 'หมดเวลา', skipped: 'ข้าม', interrupted: 'ถูกหยุด' };
const fmtDur = (ms) => ms >= 60000 ? (ms / 60000).toFixed(1) + ' นาที' : (ms / 1000).toFixed(1) + ' วินาที';
const barCls = (p) => (p >= 100 ? '' : p >= 60 ? 'mid' : 'low');
const pctBar = (p) => '<div class="pct"><span>' + p + '%</span><div class="bar ' + barCls(p) + '"><i style="width:' + p + '%"></i></div></div>';

const cases = D.cases;
const passed = cases.filter((c) => c.status === 'passed');
const failed = cases.filter((c) => c.status === 'failed');
const rate = cases.length ? Math.round((passed.length / cases.length) * 1000) / 10 : 0;
const p1 = cases.filter((c) => c.priority === 'P1');
const p1fail = p1.filter((c) => c.status !== 'passed');
// TEST-PLAN.md หัวข้อ 6.2 — ตัดสินแยกทีละเบราว์เซอร์ ต้องผ่านครบทุกเบราว์เซอร์
const perBr = D.browsers.map((b) => {
  const st = (c) => { const r = c.browsers.find((x) => x.browser === b); return r ? r.status : 'none'; };
  const ok = cases.filter((c) => st(c) === 'passed');
  const bad = cases.filter((c) => st(c) !== 'passed');
  const p1ok = p1.filter((c) => st(c) === 'passed').length;
  const r = cases.length ? Math.round((ok.length / cases.length) * 1000) / 10 : 0;
  const ex1 = p1ok === p1.length;
  const ex2 = r >= 95 && bad.every((c) => c.priority !== 'P1');
  return { b, ok: ok.length, bad, p1ok, rate: r, ex1, ex2, pass: ex1 && ex2 };
});
const ex3 = p1fail.length === 0; // ไม่มีบั๊ก P1 ค้าง
const untriaged = failed.filter((c) => !c.triage);
const ex4 = untriaged.length === 0;
const noEvidence = failed.filter((c) => !c.gif && !c.browsers.some((b) => b.shots.length || b.mp4));
const ex5 = noEvidence.length === 0;
const exitOk = perBr.length > 0 && perBr.every((x) => x.pass) && ex3 && ex4 && ex5;
const checksPassed = cases.reduce((n, c) => n + c.passed, 0);
const checksTotal = cases.reduce((n, c) => n + c.total, 0);
const notrun = cases.filter((c) => c.status === 'notrun');
const LABEL = { passed: '✅ ผ่าน', failed: '❌ ไม่ผ่าน', notrun: '⏸ ยังไม่ได้รัน' };

function header() {
  const d = new Date(D.started);
  return '<header class="top"><div class="wrap"><h1>📋 รายงานผลการทดสอบ · ' + esc(D.project) + '</h1><div class="meta">' +
    '<span>🗓️ ' + d.toLocaleString('th-TH') + '</span><span>⏱️ ' + fmtDur(D.duration) + '</span>' +
    '<span>🌐 ' + D.browsers.map((b) => BRN[b]).join(' · ') + '</span><span>🔗 ' + esc(D.baseURL) + '</span>' +
    (D.bugMode ? '<span class="chip bug">🐞 BUG_MODE=1</span>' : '<span class="chip">BUG_MODE=0</span>') + '</div></div></header>';
}

function summary() {
  const reasons = [];
  const mark = (ok) => (ok ? '✅' : '❌');
  reasons.push(mark(perBr.every((x) => x.ex1)) + ' EX1 P1 ผ่าน 100% ทุกเบราว์เซอร์: ' + perBr.map((x) => BRN[x.b] + ' ' + x.p1ok + '/' + p1.length).join(' · '));
  reasons.push(mark(perBr.every((x) => x.ex2)) + ' EX2 อัตราผ่านรวม ≥ 95% (ล้มได้ไม่เกิน ' + Math.floor(cases.length * 0.05) + ' ข้อ และต้องเป็น P2/P3): ' + perBr.map((x) => BRN[x.b] + ' ' + x.ok + '/' + cases.length + ' = ' + x.rate + '%').join(' · '));
  reasons.push(mark(ex3) + ' EX3 ไม่มีบั๊ก P1 ค้าง: ' + p1fail.length + ' ข้อ');
  reasons.push(mark(ex4) + ' EX4 ข้อที่ล้มถูกจำแนกแล้ว (เว็บผิด / แผนผิด / test เขียนผิด): ' + (failed.length - untriaged.length) + '/' + failed.length + (untriaged.length ? ' · ยังไม่จำแนก: ' + untriaged.map((c) => c.id).join(', ') : ''));
  reasons.push(mark(ex5) + ' EX5 มีรายงาน e2e/index.html + หลักฐาน (ภาพ/GIF) ของข้อที่ล้ม: ' + (failed.length - noEvidence.length) + '/' + failed.length);
  let h;
  if (notrun.length) {
    // a partial run (e.g. one file only) cannot decide the exit criteria
    h = '<div class="verdict wait"><div class="big">⏸</div><div><b>ยังตัดสินไม่ได้ · รอบนี้รันแค่ ' + (cases.length - notrun.length) + ' จาก ' + cases.length + ' test case</b>' +
      '<div class="small muted">เกณฑ์ผ่านใน TEST-PLAN.md หัวข้อ 6 ต้องดูผลครบทุกข้อ · รัน <code>npx playwright test</code> ทั้งหมดเพื่อให้ได้ผลตัดสิน</div><ul>' +
      '<li>✅ ผ่าน ' + passed.length + ' · ❌ ไม่ผ่าน ' + failed.length + ' · ⏸ ยังไม่ได้รัน ' + notrun.length + ' ข้อ</li></ul></div></div>';
  } else {
    h = '<div class="verdict ' + (exitOk ? 'ok' : 'no') + '"><div class="big">' + (exitOk ? '✅' : '❌') + '</div><div><b>' +
      (exitOk ? 'ผ่านเกณฑ์ · พร้อมปล่อยใช้งาน' : 'ไม่ผ่านเกณฑ์ · ยังไม่พร้อมปล่อยใช้งาน') + '</b>' +
      '<div class="small muted">ตัดสินตามเกณฑ์ผ่าน (Exit criteria) ใน TEST-PLAN.md หัวข้อ 6.2 · แยกทีละเบราว์เซอร์ ต้องผ่านครบทั้ง ' + perBr.length + ' เบราว์เซอร์</div><ul>' + reasons.map((r) => '<li>' + r + '</li>').join('') + '</ul></div></div>';
  }

  if (!notrun.length) {
    const mark = (ok) => (ok ? '✅' : '❌');
    h += '<div class="card"><h2>ผลตามเกณฑ์ แยกทีละเบราว์เซอร์ (หัวข้อ 6.2)</h2><div class="scroll"><table><thead><tr><th>เบราว์เซอร์</th><th>P1 ผ่าน (EX1)</th><th>ผ่านรวม (EX2)</th><th>อัตราผ่าน</th><th>ข้อที่ล้ม</th><th>ผล</th></tr></thead><tbody>' +
      perBr.map((x) => '<tr><td><b>' + BRN[x.b] + '</b></td><td>' + mark(x.ex1) + ' ' + x.p1ok + '/' + p1.length + '</td><td>' + mark(x.ex2) + ' ' + x.ok + '/' + cases.length + '</td><td>' + pctBar(Math.round(x.rate)) + '</td><td class="small">' +
        (x.bad.length ? x.bad.map((c) => '<b>' + c.id + '</b> <span class="chip ' + c.priority + '">' + c.priority + '</span>').join('<br>') : '-') + '</td><td class="res ' + (x.pass ? 'passed' : 'failed') + '">' + (x.pass ? '✅ ผ่านเกณฑ์' : '❌ ไม่ผ่าน') + '</td></tr>').join('') +
      '</tbody></table></div></div>';
  }

  h += '<div class="kpis">' +
    kpi(cases.length, 'test case ทั้งหมด') + kpi(passed.length, 'ผ่าน', 'pass') + kpi(failed.length, 'ไม่ผ่าน', failed.length ? 'fail' : '') +
    (notrun.length ? kpi(notrun.length, 'ยังไม่ได้รัน', 'wait') : '') +
    kpi(rate + '%', 'อัตราผ่าน') + kpi(checksPassed + '/' + checksTotal, 'จุดตรวจที่ผ่าน (ทุกเบราว์เซอร์)') + kpi(D.runs, 'รอบที่รัน (test × เบราว์เซอร์)') + '</div>';

  // priority + module
  const line = (label, all) => {
    const ok = all.filter((c) => c.status === 'passed').length, bad = all.filter((c) => c.status === 'failed').length;
    const wait = all.length - ok - bad, pc = all.length ? Math.round((ok / all.length) * 100) : 0;
    return '<tr><td>' + label + '</td><td>' + all.length + '</td><td>' + ok + '</td><td>' + bad + '</td>' +
      (notrun.length ? '<td class="muted">' + wait + '</td>' : '') + '<td>' + pctBar(pc) + '</td></tr>';
  };
  const pr = ['P1', 'P2', 'P3'].map((p) => line('<span class="chip ' + p + '">' + p + '</span>', cases.filter((c) => c.priority === p))).join('');
  const mods = [...new Set(cases.map((c) => c.module))].map((m) => line(esc(m), cases.filter((c) => c.module === m))).join('');
  const thead = '<thead><tr><th></th><th>ทั้งหมด</th><th>ผ่าน</th><th>ไม่ผ่าน</th>' + (notrun.length ? '<th>ยังไม่รัน</th>' : '') + '<th>อัตราผ่าน</th></tr></thead>';
  h += '<div class="grid2"><div class="card"><h2>ผลตามระดับความสำคัญ</h2><table>' + thead.replace('<th></th>', '<th>ระดับ</th>') + '<tbody>' + pr + '</tbody></table></div>' +
    '<div class="card"><h2>ผลตามโมดูล</h2><div class="scroll"><table>' + thead.replace('<th></th>', '<th>โมดูล</th>') + '<tbody>' + mods + '</tbody></table></div></div></div>';

  // defects
  if (failed.length) {
    h += '<div class="card"><h2>🐞 ข้อบกพร่องที่พบ (Defects) · ' + failed.length + ' รายการ</h2><div class="scroll"><table><thead><tr>' +
      '<th>รหัส</th><th>test case</th><th>ความรุนแรง</th><th>ผิดตรงไหน</th><th>คาดหวัง</th><th>ได้จริง</th><th>เบราว์เซอร์</th><th>จำแนก (EX4)</th></tr></thead><tbody>' +
      failed.map((c) => { const f = firstFail(c); return '<tr class="click" onclick="go(\'' + c.id + '\')"><td><b>' + c.defect + '</b></td><td><b>' + c.id + '</b><div class="small muted">' + esc(c.title) + '</div></td>' +
        '<td><span class="chip ' + c.priority + '">' + c.priority + '</span></td><td>' + esc(f.where) + '</td><td>' + esc(f.expected) + '</td><td style="color:var(--fail)">' + esc(f.received) + '</td>' +
        '<td>' + c.browsers.filter((b) => b.status !== 'passed').map((b) => BRN[b.browser]).join(', ') + '</td>' + triageCell(c) + '</tr>'; }).join('') +
      '</tbody></table></div></div>';
  }

  // all test cases
  h += '<div class="card"><h2>ผลราย test case</h2><div class="filters" id="filters">' +
    [['', 'ทั้งหมด'], ['passed', 'ผ่าน'], ['failed', 'ไม่ผ่าน']].concat(notrun.length ? [['notrun', 'ยังไม่ได้รัน']] : [])
      .map(([s, x]) => '<button data-s="' + s + '" class="' + (s ? '' : 'on') + '">' + x + '</button>').join('') +
    '<span class="muted small">|</span>' + ['P1', 'P2', 'P3'].map((p) => '<button data-p="' + p + '">' + p + '</button>').join('') +
    '<input id="q" placeholder="🔍 ค้นหารหัส หรือชื่อ test case"></div><div class="scroll"><table><thead><tr><th>รหัส</th><th>สิ่งที่ทดสอบ</th><th>โมดูล</th><th>ระดับ</th><th>เทคนิค</th>' +
    '<th>ที่มา</th><th>เบราว์เซอร์</th><th>จุดตรวจที่ผ่าน</th><th>ผล</th></tr></thead><tbody id="rows"></tbody></table></div>' +
    '<div class="small muted" style="margin-top:8px">C = Chromium · F = Firefox · W = WebKit (Safari) · คลิกแต่ละแถวเพื่อดูขั้นตอน หลักฐาน GIF/วิดีโอ และจุดที่ผิด</div></div>';
  return h;
}

function triageCell(c) {
  if (!c.triage) return '<td style="color:var(--fail)">⚠️ ยังไม่จำแนก</td>';
  return '<td><b>' + esc(c.triage.cause) + '</b>' + (c.triage.note ? '<div class="small muted">' + esc(c.triage.note) + '</div>' : '') + '</td>';
}

function kpi(v, l, cls) { return '<div class="kpi ' + (cls || '') + '"><div class="v">' + v + '</div><div class="l">' + l + '</div></div>'; }

function firstFail(c) {
  for (const b of c.browsers) {
    const ck = b.checks.find((x) => !x.ok);
    if (ck) return { where: ck.step + ' → ' + ck.name, expected: ck.expected || '-', received: ck.received || '-' };
    if (b.stoppedAt) return { where: b.stoppedAt.step + ' (หยุดกลางทาง)', expected: 'ทำขั้นตอนนี้ได้', received: b.stoppedAt.message };
    if (b.error) return { where: '-', expected: '-', received: b.error };
  }
  return { where: '-', expected: '-', received: '-' };
}

let fs = { s: '', p: '', q: '' };
function rows() {
  const list = cases.filter((c) => (!fs.s || c.status === fs.s) && (!fs.p || c.priority === fs.p) &&
    (!fs.q || (c.id + ' ' + c.title).toLowerCase().includes(fs.q.toLowerCase())));
  $('#rows').innerHTML = list.map((c) => '<tr class="click" onclick="go(\'' + c.id + '\')"><td><b>' + c.id + '</b></td><td>' + esc(c.title) + '</td><td>' + esc(c.module) + '</td>' +
    '<td><span class="chip ' + c.priority + '">' + c.priority + '</span></td><td class="small">' + esc(c.technique) + '</td><td class="small">' + esc(c.source) + '</td><td style="white-space:nowrap">' +
    D.browsers.map((b) => { const r = c.browsers.find((x) => x.browser === b); return '<span class="br ' + (r ? r.status : 'none') + '" title="' + BRN[b] + '">' + BR[b] + '</span>'; }).join('') +
    '</td><td>' + (c.status === 'notrun' ? '<span class="muted">-</span>' : pctBar(c.pct) + '<div class="small muted">' + c.passed + '/' + c.total + ' จุด</div>') +
    '</td><td class="res ' + c.status + '">' + LABEL[c.status] + '</td></tr>').join('') ||
    '<tr><td colspan="9" class="muted">ไม่พบ test case</td></tr>';
}

function detail(id) {
  const i = cases.findIndex((c) => c.id === id), c = cases[i];
  if (!c) return '<p>ไม่พบ ' + esc(id) + '</p>';
  const main = c.browsers.find((b) => b.browser === 'chromium') || c.browsers[0];
  const color = c.pct >= 100 ? 'var(--pass)' : c.pct >= 60 ? 'var(--warn)' : 'var(--fail)';
  let h = '<a class="back" href="#/">← กลับหน้าสรุป</a>' +
    '<div class="tc-head"><h1>' + c.id + '</h1><span class="status ' + c.status + '">' + LABEL[c.status] + '</span>' +
    '<span class="chip ' + c.priority + '">' + c.priority + '</span><span class="chip">' + esc(c.module) + '</span><span class="chip">เทคนิค: ' + esc(c.technique) + '</span>' +
    (c.defect ? '<span class="chip no">' + c.defect + '</span>' : '') + '</div><p style="font-size:17px;margin:0 0 16px">' + esc(c.title) + '</p>';
  if (c.status === 'notrun') {
    return h + '<div class="card"><div class="muted small">ผลที่คาดหวัง (จาก TEST-PLAN.md)</div><div style="font-size:16px;font-weight:600;margin:2px 0 12px">' + esc(c.expected) + '</div>' +
      '<p>⏸ test case นี้อยู่ในแผน แต่ <b>ไม่ได้รันในรอบนี้</b> (อาจรันเฉพาะบางไฟล์) · รัน <code>npx playwright test</code> ทั้งหมดเพื่อดูผล</p></div>';
  }

  h += '<div class="grid2"><div class="card"><div class="sumrow"><div class="ring" style="--p:' + c.pct + ';--c:' + color + '"><div><div><b>' + c.pct + '%</b><br><small>จุดตรวจผ่าน</small></div></div></div>' +
    '<div><div class="muted small">ผลที่คาดหวัง (จาก TEST-PLAN.md)</div><div style="font-size:16px;font-weight:600;margin:2px 0 8px">' + esc(c.expected) + '</div>' +
    '<div class="small" style="margin:0 0 6px">ที่มา: <b>' + esc(c.source) + '</b></div>' +
    '<div class="small muted">ผ่าน ' + c.passed + ' จาก ' + c.total + ' จุดตรวจ รวมทุกเบราว์เซอร์ · ไฟล์ ' + esc(c.file) + '</div></div></div></div>' +
    '<div class="card"><h3>ผลแต่ละเบราว์เซอร์</h3><table><thead><tr><th>เบราว์เซอร์</th><th>ผล</th><th>จุดตรวจ</th><th>เวลา</th></tr></thead><tbody>' +
    c.browsers.map((b) => '<tr><td>' + BRN[b.browser] + '</td><td class="res ' + (b.status === 'passed' ? 'passed' : 'failed') + '">' + (TH[b.status] || b.status) + '</td><td>' +
      pctBar(b.total ? Math.round((b.passed / b.total) * 100) : 0) + '<div class="small muted">' + b.passed + '/' + b.total + '</div></td><td class="small">' + fmtDur(b.duration) +
      (b.mp4 && b.browser !== 'chromium' ? '<br><a href="' + b.mp4 + '" target="_blank">▶️ วิดีโอ</a>' : '') + '</td></tr>').join('') + '</tbody></table></div></div>';

  // what went wrong
  const bad = [];
  for (const b of c.browsers) {
    for (const ck of b.checks.filter((x) => !x.ok)) bad.push([BRN[b.browser], ck.step, ck.name, ck.expected || '-', ck.received || '-']);
    if (b.stoppedAt) bad.push([BRN[b.browser], b.stoppedAt.step, 'หยุดกลางทาง (ทำขั้นตอนต่อไม่ได้)', 'ทำขั้นตอนนี้ได้', b.stoppedAt.message]);
  }
  if (bad.length) {
    h += '<div class="errbox"><h3>❌ สรุปจุดที่ผิด</h3>' +
      (c.triage ? '<p style="margin:0 0 10px">🏷️ จำแนก: <b>' + esc(c.triage.cause) + '</b>' + (c.triage.note ? ' — ' + esc(c.triage.note) : '') + '</p>' : '<p style="margin:0 0 10px;color:var(--fail)">⚠️ ยังไม่จำแนกว่าเว็บผิด / แผนผิด / test เขียนผิด (EX4)</p>') +
      '<div class="scroll"><table><thead><tr><th>เบราว์เซอร์</th><th>ขั้นตอน</th><th>จุดตรวจ</th><th>คาดหวัง</th><th>ได้จริง</th></tr></thead><tbody>' +
      bad.map((r) => '<tr>' + r.map((x, k) => '<td' + (k === 4 ? ' style="color:var(--fail);font-weight:600"' : '') + '>' + esc(x) + '</td>').join('') + '</tr>').join('') +
      '</tbody></table></div>';
    const shots = c.browsers.flatMap((b) => b.shots.map((s) => ({ ...s, browser: b.browser })));
    if (shots.length) h += '<h3 style="margin-top:14px">📸 ภาพหน้าจอ (วงแดง = จุดที่ผิด)</h3><div class="shots">' +
      shots.map((s) => '<figure><img src="' + s.file + '" onclick="zoom(this.src)" loading="lazy"><figcaption>' + BRN[s.browser] + ' · ' + esc(s.name) + '</figcaption></figure>').join('') + '</div>';
    h += '</div>';
  }

  h += '<div class="grid2"><div class="card"><h3>ขั้นตอนและจุดตรวจ <span class="muted small">(' + BRN[main.browser] + ')</span></h3><ol class="steps">' +
    (main.steps.length ? main.steps.map((st) => {
      const cks = main.checks.filter((k) => k.step === st);
      const isBad = cks.some((k) => !k.ok) || (main.stoppedAt && main.stoppedAt.step === st);
      return '<li class="' + (isBad ? 'bad' : '') + '"><div class="st">' + esc(st) + '</div><ul>' +
        cks.map((k) => '<li class="' + (k.ok ? 'ok' : 'no') + '">' + esc(k.name) + (k.ok ? '' : '<span class="detail">คาดหวัง: ' + esc(k.expected || '-') + ' · ได้จริง: ' + esc(k.received || '-') + '</span>') + '</li>').join('') +
        (main.stoppedAt && main.stoppedAt.step === st ? '<li class="no">หยุดกลางทาง<span class="detail">' + esc(main.stoppedAt.message) + '</span></li>' : '') + '</ul></li>';
    }).join('') : '<li class="muted">ไม่มีข้อมูลขั้นตอน</li>') + '</ol></div>';

  h += '<div class="card media"><h3>🎬 หลักฐานการทดสอบ</h3>';
  if (c.gif || c.mp4) {
    h += '<div class="tabs">' + (c.gif ? '<button class="on" onclick="tab(this,\'g\')">GIF</button>' : '') + (c.mp4 ? '<button class="' + (c.gif ? '' : 'on') + '" onclick="tab(this,\'v\')">วิดีโอ MP4</button>' : '') + '</div>' +
      (c.gif ? '<div id="tg"><img src="' + c.gif + '" alt="GIF ' + c.id + '"></div>' : '') +
      (c.mp4 ? '<div id="tv" style="' + (c.gif ? 'display:none' : '') + '"><video src="' + c.mp4 + '" controls preload="metadata"></video></div>' : '') +
      '<div class="small muted" style="margin-top:8px">วงสีส้ม = จุดที่คลิก · วงสีแดง + ป้าย = จุดที่ผิด · ' +
      (c.gif ? '<a href="' + c.gif + '" download>ดาวน์โหลด GIF</a> · ' : '') + (c.mp4 ? '<a href="' + c.mp4 + '" download>ดาวน์โหลด MP4</a>' : '') + '</div>';
  } else h += '<p class="muted">test นี้ทดสอบผ่าน API โดยตรง ไม่ได้เปิดหน้าเว็บ จึงไม่มี GIF/วิดีโอ</p>';
  h += '</div></div>';

  const prev = cases[i - 1], next = cases[i + 1];
  h += '<div class="nav">' + (prev ? '<a href="#/tc/' + prev.id + '">← ' + prev.id + '</a>' : '<span></span>') + (next ? '<a href="#/tc/' + next.id + '">' + next.id + ' →</a>' : '<span></span>') + '</div>';
  return h;
}

function tab(btn, k) {
  btn.parentNode.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b === btn));
  const g = $('#tg'), v = $('#tv');
  if (g) g.style.display = k === 'g' ? '' : 'none';
  if (v) v.style.display = k === 'v' ? '' : 'none';
}
function zoom(src) { const z = $('#zoom'); z.querySelector('img').src = src; z.style.display = 'grid'; }
function go(id) { location.hash = '#/tc/' + id; }

function render() {
  const m = location.hash.match(/^#\/tc\/(.+)$/);
  $('#app').innerHTML = header() + '<div class="wrap">' + (m ? detail(decodeURIComponent(m[1])) : summary()) +
    '<footer>สร้างอัตโนมัติจาก Playwright · ข้อมูลแผนและเกณฑ์ผ่านจาก TEST-PLAN.md (หัวข้อ 5–6) · การจำแนกข้อที่ล้มจาก e2e/triage.json</footer></div><div id="zoom" onclick="this.style.display=\'none\'"><img></div>';
  if (!m) {
    rows();
    $('#filters').addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.s !== undefined) { fs.s = b.dataset.s; $('#filters').querySelectorAll('[data-s]').forEach((x) => x.classList.toggle('on', x === b)); }
      if (b.dataset.p) { fs.p = fs.p === b.dataset.p ? '' : b.dataset.p; $('#filters').querySelectorAll('[data-p]').forEach((x) => x.classList.toggle('on', x.dataset.p === fs.p)); }
      rows();
    });
    $('#q').addEventListener('input', (e) => { fs.q = e.target.value; rows(); });
  }
  window.scrollTo(0, 0);
}
addEventListener('hashchange', render);
render();
`;
