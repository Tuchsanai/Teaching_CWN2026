// middleware.ts (A) — สร้าง cookie bm_sid ให้ทุก request ที่ยังไม่มี (ใส่ใน request ปัจจุบันด้วย ให้ server อ่านได้ทันที)
import { NextResponse, type NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  if (req.cookies.get('bm_sid')?.value) return NextResponse.next();
  const sid = crypto.randomUUID();
  const headers = new Headers(req.headers);
  const prev = req.headers.get('cookie');
  headers.set('cookie', (prev ? prev + '; ' : '') + `bm_sid=${sid}`);
  const res = NextResponse.next({ request: { headers } });
  res.cookies.set('bm_sid', sid, { httpOnly: true, sameSite: 'lax', path: '/', maxAge: 60 * 60 * 24 * 30 });
  return res;
}

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico|logo.svg).*)'] };
