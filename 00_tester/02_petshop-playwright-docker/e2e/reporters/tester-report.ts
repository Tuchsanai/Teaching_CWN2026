import type { FullConfig, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

/**
 * Writes test-report/TEST-REPORT.md the way a software tester would:
 * summary → results per module → every test case → defects found.
 * In GIF mode it also turns each recorded video into test-report/gifs/<TC-ID>.gif
 */

type Row = {
  id: string;
  title: string;
  module: string;
  priority: string;
  expected: string;
  file: string;
  results: Record<string, { status: string; ms: number; error?: string; video?: string; screenshot?: string }>;
};

const OUT = path.resolve('test-report');
const GIF_DIR = path.join(OUT, 'gifs');
const MP4_DIR = path.join(OUT, 'videos');
const ICON: Record<string, string> = { passed: '✅', failed: '❌', timedOut: '⏱️', skipped: '⏭️', interrupted: '⛔' };
const MODULES: Record<string, string> = {
  HOME: 'หน้าแรก', CAT: 'ค้นหา / กรองสินค้า', PRD: 'หน้าสินค้า', WISH: 'รายการโปรด', CART: 'ตะกร้าสินค้า',
  CPN: 'คูปองส่วนลด', AUTH: 'สมัคร / เข้าสู่ระบบ', CHK: 'สั่งซื้อ / ชำระเงิน', REC: 'ระบบแนะนำสินค้า', MOB: 'มือถือ', API: 'API',
};

const strip = (s = '') => s.replace(/\u001b\[[0-9;]*m/g, '');

/** Turn a Playwright error into one line a non-programmer can read: where + expected vs. actual. */
function describeError(msg: string) {
  const line = (label: string) => msg.match(new RegExp(`^\\s*${label}[^:]*:\\s*(.+)$`, 'm'))?.[1].trim();
  const locator = line('Locator')?.replace(/getByTestId\('([^']+)'\)/, '$1');
  const expected = line('Expected');
  const received = line('Received');
  if (/element\(s\) not found/.test(msg)) return `ไม่พบ ${locator ?? 'element'} บนหน้าเว็บ (คาดว่าจะเห็น ${expected ?? 'element นี้'})`;
  if (received) return `ที่ ${locator ?? 'หน้าเว็บ'}: คาดว่า ${expected} แต่ได้ ${received}`;
  if (/Timeout|timeout/.test(msg)) return `หา/กด ${locator ?? 'element'} ไม่ได้ภายในเวลาที่กำหนด (${msg.split('\n')[0]})`;
  return msg.split('\n').filter(Boolean).slice(0, 2).join(' ');
}

export default class TesterReport implements Reporter {
  private rows = new Map<string, Row>();
  private projects: string[] = [];
  private baseURL = 'http://localhost:3000';
  private started = new Date();

  onBegin(config: FullConfig, _suite: Suite) {
    this.projects = config.projects.map((p) => p.name);
    this.baseURL = (config.projects[0]?.use?.baseURL as string) ?? this.baseURL;
    this.started = new Date();
  }

  onTestEnd(test: TestCase, result: TestResult) {
    const [id, ...rest] = test.title.split(' ');
    const key = id;
    const row = this.rows.get(key) ?? {
      id,
      title: rest.join(' '),
      module: MODULES[id.split('-')[1]] ?? '-',
      priority: test.tags.find((t) => /^@P\d$/.test(t))?.slice(1) ?? 'P3',
      expected: test.annotations.find((a) => a.type === 'expected')?.description ?? '',
      file: path.basename(test.location.file),
      results: {},
    };
    const project = test.parent.project()?.name ?? 'default';
    row.results[project] = {
      status: result.status,
      ms: result.duration,
      error: result.error ? describeError(strip(result.error.message)) : undefined,
      video: result.attachments.find((a) => a.name === 'video')?.path,
      screenshot: result.attachments.find((a) => a.name === 'screenshot')?.path,
    };
    this.rows.set(key, row);
  }

  async onEnd() {
    if (!this.rows.size) return; // e.g. `playwright test --list`
    fs.mkdirSync(GIF_DIR, { recursive: true });
    fs.mkdirSync(MP4_DIR, { recursive: true });
    fs.rmSync(path.join(OUT, 'failures'), { recursive: true, force: true });
    const rows = [...this.rows.values()].sort((a, b) => a.file.localeCompare(b.file) || a.id.localeCompare(b.id));

    // 1) videos → GIFs (only when videos were recorded)
    let gifCount = 0;
    for (const row of rows) {
      const video = Object.values(row.results).find((r) => r.video && fs.existsSync(r.video))?.video;
      if (!video) continue;
      const gif = path.join(GIF_DIR, `${row.id}.gif`);
      const ok = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-vf',
        'fps=6,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
        '-loop', '0', gif], { stdio: 'inherit' });
      if (ok.status === 0) gifCount++;
      else console.warn(`⚠️  แปลง GIF ไม่สำเร็จ: ${row.id} (มี ffmpeg ใน PATH หรือยัง?)`);

      // the same recording as .mp4 (plays everywhere: Windows, LINE, PowerPoint)
      spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-crf', '26', '-preset', 'veryfast', '-movflags', '+faststart', '-an', path.join(MP4_DIR, `${row.id}.mp4`)], { stdio: 'inherit' });
    }

    // 2) failure screenshots → copy next to the report so the links work
    for (const row of rows) for (const [proj, r] of Object.entries(row.results)) {
      if (r.screenshot && fs.existsSync(r.screenshot)) {
        const dest = path.join(OUT, 'failures', `${row.id}-${proj}.png`);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.copyFileSync(r.screenshot, dest);
        r.screenshot = path.relative(OUT, dest).replace(/\\/g, '/');
      } else r.screenshot = undefined;
    }

    // 3) the report
    const bugMode = await fetch(this.baseURL).then((r) => r.text()).then((h) => /data-bug-mode="1"/.test(h)).catch(() => false);
    const all = rows.flatMap((r) => Object.values(r.results));
    const count = (s: string) => all.filter((r) => r.status === s).length;
    const passed = count('passed');
    const failed = all.length - passed - count('skipped');
    const rate = all.length ? ((passed / all.length) * 100).toFixed(1) : '0';
    const p1Failed = rows.some((r) => r.priority === 'P1' && Object.values(r.results).some((x) => x.status !== 'passed' && x.status !== 'skipped'));
    const exitOk = !p1Failed && Number(rate) >= 95;
    const secs = ((Date.now() - this.started.getTime()) / 1000).toFixed(0);
    const gifLink = (id: string) => {
      const links = [
        fs.existsSync(path.join(GIF_DIR, `${id}.gif`)) && `[▶ GIF](gifs/${id}.gif)`,
        fs.existsSync(path.join(MP4_DIR, `${id}.mp4`)) && `[🎬 MP4](videos/${id}.mp4)`,
      ].filter(Boolean);
      return links.length ? links.join(' · ') : '–';
    };

    const lines: string[] = [];
    lines.push('# 🧪 รายงานผลการทดสอบ (Test Summary Report) — PawPantry', '');
    lines.push('| หัวข้อ | รายละเอียด |', '|---|---|');
    lines.push(`| ระบบที่ทดสอบ | เว็บร้านอาหารสัตว์ PawPantry (Next.js ใน Docker) |`);
    lines.push(`| URL | ${this.baseURL} |`);
    lines.push(`| โหมดเซิร์ฟเวอร์ | ${bugMode ? '🐞 BUG_MODE=1 (ฝังบั๊กไว้ 3 จุดเพื่อฝึก)' : 'ปกติ (BUG_MODE=0)'} |`);
    lines.push(`| เบราว์เซอร์ | ${this.projects.join(', ')} |`);
    lines.push(`| เครื่องมือ | Playwright บน Windows |`);
    lines.push(`| วันที่ทดสอบ | ${this.started.toLocaleString('th-TH', { dateStyle: 'long', timeStyle: 'short' })} |`);
    lines.push(`| ใช้เวลา | ${secs} วินาที |`, '');

    lines.push('## 1. สรุปผล', '');
    lines.push('| ทั้งหมด | ✅ ผ่าน | ❌ ไม่ผ่าน | ⏭️ ข้าม | อัตราผ่าน |', '|---|---|---|---|---|');
    lines.push(`| ${all.length} | ${passed} | ${failed} | ${count('skipped')} | **${rate}%** |`, '');
    lines.push(`**เกณฑ์ผ่าน (Exit criteria):** test case ระดับ P1 ต้องผ่านทั้งหมด และอัตราผ่านรวม ≥ 95%`, '');
    lines.push(exitOk ? '> ✅ **ผลการประเมิน: ผ่านเกณฑ์ พร้อมปล่อยใช้งาน**' : '> ❌ **ผลการประเมิน: ไม่ผ่านเกณฑ์ ต้องแก้ไขข้อบกพร่องก่อนปล่อยใช้งาน**', '');

    lines.push('## 2. ผลตามโมดูล', '');
    lines.push('| โมดูล | จำนวน test case | ผ่าน | ไม่ผ่าน |', '|---|---|---|---|');
    const byModule = new Map<string, Row[]>();
    for (const r of rows) byModule.set(r.module, [...(byModule.get(r.module) ?? []), r]);
    for (const [mod, list] of byModule) {
      const res = list.flatMap((r) => Object.values(r.results));
      const ok = res.filter((x) => x.status === 'passed').length;
      lines.push(`| ${mod} | ${list.length} | ${ok} | ${res.length - ok} |`);
    }
    lines.push('');

    lines.push('## 3. ผลราย test case', '');
    lines.push(`| ID | สิ่งที่ทดสอบ | ระดับ | ผลที่คาดหวัง | ${this.projects.join(' | ')} | หลักฐาน |`);
    lines.push(`|---|---|---|---|${this.projects.map(() => '---').join('|')}|---|`);
    for (const r of rows) {
      const cells = this.projects.map((p) => (r.results[p] ? ICON[r.results[p].status] ?? r.results[p].status : '–'));
      lines.push(`| ${r.id} | ${r.title} | ${r.priority} | ${r.expected} | ${cells.join(' | ')} | ${gifLink(r.id)} |`);
    }
    lines.push('');

    lines.push('## 4. ข้อบกพร่องที่พบ (Defects)', '');
    const defects = rows.filter((r) => Object.values(r.results).some((x) => x.status !== 'passed' && x.status !== 'skipped'));
    if (!defects.length) lines.push('ไม่พบข้อบกพร่อง 🎉', '');
    defects.forEach((r, i) => {
      const fails = Object.entries(r.results).filter(([, x]) => x.status !== 'passed' && x.status !== 'skipped');
      const severity = r.priority === 'P1' ? 'สูง (High)' : r.priority === 'P2' ? 'กลาง (Medium)' : 'ต่ำ (Low)';
      lines.push(`### DEF-${String(i + 1).padStart(3, '0')} · ${r.title}`, '');
      lines.push('| หัวข้อ | รายละเอียด |', '|---|---|');
      lines.push(`| Test case | ${r.id} (${r.file}) |`);
      lines.push(`| ความรุนแรง | ${severity} |`);
      lines.push(`| เบราว์เซอร์ที่พบ | ${fails.map(([p]) => p).join(', ')} |`);
      lines.push(`| ผลที่คาดหวัง | ${r.expected} |`);
      lines.push(`| ผลที่เกิดขึ้นจริง | ❌ ${(fails[0][1].error ?? fails[0][1].status).replace(/\|/g, '\\|').slice(0, 300)} |`);
      lines.push(`| ขั้นตอนทำซ้ำ | รัน \`npx playwright test -g "${r.id}"\` หรือดู GIF ด้านล่าง |`);
      const shot = fails.find(([, x]) => x.screenshot)?.[1].screenshot;
      lines.push(`| หลักฐาน | ${gifLink(r.id)}${shot ? ` · [ภาพตอนล้ม](${shot})` : ''} |`, '');
    });

    lines.push('---', '', `รายงานนี้สร้างอัตโนมัติจาก \`reporters/tester-report.ts\` · ดูรายละเอียดทุกขั้นได้ที่ \`npx playwright show-report\``);
    fs.writeFileSync(path.join(OUT, 'TEST-REPORT.md'), lines.join('\n'), 'utf8');
    console.log(`\n📝 รายงาน: ${path.join(OUT, 'TEST-REPORT.md')}${gifCount ? `  ·  🎞️ GIF + MP4 อย่างละ ${gifCount} ไฟล์: ${GIF_DIR} , ${MP4_DIR}` : ''}`);
  }
}
