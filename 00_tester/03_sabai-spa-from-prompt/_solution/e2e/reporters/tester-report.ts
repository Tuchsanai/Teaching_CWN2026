import type { FullConfig, Reporter, Suite, TestCase, TestResult, TestStep } from '@playwright/test/reporter';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

/**
 * รายงานแบบ tester → test-report/TEST-REPORT.md
 *   1) สรุปผล + ผ่านเกณฑ์ไหม  2) ผลตามโมดูล  3) ผลราย TC ทุกเบราว์เซอร์ + ลิงก์ GIF/MP4/log  4) ข้อบกพร่อง DEF-001…
 * วิดีโอของทุก test (โหมด GIF=1 อัดทุก test) → test-report/gifs/<TC>.gif และ test-report/videos/<TC>.mp4 ด้วย ffmpeg
 * attachment "api-log" → test-report/logs/<TC>-<browser>.log (หลักฐานของ TC ที่เรียก API)
 */

type Result = { status: string; ms: number; error?: string; video?: string; screenshot?: string; log?: string; steps: string[] };
type Row = { id: string; title: string; module: string; priority: string; expected: string; file: string; notes: string[]; results: Record<string, Result> };

const OUT = path.resolve('test-report');
const GIF_DIR = path.join(OUT, 'gifs');
const MP4_DIR = path.join(OUT, 'videos');
const LOG_DIR = path.join(OUT, 'logs');
const ICON: Record<string, string> = { passed: '✅ ผ่าน', failed: '❌ ไม่ผ่าน', timedOut: '⏱️ หมดเวลา', skipped: '⏭️ ข้าม', interrupted: '⛔ หยุด' };
const MODULES: Record<string, string> = {
  HOME: 'หน้าแรก / บริการ', MOOD: 'เลือกอารมณ์', BOOK: 'การจอง', THER: 'นักบำบัด / รีวิว', AI: 'แบบทดสอบ / วิเคราะห์ผิว',
  CHAT: 'Chatbot', MEM: 'สมาชิก / แต้ม', DASH: 'หน้าบัญชี', WAL: 'Wallet / คอร์ส', GIFT: 'Gift Card', EXP: 'ประสบการณ์ / ทัวร์ 360°',
  I18N: 'หลายภาษา', MOB: 'มือถือ', API: 'API',
};

const strip = (s = '') => s.replace(/\u001b\[[0-9;]*m/g, '');
const cell = (s = '') => s.replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');

/** แปลง error ของ Playwright เป็นประโยคที่คนทั่วไปอ่านเข้าใจ: ตรงไหน + คาดว่าอะไร แต่ได้อะไร */
function describeError(msg: string) {
  const line = (label: string) => msg.match(new RegExp(`^\\s*${label}[^:]*:\\s*(.+)$`, 'm'))?.[1].trim();
  const custom = msg.split('\n')[0].match(/^Error:\s*(.+?):?\s*$/)?.[1];
  const locator = line('Locator')?.replace(/getByTestId\('([^']+)'\)/, '"$1"');
  const expected = line('Expected');
  const received = line('Received');
  const where = custom && !/expect\(/.test(custom) ? custom : locator ?? 'หน้าเว็บ/API';
  if (/element\(s\) not found/.test(msg)) return `ไม่พบ ${locator ?? 'element'} บนหน้าเว็บ (คาดว่าจะเห็น ${expected ?? 'element นี้'})`;
  if (received) return `${where}: คาดว่า ${expected} แต่ได้จริง ${received}`;
  if (/Timeout|timeout/.test(msg)) return `หา/กด ${locator ?? 'element'} ไม่ได้ภายในเวลาที่กำหนด`;
  return msg.split('\n').filter(Boolean).slice(0, 2).join(' ');
}

/** ขั้นตอนทำซ้ำจาก step ที่ตั้งชื่อเอง (test.step) และคำสั่งของ Playwright (goto / click / fill …) */
function flattenSteps(steps: TestStep[], out: string[] = []) {
  for (const s of steps) {
    if (s.category === 'test.step') {
      out.push(s.title);
      continue; // ไม่ต้องลงรายละเอียดข้างใน step ที่ตั้งชื่อแล้ว
    }
    if (s.category === 'pw:api' && /^(Navigate|Click|Fill|Select|Check|Press|Type|page\.goto|.*\.click|.*\.fill|.*\.request|GET|POST)/i.test(s.title)) out.push(s.title);
    flattenSteps(s.steps, out);
  }
  return out;
}

export default class TesterReport implements Reporter {
  private rows = new Map<string, Row>();
  private projects: string[] = [];
  private baseURL = 'http://localhost:3000';
  private started = new Date();

  /** คอลัมน์ในรายงาน = ชื่อเบราว์เซอร์ (project "time-travel" รันบน chromium จึงรวมอยู่ในคอลัมน์ chromium) */
  private browserOf(p?: { name: string; use: { browserName?: string; defaultBrowserType?: string } }) {
    return p?.use.browserName ?? p?.use.defaultBrowserType ?? p?.name ?? 'default';
  }

  onBegin(config: FullConfig, suite: Suite) {
    // เฉพาะเบราว์เซอร์ที่ถูกรันจริง (เช่น test:gif รันแค่ chromium) · ข้าม project "setup" ที่ไม่มี TC
    const order = ['chromium', 'firefox', 'webkit'];
    const used = new Set(suite.suites.filter((s) => s.project()?.name !== 'setup' && s.allTests().length).map((s) => this.browserOf(s.project())));
    this.projects = [...used].sort((a, b) => order.indexOf(a) - order.indexOf(b));
    this.baseURL = (config.projects[0]?.use?.baseURL as string) ?? this.baseURL;
    this.started = new Date();
    // ล้างหลักฐานของรอบก่อน: log ทุกรอบ · GIF/MP4 เฉพาะรอบ GIF=1 (รอบปกติไม่ได้อัดวิดีโอทุกข้อ จึงเก็บของเดิมไว้)
    fs.rmSync(LOG_DIR, { recursive: true, force: true });
    if (process.env.GIF) for (const d of [GIF_DIR, MP4_DIR]) fs.rmSync(d, { recursive: true, force: true });
  }

  onTestEnd(test: TestCase, result: TestResult) {
    if (!/^TC-[A-Z0-9]+-\d+/.test(test.title)) return; // เช่น test ของ project setup
    const [id, ...rest] = test.title.split(' ');
    const moduleTag = test.tags.map((t) => t.slice(1)).find((t) => MODULES[t]);
    const row = this.rows.get(id) ?? {
      id,
      title: rest.join(' '),
      module: MODULES[moduleTag ?? id.split('-')[1]] ?? '-',
      priority: test.tags.find((t) => /^@P\d$/.test(t))?.slice(1) ?? 'P3',
      expected: test.annotations.find((a) => a.type === 'expected')?.description ?? '',
      file: path.basename(test.location.file),
      notes: [],
      results: {},
    };
    for (const a of [...test.annotations, ...((result as { annotations?: { type: string; description?: string }[] }).annotations ?? [])]) {
      if ((a.type === 'note' || a.type === 'ต้องถาม') && a.description) {
        const n = `${a.type === 'ต้องถาม' ? '❓ ต้องถาม: ' : ''}${a.description}`;
        if (!row.notes.includes(n)) row.notes.push(n);
      }
    }
    const project = this.browserOf(test.parent.project());

    let log: string | undefined;
    const apiLog = result.attachments.find((a) => a.name === 'api-log');
    if (apiLog) {
      fs.mkdirSync(LOG_DIR, { recursive: true });
      const dest = path.join(LOG_DIR, `${id}-${project}.log`);
      if (apiLog.body) fs.writeFileSync(dest, apiLog.body);
      else if (apiLog.path && fs.existsSync(apiLog.path)) fs.copyFileSync(apiLog.path, dest);
      log = path.relative(OUT, dest).replace(/\\/g, '/');
    }

    row.results[project] = {
      status: result.status,
      ms: result.duration,
      error: result.errors.length ? result.errors.map((e) => describeError(strip(e.message ?? ''))).join(' · ') : undefined,
      video: result.attachments.find((a) => a.name === 'video')?.path,
      screenshot: result.attachments.find((a) => a.name === 'screenshot')?.path,
      log,
      steps: flattenSteps(result.steps),
    };
    this.rows.set(id, row);
  }

  async onEnd() {
    if (!this.rows.size) return; // เช่น `playwright test --list`
    fs.mkdirSync(GIF_DIR, { recursive: true });
    fs.mkdirSync(MP4_DIR, { recursive: true });
    fs.rmSync(path.join(OUT, 'failures'), { recursive: true, force: true });
    const rows = [...this.rows.values()].sort((a, b) => a.file.localeCompare(b.file) || a.id.localeCompare(b.id));

    // 1) วิดีโอ .webm → GIF + MP4 (ใช้วิดีโอของ chromium ก่อน ถ้าไม่มีใช้ของเบราว์เซอร์อื่น)
    let gifCount = 0;
    let mp4Count = 0;
    for (const row of rows) {
      const order = ['chromium', ...Object.keys(row.results).filter((p) => p !== 'chromium')];
      const video = order.map((p) => row.results[p]?.video).find((v) => v && fs.existsSync(v));
      if (!video) continue;
      // รอบปกติ (ไม่ใช่ GIF=1) อัดเฉพาะข้อที่ล้ม — ถ้ามี GIF/MP4 จากรอบ test:gif อยู่แล้วให้เก็บของเดิม (ช้าและมีป้ายชื่อ อ่านง่ายกว่า)
      if (!process.env.GIF && fs.existsSync(path.join(GIF_DIR, `${row.id}.gif`)) && fs.existsSync(path.join(MP4_DIR, `${row.id}.mp4`))) continue;

      const gif = path.join(GIF_DIR, `${row.id}.gif`);
      const g = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-vf',
        'fps=8,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
        '-loop', '0', gif], { stdio: 'inherit' });
      if (g.status === 0 && fs.existsSync(gif)) gifCount++;
      else console.warn(`⚠️  แปลง GIF ไม่สำเร็จ: ${row.id} (มี ffmpeg ใน PATH หรือยัง?)`);

      const mp4 = path.join(MP4_DIR, `${row.id}.mp4`);
      const m = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-crf', '26', '-preset', 'veryfast', '-movflags', '+faststart', '-an', mp4],
        { stdio: 'inherit' });
      if (m.status === 0 && fs.existsSync(mp4)) mp4Count++;
      else console.warn(`⚠️  แปลง MP4 ไม่สำเร็จ: ${row.id}`);
    }

    // 2) ภาพหน้าจอตอนล้ม → คัดลอกมาไว้ข้างรายงานให้ลิงก์ใช้ได้
    for (const row of rows) for (const [proj, r] of Object.entries(row.results)) {
      if (r.screenshot && fs.existsSync(r.screenshot)) {
        const dest = path.join(OUT, 'failures', `${row.id}-${proj}.png`);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.copyFileSync(r.screenshot, dest);
        r.screenshot = path.relative(OUT, dest).replace(/\\/g, '/');
      } else r.screenshot = undefined;
    }

    // 3) รายงาน
    const html = await fetch(this.baseURL).then((r) => r.text()).catch(() => '');
    const bugMode = html.match(/data-bug-mode="(\d)"/)?.[1] ?? '?';
    const all = rows.flatMap((r) => Object.values(r.results));
    const count = (s: string) => all.filter((r) => r.status === s).length;
    const passed = count('passed');
    const skipped = count('skipped');
    const failed = all.length - passed - skipped;
    const rate = all.length ? ((passed / all.length) * 100).toFixed(1) : '0';
    const bad = (x: Result) => x.status !== 'passed' && x.status !== 'skipped';
    const p1Rows = rows.filter((r) => r.priority === 'P1');
    const p1Failed = p1Rows.filter((r) => Object.values(r.results).some(bad));
    // เกณฑ์ของ TEST-PLAN นับราย TC: TC ผ่านเมื่อไม่ล้มในเบราว์เซอร์ใดเลย (ข้อที่ถูกข้ามในบางเบราว์เซอร์ดูจากเบราว์เซอร์ที่รันได้)
    const tcPassed = rows.filter((r) => !Object.values(r.results).some(bad) && Object.values(r.results).some((x) => x.status === 'passed'));
    const tcRate = rows.length ? (tcPassed.length / rows.length) * 100 : 0;
    const exitOk = p1Failed.length === 0 && tcRate >= 95;
    const gifFiles = fs.readdirSync(GIF_DIR).filter((x) => x.endsWith('.gif'));
    const mp4Files = fs.readdirSync(MP4_DIR).filter((x) => x.endsWith('.mp4'));
    const secs = ((Date.now() - this.started.getTime()) / 1000).toFixed(0);
    const evidence = (r: Row) => {
      const links = [
        fs.existsSync(path.join(GIF_DIR, `${r.id}.gif`)) && `[▶ GIF](gifs/${r.id}.gif)`,
        fs.existsSync(path.join(MP4_DIR, `${r.id}.mp4`)) && `[🎬 MP4](videos/${r.id}.mp4)`,
        ...Object.entries(r.results).filter(([, x]) => x.log).map(([p, x]) => `[📄 log ${p}](${x.log})`),
      ].filter(Boolean);
      return links.length ? links.join(' · ') : '–';
    };

    const L: string[] = [];
    L.push('# 🧪 รายงานผลการทดสอบ (Test Summary Report) — สบายใจ สปา', '');
    L.push('| หัวข้อ | รายละเอียด |', '|---|---|');
    L.push('| ระบบที่ทดสอบ | เว็บสบายใจ สปา · Sabai Jai Wellness Spa (Next.js + PostgreSQL ใน Docker) |');
    L.push(`| URL | ${this.baseURL} |`);
    const modeText = bugMode === '1' ? '🐞 BUG_MODE=1 (โหมดฝังบั๊กสำหรับฝึก)' : bugMode === '0' ? 'ปกติ (BUG_MODE=0)' : 'ไม่ทราบ (อ่าน data-bug-mode ไม่ได้)';
    L.push(`| โหมดเซิร์ฟเวอร์ | ${modeText} — อ่านจาก \`<html data-bug-mode>\` |`);
    L.push('| ข้อมูลทดสอบ | `POST /api/test/reset {"now":"2026-10-08T10:00:00+07:00"}` ครั้งเดียวก่อนรัน (R0) · TC ที่ต้องย้ายเวลา (`*.serial.spec.ts`) รันทีละข้อบน chromium หลัง 3 เบราว์เซอร์จบ แล้ว reset กลับ R0 |');
    L.push(`| เบราว์เซอร์ | ${this.projects.join(', ')} |`);
    L.push('| เครื่องมือ | Playwright (TypeScript) บน Windows · locale th-TH · Asia/Bangkok · 1280×800 |');
    L.push(`| วันที่ทดสอบ | ${this.started.toLocaleString('th-TH', { dateStyle: 'long', timeStyle: 'short', timeZone: 'Asia/Bangkok' })} |`);
    L.push(`| ใช้เวลา | ${secs} วินาที |`, '');

    L.push('## 1. สรุปผล', '');
    L.push('| นับราย TC (เกณฑ์ของแผน) | TC ทั้งหมด | ✅ TC ที่ผ่าน | ❌ TC ที่ล้ม | อัตราผ่านราย TC | P1 ที่ไม่ผ่าน |', '|---|---|---|---|---|---|');
    const p1List = p1Failed.length ? ` (${p1Failed.map((r) => r.id).join(', ')})` : '';
    L.push(`| | ${rows.length} | ${tcPassed.length} | ${rows.length - tcPassed.length} | **${tcRate.toFixed(1)}%** | ${p1Failed.length}/${p1Rows.length}${p1List} |`, '');
    L.push('| นับรายรอบ (TC × เบราว์เซอร์) | ทั้งหมด | ✅ ผ่าน | ❌ ไม่ผ่าน | ⏭️ ข้าม | อัตราผ่านรายรอบ |', '|---|---|---|---|---|---|');
    L.push(`| | ${all.length} | ${passed} | ${failed} | ${skipped} | ${rate}% |`, '');
    L.push('| เบราว์เซอร์ | ✅ ผ่าน | ❌ ล้ม | ⏭️ ข้าม | TC ที่ล้ม |', '|---|---|---|---|---|');
    for (const p of this.projects) {
      const res = rows.filter((r) => r.results[p]).map((r) => [r.id, r.results[p]] as const);
      const fails = res.filter(([, x]) => bad(x)).map(([id]) => id);
      const count = (st: string) => res.filter(([, x]) => x.status === st).length;
      L.push(`| ${p} | ${count('passed')} | ${fails.length} | ${count('skipped')} | ${fails.join(', ') || '–'} |`);
    }
    L.push('');
    L.push(`**หลักฐาน:** GIF ${gifFiles.length} ไฟล์ (test-report/gifs) · MP4 ${mp4Files.length} ไฟล์ (test-report/videos) · log ของ API ใน test-report/logs`, '');
    L.push('**เกณฑ์ผ่าน (Exit criteria ตาม TEST-PLAN.md §6):** TC ระดับ P1 ต้องผ่านทั้งหมด และผ่านรวม ≥ 95% (อย่างน้อย 32 จาก 33 TC) · TC ที่เปิดหน้าเว็บต้องมีทั้ง GIF และ MP4', '');
    L.push(exitOk ? '> ✅ **ผลการประเมิน: ผ่านเกณฑ์**' : '> ❌ **ผลการประเมิน: ไม่ผ่านเกณฑ์ ต้องแก้ไขข้อบกพร่องก่อนปล่อยใช้งาน**', '');

    L.push('## 2. ผลตามโมดูล', '');
    L.push('| โมดูล | จำนวน TC | ผลรัน | ผ่าน | ไม่ผ่าน |', '|---|---|---|---|---|');
    const byModule = new Map<string, Row[]>();
    for (const r of rows) byModule.set(r.module, [...(byModule.get(r.module) ?? []), r]);
    for (const [mod, list] of byModule) {
      const res = list.flatMap((r) => Object.values(r.results));
      const ok = res.filter((x) => x.status === 'passed').length;
      L.push(`| ${mod} | ${list.length} | ${res.length} | ${ok} | ${res.length - ok} |`);
    }
    L.push('');

    L.push('## 3. ผลราย test case', '');
    L.push(`| ID | สิ่งที่ทดสอบ | ระดับ | ผลที่คาดหวัง | ${this.projects.join(' | ')} | หลักฐาน |`);
    L.push(`|---|---|---|---|${this.projects.map(() => '---').join('|')}|---|`);
    for (const r of rows) {
      const cells = this.projects.map((p) => {
        const x = r.results[p];
        return x ? `${ICON[x.status] ?? x.status} (${(x.ms / 1000).toFixed(1)}s)` : '–';
      });
      L.push(`| ${r.id} | ${cell(r.title)} | ${r.priority} | ${cell(r.expected)} | ${cells.join(' | ')} | ${evidence(r)} |`);
    }
    L.push('');

    const noted = rows.filter((r) => r.notes.length);
    if (noted.length) {
      L.push('### หมายเหตุของแต่ละ TC (ข้อมูลที่ปรับเพื่อรันขนานได้ / ค่าที่ "ต้องถาม" และค่าที่เว็บแสดงจริง)', '');
      L.push('| ID | หมายเหตุ |', '|---|---|');
      for (const r of noted) L.push(`| ${r.id} | ${r.notes.map(cell).join('<br>')} |`);
      L.push('');
    }

    L.push('## 4. ข้อบกพร่องที่พบ (Defects)', '');
    const defects = rows.filter((r) => Object.values(r.results).some(bad));
    if (!defects.length) L.push('ไม่พบข้อบกพร่อง 🎉', '');
    defects.forEach((r, i) => {
      const fails = Object.entries(r.results).filter(([, x]) => bad(x));
      const severity = r.priority === 'P1' ? 'P1 · สูง (เงินผิด / จองไม่ได้ / จองซ้อน)'
        : r.priority === 'P2' ? 'P2 · กลาง (ฟีเจอร์สำคัญทำงานผิด)' : 'P3 · ต่ำ (ความสวยงาม / เกิดไม่บ่อย)';
      const steps = fails[0][1].steps.slice(0, 15);
      L.push(`### DEF-${String(i + 1).padStart(3, '0')} · ${r.id} ${r.title}`, '');
      L.push('| หัวข้อ | รายละเอียด |', '|---|---|');
      L.push(`| Test case | ${r.id} (\`tests/${r.file}\`) |`);
      L.push(`| ระดับ | ${severity} |`);
      L.push(`| เบราว์เซอร์ที่พบ | ${fails.map(([p]) => p).join(', ')} |`);
      L.push(`| โหมดเซิร์ฟเวอร์ | BUG_MODE=${bugMode} |`);
      L.push(`| ขั้นตอนทำซ้ำ | ${steps.map((s, n) => `${n + 1}. ${cell(s)}`).join('<br>')}${steps.length ? '<br>' : ''}รันซ้ำ: \`npx playwright test -g "${r.id}"\` |`);
      L.push(`| ผลที่คาดหวัง | ${cell(r.expected)} |`);
      L.push(`| ผลที่เกิดขึ้นจริง | ${fails.map(([p, x]) => `❌ (${p}) ${cell((x.error ?? x.status).slice(0, 400))}`).join('<br>')} |`);
      const shot = fails.find(([, x]) => x.screenshot)?.[1].screenshot;
      L.push(`| หลักฐาน | ${evidence(r)}${shot ? ` · [📷 ภาพตอนล้ม](${shot})` : ''} |`, '');
    });

    L.push('---', '', 'รายงานนี้สร้างอัตโนมัติจาก `reporters/tester-report.ts` · ดูรายละเอียดทุกขั้นได้ที่ `npm run report`');
    fs.writeFileSync(path.join(OUT, 'TEST-REPORT.md'), L.join('\n'), 'utf8');
    console.log(`\n📝 รายงาน: ${path.join(OUT, 'TEST-REPORT.md')}` +
      (gifCount || mp4Count ? `\n🎞️ GIF ${gifCount} ไฟล์ → ${GIF_DIR}\n🎬 MP4 ${mp4Count} ไฟล์ → ${MP4_DIR}` : ''));
  }
}
