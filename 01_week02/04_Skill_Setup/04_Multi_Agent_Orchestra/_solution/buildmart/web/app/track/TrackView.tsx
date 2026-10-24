'use client';
// app/track/TrackView.tsx (B2) — ติดตามคำสั่งซื้อด้วยเลข BM-… + เบอร์โทร → timeline 4 ขั้น
import { useEffect, useState } from 'react';
import { api, baht } from '../cart/Summary';

const STEPS = [
  { code: 'received', label: 'รับคำสั่งซื้อ', icon: '📝' },
  { code: 'preparing', label: 'เตรียมสินค้า', icon: '📦' },
  { code: 'shipping', label: 'กำลังจัดส่ง', icon: '🚚' },
  { code: 'delivered', label: 'ส่งแล้ว', icon: '🏠' },
];
const BRANCH: Record<string, string> = { LKB: 'ลาดกระบัง', BNA: 'บางนา', RST: 'รังสิต' };
const SLOT: Record<string, string> = { morning: 'ช่วงเช้า 08:00–12:00', afternoon: 'ช่วงบ่าย 13:00–17:00' };

type Track = {
  orderNo: string;
  status: string;
  statusLabel: string;
  history: { status: string; changedAt: string; label: string }[];
  branch: string;
  deliveryDate: string;
  deliverySlot: string;
  customerName: string;
  items: { sku: string; name: string; qty: number; unit: string }[];
  total: number;
};

const fmtTime = (iso: string) =>
  new Date(iso).toLocaleString('th-TH', { timeZone: 'Asia/Bangkok', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
const fmtDate = (d: string) =>
  new Date(d + 'T00:00:00+07:00').toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok', weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

export default function TrackView({ initialNo = '', initialPhone = '' }: { initialNo?: string; initialPhone?: string }) {
  const [no, setNo] = useState(initialNo);
  const [phone, setPhone] = useState(initialPhone);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [data, setData] = useState<Track | null>(null);

  const lookup = async (n = no, p = phone) => {
    setBusy(true);
    setErr('');
    try {
      setData(await api<Track>('/api/track', { method: 'POST', json: { orderNo: n.trim(), phone: p.trim() } }));
    } catch (e: any) {
      setData(null);
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (initialNo && initialPhone) lookup(initialNo, initialPhone);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const curIdx = data ? Math.max(0, STEPS.findIndex((s) => s.code === data.status)) : -1;
  const when = (code: string) => {
    const h = data?.history.filter((x) => x.status === code).pop();
    return h ? fmtTime(h.changedAt) : '';
  };

  return (
    <>
      <form
        className="b2-card b2-form"
        onSubmit={(e) => {
          e.preventDefault();
          lookup();
        }}
      >
        <div className="b2-track-form">
          <label>
            เลขที่คำสั่งซื้อ
            <input
              className="input"
              data-testid="track-order-no"
              placeholder="BM-YYYYMMDD-NNNN"
              value={no}
              onChange={(e) => setNo(e.target.value.toUpperCase())}
              required
            />
          </label>
          <label>
            เบอร์โทรที่ใช้สั่งซื้อ
            <input className="input" data-testid="track-phone" inputMode="tel" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          </label>
          <button className="btn" type="submit" data-testid="track-submit" disabled={busy} style={{ height: 44 }}>
            {busy ? 'กำลังค้นหา…' : '🔎 ติดตาม'}
          </button>
        </div>
        {err && <div className="b2-msg err">{err}</div>}
      </form>

      {data && (
        <div className="b2-card" style={{ marginTop: 16 }}>
          <div className="b2-status-now">
            คำสั่งซื้อ <b style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{data.orderNo}</b> · สถานะปัจจุบัน:{' '}
            <b data-testid="track-current" data-status={data.status}>
              {data.statusLabel}
            </b>
          </div>
          <ol className="b2-steps" style={{ listStyle: 'none', padding: 0 }}>
            {STEPS.map((s, i) => (
              <li
                key={s.code}
                className={`b2-step${i === curIdx ? ' current' : ''}`}
                data-testid="track-step"
                data-status={s.code}
                data-active={i <= curIdx ? 'true' : 'false'}
                aria-current={i === curIdx ? 'step' : undefined}
              >
                <div className="dot" aria-hidden>
                  {s.icon}
                </div>
                <div className="lbl">{s.label}</div>
                <div className="when">{i <= curIdx ? when(s.code) : ''}</div>
              </li>
            ))}
          </ol>
          <dl className="b2-kv">
            <dt>ผู้สั่งซื้อ</dt>
            <dd>{data.customerName}</dd>
            <dt>ส่งจากสาขา</dt>
            <dd>
              {BRANCH[data.branch] || data.branch} ({data.branch})
            </dd>
            <dt>วันส่ง</dt>
            <dd>
              {data.deliveryDate ? fmtDate(data.deliveryDate) : '-'} · {SLOT[data.deliverySlot] || data.deliverySlot}
            </dd>
            <dt>รายการ</dt>
            <dd>{data.items.map((i) => `${i.name} × ${i.qty.toLocaleString()} ${i.unit}`).join(' · ')}</dd>
            <dt>ยอดสุทธิ</dt>
            <dd className="price">฿{baht(data.total)}</dd>
          </dl>
        </div>
      )}
    </>
  );
}
