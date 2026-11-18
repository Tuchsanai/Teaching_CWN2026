// GET /api/products/[sku] → product + tiers[3] + stock[3] (B1)
import { NextResponse } from 'next/server';
import { getProduct } from '../_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(_req: Request, { params }: { params: { sku: string } }) {
  try {
    const p = await getProduct(decodeURIComponent(params.sku));
    if (!p) return NextResponse.json({ error: 'ไม่พบสินค้า' }, { status: 404 });
    return NextResponse.json(p);
  } catch (e) {
    console.error('[api/products/sku]', e);
    return NextResponse.json({ error: 'อ่านข้อมูลสินค้าไม่สำเร็จ' }, { status: 500 });
  }
}
