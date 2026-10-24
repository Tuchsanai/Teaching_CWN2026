// reporter เล็ก ๆ: เก็บผลแต่ละ TC ต่อเบราว์เซอร์ลง test-report/summary.json (รวมกับรอบก่อนของ project ที่ไม่ได้รัน)
// แล้วสร้าง e2e/index.html ใหม่ทุกครั้งที่รันจบ
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from './build-report.mjs';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, 'test-report');
const strip = (s = '') => s.replace(/\u001b\[[0-9;]*m/g, '');

export default class IndexReporter {
  onBegin(_config, suite) {
    this.rows = {};
    this.projects = new Set(suite.suites.filter((s) => s.allTests().length).map((s) => s.title));
  }
  onTestEnd(test, result) {
    const project = test.parent.project()?.name ?? '?';
    const id = test.title.split(' ')[0];
    const failedSteps = [];
    const walk = (steps) => steps.forEach((s) => { if (s.error && s.category === 'test.step') failedSteps.push(s.title); walk(s.steps); });
    walk(result.steps);
    (this.rows[project] ??= {})[id] = {
      status: result.status, // passed | failed | timedOut | skipped | interrupted
      duration: result.duration,
      errors: result.errors.map((e) => strip(e.message ?? String(e.value)).split('\n').slice(0, 6).join('\n')).slice(0, 6),
      failedSteps: [...new Set(failedSteps)],
      title: test.title,
    };
  }
  onEnd(result) {
    mkdirSync(OUT, { recursive: true });
    const file = join(OUT, 'summary.json');
    const prev = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : { projects: {} };
    const at = new Date().toISOString();
    for (const p of this.projects) prev.projects[p] = { at, gif: process.env.GIF === '1', results: this.rows[p] ?? {} };
    writeFileSync(file, JSON.stringify(prev, null, 2));
    // ประวัติทุกรอบ ใช้เช็กว่าผลนิ่งไหม
    const hfile = join(OUT, 'history.json');
    const hist = existsSync(hfile) ? JSON.parse(readFileSync(hfile, 'utf8')) : [];
    hist.push({ at, status: result.status, gif: process.env.GIF === '1',
      projects: Object.fromEntries([...this.projects].map((p) => [p, Object.fromEntries(Object.entries(this.rows[p] ?? {}).map(([k, v]) => [k, v.status]))])) });
    writeFileSync(hfile, JSON.stringify(hist, null, 2));
    build();
  }
  printsToStdio() { return false; }
}
