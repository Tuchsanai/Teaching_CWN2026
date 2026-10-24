import { test, expect, step, check, open, plan, login, logout, register, addToCart, DEMO, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.1 เข้าสู่ระบบ / สมัครสมาชิก

test('TC-AUTH-01 login ด้วยบัญชีตัวอย่าง', plan('TC-AUTH-01', '@auth'), async ({ page }) => {
  await step('1. เปิดหน้าเข้าสู่ระบบ กรอก demo@pawpantry.test / Paw12345 แล้วกดเข้าสู่ระบบ', async () => {
    await open(page, '/login');
    await page.getByTestId('login-email').fill(DEMO.email);
    await page.getByTestId('login-password').fill(DEMO.password);
    await page.getByTestId('login-submit').click();
    await page.waitForURL((u) => !u.pathname.startsWith('/login')).catch(() => {});
  });
  await step('2. ดูหัวเว็บ', async () => {
    await check(page, 'ออกจากหน้า /login แล้ว', null, () => expect.soft(page).not.toHaveURL(/\/login/));
    await check(page, 'หัวเว็บแสดงชื่อผู้ใช้', page.getByTestId('user-menu'), () => expect.soft(page.getByTestId('user-menu')).toBeVisible());
    await check(page, 'ไม่มีปุ่ม "เข้าสู่ระบบ" บนหัวเว็บ', page.getByTestId('login-link'), () => expect.soft(page.getByTestId('login-link')).toHaveCount(0));
    await check(page, 'มีปุ่ม "ออกจากระบบ"', page.getByTestId('logout-button'), () => expect.soft(page.getByTestId('logout-button')).toBeVisible());
  });
  await step('3. เปิด /account', async () => {
    await open(page, '/account');
    await check(page, 'เปิด /account ได้ ไม่ถูกส่งกลับไป login', page.getByTestId('profile-card'), () => expect.soft(page).toHaveURL(/\/account$/));
  });
});

test('TC-AUTH-02 รหัสผ่านผิด และตัวพิมพ์ผิด', plan('TC-AUTH-02', '@auth'), async ({ page }) => {
  for (const [n, pw] of [['1', 'Paw12346'], ['2', 'paw12345']] as const) {
    await step(`${n}. login ด้วยรหัสผ่าน ${pw}`, async () => {
      await open(page, '/login');
      await page.getByTestId('login-email').fill(DEMO.email);
      await page.getByTestId('login-password').fill(pw);
      await page.getByTestId('login-submit').click();
      await page.waitForTimeout(800);
      await check(page, `${pw}: ยังอยู่ที่ /login`, null, () => expect.soft(page).toHaveURL(/\/login/));
      await check(page, `${pw}: ข้อความ "อีเมลหรือรหัสผ่านไม่ถูกต้อง"`, page.getByTestId('login-error'),
        () => expect.soft(page.getByTestId('login-error')).toHaveText('อีเมลหรือรหัสผ่านไม่ถูกต้อง'), { near: page.getByTestId('login-submit') });
      await check(page, `${pw}: หัวเว็บยังมีปุ่ม "เข้าสู่ระบบ"`, page.getByTestId('login-link'), () => expect.soft(page.getByTestId('login-link')).toBeVisible());
    });
  }
});

test('TC-AUTH-03 ยังไม่ login กดชำระเงิน แล้วกลับมาหน้าเดิม', plan('TC-AUTH-03', '@auth'), async ({ page }) => {
  await step('1. ใส่ลูกแมว 400 g 1 ชิ้นลงตะกร้า (ยังไม่ login)', async () => {
    await addToCart(page, P.kitten400);
  });
  await step('2. ไปตะกร้า กด "ดำเนินการชำระเงิน"', async () => {
    await open(page, '/cart');
    await page.getByTestId('checkout-button').click();
    await page.waitForURL(/\/login/);
    await check(page, 'ถูกพาไป /login?next=/checkout', null, () => expect.soft(page).toHaveURL(/\/login\?next=(%2F|\/)checkout$/));
  });
  await step('3. login demo', async () => {
    await page.getByTestId('login-email').fill(DEMO.email);
    await page.getByTestId('login-password').fill(DEMO.password);
    await page.getByTestId('login-submit').click();
    await page.waitForURL((u) => !u.pathname.startsWith('/login')).catch(() => {});
    await check(page, 'กลับมาที่ /checkout', null, () => expect.soft(page).toHaveURL(/\/checkout$/));
    await check(page, 'ตะกร้ายังมีของครบ 🛒 = 1', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('1'));
  });
});

test('TC-AUTH-04 ออกจากระบบแล้วเปิด /account', plan('TC-AUTH-04', '@auth'), async ({ page }) => {
  await step('1. login demo แล้วกด "ออกจากระบบ"', async () => {
    await login(page);
    await logout(page);
    await check(page, 'หัวเว็บกลับเป็นปุ่ม "เข้าสู่ระบบ"', page.getByTestId('login-link'), () => expect.soft(page.getByTestId('login-link')).toBeVisible());
  });
  await step('2. เปิด /account', async () => {
    await open(page, '/account');
    await page.waitForURL(/\/login/).catch(() => {});
    await check(page, 'ถูกพาไป /login?next=/account', null, () => expect.soft(page).toHaveURL(/\/login\?next=(%2F|\/)account$/));
  });
});

test('TC-REG-01 สมัครสมาชิกใหม่', plan('TC-REG-01', '@register'), async ({ page }) => {
  await step('1. สมัคร "ทดสอบ ใหม่" · new1@pawpantry.test · Abcd1234 ×2 · ติ๊กยอมรับ', async () => {
    await register(page, 'ทดสอบ ใหม่', 'new1@pawpantry.test', 'Abcd1234');
    await page.waitForURL(/\/account/).catch(() => {});
    await check(page, 'ไปหน้า /account ที่มี welcome', null, () => expect.soft(page).toHaveURL(/\/account\?.*welcome/));
    await check(page, 'หัวเว็บแสดง "ทดสอบ ใหม่"', page.getByTestId('user-menu'), () => expect.soft(page.getByTestId('user-menu')).toContainText('ทดสอบ ใหม่'));
    await check(page, 'ประวัติการสั่งซื้อ 0 รายการ', page.getByTestId('profile-card'), () => expect.soft(page.getByTestId('order-row')).toHaveCount(0));
  });
  await step('2. ออกจากระบบ แล้ว login ด้วยรหัสใหม่', async () => {
    await logout(page);
    await open(page, '/login');
    await page.getByTestId('login-email').fill('new1@pawpantry.test');
    await page.getByTestId('login-password').fill('Abcd1234');
    await page.getByTestId('login-submit').click();
    await check(page, 'login ด้วยรหัสใหม่ได้ (หัวเว็บแสดง "ทดสอบ ใหม่")', page.getByTestId('user-menu'),
      () => expect.soft(page.getByTestId('user-menu')).toContainText('ทดสอบ ใหม่'), { near: page.getByTestId('login-submit') });
  });
});

test('TC-REG-02 รหัสผ่าน 7 ตัว vs 8 ตัว', plan('TC-REG-02', '@register'), async ({ page }) => {
  await step('1. สมัครด้วยรหัสผ่าน 7 ตัว Abc1234', async () => {
    await register(page, 'ทดสอบ เจ็ด', 'seven@pawpantry.test', 'Abc1234');
    await page.waitForTimeout(800);
    await check(page, '7 ตัว: ยังอยู่ /register (ไม่สร้างบัญชี)', null, () => expect.soft(page).toHaveURL(/\/register/));
    await check(page, '7 ตัว: ข้อความ "รหัสผ่านต้องมีอย่างน้อย 8 ตัว และมีตัวเลข"', page.getByTestId('error-password'),
      () => expect.soft(page.getByTestId('error-password')).toHaveText('รหัสผ่านต้องมีอย่างน้อย 8 ตัว และมีตัวเลข'), { near: page.getByTestId('reg-password') });
    await check(page, '7 ตัว: ยังไม่ได้ login', page.getByTestId('login-link'), () => expect.soft(page.getByTestId('login-link')).toBeVisible());
  });
  await step('2. แก้เป็นรหัสผ่าน 8 ตัว Abcd1234 แล้วสมัครอีกครั้ง', async () => {
    await page.getByTestId('reg-password').fill('Abcd1234');
    await page.getByTestId('reg-confirm').fill('Abcd1234');
    await page.getByTestId('reg-submit').click();
    await page.waitForURL(/\/account/).catch(() => {});
    await check(page, '8 ตัว: สมัครสำเร็จ (ไปหน้า /account)', null, () => expect.soft(page).toHaveURL(/\/account/));
  });
});

test('TC-REG-03 สมัครด้วยอีเมลที่มีแล้ว (ตัวพิมพ์ใหญ่)', plan('TC-REG-03', '@register'), async ({ page }) => {
  await step('1. สมัครด้วย DEMO@pawpantry.test', async () => {
    await register(page, 'ทดสอบ ซ้ำ', 'DEMO@pawpantry.test', 'Abcd1234');
    await page.waitForTimeout(800);
    await check(page, 'ไม่สร้างบัญชี (ยังอยู่ /register)', null, () => expect.soft(page).toHaveURL(/\/register/));
    await check(page, 'ข้อความ "อีเมลนี้ถูกใช้แล้ว"', page.getByTestId('error-email'),
      () => expect.soft(page.getByTestId('error-email')).toHaveText('อีเมลนี้ถูกใช้แล้ว'), { near: page.getByTestId('reg-email') });
  });
});
