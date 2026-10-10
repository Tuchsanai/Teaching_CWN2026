import { request, type FullConfig } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';

// วันล็อกจาก TEST-DATA.md: TODAY=2026-10-10T10:00:00+07:00
export const TODAY = '2026-10-10T10:00:00+07:00';

export default async function globalSetup(config: FullConfig) {
  const baseURL = (config.projects[1]?.use?.baseURL as string) ?? 'http://localhost:3000';
  const api = await request.newContext({ baseURL });

  // Entry EN-3: /api/health ต้องเป็น {"ok":true,"db":true} ตรงตัว
  const h = await api.get('/api/health', { timeout: 10_000 }).catch((e) => { throw new Error(`เว็บไม่ตอบ ${baseURL}/api/health: ${e.message}`); });
  const body = await h.text();
  if (h.status() !== 200 || body.replace(/\s/g, '') !== '{"ok":true,"db":true}') {
    throw new Error(`ยังเริ่มทดสอบไม่ได้ (EN-3): /api/health ตอบ ${h.status()} ${body}`);
  }

  // reset ครั้งเดียวก่อนเริ่ม (แต่ละ test ยัง reset ของตัวเองอีกครั้งตามแผนหัวข้อ 5)
  const r = await api.post('/api/test/reset', { data: { now: TODAY } });
  if (!r.ok()) throw new Error(`POST /api/test/reset ไม่สำเร็จ: ${r.status()} ${await r.text()}`);

  // อ่านโหมดบั๊กจาก <html data-bug-mode> ไว้แสดงในรายงาน
  const html = await (await api.get('/')).text();
  const bugMode = html.match(/data-bug-mode="(\d)"/)?.[1] ?? '?';
  mkdirSync('test-report', { recursive: true });
  writeFileSync('test-report/meta.json', JSON.stringify({ bugMode, health: body, today: TODAY, startedAt: new Date().toISOString() }, null, 2));
  await api.dispose();
}
