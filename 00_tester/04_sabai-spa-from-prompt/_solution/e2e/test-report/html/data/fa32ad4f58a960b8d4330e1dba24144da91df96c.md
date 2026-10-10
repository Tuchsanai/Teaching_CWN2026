# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: book.spec.ts >> TC-BOOK-03 รอบเวลา + เวลาปิดร้าน + เวลาไม่ตรงรอบ
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: จำนวนรอบ S01

expect(received).toBe(expected) // Object.is equality

Expected: 23
Received: 22
```

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "21:00"
Received: "20:30"
```

```
Error: จำนวนรอบ S02

expect(received).toBe(expected) // Object.is equality

Expected: 22
Received: 21
```

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "20:30"
Received: "20:00"
```

# Test source

```ts
  1   | import { tc, test, expect, open, bookStep1, bookStep2, bookToStep3, fillContact, toSummary, amount, loginUI, quoteTotal } from './fixtures';
  2   | 
  3   | const S = test.step;
  4   | 
  5   | // ตัวช่วย: จองแบบไม่ล็อกอินผ่าน API (ใช้กับจุดตรวจ ❌/4xx ที่หน้าเว็บสร้างไม่ได้ — แผน 2.3 ข้อ 4)
  6   | const anonBooking = (date: string, time: string, extra: Record<string, unknown> = {}) => ({
  7   |   type: 'single', serviceCode: 'S01', people: 1, date, time,
  8   |   contactName: 'ทดสอบ API', contactPhone: '0812345678', quotedTotal: 1000, ...extra,
  9   | });
  10  | 
  11  | tc('TC-BOOK-01', async ({ page, api }) => {
  12  |   await S('ขั้น 1: เปิดหน้าจองนวดไทย 60 นาที แบบไม่ล็อกอิน', async () => {
  13  |     await bookStep1(page, { service: 'S01', type: 'single' });
  14  |   });
  15  |   await S('แถบขั้นตอนมี 4 ขั้น', async () => {
  16  |     await expect.soft(page.getByTestId('book-step-indicator')).toContainText('จาก 4');
  17  |     for (const label of ['1. บริการ', '2. วัน/เวลา', '3. ข้อมูลติดต่อ', '4. ยืนยัน']) {
  18  |       await expect.soft(page.getByText(label, { exact: true }).first()).toBeVisible();
  19  |     }
  20  |   });
  21  |   await S('ขั้น 2: เลือก 20 ต.ค. 14:00 พี่สมศรี (T01)', async () => {
  22  |     await bookStep2(page, { date: '2026-10-20', time: '14:00', therapist: 'T01' });
  23  |   });
  24  |   await S('ขั้น 3: กรอกชื่อ "ทดสอบ E2E" เบอร์ 0812345678', async () => {
  25  |     await fillContact(page, 'ทดสอบ E2E', '0812345678');
  26  |     await toSummary(page);
  27  |   });
  28  |   await S('ขั้น 4: ใบสรุปมีสมุนไพร "ไพล, ตะไคร้" และยอดสุทธิ ฿1,000', async () => {
  29  |     // ใบสรุปแสดงสมุนไพรเป็นชิป <li> ทีละตัว → เทียบเป็นรายการ "ไพล, ตะไคร้"
  30  |     expect.soft((await page.getByTestId('book-herbs').locator('li').allInnerTexts()).map((t) => t.trim()).join(', ')).toBe('ไพล, ตะไคร้');
  31  |     expect.soft(await amount(page, 'summary-total')).toBe(1000);
  32  |   });
  33  |   await S('กดยืนยัน → ข้อความยืนยันพร้อมรหัสการจอง B + ตัวเลข (ทันที)', async () => {
  34  |     await page.getByTestId('book-confirm').click();
  35  |     await expect.soft(page.getByTestId('booking-confirmation')).toHaveText(/B\d+/);
  36  |   });
  37  |   await S('หลังรีโหลด: ตารางคิว 20 ต.ค. มีนัด 14:00 ของ T01 1 รายการ', async () => {
  38  |     const rows = (await api.adminBookings('2026-10-20'))
  39  |       .filter((b) => b.time.startsWith('14:00') && b.status !== 'cancelled' && b.therapists.some((t: string) => t.startsWith('T01')));
  40  |     expect.soft(rows.length).toBe(1);
  41  |   });
  42  | });
  43  | 
  44  | tc('TC-BOOK-02', async ({ page, api }) => {
  45  |   await S('ขั้น 2: ช่องวันมี min = 2026-10-11 และ max = 2026-11-09', async () => {
  46  |     await bookStep1(page, { service: 'S01', type: 'single' });
  47  |     const d = page.getByTestId('book-date');
  48  |     await expect.soft(d).toHaveAttribute('min', '2026-10-11');
  49  |     await expect.soft(d).toHaveAttribute('max', '2026-11-09');
  50  |   });
  51  |   const anon = await api.anon();
  52  |   for (const [date, ok, label] of [
  53  |     ['2026-10-10', false, '10 ต.ค. (+0) ❌'],
  54  |     ['2026-10-11', true, '11 ต.ค. (+1) ✅'],
  55  |     ['2026-11-09', true, '9 พ.ย. (+30) ✅'],
  56  |     ['2026-11-10', false, '10 พ.ย. (+31) ❌'],
  57  |   ] as const) {
  58  |     await S(`จอง S01 วันที่ ${label}`, async () => {
  59  |       const r = await anon.post('/api/bookings', anonBooking(date, '14:00'));
  60  |       if (ok) expect.soft(r.status, `${date} ต้องจองได้`).toBe(201);
  61  |       else expect.soft(r.status >= 400 && r.status < 500, `${date} ต้องได้ 4xx (ได้ ${r.status})`).toBe(true);
  62  |     });
  63  |   }
  64  | });
  65  | 
  66  | tc('TC-BOOK-03', async ({ page, api }) => {
  67  |   const slotsOnPage = async () => (await page.locator('[data-testid^="book-slot-"]').evaluateAll(
  68  |     (es) => es.map((e) => e.getAttribute('data-testid')!.replace('book-slot-', ''))));
  69  |   await S('S01 (60 นาที) วันที่ 21 ต.ค.: 23 รอบ 10:00–21:00 ไม่มี 09:30 / 21:30', async () => {
  70  |     await bookStep1(page, { service: 'S01', type: 'single' });
  71  |     await page.getByTestId('book-date').fill('2026-10-21');
  72  |     await expect(page.getByTestId('book-slot-10:00')).toBeVisible();
  73  |     const s = await slotsOnPage();
  74  |     expect.soft(s.length, 'จำนวนรอบ S01').toBe(23);
  75  |     expect.soft(s[0]).toBe('10:00');
  76  |     expect.soft(s[s.length - 1]).toBe('21:00');
  77  |     expect.soft(s).not.toContain('09:30');
  78  |     expect.soft(s).not.toContain('21:30');
  79  |   });
  80  |   await S('S02 (90 นาที) วันที่ 21 ต.ค.: 22 รอบ สุดท้าย 20:30', async () => {
  81  |     await bookStep1(page, { service: 'S02', type: 'single' });
  82  |     await page.getByTestId('book-date').fill('2026-10-21');
  83  |     await expect(page.getByTestId('book-slot-10:00')).toBeVisible();
  84  |     const s = await slotsOnPage();
  85  |     expect.soft(s.length, 'จำนวนรอบ S02').toBe(22);
> 86  |     expect.soft(s[s.length - 1]).toBe('20:30');
      |                                  ^ Error: expect(received).toBe(expected) // Object.is equality
  87  |   });
  88  |   await S('ยิงจอง S01 เวลา 10:15 → 4xx และไม่บันทึก (หลังรีโหลด)', async () => {
  89  |     const anon = await api.anon();
  90  |     const r = await anon.post('/api/bookings', anonBooking('2026-10-21', '10:15'));
  91  |     expect.soft(r.status >= 400 && r.status < 500, `10:15 ต้องได้ 4xx (ได้ ${r.status})`).toBe(true);
  92  |     const rows = (await api.adminBookings('2026-10-21')).filter((b) => b.time.startsWith('10:15'));
  93  |     expect.soft(rows.length).toBe(0);
  94  |   });
  95  | });
  96  | 
  97  | tc('TC-BOOK-04', async ({ page, api }) => {
  98  |   const anon = await api.anon();
  99  |   for (const t of ['13:30', '14:30']) {
  100 |     await S(`T03 วันที่ 12 ต.ค. เริ่ม ${t} (ทับ B01 14:00–15:00) → ❌ "เวลานี้ถูกจองแล้ว"`, async () => {
  101 |       const r = await anon.post('/api/bookings', anonBooking('2026-10-12', t, { therapists: ['T03'] }));
  102 |       expect.soft(r.status, `${t} ต้องถูกปฏิเสธ`).toBe(409);
  103 |       expect.soft(r.json?.message).toBe('เวลานี้ถูกจองแล้ว');
  104 |     });
  105 |   }
  106 |   await S('หลังรีโหลด: ตารางคิว 12 ต.ค. ของ T03 มีแค่ B01', async () => {
  107 |     const rows = (await api.adminBookings('2026-10-12')).filter((b) => b.status !== 'cancelled' && b.therapists.some((x: string) => x.startsWith('T03')));
  108 |     expect.soft(rows.map((b) => b.code)).toEqual(['B01']);
  109 |   });
  110 |   await S('หน้าเว็บ: จอง T03 เวลา 15:00 (จบเดิม = เริ่มใหม่) → ✅', async () => {
  111 |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-12', time: '15:00', therapist: 'T03' });
  112 |     await fillContact(page, 'ทดสอบต่อคิว', '0812345678');
  113 |     await toSummary(page);
  114 |     await page.getByTestId('book-confirm').click();
  115 |     await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  116 |   });
  117 | });
  118 | 
  119 | tc('TC-BOOK-05', async ({ page, api }) => {
  120 |   await S('จอง S01 22 ต.ค. 13:00 นักบำบัด "ใครก็ได้" ชื่อ "ทดสอบกดซ้ำ"', async () => {
  121 |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-22', time: '13:00' });
  122 |     await fillContact(page, 'ทดสอบกดซ้ำ', '0812345678');
  123 |     await toSummary(page);
  124 |   });
  125 |   await S('ดับเบิลแตะปุ่ม "ยืนยันการจอง" → เห็นรหัสการจอง 1 รหัส (ทันที)', async () => {
  126 |     await page.getByTestId('book-confirm').dblclick();
  127 |     const msg = page.getByTestId('booking-confirmation');
  128 |     await expect(msg).toBeVisible();
  129 |     await expect.soft(msg).toHaveCount(1);
  130 |     expect.soft((await msg.innerText()).match(/B\d+/g)?.length ?? 0).toBe(1);
  131 |   });
  132 |   await S('หลังรีโหลด: ตารางคิว 22 ต.ค. มีชื่อ "ทดสอบกดซ้ำ" 1 แถว', async () => {
  133 |     const rows = (await api.adminBookings('2026-10-22')).filter((b) => String(b.customer).startsWith('ทดสอบกดซ้ำ'));
  134 |     expect.soft(rows.length).toBe(1);
  135 |   });
  136 | });
  137 | 
  138 | tc('TC-BOOK-07', async ({ page, api }) => {
  139 |   await loginUI(page, 'U02');
  140 |   const u02 = await api.as('U02');
  141 |   const couple = (people: number, time: string, quotedTotal = 2520) => ({ type: 'couple', serviceCode: 'S02', people, date: '2026-10-17', time, quotedTotal });
  142 |   for (const n of [1, 3]) {
  143 |     await S(`จองคู่ ${n} คน → ❌`, async () => {
  144 |       const r = await u02.post('/api/bookings', couple(n, '20:30'));
  145 |       expect.soft(r.status >= 400 && r.status < 500, `คู่ ${n} คน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  146 |     });
  147 |   }
  148 |   await S('จองคู่ 2 คน 19:30 (ทับ B02 19:00–20:30) → ❌ "เวลานี้ถูกจองแล้ว"', async () => {
  149 |     const r = await u02.post('/api/bookings', couple(2, '19:30'));
  150 |     expect.soft(r.status).toBe(409);
  151 |     expect.soft(r.json?.message).toBe('เวลานี้ถูกจองแล้ว');
  152 |   });
  153 |   await S('หน้าเว็บ: จองคู่ 2 คน 20:30 → ✅ ราคา ฿2,520', async () => {
  154 |     await bookToStep3(page, { service: 'S02', type: 'couple', people: 2, date: '2026-10-17', time: '20:30' });
  155 |     expect.soft(await quoteTotal(page)).toBe(2520);
  156 |     await toSummary(page);
  157 |     expect.soft(await amount(page, 'summary-total')).toBe(2520);
  158 |     await page.getByTestId('book-confirm').click();
  159 |     await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  160 |   });
  161 | });
  162 | 
  163 | tc('TC-BOOK-08', async ({ page, api }) => {
  164 |   await loginUI(page, 'U08');
  165 |   const u08 = await api.as('U08');
  166 |   const group = (people: number) => ({ type: 'group', serviceCode: 'S01', people, date: '2026-10-20', time: '10:00' });
  167 |   await S('กลุ่ม 2 คน → ❌ (ไม่ใช่กลุ่ม)', async () => {
  168 |     const r = await u08.post('/api/price', group(2));
  169 |     expect.soft(r.status >= 400 && r.status < 500, `2 คน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  170 |   });
  171 |   await S('กลุ่ม 3 คน → ✅', async () => {
  172 |     const r = await u08.post('/api/price', group(3));
  173 |     expect.soft(r.status).toBe(200);
  174 |   });
  175 |   await S('กลุ่ม 6 คน → ✅ (จองได้จริง)', async () => {
  176 |     const q = await u08.post('/api/price', group(6));
  177 |     expect.soft(q.status).toBe(200);
  178 |     const r = await u08.post('/api/bookings', { ...group(6), quotedTotal: q.json?.total });
  179 |     expect.soft(r.status).toBe(201);
  180 |   });
  181 |   await S('หน้าเว็บ: กลุ่ม 7 คน → ข้อความ "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน" และมีเบอร์โทรร้าน', async () => {
  182 |     await bookStep1(page, { service: 'S01', type: 'group', people: 7 });
  183 |     await expect.soft(page.getByTestId('book-error-message')).toContainText('กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน');
  184 |     await expect.soft(page.getByTestId('shop-phone')).toHaveText(/\d{2,3}-?\d{3}-?\d{4}/);
  185 |   });
  186 | });
```