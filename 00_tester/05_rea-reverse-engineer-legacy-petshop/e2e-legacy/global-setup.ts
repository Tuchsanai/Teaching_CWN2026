import type { FullConfig } from '@playwright/test';

// Before every run: make sure the container is up, then reset stock/users/orders to the seed data.
export default async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:4000';

  const health = await fetch(`${baseURL}/api/health`).catch(() => null);
  if (!health?.ok) {
    throw new Error(`เว็บยังไม่พร้อมที่ ${baseURL} — รัน "docker compose up -d --build" ในโฟลเดอร์ petshop ก่อน`);
  }

  const reset = await fetch(`${baseURL}/api/test/reset`, { method: 'POST' });
  if (!reset.ok) throw new Error(`reset ไม่สำเร็จ (${reset.status}) — ตั้ง ALLOW_TEST_RESET=1 ใน docker-compose.yml`);
}
