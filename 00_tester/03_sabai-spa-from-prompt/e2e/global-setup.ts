import type { FullConfig } from '@playwright/test';

/** เวลาที่ล็อกไว้ของทุก test (R0 ใน TEST-PLAN.md): today = 2026-10-08 (พฤ.) จองได้ 2026-10-09 ถึง 2026-11-07 */
export const FIXED_NOW = '2026-10-08T10:00:00+07:00';

// reset แค่ครั้งเดียวตรงนี้ — ห้าม reset ใน test เพราะ chromium / firefox / webkit รันพร้อมกัน
export default async function globalSetup(config: FullConfig) {
  const baseURL = (config.projects[0].use.baseURL as string) ?? 'http://localhost:3000';

  const health = await fetch(`${baseURL}/api/health`).catch(() => null);
  const body = health ? await health.json().catch(() => null) : null;
  if (!health?.ok || !body?.db) {
    throw new Error(
      `\n❌ เว็บสปายังไม่พร้อมที่ ${baseURL} (${health ? `HTTP ${health.status} db=${body?.db}` : 'เชื่อมต่อไม่ได้'})\n` +
        `   วิธีเปิด (PowerShell):\n` +
        `     cd spa\n` +
        `     docker compose up -d --build\n` +
        `   แล้วรอจน http://localhost:3000/api/health ตอบ {"ok":true,"db":true} จึงรัน test ใหม่\n`,
    );
  }

  const reset = await fetch(`${baseURL}/api/test/reset`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ now: FIXED_NOW }),
  });
  const data = await reset.json().catch(() => null);
  if (!reset.ok || !data?.ok || data.today !== '2026-10-08') {
    throw new Error(
      `❌ reset ไม่สำเร็จ (HTTP ${reset.status}) — ตรวจว่า spa/docker-compose.yml ตั้ง ALLOW_TEST_RESET: "1" ` +
        `แล้วรัน docker compose up -d ใหม่ · คำตอบ: ${JSON.stringify(data)}`,
    );
  }
}
