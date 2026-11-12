// POST /api/track {orderNo, phone} (B2) → {orderNo, status, statusLabel, history[], ...} · เลข/เบอร์ไม่ตรง → 404
import { digits, errorJson, HttpError, readJson } from '../cart/_lib';
import { getOrder } from '../orders/_order';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const b = await readJson(req);
  try {
    const no = String(b.orderNo ?? '').trim();
    const phone = digits(b.phone);
    if (!no || !phone) throw new HttpError(400, 'กรุณากรอกเลขคำสั่งซื้อและเบอร์โทร');
    const o = await getOrder(no);
    if (!o || digits(o.phone) !== phone) throw new HttpError(404, 'ไม่พบคำสั่งซื้อ ตรวจสอบเลขคำสั่งซื้อและเบอร์โทรอีกครั้ง');
    return Response.json({
      orderNo: o.orderNo,
      status: o.status,
      statusLabel: o.statusLabel,
      history: o.history,
      branch: o.branch,
      deliveryDate: o.deliveryDate,
      deliverySlot: o.deliverySlot,
      customerName: o.customerName,
      items: o.items,
      total: o.totals?.total,
      createdAt: o.createdAt,
    });
  } catch (e) {
    return errorJson(e);
  }
}
