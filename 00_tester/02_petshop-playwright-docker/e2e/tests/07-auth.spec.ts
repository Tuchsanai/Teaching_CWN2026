import { test, expect, open, uniqueEmail, loginByUi, DEMO } from './fixtures';

test.describe('สมัครสมาชิก / เข้าสู่ระบบ', () => {
  test('TC-AUTH-01 สมัครสมาชิกสำเร็จ', {
    tag: ['@auth', '@P1'],
    annotation: { type: 'expected', description: 'ไปหน้า /account เห็น "ยินดีต้อนรับ มะลิ ทดสอบ!" และชื่อขึ้นที่เมนูด้านบน' },
  }, async ({ page }) => {
    await open(page, '/register');
    await page.getByTestId('reg-name').fill('มะลิ ทดสอบ');
    await page.getByTestId('reg-email').fill(uniqueEmail('mali'));
    await page.getByTestId('reg-password').fill('Meow2026');
    await expect(page.getByTestId('password-strength')).toBeVisible();
    await page.getByTestId('reg-confirm').fill('Meow2026');
    await page.getByTestId('reg-pet-cat').check();
    await page.getByTestId('reg-terms').check();
    await page.getByTestId('reg-submit').click();

    await expect(page).toHaveURL(/\/account\?welcome=1/);
    await expect(page.getByTestId('welcome-banner')).toContainText('ยินดีต้อนรับ มะลิ ทดสอบ!');
    await expect(page.getByTestId('user-menu')).toContainText('มะลิ ทดสอบ');
  });

  test('TC-AUTH-02 ส่งฟอร์มสมัครเปล่า เห็น error ทุกช่อง', {
    tag: ['@auth', '@P2'],
    annotation: { type: 'expected', description: 'error ใต้ช่อง ชื่อ อีเมล รหัสผ่าน และเงื่อนไข และยังอยู่หน้า /register' },
  }, async ({ page }) => {
    await open(page, '/register');
    await page.getByTestId('reg-submit').click();
    await expect(page.getByTestId('error-name')).toHaveText('กรุณากรอกชื่อ');
    await expect(page.getByTestId('error-email')).toHaveText('อีเมลไม่ถูกต้อง');
    await expect(page.getByTestId('error-password')).toHaveText('รหัสผ่านต้องมีอย่างน้อย 8 ตัว และมีตัวเลข');
    await expect(page.getByTestId('error-terms')).toHaveText('กรุณายอมรับเงื่อนไข');
    await expect(page).toHaveURL(/\/register/);
  });

  test('TC-AUTH-03 รหัสผ่านอ่อน และยืนยันรหัสผ่านไม่ตรงกัน', {
    tag: ['@auth', '@P2'],
    annotation: { type: 'expected', description: '"abcdefgh" (ไม่มีตัวเลข) ไม่ผ่าน และรหัสยืนยันต่างกันขึ้น "รหัสผ่านไม่ตรงกัน"' },
  }, async ({ page }) => {
    await open(page, '/register');
    await page.getByTestId('reg-name').fill('ทดสอบ รหัสผ่าน');
    await page.getByTestId('reg-email').fill(uniqueEmail('weak'));
    await page.getByTestId('reg-password').fill('abcdefgh');
    await page.getByTestId('reg-confirm').fill('abcdefgx');
    await page.getByTestId('reg-terms').check();
    await page.getByTestId('reg-submit').click();
    await expect(page.getByTestId('error-password')).toHaveText('รหัสผ่านต้องมีอย่างน้อย 8 ตัว และมีตัวเลข');
    await expect(page.getByTestId('error-confirm')).toHaveText('รหัสผ่านไม่ตรงกัน');
  });

  test('TC-AUTH-04 สมัครด้วยอีเมลที่มีอยู่แล้ว', {
    tag: ['@auth', '@P2'],
    annotation: { type: 'expected', description: 'ใช้อีเมล demo@pawpantry.test → "อีเมลนี้ถูกใช้แล้ว"' },
  }, async ({ page }) => {
    await open(page, '/register');
    await page.getByTestId('reg-name').fill('คนซ้ำ');
    await page.getByTestId('reg-email').fill(DEMO.email);
    await page.getByTestId('reg-password').fill('Dupe1234');
    await page.getByTestId('reg-confirm').fill('Dupe1234');
    await page.getByTestId('reg-terms').check();
    await page.getByTestId('reg-submit').click();
    await expect(page.getByTestId('error-email')).toHaveText('อีเมลนี้ถูกใช้แล้ว');
  });

  test('TC-AUTH-05 เข้าสู่ระบบด้วยรหัสผ่านผิด', {
    tag: ['@auth', '@P1'],
    annotation: { type: 'expected', description: 'ขึ้น "อีเมลหรือรหัสผ่านไม่ถูกต้อง" และยังไม่ได้เข้าสู่ระบบ' },
  }, async ({ page }) => {
    await open(page, '/login');
    await loginByUi(page, DEMO.email, 'wrong-pass1');
    await expect(page.getByTestId('login-error')).toHaveText('อีเมลหรือรหัสผ่านไม่ถูกต้อง');
    await expect(page.getByTestId('login-link')).toBeVisible();
  });

  test('TC-AUTH-06 เข้าสู่ระบบสำเร็จ แล้วออกจากระบบ', {
    tag: ['@auth', '@P1'],
    annotation: { type: 'expected', description: 'เห็นชื่อ "สมใจ ใจดี" ที่เมนู กดออกจากระบบแล้วกลับเป็นปุ่มเข้าสู่ระบบ' },
  }, async ({ page }) => {
    await open(page, '/');
    await page.getByTestId('login-link').click();
    await loginByUi(page, DEMO.email, DEMO.password);
    await expect(page.getByTestId('user-menu')).toContainText(DEMO.name);

    await page.getByTestId('logout-button').click();
    await expect(page.getByTestId('login-link')).toBeVisible();
  });
});
