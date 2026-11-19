/**
 * Page guard (DESIGN §10 · FR-18, NFR-06): anyone without a session cookie is
 * sent to /login for every page. API routes are not redirected here — each
 * Route Handler validates the session in the database and calls canAccess()
 * (401 / 403 / 404). Runs on the edge runtime, so it only checks the cookie.
 */
import { NextResponse, type NextRequest } from 'next/server';
import { SESSION_COOKIE } from './lib/session-cookie';

const PUBLIC_PAGES = new Set(['/login']);

export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  if (pathname.startsWith('/api/')) return NextResponse.next(); // also excluded by the matcher
  if (PUBLIC_PAGES.has(pathname)) return NextResponse.next();
  if (req.cookies.get(SESSION_COOKIE)?.value) return NextResponse.next();
  const url = req.nextUrl.clone();
  url.pathname = '/login';
  url.search = '';
  if (pathname !== '/') url.searchParams.set('next', `${pathname}${search}`);
  return NextResponse.redirect(url);
}

export const config = {
  // Pages only. /api/* is excluded on purpose: Route Handlers check the session
  // themselves, and running middleware on uploads would make Next.js buffer (and
  // cap) the request body before lib/photo-store can count the bytes itself.
  matcher: ['/((?!api/|_next/static|_next/image|favicon\\.ico|logo\\.png|robots\\.txt).*)'],
};
