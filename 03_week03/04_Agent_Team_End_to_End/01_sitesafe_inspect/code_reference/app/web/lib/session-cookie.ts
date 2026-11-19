/** Session cookie name and attributes (shared by lib/auth.ts and middleware.ts, edge-safe). */
export const SESSION_COOKIE = 'sitesafe_session';
/** Session lifetime: 12 hours. */
export const SESSION_TTL_SECONDS = 12 * 60 * 60;

export const SESSION_COOKIE_OPTIONS = {
  httpOnly: true,
  secure: true,
  sameSite: 'lax' as const,
  path: '/',
};
