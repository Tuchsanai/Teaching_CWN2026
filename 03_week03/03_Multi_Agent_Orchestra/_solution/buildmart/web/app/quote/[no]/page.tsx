// /quote/[no] (B2) — ใบเสนอราคา QT-YYYYMMDD-NNNN (พิมพ์ได้ · อายุ 7 วัน · ปุ่มแปลงเป็นคำสั่งซื้อ)
import Link from 'next/link';
import { formatBaht } from '@/shared/pricing.js';
import { getQuote } from '../../api/quotes/_quote';
import QuoteActions from './QuoteActions';
import '../../cart/shop.css';

export const dynamic = 'force-dynamic';

export function generateMetadata({ params }: { params: { no: string } }) {
  return { title: `ใบเสนอราคา ${decodeURIComponent(params.no)} — บ้านช่าง BuildMart` };
}

const thDate = (iso: string) =>
  new Date(iso).toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok', day: 'numeric', month: 'long', year: 'numeric' });
const kg = (n: number) => Number(n || 0).toLocaleString('en-US', { maximumFractionDigits: 2 });

export default async function QuotePage({ params }: { params: { no: string } }) {
  const q = await getQuote(decodeURIComponent(params.no));
  if (!q) {
    return (
      <div className="b2-card b2-empty">
        <div className="big">🔎</div>
        <h2>ไม่พบใบเสนอราคา {decodeURIComponent(params.no)}</h2>
        <Link href="/cart" className="btn">
          กลับตะกร้า
        </Link>
      </div>
    );
  }
  const t = q.totals;
  return (
    <div className="b2-page">
      <article className="b2-doc">
        {q.expired && <div className="b2-expired">ใบเสนอราคานี้หมดอายุแล้ว (เกิน 7 วัน) — กรุณาขอใบใหม่</div>}
        <header className="b2-doc-head">
          <div className="shop">
            <b>
              บ้านช่าง <span>BuildMart</span>
            </b>
            <div>ร้านวัสดุก่อสร้าง · เปิด จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00</div>
            <div>ลาดกระบัง 02-111-0001 · บางนา 02-111-0002 · รังสิต 02-111-0003 · LINE @buildmart-demo</div>
          </div>
          <div className="title">
            <h1>ใบเสนอราคา</h1>
            <div className="muted" style={{ fontSize: 13 }}>
              QUOTATION
            </div>
            <div className="no" data-testid="quote-no">
              {q.quoteNo}
            </div>
          </div>
        </header>

        <section className="b2-doc-meta">
          <div className="box">
            <h3>เสนอราคาให้</h3>
            <div>
              <b>{q.customerName || 'ลูกค้าทั่วไป'}</b>
            </div>
            {q.company && <div>{q.company}</div>}
            {q.taxId && <div>เลขประจำตัวผู้เสียภาษี {q.taxId}</div>}
          </div>
          <div className="box">
            <h3>รายละเอียดเอกสาร</h3>
            <div>วันที่ออก: {thDate(q.createdAt)}</div>
            <div>
              ใช้ได้ถึง: <b data-testid="quote-expires">{thDate(q.expiresAt)}</b> (7 วัน)
            </div>
            <div>
              ขนส่ง: {t.vehicleLabel} · น้ำหนักรวม {kg(t.weight)} กก.
            </div>
          </div>
        </section>

        <table className="b2-table">
          <thead>
            <tr>
              <th>#</th>
              <th>รหัส</th>
              <th>รายการ</th>
              <th className="num">จำนวน</th>
              <th className="num">ราคา/หน่วย</th>
              <th className="num">จำนวนเงิน</th>
            </tr>
          </thead>
          <tbody>
            {q.items.map((i, n) => (
              <tr key={i.sku} data-testid="quote-row" data-sku={i.sku} data-qty={i.qty}>
                <td>{n + 1}</td>
                <td className="b2-sku">{i.sku}</td>
                <td>
                  {i.name}
                  {i.unitPrice < i.price && (
                    <div className="muted" style={{ fontSize: 12 }}>
                      ราคาส่ง (ปกติ {formatBaht(i.price)})
                    </div>
                  )}
                </td>
                <td className="num">
                  {i.qty.toLocaleString()} {i.unit}
                </td>
                <td className="num">{formatBaht(i.unitPrice)}</td>
                <td className="num">{formatBaht(i.lineTotal)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <section className="b2-doc-foot">
          <div className="b2-doc-note">
            <b>เงื่อนไข</b>
            <ul>
              <li>ราคาสินค้ายังไม่รวม VAT · คิด VAT 7% จาก (ยอดหลังส่วนลด + ค่าส่ง)</li>
              <li>ราคาส่ง: 50–199 ชิ้น ลด 5% · 200 ชิ้นขึ้นไป ลด 10% (ต่อรายการ)</li>
              <li>ใบเสนอราคามีอายุ 7 วันนับจากวันที่ออก · สต็อกยืนยันอีกครั้งตอนสั่งซื้อ</li>
            </ul>
          </div>
          <div className="b2-sum">
            <div className="row">
              <span>ยอดสินค้า</span>
              <span data-testid="quote-subtotal">{formatBaht(t.subtotal)}</span>
            </div>
            {t.discount > 0 && (
              <div className="row disc">
                <span>ส่วนลดคูปอง {t.coupon}</span>
                <span>−{formatBaht(t.discount)}</span>
              </div>
            )}
            <div className="row">
              <span>ยอดหลังส่วนลด</span>
              <span>{formatBaht(t.afterDiscount)}</span>
            </div>
            <div className="row">
              <span>ค่าส่ง ({t.vehicleLabel})</span>
              <span>{formatBaht(t.shipping)}</span>
            </div>
            <div className="row">
              <span>VAT 7%</span>
              <span>{formatBaht(t.vat)}</span>
            </div>
            <div className="row total">
              <span>ยอดสุทธิ</span>
              <span>
                ฿<span data-testid="quote-total">{formatBaht(t.total)}</span>
              </span>
            </div>
          </div>
        </section>

        <div className="b2-sign">
          <div>ผู้เสนอราคา · บ้านช่าง BuildMart</div>
          <div>ผู้อนุมัติสั่งซื้อ</div>
        </div>
      </article>
      <QuoteActions quoteNo={q.quoteNo} expired={q.expired} />
    </div>
  );
}
