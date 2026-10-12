import { request, type FullConfig } from '@playwright/test';
import { TODAY } from './tests/fixtures';

// ตรวจว่าเว็บพร้อม (/api/health db:true) และ reset ครั้งแรก · แต่ละ test ยัง reset ของตัวเอง
export default async function globalSetup(config: FullConfig) {
  const baseURL = (config.projects[0]?.use?.baseURL as string) ?? 'http://localhost:4000';
  const api = await request.newContext({ baseURL });
  const h = await api.get('/api/health', { timeout: 10_000 }).catch((e) => { throw new Error(`เว็บไม่ตอบ ${baseURL}/api/health: ${e.message}`); });
  const body = await h.json().catch(() => null);
  if (h.status() !== 200 || body?.db !== true) throw new Error(`ยังเริ่มทดสอบไม่ได้: /api/health ตอบ ${h.status()} ${JSON.stringify(body)}`);
  const r = await api.post('/api/test/reset', { data: { now: TODAY } });
  if (!r.ok()) throw new Error(`POST /api/test/reset ไม่สำเร็จ: ${r.status()} ${await r.text()}`);
  await api.dispose();
}
