import { test, expect, open, note, pause, THAI, openChat } from './fixtures';
import type { Page } from '@playwright/test';

/** พิมพ์ข้อความในแชทแล้วรอข้อความตอบล่าสุดของบอท · คืน { text, ms } */
async function ask(page: Page, text: string) {
  const msgs = page.getByTestId('chat-messages').getByTestId(/^chat-msg-\d+$/);
  const before = await msgs.count();
  const t0 = Date.now();
  await page.getByTestId('chat-input').fill(text);
  await page.getByTestId('chat-send').click();
  const reply = page.getByTestId(`chat-msg-${before + 1}`);
  await expect(reply).toHaveAttribute('data-from', 'bot', { timeout: 10_000 });
  const ms = Date.now() - t0;
  return { text: (await reply.textContent()) ?? '', ms };
}

/** ข้อความล่าสุดของบอท */
async function lastBot(page: Page) {
  return (await page.getByTestId('chat-messages').locator('[data-from="bot"]').last().textContent()) ?? '';
}

test.describe('Chatbot', () => {
  test('TC-CHAT-01 chatbot ตอบเวลาเปิด–ปิดและราคา ในภาษาที่ลูกค้าพิมพ์', {
    tag: ['@CHAT', '@P2'],
    annotation: {
      type: 'expected',
      description:
        '"营业时间?" → ขึ้นต้นด้วย "我们每天营业 10:00–22:00，全年无休。" · "多少钱?" → มี "曼谷放松套餐 Bangkok Relax (120 分钟) ฿2,900/人" · "เปิดกี่โมง" → ตอบภาษาไทยและมี 10:00–22:00 · ' +
        '"what time do you open" → ตอบภาษาอังกฤษ · ตอบแต่ละข้อ ≤ 2 วินาที (NFR-05) · คำตอบเหมือนเดิม 10/10 ครั้ง (NFR-12)',
    },
  }, async ({ page }) => {
    await open(page, '/');
    await openChat(page);

    const checks: [string, (s: string) => void][] = [
      ['营业时间?', (s) => expect.soft(s.startsWith('我们每天营业 10:00–22:00，全年无休。'), `营业时间? → ${s}`).toBe(true)],
      ['多少钱?', (s) => expect.soft(s, '多少钱?').toContain('曼谷放松套餐 Bangkok Relax (120 分钟) ฿2,900/人')],
      ['เปิดกี่โมง', (s) => {
        expect.soft(s, 'เปิดกี่โมง ต้องตอบภาษาไทย').toMatch(THAI);
        expect.soft(s, 'เปิดกี่โมง').toContain('10:00–22:00');
      }],
      ['what time do you open', (s) => {
        expect.soft(s, 'what time do you open ต้องตอบภาษาอังกฤษ').toMatch(/[a-z]/i);
        expect.soft(s, 'what time do you open ต้องไม่มีภาษาไทย/จีน').not.toMatch(new RegExp('[' + String.fromCharCode(0x0e01) + '-' + String.fromCharCode(0x0e3a) + String.fromCharCode(0x0e40) + '-' + String.fromCharCode(0x0e5b) + String.fromCharCode(0x4e00) + '-' + String.fromCharCode(0x9fff) + ']'));
      }],
    ];
    const answers: Record<string, string[]> = {};
    let slowest = 0;
    for (const [q, check] of checks) {
      await test.step(`"${q}" ถาม 10 ครั้ง`, async () => {
        answers[q] = [];
        for (let i = 0; i < 10; i++) {
          const { text, ms } = await ask(page, q);
          slowest = Math.max(slowest, ms);
          answers[q].push(text);
          if (i === 0) check(text);
        }
        expect.soft(new Set(answers[q]).size, `"${q}" ต้องตอบเหมือนเดิม 10/10 ครั้ง`).toBe(1);
      });
    }
    note(`ต้องถาม #6: คำตอบภาษาไทย = "${answers['เปิดกี่โมง'][0]}" · ภาษาอังกฤษ = "${answers['what time do you open'][0]}"`, 'ต้องถาม');
    // เวลาที่วัดรวมเวลาพิมพ์/กดของ Playwright ด้วย (โหมด GIF มี slowMo) จึงตรวจเกณฑ์ 2 วินาทีเฉพาะตอนรันปกติ
    if (!process.env.GIF) expect(slowest, 'ตอบช้าสุด (ms) ต้อง ≤ 2000').toBeLessThanOrEqual(2000);
  });

  test('TC-CHAT-02 จองผ่าน chatbot ด้วยกฎเดียวกับหน้าจอง และสรุปราคารวมค่ารถ', {
    tag: ['@CHAT', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'chat-quick-book → bangkok-relax → "พรุ่งนี้" → 7 คน "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567" → 4 คน → 10:00 → ต้องการรถ → Bang Na Lakeside (15.1) "ไม่มีบริการรับส่งสำหรับระยะนี้" → Chatuchak Park (12.0) → ' +
          'Mei 0812345678 → สรุป ฿11,600 − ฿1,160 + ค่ารถ ฿300 = ฿10,740 → ยืนยันแล้วได้รหัสจอง วันที่ 2026-10-09 · availability รอบนั้นของนักบำบัดที่ได้รับมอบหมายเป็น booked · พิมพ์ "ยกเลิก" ระหว่างทางแล้วการจองหยุด',
      },
      {
        type: 'note',
        description:
          'ทั้ง 3 เบราว์เซอร์จอง "พรุ่งนี้" (2026-10-09) พร้อมกัน แพ็กเกจ 4 คนใช้นักบำบัด 4 จาก 6 คน จึงแยกเวลา: chromium 10:00 · firefox 13:00 · webkit 16:30 · ' +
          'ลูกค้าทั่วไปดู source "chatbot" ผ่าน API ไม่ได้ (GET /api/bookings ต้อง login) จึงตรวจจากรหัสจองและ availability แทน',
      },
    ],
  }, async ({ page, browserName }) => {
    const time = { chromium: '10:00', firefox: '13:00', webkit: '16:30' }[browserName] ?? '10:00';
    const date = '2026-10-09';
    const bookedCount = async () => {
      let n = 0;
      for (let id = 1; id <= 6; id++) {
        const r = await (await page.request.get(`/api/availability?service=bangkok-relax&date=${date}&people=1&therapistId=${id}`)).json();
        if (r.slots.find((s: { time: string }) => s.time === time)?.status === 'booked') n++;
      }
      return n;
    };
    const before = await bookedCount();

    await open(page, '/');
    await openChat(page);
    const msgs = page.getByTestId('chat-messages').getByTestId(/^chat-msg-\d+$/);
    const n0 = await msgs.count();
    await page.getByTestId('chat-quick-book').click();
    await expect(page.getByTestId(`chat-msg-${n0 + 1}`)).toHaveAttribute('data-from', 'bot');

    await ask(page, 'bangkok-relax');
    await ask(page, 'พรุ่งนี้');
    expect.soft((await ask(page, '7')).text, '7 คน').toContain('กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567');
    await ask(page, '4');
    await ask(page, time);
    await ask(page, 'ใช่');
    expect.soft((await ask(page, 'Bang Na Lakeside')).text, '15.1 กม.').toContain('ไม่มีบริการรับส่งสำหรับระยะนี้');
    await ask(page, 'Chatuchak Park');
    await ask(page, 'Mei');
    const summary = (await ask(page, '0812345678')).text;
    await pause(page);
    for (const s of ['฿11,600', '฿1,160', '฿300', '฿10,740']) expect.soft(summary, `สรุปราคาต้องมี ${s}`).toContain(s);
    expect.soft(summary, 'สรุปต้องมีเวลา').toContain(time);

    const done = (await ask(page, 'ยืนยัน')).text;
    const code = done.match(/SB\d{5}/)?.[0];
    expect(code, `ต้องได้รหัสจอง (ข้อความ: ${done})`).toBeTruthy();
    note(`รหัสจองจากแชท (${browserName}) = ${code} วันที่ ${date} เวลา ${time}`);
    await pause(page);
    expect(await bookedCount(), `นักบำบัดที่ถูกจองเวลา ${time} ต้องเพิ่ม 4 คน`).toBe(before + 4);

    await test.step('พิมพ์ "ยกเลิก" ระหว่างทาง → การจองหยุด', async () => {
      const mid = await bookedCount();
      await ask(page, 'จอง');
      await ask(page, 'bangkok-relax');
      const stop = await ask(page, 'ยกเลิก');
      expect.soft(stop.text, 'ข้อความหลังยกเลิก').not.toContain('SB');
      expect(await bookedCount(), 'หลังยกเลิกต้องไม่มีการจองเพิ่ม').toBe(mid);
    });
  });
});
