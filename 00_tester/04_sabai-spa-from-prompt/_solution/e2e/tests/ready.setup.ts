import { test as setup, expect } from '@playwright/test';

// โปรเจกต์ setup: เช็กว่าเว็บพร้อมและเวลาเว็บถูกล็อกเป็น R0 แล้ว (global-setup reset ให้แล้ว — ที่นี่ไม่ reset ซ้ำ)
// มีไว้เพื่อให้ project "time-travel" (teardown) รันหลัง chromium / firefox / webkit จบทั้งหมด
setup('เว็บพร้อมและเวลาเว็บล็อกเป็น 2026-10-08', async ({ request }) => {
  const cfg = await (await request.get('/api/config')).json();
  expect(cfg.today).toBe('2026-10-08');
});
