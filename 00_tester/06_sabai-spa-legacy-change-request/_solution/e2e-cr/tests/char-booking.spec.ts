import { test, expect, guestToStep3, settlePrice, amount } from './fixtures';

// Characterization: ล็อกพฤติกรรมเดิมของหน้าจอง (ไม่ใช่ตัดสินว่าถูก)
// ยอดอ้างอิง [E ev_8dc23d9f] = REA capture-browser-scenario (rea-out/scenario.json · docs/REA-INVENTORY.md)
//   S01 เดี่ยว 1 คน 12 ต.ค. 2026 15:00–16:00 → summary-amount-total data-amount="1000" (฿1,000)
const E_TOTAL = 1000;

test('CHAR-BOOK-01 ไม่ล็อกอิน จอง S01 12 ต.ค. 15:00 → หน้าสรุปยอด ฿1,000 และโครงหน้าสรุปเดิม', async ({ page }) => {
  test.info().annotations.push({
    type: 'source',
    description: `[E ev_8dc23d9f] ยอดหน้าสรุป ฿${E_TOTAL.toLocaleString('en-US')} จาก rea-out/scenario.json (docs/REA-INVENTORY.md) · characterization ล็อกพฤติกรรมเดิม`,
  });

  await guestToStep3(page, { service: 'S01', date: '2026-10-12', time: '15:00' });
  await page.getByTestId('book-contact-name').fill('ทดสอบตาข่าย');
  await page.getByTestId('book-contact-phone').fill('0812345678');
  await settlePrice(page);
  await page.getByTestId('book-next-3').click();

  const summary = page.getByTestId('book-summary');
  await expect(summary).toBeVisible();
  expect(await amount(page, 'summary-amount-total')).toBe(E_TOTAL);
  expect(await amount(page, 'summary-amount-gross')).toBe(E_TOTAL);

  // โครงหน้าสรุปเดิม · /children: equal = ห้ามมีแถว/ปุ่มเกินหรือขาด (CR ที่เพิ่มบรรทัดในใบสรุปจะทำให้ test นี้แดง → ต้องอัปเดตอย่างตั้งใจ)
  await expect(summary).toMatchAriaSnapshot(`
    - region "4. สรุปก่อนจ่าย":
      - /children: equal
      - heading "4. สรุปก่อนจ่าย" [level=2]
      - paragraph:
        - strong: นวดไทย 60 นาที
        - text: · เดี่ยว · 1 คน
      - paragraph: "วันเวลา: 12 ต.ค. 2026 15:00–16:00"
      - strong: สมุนไพรที่ใช้ในบริการนี้
      - list:
        - listitem: ไพล
        - listitem: ตะไคร้
      - table:
        - rowgroup:
          - /children: equal
          - row "ราคาเต็ม (฿1,000 × 1) ฿1,000"
          - row "ยอดสุทธิ ฿1,000"
          - row "ชำระที่ร้าน / ช่องทางอื่น ฿1,000"
      - paragraph: "ยอดสุทธิ: ฿1,000"
      - button "ย้อนกลับ"
      - button "ยืนยันการจอง"
  `);
});
