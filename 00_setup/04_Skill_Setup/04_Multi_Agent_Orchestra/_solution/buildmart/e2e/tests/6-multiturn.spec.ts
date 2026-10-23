// 🧵 บทสนทนาหลายรอบ M01–M06 (BUILDMART ข้อ 7) — พิมพ์ทุกรอบใน session เดียว (context ใหม่ = ตะกร้าเริ่มว่าง)
// ทุกบท 5 รอบ · ทุกรอบต้องผ่าน (expect.soft → เล่นครบทุกรอบแม้รอบก่อนพลาด ให้วิดีโอ/รายงานเห็นทุกรอบ) · ค้างภาพ 3 วิหลังแต่ละรอบ
// ตรวจ: คำตอบ (mock ตรงตัว · ai ยืดหยุ่น) · ป้ายอ้างอิง · ตะกร้าจริงจาก /api/cart · nav-cart-count · เลข QT + รายการในใบเสนอราคา
import type { Page, TestInfo } from '@playwright/test';
import { bmCase, expect, intro, ask, expectAnswer, say, show, attachJson, apiJson, getStock, type Check, type Answer } from './_bm';

const HOLD_TURN = 3000;
const navCount = async (page: Page) => Number((await page.getByTestId('nav-cart-count').innerText().catch(() => '0')).replace(/\D/g, '') || 0);
const cartApi = (page: Page) => apiJson(page.request, 'GET', '/api/cart');

type TurnLog = { n: number; q: string; answer: string; cites: string[]; ok: boolean; cart?: string[]; cartCount?: number; quoteNo?: string; note?: string };

/** ตัวช่วยต่อบท: ถาม → ตรวจคำตอบ/cite แบบ soft → จดผล */
function dialog(page: Page, info: TestInfo) {
  const log: TurnLog[] = [];
  let n = 0;
  const turn = async (q: string, checks: Check[] | ((a: Answer) => Promise<Check[]> | Check[]), cite?: string) => {
    n++;
    const ans = await ask(page, info, q, { attachName: `answer-${n}`, holdMs: HOLD_TURN });
    const cs = typeof checks === 'function' ? await checks(ans) : checks;
    let ok = expectAnswer(ans.text, cs, { soft: true, label: `รอบ ${n}` });
    if (cite) {
      const hit = ans.cites.includes(cite);
      expect.soft(ans.cites, `รอบ ${n}: ควรมีป้ายอ้างอิง ${cite}`).toContain(cite);
      ok &&= hit;
    }
    const rec: TurnLog = { n, q, answer: ans.text, cites: ans.cites, ok };
    log.push(rec);
    return { ans, rec };
  };
  /** ตรวจตะกร้า: SKU × qty + ตัวเลขบนไอคอนเพิ่ม */
  const cartHas = async (rec: TurnLog, sku: string, qty: number, navBefore: number) => {
    const ok1 = await expect
      .poll(async () => ((await cartApi(page)).items || []).find((i: any) => i.sku === sku)?.qty ?? 0, { timeout: 15_000 })
      .toBe(qty)
      .then(() => true)
      .catch(() => false);
    expect.soft(ok1, `รอบ ${rec.n}: ตะกร้าควรมี ${sku} × ${qty}`).toBe(true);
    const ok2 = await expect.poll(() => navCount(page), { timeout: 10_000 }).toBeGreaterThan(navBefore).then(() => true).catch(() => false);
    expect.soft(ok2, `รอบ ${rec.n}: nav-cart-count ควรเพิ่มจาก ${navBefore}`).toBe(true);
    const cart = await cartApi(page);
    rec.cart = (cart.items || []).map((i: any) => `${i.sku}×${i.qty}`);
    rec.cartCount = await navCount(page);
    rec.ok &&= ok1 && ok2;
    await say(page, `ตะกร้า: ${rec.cart.join(', ') || '(ว่าง)'} · ไอคอนตะกร้า ${navBefore} → ${rec.cartCount}`);
    await show(page, page.getByTestId('nav-cart-count'), 2000);
  };
  /** ตรวจเลข QT ในคำตอบ + ใบเสนอราคามี SKU × qty */
  const quoteHas = async (rec: TurnLog, sku: string, qty: number) => {
    const no = rec.answer.match(/QT-\d{8}-\d{4}/)?.[0];
    expect.soft(no, `รอบ ${rec.n}: ควรได้เลข QT-`).toBeTruthy();
    if (!no) return (rec.ok = false);
    rec.quoteNo = no;
    const q = await apiJson(page.request, 'GET', `/api/quotes/${no}`).catch(() => null);
    const items: any[] = q?.items || q?.quote?.items || [];
    const line = items.find((i) => i.sku === sku);
    expect.soft(Number(line?.qty), `รอบ ${rec.n}: ใบเสนอราคา ${no} ควรมี ${sku} × ${qty}`).toBe(qty);
    rec.ok &&= Number(line?.qty) === qty;
    await page.goto(`/quote/${no}`);
    await say(page, `ใบเสนอราคา ${no}: ${items.map((i) => `${i.sku}×${i.qty}`).join(', ')}`);
    await show(page, page.getByTestId('quote-row').first(), HOLD_TURN);
    return true;
  };
  const finish = async () => {
    await attachJson(info, 'turns', log);
    await say(page, `จบบทสนทนา ${log.length} รอบ · ผ่าน ${log.filter((t) => t.ok).length}/${log.length} รอบ`);
    await page.waitForTimeout(2500);
    expect(log.length, 'บทสนทนาต้องมีอย่างน้อย 4 รอบ').toBeGreaterThanOrEqual(4);
  };
  return { turn, cartHas, quoteHas, finish, log };
}

// ตัวเลขตรงค่า (136.5 = 136.50 · หลัง norm() ไม่มี comma)
const N = (n: number) => new RegExp(`(^|[^\\d.])${String(n).replace('.', '\\.')}${String(n).includes('.') ? '0*' : ''}(?![\\d])`);
const OPTS = { timeout: 10 * 60_000 };

bmCase('M01', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('ปูกระเบื้อง 60x60 ต้องใช้เกรียงฟันกี่มิล', [/(^|[^\d.x])10(?![\d.x])/], 'BM-DS-CEM.pdf');
  await d.turn('ปูนกาวอันนั้นถุงละเท่าไร', [{ mock: /CEM-004/, ai: /CEM-004|ปูนกาว/ }, N(185)]);
  await d.turn('ถ้าซื้อ 60 ถุงล่ะ', [/175\.75/, N(10545)]);
  const nav = await navCount(page);
  const { rec } = await d.turn('ใส่ตะกร้าให้เลย', [/./]);
  await d.cartHas(rec, 'CEM-004', 60, nav);
  const t5 = await d.turn('ขอใบเสนอราคาด้วย', [/QT-\d{8}-\d{4}/]);
  await d.quoteHas(t5.rec, 'CEM-004', 60);
  await d.finish();
}, OPTS);

bmCase('M02', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('ทาบเหล็ก DB12 ต้องยาวเท่าไร', [N(48)], 'BM-DS-STL.pdf');
  await d.turn('แล้วถ้าเป็น DB16 ล่ะ', [N(64)], 'BM-DS-STL.pdf');
  await d.turn('ตัวเมื่อกี้ถ้าซื้อ 200 เส้น ได้ราคาเส้นละเท่าไร', [N(306), N(61200)]);
  // สต็อก STL-004 ตรง DB ขณะทดสอบ (seed: LKB 400 · BNA 300 · RST 200)
  const stock = await getStock(page.request, 'STL-004');
  await attachJson(info, 'checked', { 'STL-004 stock (DB)': stock });
  await d.turn('สาขาไหนมีของพอบ้าง', Object.values(stock).filter((v) => v > 0).map((v) => N(v)));
  const nav = await navCount(page);
  const { rec } = await d.turn('ใส่ตะกร้า 200 เส้นตามนั้นเลย', [/./]);
  await d.cartHas(rec, 'STL-004', 200, nav);
  await d.finish();
}, OPTS);

bmCase('M03', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('สีทาภายนอกรับประกันกี่ปี', [{ mock: /8\s*ปี/, ai: /(^|\D)8\s*ปี|แปดปี/ }], 'BM-DS-PNT.pdf');
  await d.turn('ผนัง 120 ตร.ม. ทา 2 เที่ยว ต้องใช้สีตัวนั้นกี่แกลลอน', [{ mock: /(^|\D)8\s*แกลลอน/, ai: /(^|\D)8\s*(?:แกลลอน|gal)/i }, { mock: /PNT-001/, ai: /PNT-001|ภายนอก/ }]);
  await d.turn('ทาเที่ยวที่สองต้องรอนานเท่าไร', [{ mock: /2\s*ชั่วโมง/, ai: /(^|\D)2\s*(?:ชั่วโมง|ชม)|สองชั่วโมง/ }], 'BM-DS-PNT.pdf');
  const nav = await navCount(page);
  const { rec } = await d.turn('ใส่ตะกร้าให้ตามจำนวนนั้น', [/./]);
  await d.cartHas(rec, 'PNT-001', 8, nav);
  await d.turn('ถ้าเป็นผนังปูนใหม่ ต้องรอกี่วันก่อนทารองพื้น', [{ mock: /28\s*วัน/, ai: /(^|\D)28\s*วัน|4\s*สัปดาห์/ }], 'BM-DS-PNT.pdf');
  await d.finish();
}, OPTS);

bmCase('M04', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('เทพื้นคอนกรีต 5 คิว ต้องใช้ปูนกี่ถุง', [N(35)]);
  const nav = await navCount(page);
  const { rec } = await d.turn('ใส่ตะกร้าให้เลย', [/./]);
  await d.cartHas(rec, 'CEM-001', 35, nav);
  await d.turn('ต้องบ่มคอนกรีตกี่วัน', [{ mock: /7\s*วัน/, ai: /(^|\D)7\s*วัน|เจ็ดวัน/ }], 'BM-DS-CEM.pdf');
  // "ของที่ใส่ตะกร้าเมื่อกี้" → น้ำหนัก/รถ/ค่าส่ง ต้องตรงตะกร้าจริง (บอทใส่ทราย+หินมาด้วยก็ได้ ตาม [CALC])
  const t = (await cartApi(page)).totals;
  await attachJson(info, 'checked-cart-totals', t);
  const VEH: Record<string, RegExp> = { pickup: /กระบะ/, six: /6\s*ล้อ|หกล้อ/, ten: /10\s*ล้อ|สิบล้อ/ };
  const veh = VEH[t.vehicle] || (/6/.test(t.vehicleLabel) ? VEH.six : /10/.test(t.vehicleLabel) ? VEH.ten : VEH.pickup);
  await d.turn('ของที่ใส่ตะกร้าเมื่อกี้หนักรวมเท่าไร ส่งด้วยรถอะไร', [N(Math.round(t.weight)), veh, N(t.shipping)]);
  const t5 = await d.turn('ขอใบเสนอราคาด้วย', [/QT-\d{8}-\d{4}/]);
  await d.quoteHas(t5.rec, 'CEM-001', 35);
  await d.finish();
}, OPTS);

bmCase('M05', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('สายไฟ THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์', [/16/], 'BM-DS-ELC-PIP.pdf');
  await d.turn('เบรกเกอร์ตัวนั้นร้านมีขายไหม ราคาเท่าไร', [{ mock: /ELC-002/, ai: /ELC-002|เบรกเกอร์/ }, N(145)]);
  await d.turn('รับประกันกี่ปี', [{ mock: /2\s*ปี/, ai: /(^|\D)2\s*ปี|สองปี/ }], 'BM-DS-ELC-PIP.pdf');
  const nav = await navCount(page);
  const { rec } = await d.turn('เอา 10 ตัว ใส่ตะกร้าให้หน่อย', [/./]);
  await d.cartHas(rec, 'ELC-002', 10, nav);
  const t = (await cartApi(page)).totals; // ELC-002 × 10 → 1,450 + กระบะ 500 + VAT 136.50 = 2,086.50
  await attachJson(info, 'checked-cart-totals', t);
  await d.turn('ยอดสุทธิรวมค่าส่งและ VAT เท่าไร', [N(t.subtotal), N(t.shipping), N(t.vat), N(t.total)]);
  await d.finish();
}, OPTS);

bmCase('M06', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const d = dialog(page, info);
  await d.turn('กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม', [/ได้/, /0\.5\s*%|R\s?10/], 'BM-DS-TIL.pdf');
  await d.turn('พื้นที่ 50 ตร.ม. ต้องใช้กี่กล่อง', [N(39)]);
  const nav = await navCount(page);
  const { rec } = await d.turn('ใส่ตะกร้าให้หน่อย', [/./]);
  await d.cartHas(rec, 'TIL-001', 39, nav);
  await d.turn('ถ้าไม่ได้ใช้ ขอคืนได้ภายในกี่วัน', [{ mock: /7\s*วัน/, ai: /(^|\D)7\s*วัน|เจ็ดวัน/ }], 'BM-POLICY.pdf');
  const t = (await cartApi(page)).totals;
  await attachJson(info, 'checked-cart-totals', t);
  // ยอดก่อน VAT ≥ 5,000 แต่ < 30,000 → BUILD5 ใช้ได้ · CONTRACTOR10 ใช้ไม่ได้ (ต้องบอกว่าตัวไหนใช้ไม่ได้)
  await d.turn('ยอดในตะกร้าตอนนี้ใช้คูปองอะไรได้', [
    /BUILD5/i,
    /CONTRACTOR10/i,
    {
      mock: /CONTRACTOR10[^\n]{0,80}(?:ไม่ได้|ไม่ถึง|ยังไม่|ไม่ครบ|ขาดอีก|ต้อง(?:มี)?ยอด)|(?:ไม่ได้|ไม่ถึง|ยังไม่)[^\n]{0,40}CONTRACTOR10/i,
      // ai: เรียบเรียงต่างกันได้ แต่ต้องบอกว่า CONTRACTOR10 ใช้ไม่ได้ (ยอดไม่ถึง 30,000)
      ai: /CONTRACTOR10[\s\S]{0,200}(?:ไม่ได้|ไม่ถึง|ยังไม่|ไม่ครบ|ขาดอีก|ไม่สามารถ|ไม่เข้าเงื่อนไข|ต่ำกว่า|ต้อง(?:มี)?ยอด|30000)|(?:ไม่ได้|ไม่ถึง|ยังไม่|ไม่สามารถ)[\s\S]{0,80}CONTRACTOR10/i,
    },
  ]);
  await d.finish();
}, OPTS);
