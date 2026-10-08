import { test, expect, open, note, pause, baht } from './fixtures';

/** SPEC §2.1 — คะแนนเฉลี่ย / จำนวนรีวิว */
const RATINGS: Record<number, [string, number]> = { 1: ['4.9', 10], 2: ['4.5', 2], 3: ['4.4', 5], 4: ['4.7', 10], 5: ['5.0', 3] };

test.describe('นักบำบัด / รีวิว', () => {
  test('TC-THER-01 คะแนนรีวิว และตัวกรอง "4.5 ดาวขึ้นไป"', {
    tag: ['@THER', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'filter-all → 6 คน · therapist-rating-1 4.9 (10 รีวิว) · 2 = 4.5 (2) · 3 = 4.4 (5) · 4 = 4.7 (10) · 5 = 5.0 (3) · filter-45 → แสดง 4 คน คือ id 1, 2, 4, 5 · ' +
        'ไม่แสดง id 3 (4.4) และ id 6 (ไม่มีรีวิว) · GET /api/therapists?minRating=4.5 ได้ 4 คน · therapist-toggle-reviews-1 เปิดข้อความรีวิว',
    },
  }, async ({ page, apiLog }) => {
    await open(page, '/therapists');
    await page.getByTestId('filter-all').click();
    const cards = page.getByTestId('therapist-list').getByTestId(/^therapist-card-\d+$/);
    await expect(cards).toHaveCount(6);
    for (const [id, [rating, count]] of Object.entries(RATINGS)) {
      await page.getByTestId(`therapist-card-${id}`).scrollIntoViewIfNeeded();
      await expect.soft(page.getByTestId(`therapist-rating-${id}`), `คะแนน id ${id}`).toHaveText(rating);
      expect.soft(baht(await page.getByTestId(`therapist-review-count-${id}`).textContent()), `จำนวนรีวิว id ${id}`).toBe(count);
    }
    note(`ต้องถาม #10: ข้อความของนักบำบัดที่ยังไม่มีรีวิว (id 6) ที่เว็บแสดงจริง = "${(await page.getByTestId('therapist-review-count-6').textContent())?.trim()}"`, 'ต้องถาม');

    await page.evaluate(() => window.scrollTo(0, 0));
    await page.getByTestId('filter-45').click();
    await expect(cards).toHaveCount(4);
    const ids = await cards.evaluateAll((els) => els.map((e) => Number(e.getAttribute('data-testid')!.split('-').pop())).sort());
    expect(ids, 'filter-45 แสดง id 1, 2, 4, 5').toEqual([1, 2, 4, 5]);
    await pause(page);

    const api = await apiLog.call(page.request, 'GET', '/api/therapists?minRating=4.5');
    expect((api.body.therapists as { id: number }[]).map((x) => x.id).sort()).toEqual([1, 2, 4, 5]);

    await page.getByTestId('therapist-toggle-reviews-1').click();
    await expect(page.getByTestId('therapist-reviews-1')).toBeVisible();
    await expect(page.getByTestId('therapist-reviews-1')).not.toBeEmpty();
    await pause(page);
  });
});
