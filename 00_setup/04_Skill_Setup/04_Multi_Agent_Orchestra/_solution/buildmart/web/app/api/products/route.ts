// GET /api/products?q&category&min&max&inStock&sort=price_asc|price_desc&page → { items, total, page, pages } (B1)
import { NextResponse, type NextRequest } from 'next/server';
import { parseSearch, searchProducts } from './_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    return NextResponse.json(await searchProducts(parseSearch(req.nextUrl.searchParams)));
  } catch (e) {
    console.error('[api/products]', e);
    return NextResponse.json({ error: 'ค้นหาสินค้าไม่สำเร็จ' }, { status: 500 });
  }
}
