import type { FullConfig } from '@playwright/test';

// Entry criteria (TEST-PLAN.md หัวข้อ 6): the site must be healthy, then reset it to the seed data.
export default async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:3000';

  // EN2: GET /api/health → 200 และ {"ok":true}
  const health = await fetch(`${baseURL}/api/health`).catch(() => null);
  const body = health?.ok ? await health.json().catch(() => null) : null;
  if (!health?.ok || body?.ok !== true) {
    throw new Error(`เว็บยังไม่พร้อมที่ ${baseURL} — รัน "docker compose up -d --build" ในโฟลเดอร์ petshop ก่อน`);
  }

  // EN3: POST /api/test/reset → 200
  const reset = await fetch(`${baseURL}/api/test/reset`, { method: 'POST' });
  if (!reset.ok) throw new Error(`reset ไม่สำเร็จ (${reset.status}) — ตั้ง ALLOW_TEST_RESET=1 ใน docker-compose.yml`);
}
