import { test as base, expect, type Page, type APIRequestContext } from '@playwright/test';

export const test = base;
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
