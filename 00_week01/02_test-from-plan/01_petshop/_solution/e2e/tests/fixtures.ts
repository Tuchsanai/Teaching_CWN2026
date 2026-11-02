import { test as base, expect, type Page, type APIRequestContext } from '@playwright/test';

const GIF = !!process.env.GIF;

// GIF mode: show a caption with the test-case title and a red ripple wherever Playwright clicks,
// so a viewer can follow each step in the recorded GIF.
const overlayScript = (caption: string) => `
  (() => {
    const add = () => {
      if (document.getElementById('__pw-caption')) return;
      const bar = document.createElement('div');
      bar.id = '__pw-caption';
      bar.textContent = ${JSON.stringify('🎬 ' + caption)};
      bar.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483647;pointer-events:none;' +
        'background:rgba(30,42,58,.92);color:#fff;font:700 22px/1.4 "IBM Plex Sans Thai",sans-serif;' +
        'padding:10px 20px;border-radius:999px;box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:80vw';
      document.documentElement.appendChild(bar);
      const css = document.createElement('style');
      css.textContent = '@keyframes __pwr{from{transform:translate(-50%,-50%) scale(.3);opacity:1}to{transform:translate(-50%,-50%) scale(1.6);opacity:0}}';
      document.documentElement.appendChild(css);
      document.addEventListener('mousedown', (e) => {
        const dot = document.createElement('div');
        dot.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;width:60px;height:60px;' +
          'border:4px solid #ff2d2d;border-radius:50%;left:' + e.clientX + 'px;top:' + e.clientY + 'px;' +
          'animation:__pwr .7s ease-out forwards';
        document.documentElement.appendChild(dot);
        setTimeout(() => dot.remove(), 800);
      }, true);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
  })();`;

export const test = base.extend<{ page: Page }>({
  page: async ({ page }, use, testInfo) => {
    if (GIF) await page.addInitScript(overlayScript(testInfo.title));
    await use(page);
    if (GIF) await page.waitForTimeout(2500); // hold the last frame so the GIF ends on the result
  },
});

export { expect };

/** Open a page and wait until the app has loaded cart/wishlist from localStorage. */
export async function open(page: Page, path: string) {
  await page.goto(path);
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
}

export const DEMO = { email: 'demo@pawpantry.test', password: 'Paw12345', name: 'สมใจ ใจดี' };

export function uniqueEmail(tag: string) {
  return `${tag}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@test.dev`;
}

/** Create a fresh account through the API (also logs this browser context in). */
export async function registerByApi(request: APIRequestContext, name = 'นักทดสอบ ใจเย็น') {
  const user = { name, email: uniqueEmail('buyer'), password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true };
  const res = await request.post('/api/auth/register', { data: user });
  expect(res.ok(), await res.text()).toBeTruthy();
  return user;
}

export async function loginByUi(page: Page, email: string, password: string) {
  await page.getByTestId('login-email').fill(email);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
}

/** Parse "฿1,234" → 1234 */
export function baht(text: string | null) {
  return Number((text ?? '').replace(/[^\d]/g, ''));
}

export const CAT_SLUGS = [
  'kitten-salmon-dry', 'adult-chicken-dry', 'senior-tuna-dry', 'tuna-pouch', 'kitten-chicken-mousse',
  'duck-grainfree-dry', 'lickable-salmon-treat', 'freeze-dried-chicken-cat', 'hairball-control-dry', 'urinary-care-dry',
  'cat-feather-wand', 'cat-tunnel', 'cat-scratcher', 'cat-fountain',
];
export const CHICKEN_SLUGS = [
  'adult-chicken-dry', 'kitten-chicken-mousse', 'freeze-dried-chicken-cat', 'urinary-care-dry',
  'puppy-chicken-dry', 'dental-chew-treat', 'small-breed-chicken-dry',
];
