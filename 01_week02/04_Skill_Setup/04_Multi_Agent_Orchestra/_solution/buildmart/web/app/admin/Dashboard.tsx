'use client';
// แดชบอร์ดหลังร้าน: ยอดขาย (วันนี้/7 วัน + กราฟ SVG) · 5 ขายดี (แท่ง CSS) · DLQ · แจ้งเตือน · สต็อกต่ำ · คำสั่งซื้อ · ตารางสต็อก
import { useCallback, useEffect, useMemo, useState } from 'react';
import { formatBaht } from '@/shared/pricing.js';

type Day = { day: string; total: number; orders: number };
type Dash = {
  today: { total: number; orders: number };
  week: { total: number; orders: number; days: Day[] };
  top: { sku: string; name: string; unit: string; qty: number; revenue: number }[];
  statusCount: Record<string, number>;
  lowStockCount: number;
  unreadNotifications: number;
  dlq: number | null;
};
type Note = { id: number; kind: 'order' | 'low_stock'; message: string; ref: string | null; createdAt: string; read: boolean };
type Order = {
  orderNo: string;
  customerName: string;
  phone: string;
  branch: string;
  deliveryDate: string | null;
  slot: string | null;
  total: number;
  status: string;
  createdAt: string;
  items: { sku: string; name: string; qty: number; unit: string }[];
};
type StockItem = {
  sku: string;
  name: string;
  category: string;
  unit: string;
  reorderPoint: number;
  stock: Record<Branch, number>;
  low: Branch[];
};
type Branch = 'LKB' | 'BNA' | 'RST';

const BRANCHES: Branch[] = ['LKB', 'BNA', 'RST'];
const BRANCH_NAME: Record<string, string> = { LKB: 'ลาดกระบัง', BNA: 'บางนา', RST: 'รังสิต' };
const STATUS: { value: string; label: string }[] = [
  { value: 'received', label: 'รับคำสั่งซื้อ' },
  { value: 'preparing', label: 'เตรียมสินค้า' },
  { value: 'shipping', label: 'กำลังจัดส่ง' },
  { value: 'delivered', label: 'ส่งแล้ว' },
];
const statusLabel = (s: string) => STATUS.find((x) => x.value === s)?.label ?? s;
const baht = (n: number) => formatBaht(n);
const thDay = (iso: string) =>
  new Date(iso + 'T00:00:00').toLocaleDateString('th-TH', { weekday: 'short', day: 'numeric', month: 'short' });
const thTime = (iso: string) =>
  new Date(iso).toLocaleString('th-TH', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(url, { cache: 'no-store' });
  if (r.status === 401) {
    window.location.reload(); // cookie หมดอายุ → กลับไปหน้าล็อกอิน
    throw new Error('unauthorized');
  }
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return r.json();
}

/* ---------------- กราฟ ---------------- */

function SalesChart({ days }: { days: Day[] }) {
  const W = 560;
  const H = 220;
  const pad = { l: 8, r: 8, t: 26, b: 44 };
  const max = Math.max(1, ...days.map((d) => d.total));
  const bw = (W - pad.l - pad.r) / Math.max(days.length, 1);
  const short = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 100000 ? 0 : 1)}k` : n.toFixed(0));
  return (
    <svg className="adm-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="กราฟยอดขาย 7 วันล่าสุด">
      <line x1={pad.l} x2={W - pad.r} y1={H - pad.b} y2={H - pad.b} stroke="var(--line)" />
      {days.map((d, i) => {
        const h = ((H - pad.t - pad.b) * d.total) / max;
        const x = pad.l + i * bw + bw * 0.18;
        const y = H - pad.b - h;
        const isToday = i === days.length - 1;
        return (
          <g key={d.day}>
            <title>{`${thDay(d.day)} · ${baht(d.total)} บาท · ${d.orders} คำสั่งซื้อ`}</title>
            <rect x={x} y={y} width={bw * 0.64} height={Math.max(h, d.total > 0 ? 2 : 0)} rx={5}
              fill={isToday ? 'var(--brand)' : '#f6a774'} />
            {d.total > 0 && (
              <text x={x + bw * 0.32} y={y - 6} textAnchor="middle" className="adm-chart-val">
                {short(d.total)}
              </text>
            )}
            <text x={x + bw * 0.32} y={H - pad.b + 18} textAnchor="middle" className="adm-chart-lbl">
              {thDay(d.day).split(' ')[0]}
            </text>
            <text x={x + bw * 0.32} y={H - pad.b + 34} textAnchor="middle" className="adm-chart-sub">
              {d.day.slice(8)}/{d.day.slice(5, 7)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function TopProducts({ top }: { top: Dash['top'] }) {
  if (!top.length) return <p className="muted adm-empty">ยังไม่มียอดขายใน 7 วันนี้</p>;
  const max = Math.max(...top.map((t) => t.qty));
  return (
    <ol className="adm-top">
      {top.map((t, i) => (
        <li key={t.sku}>
          <div className="adm-top-head">
            <span className="adm-rank">{i + 1}</span>
            <span className="adm-top-name" title={t.name}>
              {t.name}
            </span>
            <span className="adm-top-qty">
              {t.qty.toLocaleString()} {t.unit}
            </span>
          </div>
          <div className="adm-bar">
            <span style={{ width: `${(100 * t.qty) / max}%` }} />
          </div>
          <div className="adm-top-sub muted">
            {t.sku} · {baht(t.revenue)} บาท
          </div>
        </li>
      ))}
    </ol>
  );
}

/* ---------------- หน้า ---------------- */

export default function Dashboard() {
  const [dash, setDash] = useState<Dash | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [unread, setUnread] = useState(0);
  const [orders, setOrders] = useState<Order[]>([]);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [orderMsg, setOrderMsg] = useState<Record<string, string>>({});
  const [orderFilter, setOrderFilter] = useState('');
  const [orderQ, setOrderQ] = useState('');
  const [stock, setStock] = useState<StockItem[]>([]);
  const [edit, setEdit] = useState<Record<string, Partial<Record<Branch | 'rp', string>>>>({});
  const [stockMsg, setStockMsg] = useState<Record<string, string>>({});
  const [stockQ, setStockQ] = useState('');
  const [onlyLow, setOnlyLow] = useState(false);
  const [error, setError] = useState('');

  const loadDash = useCallback(() => getJson<Dash>('/api/admin/dashboard').then(setDash), []);
  const loadNotes = useCallback(
    () =>
      getJson<{ items: Note[]; unread: number }>('/api/admin/notifications?limit=30').then((j) => {
        setNotes(j.items);
        setUnread(j.unread);
      }),
    [],
  );
  const loadOrders = useCallback(() => {
    const p = new URLSearchParams();
    if (orderFilter) p.set('status', orderFilter);
    if (orderQ.trim()) p.set('q', orderQ.trim());
    return getJson<{ items: Order[] }>(`/api/admin/orders?${p}`).then((j) => setOrders(j.items));
  }, [orderFilter, orderQ]);
  const loadStock = useCallback(() => getJson<{ items: StockItem[] }>('/api/admin/stock').then((j) => setStock(j.items)), []);

  useEffect(() => {
    const all = () =>
      Promise.all([loadDash(), loadNotes(), loadStock()])
        .then(() => setError(''))
        .catch((e) => e.message !== 'unauthorized' && setError('โหลดข้อมูลไม่สำเร็จ — กำลังลองใหม่'));
    all();
    const t = setInterval(all, 5000);
    return () => clearInterval(t);
  }, [loadDash, loadNotes, loadStock]);

  useEffect(() => {
    loadOrders().catch(() => {});
    const t = setInterval(() => loadOrders().catch(() => {}), 5000);
    return () => clearInterval(t);
  }, [loadOrders]);

  async function markAllRead() {
    await fetch('/api/admin/notifications', { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: '{}' });
    loadNotes();
  }

  async function saveStatus(o: Order) {
    const status = draft[o.orderNo] ?? o.status;
    setOrderMsg((m) => ({ ...m, [o.orderNo]: 'กำลังบันทึก…' }));
    const r = await fetch('/api/admin/orders', {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ orderNo: o.orderNo, status }),
    });
    const j = await r.json().catch(() => ({}));
    setOrderMsg((m) => ({ ...m, [o.orderNo]: r.ok ? `✓ บันทึกแล้ว: ${statusLabel(status)}` : `✗ ${j.error || 'ไม่สำเร็จ'}` }));
    if (r.ok) {
      setOrders((list) => list.map((x) => (x.orderNo === o.orderNo ? { ...x, status } : x)));
      setDraft((d) => {
        const n = { ...d };
        delete n[o.orderNo];
        return n;
      });
      loadDash();
    }
  }

  async function saveStock(item: StockItem) {
    const e = edit[item.sku] || {};
    const body: any = { sku: item.sku, stock: {} };
    for (const b of BRANCHES) if (e[b] !== undefined) body.stock[b] = Number(e[b]);
    if (e.rp !== undefined) body.reorderPoint = Number(e.rp);
    setStockMsg((m) => ({ ...m, [item.sku]: 'กำลังบันทึก…' }));
    const r = await fetch('/api/admin/stock', {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok) {
      setStock((list) => list.map((x) => (x.sku === item.sku ? j.item : x)));
      setEdit((d) => {
        const n = { ...d };
        delete n[item.sku];
        return n;
      });
      setStockMsg((m) => ({ ...m, [item.sku]: '✓ บันทึกแล้ว' }));
      loadDash();
    } else {
      setStockMsg((m) => ({ ...m, [item.sku]: `✗ ${j.error || 'ไม่สำเร็จ'}` }));
    }
  }

  const lowList = useMemo(
    () => stock.flatMap((s) => s.low.map((b) => ({ ...s, branch: b, qty: s.stock[b] }))),
    [stock],
  );
  const shownStock = useMemo(() => {
    const q = stockQ.trim().toLowerCase();
    return stock.filter(
      (s) => (!onlyLow || s.low.length) && (!q || s.sku.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)),
    );
  }, [stock, stockQ, onlyLow]);
  const pending = dash ? dash.statusCount.received + dash.statusCount.preparing + dash.statusCount.shipping : 0;

  return (
    <div className="adm-page">
      {error && <div className="adm-error">{error}</div>}

      {/* ---------- ตัวเลขสรุป ---------- */}
      <section className="adm-stats">
        <div className="adm-stat accent">
          <div className="adm-stat-label">ยอดขายวันนี้</div>
          <div className="adm-stat-value" data-testid="admin-sales-today">
            ฿{baht(dash?.today.total ?? 0)}
          </div>
          <div className="adm-stat-sub">{dash?.today.orders ?? 0} คำสั่งซื้อ</div>
        </div>
        <div className="adm-stat">
          <div className="adm-stat-label">ยอดขาย 7 วัน</div>
          <div className="adm-stat-value" data-testid="admin-sales-week">
            ฿{baht(dash?.week.total ?? 0)}
          </div>
          <div className="adm-stat-sub">{dash?.week.orders ?? 0} คำสั่งซื้อ</div>
        </div>
        <div className="adm-stat">
          <div className="adm-stat-label">รอดำเนินการ</div>
          <div className="adm-stat-value">{pending}</div>
          <div className="adm-stat-sub">
            รับแล้ว {dash?.statusCount.received ?? 0} · เตรียม {dash?.statusCount.preparing ?? 0} · ส่ง{' '}
            {dash?.statusCount.shipping ?? 0}
          </div>
        </div>
        <div className={`adm-stat ${dash?.lowStockCount ? 'warn' : ''}`}>
          <div className="adm-stat-label">สต็อกต่ำกว่าจุดสั่งซื้อ</div>
          <div className="adm-stat-value">{dash?.lowStockCount ?? 0}</div>
          <div className="adm-stat-sub">รายการ × สาขา</div>
        </div>
        <div className={`adm-stat ${dash?.dlq ? 'danger' : ''}`}>
          <div className="adm-stat-label">ข้อความแชทล้มเหลว (chat.dlq)</div>
          <div className="adm-stat-value" data-testid="admin-dlq-count">
            {dash ? (dash.dlq ?? '–') : '…'}
          </div>
          <div className="adm-stat-sub">
            <a href="http://localhost:15672/#/queues" target="_blank" rel="noreferrer">
              เปิด RabbitMQ UI ↗
            </a>
          </div>
        </div>
      </section>

      {/* ---------- กราฟ ---------- */}
      <section className="adm-grid-2">
        <div className="card">
          <div className="adm-card-head">
            <h2>ยอดขาย 7 วันล่าสุด</h2>
            <span className="muted">บาท (รวม VAT)</span>
          </div>
          {dash ? <SalesChart days={dash.week.days} /> : <p className="muted">กำลังโหลด…</p>}
        </div>
        <div className="card">
          <div className="adm-card-head">
            <h2>5 สินค้าขายดี</h2>
            <span className="muted">7 วันล่าสุด · ตามจำนวน</span>
          </div>
          {dash ? <TopProducts top={dash.top} /> : <p className="muted">กำลังโหลด…</p>}
        </div>
      </section>

      {/* ---------- แจ้งเตือน + สต็อกต่ำ ---------- */}
      <section className="adm-grid-2">
        <div className="card">
          <div className="adm-card-head">
            <h2>
              🔔 แจ้งเตือน {unread > 0 && <span className="adm-pill">{unread} ใหม่</span>}
            </h2>
            <button type="button" className="adm-link-btn" onClick={markAllRead} disabled={!unread}>
              อ่านทั้งหมดแล้ว
            </button>
          </div>
          <ul className="adm-notes" data-testid="admin-notifications">
            {notes.length === 0 && <li className="muted adm-empty">ยังไม่มีแจ้งเตือน — จะขึ้นเมื่อมีคำสั่งซื้อใหม่ (คิว order.events)</li>}
            {notes.map((n) => (
              <li key={n.id} data-testid="admin-notification" data-kind={n.kind} className={n.read ? 'read' : ''}>
                <span className="adm-note-icon" aria-hidden>
                  {n.kind === 'order' ? '🧾' : '⚠️'}
                </span>
                <div>
                  <div className="adm-note-msg">{n.message}</div>
                  <div className="muted adm-note-time">
                    {n.kind === 'order' ? 'คำสั่งซื้อใหม่' : 'สต็อกต่ำ'} · {thTime(n.createdAt)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <div className="adm-card-head">
            <h2>⚠️ สินค้าต่ำกว่าจุดสั่งซื้อซ้ำ</h2>
            <span className="muted">{lowList.length} รายการ</span>
          </div>
          <ul className="adm-low" data-testid="admin-low-stock">
            {lowList.length === 0 && <li className="muted adm-empty">สต็อกทุกสาขาเพียงพอ 👍</li>}
            {lowList.map((l) => (
              <li key={`${l.sku}-${l.branch}`} data-sku={l.sku} data-branch={l.branch}>
                <div>
                  <b>{l.name}</b>
                  <div className="muted">
                    {l.sku} · สาขา{BRANCH_NAME[l.branch]} ({l.branch})
                  </div>
                </div>
                <div className="adm-low-qty">
                  <span className={l.qty === 0 ? 'zero' : ''}>
                    {l.qty.toLocaleString()} {l.unit}
                  </span>
                  <small className="muted">จุดสั่งซื้อ {l.reorderPoint.toLocaleString()}</small>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* ---------- คำสั่งซื้อ ---------- */}
      <section className="card" id="orders">
        <div className="adm-card-head">
          <h2>🧾 คำสั่งซื้อ</h2>
          <div className="adm-tools">
            <input className="input" placeholder="ค้นเลขที่ / ชื่อ / เบอร์" value={orderQ} onChange={(e) => setOrderQ(e.target.value)} />
            <select className="select" value={orderFilter} onChange={(e) => setOrderFilter(e.target.value)}>
              <option value="">ทุกสถานะ</option>
              {STATUS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>เลขที่ / เวลา</th>
                <th>ลูกค้า</th>
                <th>สินค้า</th>
                <th>สาขา / วันส่ง</th>
                <th className="num">ยอดสุทธิ</th>
                <th>สถานะ</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted adm-empty">
                    ยังไม่มีคำสั่งซื้อ
                  </td>
                </tr>
              )}
              {orders.map((o) => {
                const value = draft[o.orderNo] ?? o.status;
                return (
                  <tr key={o.orderNo} data-testid="admin-order-row" data-order={o.orderNo}>
                    <td>
                      <b className="mono">{o.orderNo}</b>
                      <div className="muted small">{thTime(o.createdAt)}</div>
                    </td>
                    <td>
                      {o.customerName}
                      <div className="muted small">{o.phone}</div>
                    </td>
                    <td className="small">
                      {o.items.slice(0, 3).map((i) => (
                        <div key={i.sku}>
                          {i.sku} × {i.qty}
                        </div>
                      ))}
                      {o.items.length > 3 && <div className="muted">+ อีก {o.items.length - 3} รายการ</div>}
                    </td>
                    <td className="small">
                      {BRANCH_NAME[o.branch] ?? o.branch}
                      <div className="muted">
                        {o.deliveryDate ?? '-'} {o.slot === 'morning' ? 'เช้า' : o.slot === 'afternoon' ? 'บ่าย' : ''}
                      </div>
                    </td>
                    <td className="num">฿{baht(o.total)}</td>
                    <td>
                      <div className="adm-status">
                        <span className={`adm-st st-${o.status}`}>{statusLabel(o.status)}</span>
                        <select
                          className="select"
                          data-testid="admin-status-select"
                          aria-label={`สถานะของ ${o.orderNo}`}
                          value={value}
                          onChange={(e) => setDraft((d) => ({ ...d, [o.orderNo]: e.target.value }))}
                        >
                          {STATUS.map((s) => (
                            <option key={s.value} value={s.value}>
                              {s.label}
                            </option>
                          ))}
                        </select>
                        <button
                          type="button"
                          className="btn"
                          data-testid="admin-status-save"
                          disabled={value === o.status}
                          onClick={() => saveStatus(o)}
                        >
                          บันทึก
                        </button>
                      </div>
                      {orderMsg[o.orderNo] && <div className="small adm-msg">{orderMsg[o.orderNo]}</div>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* ---------- สต็อก ---------- */}
      <section className="card" id="stock">
        <div className="adm-card-head">
          <h2>📦 สต็อกสินค้า (แก้ไขได้)</h2>
          <div className="adm-tools">
            <input className="input" placeholder="ค้น SKU / ชื่อสินค้า" value={stockQ} onChange={(e) => setStockQ(e.target.value)} />
            <label className="adm-check">
              <input type="checkbox" checked={onlyLow} onChange={(e) => setOnlyLow(e.target.checked)} /> เฉพาะสต็อกต่ำ
            </label>
          </div>
        </div>
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>SKU / สินค้า</th>
                {BRANCHES.map((b) => (
                  <th key={b} className="num">
                    {BRANCH_NAME[b]}
                  </th>
                ))}
                <th className="num">จุดสั่งซื้อซ้ำ</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {shownStock.map((s) => {
                const e = edit[s.sku] || {};
                const dirty = Object.keys(e).length > 0;
                const set = (k: Branch | 'rp', v: string) => setEdit((d) => ({ ...d, [s.sku]: { ...d[s.sku], [k]: v } }));
                return (
                  <tr key={s.sku} data-testid="admin-stock-row" data-sku={s.sku} className={s.low.length ? 'low' : ''}>
                    <td>
                      <b className="mono">{s.sku}</b>
                      <div className="small">{s.name}</div>
                    </td>
                    {BRANCHES.map((b) => (
                      <td key={b} className="num">
                        <input
                          className={`input adm-qty ${s.low.includes(b) ? 'is-low' : ''}`}
                          type="number"
                          min={0}
                          data-testid="admin-stock-qty"
                          data-branch={b}
                          aria-label={`${s.sku} สาขา${BRANCH_NAME[b]}`}
                          value={e[b] ?? String(s.stock[b])}
                          onChange={(ev) => set(b, ev.target.value)}
                        />
                      </td>
                    ))}
                    <td className="num">
                      <input
                        className="input adm-qty"
                        type="number"
                        min={0}
                        data-testid="admin-stock-reorder"
                        aria-label={`${s.sku} จุดสั่งซื้อซ้ำ`}
                        value={e.rp ?? String(s.reorderPoint)}
                        onChange={(ev) => set('rp', ev.target.value)}
                      />
                    </td>
                    <td>
                      <button type="button" className="btn secondary" data-testid="admin-stock-save" disabled={!dirty}
                        onClick={() => saveStock(s)}>
                        บันทึก
                      </button>
                      {stockMsg[s.sku] && <div className="small adm-msg">{stockMsg[s.sku]}</div>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
