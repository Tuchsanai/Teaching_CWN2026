// ข้อ 7 ชุด B · หน้าจอรีวิว (3 คะแนน) · ใบโจทย์กำหนดแค่ปุ่ม review-{รหัสนัด} → ตรวจปุ่ม + ผลหลังรีวิว (รีวิวผ่าน API)
import { test, expect, loginUI, logoutUI, open, USERS } from '../fixtures';

const V = JSON.parse(process.env.VARIANT_JSON ?? '{}');
const USER = (V.reviewUser ?? 'U01') as keyof typeof USERS;
const BK: string = V.reviewBooking ?? 'B13';
const EXP = ({ 0: { th: 'T03', rating: '4.5' }, 1: { th: 'T05', rating: '4.0' }, 2: { th: 'T03', rating: '4.3' } } as any)[V.v ?? 0];

async function reviewViaApi(api: any) {
  const u = await api.as(USER);
  let r = await u.post('/api/reviews', { bookingId: Number(BK.slice(1)), stars: V.reviewStars });
  if (r.status !== 201) r = await u.post('/api/reviews', { bookingId: BK, stars: V.reviewStars });
  expect(r.status).toBe(201);
}

test(`[w=1] B7-u1 ${USER} เห็นปุ่ม review-${BK} ในหน้า /account`, async ({ page }) => {
  await loginUI(page, USER);
  await open(page, '/account');
  await expect(page.getByTestId(`review-${BK}`)).toBeVisible();
});

test(`[w=1] B7-u2 หลังรีวิวแล้ว ปุ่ม review-${BK} หาย`, async ({ page, api }) => {
  await reviewViaApi(api);
  await loginUI(page, USER);
  await open(page, '/account');
  // รอให้รายการนัดของ BK แสดงก่อน แล้วจึงตรวจว่าไม่มีปุ่มรีวิว
  await expect(page.getByTestId(`booking-${BK}`)).toBeVisible();
  await page.waitForTimeout(800);
  await expect(page.getByTestId(`review-${BK}`)).toHaveCount(0);
});

test(`[w=1] B7-u3 หน้านักบำบัดแสดงคะแนนใหม่ ${EXP.rating}`, async ({ page, api }) => {
  await reviewViaApi(api);
  await open(page, '/therapists');
  await expect(page.getByTestId(`therapist-rating-${EXP.th}`).first()).toContainText(EXP.rating);
});
