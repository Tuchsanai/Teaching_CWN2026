// 💬 แชทบอท C01–C14 (mock = ตรวจตรงตัว · ai = regex ยืดหยุ่น)
import { bmCase, expect, intro, ask, expectAnswer, say, show, hold, attachJson, apiJson, getStock, norm, MODE } from './_bm';

const cartCount = async (page: import('@playwright/test').Page) => Number((await page.getByTestId('nav-cart-count').innerText()).replace(/\D/g, '') || 0);

/** เคสถามคำถามเดียว */
function simple(id: string, q: string, checks: Parameters<typeof expectAnswer>[1]) {
  bmCase(id, async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    const ans = await ask(page, info, q);
    expectAnswer(ans.text, checks);
  });
}

// ai: Qwen ตอบได้หลายรูป (07:00 / 7.00 น. / 7 โมงเช้า / เจ็ดโมง) — ทุกเคสตรวจบนข้อความที่ผ่าน norm() แล้ว (comma/เลขไทย/ช่องว่าง)
simple('C01', 'ร้านเปิดกี่โมงครับ', [
  { mock: '07:00', ai: /(^|\D)0?7\s*[:.]\s*00|(^|\D)7\s*โมง|เจ็ดโมง|(^|\D)7\s*a\.?m/i },
  { mock: '18:00', ai: /18\s*[:.]\s*00|(^|\D)6\s*โมงเย็น|หกโมงเย็น|(^|\D)6\s*p\.?m/i },
]);

simple('C02', 'วันอาทิตย์เปิดไหม', [
  { mock: '08:00', ai: /(^|\D)0?8\s*[:.]\s*00|(^|\D)8\s*โมง|แปดโมง/ },
  { mock: '12:00', ai: /12\s*[:.]\s*00|เที่ยง/ },
]);

simple('C03', 'ปูนซีเมนต์ถุงละเท่าไร', [/(^|\D)145(\D|$)/]);

bmCase('C04', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const stock = await getStock(page.request, 'STL-003');
  await attachJson(info, 'checked', { 'STL-003 stock (DB)': stock });
  const ans = await ask(page, info, 'เหล็ก DB12 มีกี่สาขาที่มีของ');
  const inStock = Object.values(stock).filter((n) => n > 0).length;
  if (MODE === 'mock') {
    // ต้องบอกสต็อกตรง DB ทุกสาขา
    expectAnswer(ans.text, Object.values(stock).map((n) => n.toLocaleString('en-US')));
  } else {
    // ai ผ่านเมื่อข้อใดข้อหนึ่งจริง: ① บอกสต็อกตรง DB ครบทุกสาขา ② "3 สาขา" / "ทั้ง 3" / "ครบทั้งสาม" ③ ไล่ชื่อสาขาที่มีของครบ
    const a = norm(ans.text);
    const p = await apiJson(page.request, 'GET', '/api/products/STL-003');
    const names: string[] = (p.stock || []).filter((s: any) => Number(s.qty) > 0).map((s: any) => s.name);
    const TH = ['ศูนย์', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า'][inStock] || String(inStock);
    const nums = Object.values(stock).every((n) => new RegExp(`(^|\\D)${n}(\\D|$)`).test(a));
    const count = new RegExp(`(^|\\D)${inStock}\\s*สาขา|(?:ทั้ง|ครบ)(?:หมด|ทั้ง)?\\s*(?:${inStock}|${TH})|${TH}\\s*สาขา`).test(a);
    const listed = names.length > 0 && names.every((n) => a.includes(n));
    await attachJson(info, 'ai-check', { nums, count, listed, names });
    expect(nums || count || listed, 'บอกจำนวนสาขา/สต็อกตรง DB หรือไล่ชื่อสาขาที่มีของครบ').toBe(true);
  }
});

simple('C05', 'ถ้าซื้อเหล็ก DB12 60 เส้น ได้ราคาเท่าไร', [/185\.25/]);

simple('C06', 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง', [/(^|\D)21(\D|$)/]); // 21 ถุง / 21ถุง / ๒๑ ถุง

bmCase('C07', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const before = await cartCount(page);
  const a1 = await ask(page, info, 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง', { attachName: 'answer-1', holdMs: 3000 });
  expectAnswer(a1.text, [/(^|\D)21(\D|$)/]);
  const ans = await ask(page, info, 'ใส่ตะกร้าให้เลย');
  await expect.poll(() => cartCount(page), { timeout: 15_000 }).toBeGreaterThan(before);
  const cart = await apiJson(page.request, 'GET', '/api/cart');
  const cem = (cart.items || []).find((i: any) => i.sku === 'CEM-001');
  await attachJson(info, 'checked', { navCartBefore: before, navCartAfter: await cartCount(page), cart: cart.items?.map((i: any) => `${i.sku}×${i.qty}`) });
  await say(page, `ตัวเลขตะกร้าเพิ่ม ${before} → ${await cartCount(page)}`);
  await show(page, page.getByTestId('nav-cart-count'));
  expect(cem?.qty).toBe(21);
  expect(ans.text.length).toBeGreaterThan(0);
});

bmCase('C08', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await say(page, 'เตรียมตะกร้า: CEM-001 × 10');
  await apiJson(page.request, 'POST', '/api/cart', { sku: 'CEM-001', qty: 10 });
  await page.reload();
  await show(page, page.getByTestId('nav-cart-count'), 1500);
  const ans = await ask(page, info, 'ขอใบเสนอราคาหน่อย');
  expectAnswer(ans.text, [/QT-\d{8}-\d{4}/]);
  const no = ans.text.match(/QT-\d{8}-\d{4}/)![0];
  const q = await apiJson(page.request, 'GET', `/api/quotes/${no}`);
  await attachJson(info, 'checked', { quoteNo: no, exists: !!q });
});

simple('C09', 'ส่งของน้ำหนัก 5 ตันใช้รถอะไร ค่าส่งเท่าไร', [{ mock: /6\s*ล้อ/, ai: /(^|\D)6\s*ล้อ|หกล้อ/ }, /(^|\D)1500(\D|$)/]);

simple('C10', 'มีโค้ดส่วนลดไหม', [/BUILD5/i, /CONTRACTOR10/i]);

// C11/C12 ตรวจตามความหมาย: คำปฏิเสธ + พูดถึงวัสดุ/สินค้า/ร้าน (ai เรียบเรียงต่างกันได้)
simple('C11', 'มีกระเบื้องยางขายไหม', [
  { mock: /ไม่มี|ไม่พบ|ไม่ได้(?:จำหน่าย|ขาย)|ไม่มีจำหน่าย/, ai: /ขออภัย|ไม่สามารถ|ไม่มี|ไม่ได้|ไม่พบ|ยังไม่/ },
  { mock: /./, ai: /กระเบื้อง|วัสดุ|สินค้า|ร้าน/ },
]);

simple('C12', 'ช่วยเขียนโค้ด Python ให้หน่อย', [
  /ขออภัย|ขอโทษ|ไม่สามารถ|ไม่มี|ไม่ได้/,
  /วัสดุ|ก่อสร้าง|สินค้า|ร้าน/,
]);

bmCase('C13', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const a1 = await ask(page, info, 'ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน', { attachName: 'answer-1' });
  expectAnswer(a1.text, [{ mock: /(^|\D)8\s*แกลลอน/, ai: /(^|\D)8\s*(?:แกลลอน|gal)|แปดแกลลอน/i }]);
  const a2 = await ask(page, info, 'แล้วราคารวมเท่าไร');
  expectAnswer(a2.text, [/(^|\D)7120(\D|$)/]); // 7,120 / 7120 / ๗,๑๒๐ → norm() เป็น 7120
});

simple('C14', 'สาขาบางนาเบอร์อะไร', [/02\s?[-.]?\s?111\s?[-.]?\s?0002/]);
