// POST /api/calc/[type] (concrete|wall|tile|paint|rebar) body = input ของ shared/calc.js → ผล calculate() (B1)
// เติม name/price/unitPrice/lineTotal ให้แต่ละ row (ราคาจาก DB · ราคาส่งตามจำนวน) + estimate รวม
import { NextResponse } from 'next/server';
import { calculate, CALC_TYPES } from '@/shared/calc.js';
import { tierPrice, round2 } from '@/shared/pricing.js';
import { productsBySku } from '../../products/_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request, { params }: { params: { type: string } }) {
  const type = String(params.type || '').toLowerCase();
  if (!CALC_TYPES.includes(type)) return NextResponse.json({ error: `ไม่รู้จักประเภท ${type}` }, { status: 404 });
  let input: Record<string, unknown> = {};
  try {
    input = (await req.json()) || {};
  } catch {
    /* body ว่าง → ใช้ค่าเริ่มต้น */
  }
  let result: any;
  try {
    result = calculate(type, input);
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'คำนวณไม่สำเร็จ' }, { status: 400 });
  }
  try {
    const info = await productsBySku(result.rows.map((r: any) => r.sku));
    result.rows = result.rows.map((r: any) => {
      const p = info[r.sku];
      if (!p) return r;
      const unitPrice = tierPrice(p.price, r.qty);
      return { ...r, name: p.name, price: p.price, unitPrice, lineTotal: round2(unitPrice * r.qty) };
    });
    result.estimate = round2(result.rows.reduce((s: number, r: any) => s + (r.lineTotal || 0), 0));
  } catch (e) {
    console.error('[api/calc] price lookup', e);
  }
  return NextResponse.json({ type, input, ...result });
}
