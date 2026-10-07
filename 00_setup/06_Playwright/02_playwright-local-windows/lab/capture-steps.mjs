// capture-steps.mjs — จับภาพทีละขั้นของ test "ค้นหาในเว็บ" พร้อมวงกลมสีแดงรอบจุดที่กด (ใช้ทำภาพประกอบ README)
// ใช้:  node capture-steps.mjs   → ได้ภาพใน ../img/lab4-step-*.png
import { chromium } from '@playwright/test';

const out = (n) => `../img/lab4-step-${n}.png`;

// วาดวงรีสีแดงรอบ element (เป็น overlay ชั่วคราว ไม่แก้หน้าเว็บจริง)
async function circle(page, locator) {
  const box = await locator.boundingBox();
  await page.evaluate(({ x, y, width, height }) => {
    document.getElementById('__circle')?.remove();
    const d = document.createElement('div');
    d.id = '__circle';
    const pad = 14;
    Object.assign(d.style, {
      position: 'fixed', left: `${x - pad}px`, top: `${y - pad}px`,
      width: `${width + pad * 2}px`, height: `${height + pad * 2}px`,
      border: '5px solid #e11d2e', borderRadius: '50%', zIndex: 2147483647, pointerEvents: 'none',
    });
    document.body.appendChild(d);
  }, box);
}
const clear = (page) => page.evaluate(() => document.getElementById('__circle')?.remove());

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

// ขั้น 1: หน้าแรก วงปุ่ม Search
await page.goto('https://playwright.dev/');
const search = page.getByRole('button', { name: 'Search' });
await circle(page, search);
await page.screenshot({ path: out(1) });
await clear(page);

// ขั้น 2: พิมพ์ "locator" วงผลลัพธ์แรก
await search.click();
await page.getByPlaceholder('Search docs').fill('locator');
const first = page.getByRole('option', { name: /Locators/ }).first();
await first.waitFor();
await circle(page, first);
await page.screenshot({ path: out(2) });
await clear(page);

// ขั้น 3: เปิดหน้า Locators วงหัวข้อที่ test ตรวจ
await first.click();
const heading = page.getByRole('heading', { name: 'Locators', level: 1 });
await heading.waitFor();
await circle(page, heading);
await page.screenshot({ path: out(3) });

await browser.close();
console.log('saved', [1, 2, 3].map(out).join(', '));
