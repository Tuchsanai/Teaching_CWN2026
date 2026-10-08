import { test, expect, open, note, pause } from './fixtures';
import type { Page } from '@playwright/test';

/** ชุดคำตอบ (goal, time, pressure, transfer) → ผลที่คาดหวัง (SPEC §6.2) */
const SETS: Record<string, [string[], string]> = {
  A: [['pain', '60', 'strong', 'no'], 'thai-massage'],
  B: [['skin', '90', 'soft', 'no'], 'aloe-hydrating-facial'],
  C: [['skin', '90', 'soft', 'yes'], 'bangkok-relax'],
  D: [['relax', '60', 'medium', 'no'], 'foot-reflexology'],
  E: [['relax', '120', 'medium', 'no'], 'aroma-oil'],
};

async function answer(page: Page, values: string[]) {
  // ตอบครบ 4 ข้อแล้วการ์ดคำถามจะหายไป (แสดง quiz-result แทน)
  const answered = async () =>
    (await page.getByTestId('quiz-answered').count()) === 0 ? 4 : Number(((await page.getByTestId('quiz-answered').textContent()) ?? '0').split('/')[0]);
  const start = await answered();
  for (const [i, v] of values.entries()) {
    // การ์ดคำถามเล่นแอนิเมชันตอนเปลี่ยนข้อ: ถ้าคลิกตอนการ์ดกำลังขยับแล้วไม่ติด ให้กดใหม่ (เหมือนผู้ใช้กดซ้ำ)
    await expect(async () => {
      if ((await answered()) < start + i + 1) await page.getByTestId(`quiz-option-${v}`).click({ timeout: 2000 });
      expect(await answered()).toBe(start + i + 1);
    }).toPass({ timeout: 10_000 });
  }
}

test.describe('แบบทดสอบ / วิเคราะห์ผิว', () => {
  test('TC-AI-01 แบบทดสอบ 4 ข้อ ต้องตอบครบก่อนแสดงผล และใช้กฎแรกที่ตรง', {
    tag: ['@AI', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'quiz-progress เริ่มที่ "ข้อ 1/4" · ตอบ 3 ข้อแล้วยังไม่มี quiz-result · ตอบครบ 4 ข้อ → quiz-result 1 รายการ: A (pain,60,strong,no) → thai-massage · B (skin,90,soft,no) → aloe-hydrating-facial · ' +
        'C (skin,90,soft,yes) → bangkok-relax (กฎ transfer ชนะ) · D (relax,60,medium,no) → foot-reflexology · E (relax,120,medium,no) → aroma-oil · A ได้ผลเดิม 10/10 ครั้ง · quiz-book ไป /book',
    },
  }, async ({ page }) => {
    await open(page, '/quiz');
    await expect(page.getByTestId('quiz-progress')).toHaveText('ข้อ 1/4');
    await answer(page, SETS.A[0].slice(0, 3));
    await expect(page.getByTestId('quiz-result'), 'ตอบ 3 ข้อยังต้องไม่มีผล').toHaveCount(0);
    await page.getByTestId(`quiz-option-${SETS.A[0][3]}`).click();
    await expect(page.getByTestId('quiz-result')).toHaveCount(1);
    await expect(page.getByTestId('quiz-result')).toHaveAttribute('data-service', SETS.A[1]);
    note(`ต้องถาม #6: ข้อความเหตุผลชุด A ที่เว็บแสดงจริง = "${(await page.getByTestId('quiz-reason').textContent())?.trim()}"`, 'ต้องถาม');
    await pause(page);

    for (const [name, [values, service]] of Object.entries(SETS)) {
      await test.step(`ชุด ${name} (${values.join(', ')}) → ${service}`, async () => {
        await page.getByTestId('quiz-restart').click();
        await expect(page.getByTestId('quiz-progress')).toHaveText('ข้อ 1/4');
        await answer(page, values);
        await expect.soft(page.getByTestId('quiz-result'), `ชุด ${name}`).toHaveAttribute('data-service', service);
      });
    }

    await test.step('ชุด A ทำซ้ำ 10 ครั้ง ต้องได้ thai-massage ทุกครั้ง', async () => {
      const got: string[] = [];
      for (let i = 0; i < 10; i++) {
        await page.getByTestId('quiz-restart').click();
        await answer(page, SETS.A[0]);
        await expect(page.getByTestId('quiz-result')).toHaveCount(1);
        got.push((await page.getByTestId('quiz-result').getAttribute('data-service'))!);
      }
      expect(got).toEqual(Array(10).fill('thai-massage'));
    });

    await page.getByTestId('quiz-book').click();
    await expect(page).toHaveURL(/\/book/);
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    note(`ต้องถาม #7: quiz-book เลือกบริการไว้ให้ที่ /book หรือไม่ — service-option-thai-massage aria-checked="${await page.getByTestId('service-option-thai-massage').getAttribute('aria-checked')}"`, 'ต้องถาม');
  });

  test('TC-AI-02 วิเคราะห์ผิว + ภาพจำลอง ทำในเบราว์เซอร์ ร้านไม่เก็บรูปใบหน้า', {
    tag: ['@AI', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'skin-result data-type เป็น sensitive / dull / dry / balanced ตามกฎ SPEC §6.2 จาก skin-avg (ความสว่าง = round(0.299R+0.587G+0.114B) = skin-brightness · ความแดง = round(R−G) = skin-redness) · ได้ผลเดิม 10/10 ครั้ง · ' +
        'skin-disclaimer "ผลนี้เป็นคำแนะนำเบื้องต้น ไม่ใช่การวินิจฉัยของแพทย์" · sim-treatment turmeric-facial → sim-after data-filter "brightness(1.10) saturate(1.06) contrast(1.03)" · ' +
        'sim-label "ภาพจำลองเท่านั้น ผลจริงแต่ละคนต่างกัน" · รูปที่อัปโหลดมี src ขึ้นต้นด้วย blob: · ไม่มี request ส่งรูปออก (0 ครั้ง) · privacy-no-face มี "ร้านไม่เก็บรูปใบหน้าลูกค้า"',
    },
  }, async ({ page }) => {
    // จับทุก request ที่ส่งข้อมูลออก (POST/PUT/PATCH หรือมี body) ระหว่างอยู่หน้า /skin
    const outgoing: string[] = [];
    page.on('request', (r) => {
      if (r.method() !== 'GET' || (r.postDataBuffer()?.length ?? 0) > 0) outgoing.push(`${r.method()} ${r.url()}`);
    });
    await open(page, '/skin');

    const seen: string[] = [];
    for (let i = 0; i < 10; i++) {
      await page.getByTestId('skin-sample').click();
      const result = page.getByTestId('skin-result');
      await expect(result).toBeVisible();
      const avg = page.getByTestId('skin-avg');
      const [r, g, b] = await Promise.all(['data-r', 'data-g', 'data-b'].map(async (a) => Number(await avg.getAttribute(a))));
      const brightness = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
      const redness = Math.round(r - g);
      const type = redness >= 45 ? 'sensitive' : brightness < 120 ? 'dull' : brightness >= 170 ? 'dry' : 'balanced';
      if (i === 0) {
        await expect.soft(page.getByTestId('skin-brightness'), 'ความสว่าง').toHaveText(String(brightness));
        await expect.soft(page.getByTestId('skin-redness'), 'ความแดง').toHaveText(String(redness));
        await expect.soft(result, `ประเภทผิวตามกฎ (R${r} G${g} B${b})`).toHaveAttribute('data-type', type);
        note(`ต้องถาม #5: ผลของ sample-face.jpg ที่เว็บแสดงจริง = ${await result.getAttribute('data-type')} (R ${r} · G ${g} · B ${b} · ความสว่าง ${brightness} · ความแดง ${redness})`, 'ต้องถาม');
      }
      seen.push(`${await result.getAttribute('data-type')}|${r},${g},${b}`);
    }
    expect.soft(new Set(seen).size, 'ได้ผลเดิม 10/10 ครั้ง').toBe(1);
    expect.soft(['sensitive', 'dull', 'dry', 'balanced']).toContain(seen[0].split('|')[0]);
    await expect(page.getByTestId('skin-disclaimer')).toHaveText('ผลนี้เป็นคำแนะนำเบื้องต้น ไม่ใช่การวินิจฉัยของแพทย์');

    await page.getByTestId('sim-treatment').selectOption('turmeric-facial');
    await page.getByTestId('sim-compare').scrollIntoViewIfNeeded();
    await expect(page.getByTestId('sim-after')).toHaveAttribute('data-filter', 'brightness(1.10) saturate(1.06) contrast(1.03)');
    await expect(page.getByTestId('sim-label')).toHaveText('ภาพจำลองเท่านั้น ผลจริงแต่ละคนต่างกัน');
    await pause(page);

    // อัปโหลดรูปจากเครื่อง (ใช้รูปตัวอย่างของเว็บเป็นไฟล์)
    const sample = await (await page.request.get('/assets/skin/sample-face.jpg')).body();
    outgoing.length = 0;
    await page.getByTestId('skin-file').setInputFiles({ name: 'my-face.jpg', mimeType: 'image/jpeg', buffer: sample });
    await expect(page.getByTestId('skin-result')).toBeVisible();
    const src = await page.getByTestId('skin-preview').getAttribute('src');
    expect(src, 'รูปที่อัปโหลดต้องเป็น blob:').toMatch(/^blob:/);
    await page.waitForTimeout(1000);
    expect(outgoing, 'ต้องไม่มี request ส่งรูปออก').toEqual([]);
    await pause(page);

    await open(page, '/privacy');
    await expect(page.getByTestId('privacy-no-face')).toContainText('ร้านไม่เก็บรูปใบหน้าลูกค้า');
  });
});
