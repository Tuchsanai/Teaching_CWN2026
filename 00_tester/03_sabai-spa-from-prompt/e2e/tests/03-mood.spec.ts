import { test, expect, open, note } from './fixtures';

/** SPEC §6.2 — แนะนำตามอารมณ์ (ตามลำดับ) */
const RULES: Record<string, string[]> = {
  relax: ['aroma-oil', 'foot-reflexology'],
  stressed: ['aroma-oil', 'herbal-compress', 'coconut-rice-scrub'],
  tired: ['foot-reflexology', 'thai-massage', 'bangkok-relax'],
  sore: ['thai-massage', 'herbal-compress'],
};

test.describe('เลือกอารมณ์', () => {
  test('TC-MOOD-01 เลือกอารมณ์ 4 แบบ ได้คำแนะนำ 1–3 บริการตามกฎตายตัว', {
    tag: ['@MOOD', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'relax → aroma-oil, foot-reflexology · stressed → aroma-oil, herbal-compress, coconut-rice-scrub · tired → foot-reflexology, thai-massage, bangkok-relax · ' +
        'sore → thai-massage, herbal-compress · ลำดับถูกต้อง และได้ผลเดิม 10/10 ครั้ง (NFR-12) · กด mood-book-aroma-oil ไป /book',
    },
  }, async ({ page }) => {
    await open(page, '/mood');
    for (const [mood, expected] of Object.entries(RULES)) {
      await test.step(`${mood} กด 10 ครั้ง → ${expected.join(', ')}`, async () => {
        const results: string[] = [];
        for (let i = 0; i < 10; i++) {
          await page.getByTestId(`mood-${mood}`).click();
          const result = page.getByTestId('mood-result');
          await expect(result).toHaveAttribute('data-mood', mood);
          const recs = await result.getByTestId(/^mood-rec-/).evaluateAll((els) => els.map((e) => e.getAttribute('data-testid')!.replace('mood-rec-', '')));
          results.push(recs.join(','));
        }
        expect.soft(results[0].split(','), `ลำดับคำแนะนำของ ${mood}`).toEqual(expected);
        expect.soft(new Set(results).size, `${mood} ต้องได้ผลเดิมทั้ง 10 ครั้ง`).toBe(1);
      });
    }

    await page.getByTestId('mood-relax').click();
    await page.getByTestId('mood-book-aroma-oil').click();
    await expect(page).toHaveURL(/\/book/);
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    const checked = await page.getByTestId('service-option-aroma-oil').getAttribute('aria-checked');
    note(`ต้องถาม #7: กด mood-book-aroma-oil แล้วหน้า /book เลือก aroma-oil ไว้ให้หรือไม่ — ค่าจริง aria-checked="${checked}"`, 'ต้องถาม');
  });
});
