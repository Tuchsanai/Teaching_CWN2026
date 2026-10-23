'use client';
// components/CalcApp.tsx (B1) — เครื่องคำนวณวัสดุ 5 แท็บ (POST /api/calc/[type] → shared/calc.js) + "เพิ่มทั้งหมดลงตะกร้า"
import Link from 'next/link';
import { useState } from 'react';
import { formatBaht } from '@/shared/pricing.js';
import { addToCart, notifyCart } from './ProductCart';

type CalcType = 'concrete' | 'wall' | 'tile' | 'paint' | 'rebar';
type Row = { sku: string; qty: number; unit: string; label: string; name?: string; unitPrice?: number; lineTotal?: number };
type Result = { type: CalcType; rows: Row[]; bars?: number; weightKg?: number; estimate?: number; extra?: any };

const TABS: { id: CalcType; icon: string; title: string; hint: string }[] = [
  { id: 'concrete', icon: '🏗️', title: 'คอนกรีต', hint: 'ส่วนผสม 1:2:4 · ปูน 7 ถุง ทราย 0.5 ลบ.ม. หิน 0.9 ลบ.ม. ต่อคอนกรีต 1 ลบ.ม.' },
  { id: 'wall', icon: '🧱', title: 'ก่อผนัง', hint: 'อิฐมอญ 140 ก้อน + ปูนก่อ 0.25 ถุง /ตร.ม. · อิฐมวลเบา 8.33 ก้อน + ปูนก่อ 0.12 ถุง /ตร.ม.' },
  { id: 'tile', icon: '🔲', title: 'ปูกระเบื้อง', hint: 'เผื่อเศษ 10% · กล่องละ 1.44 ตร.ม. · ปูนกาว 1 ถุง/4 ตร.ม. · ยาแนว 1 ถุง/5 ตร.ม.' },
  { id: 'paint', icon: '🎨', title: 'ทาสี', hint: 'สี 1 แกลลอนทาได้ 30 ตร.ม./เที่ยว · รองพื้น 1 แกลลอน/40 ตร.ม.' },
  { id: 'rebar', icon: '🔩', title: 'เหล็กเส้น', hint: 'เหล็กยาวเส้นละ 10 ม. · น้ำหนัก RB6 0.222 · RB9 0.499 · DB12 0.888 · DB16 1.578 กก./ม.' },
];

const REBAR_SIZES = ['RB6', 'RB9', 'DB12', 'DB16'];

export default function CalcApp({ initialTab = 'concrete' }: { initialTab?: CalcType }) {
  const [tab, setTab] = useState<CalcType>(initialTab);
  const [volume, setVolume] = useState('');
  const [wallArea, setWallArea] = useState('');
  const [wallType, setWallType] = useState('brick');
  const [tileArea, setTileArea] = useState('');
  const [paintArea, setPaintArea] = useState('');
  const [coats, setCoats] = useState('2');
  const [paintType, setPaintType] = useState('interior');
  const [rebarSize, setRebarSize] = useState('DB12');
  const [length, setLength] = useState('');

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const [adding, setAdding] = useState(false);
  const [addMsg, setAddMsg] = useState<{ ok: boolean; text: string } | null>(null);

  function inputFor(t: CalcType): { body: Record<string, unknown>; value: string } {
    switch (t) {
      case 'concrete':
        return { body: { volume: Number(volume) }, value: volume };
      case 'wall':
        return { body: { area: Number(wallArea), wallType }, value: wallArea };
      case 'tile':
        return { body: { area: Number(tileArea) }, value: tileArea };
      case 'paint':
        return { body: { area: Number(paintArea), coats: Number(coats) || 2, paintType }, value: paintArea };
      case 'rebar':
        return { body: { size: rebarSize, length: Number(length) }, value: length };
    }
  }

  function switchTab(t: CalcType) {
    setTab(t);
    setResult(null);
    setError('');
    setAddMsg(null);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const { body, value } = inputFor(tab);
    if (!(Number(value) > 0)) {
      setError('กรุณากรอกตัวเลขที่มากกว่า 0');
      setResult(null);
      return;
    }
    setBusy(true);
    setError('');
    setAddMsg(null);
    try {
      const r = await fetch(`/api/calc/${tab}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j?.error || 'คำนวณไม่สำเร็จ');
      setResult(j);
    } catch (err: any) {
      setError(err?.message || 'คำนวณไม่สำเร็จ');
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  async function onAddAll() {
    if (!result) return;
    const rows = result.rows.filter((r) => r.qty > 0);
    setAdding(true);
    setAddMsg(null);
    let count: number | undefined;
    try {
      for (const r of rows) ({ count } = await addToCart(r.sku, r.qty));
      notifyCart(count);
      setAddMsg({ ok: true, text: `เพิ่ม ${rows.length} รายการลงตะกร้าแล้ว` });
    } catch (err: any) {
      notifyCart();
      setAddMsg({ ok: false, text: err?.message || 'เพิ่มลงตะกร้าไม่สำเร็จ' });
    } finally {
      setAdding(false);
    }
  }

  const meta = TABS.find((t) => t.id === tab)!;

  return (
    <div className="calc">
      <div className="calc-tabs" role="tablist" aria-label="ประเภทงาน">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className={`calc-tab${tab === t.id ? ' active' : ''}`}
            data-testid={`calc-tab-${t.id}`}
            onClick={() => switchTab(t.id)}
          >
            <span aria-hidden>{t.icon}</span> {t.title}
          </button>
        ))}
      </div>

      <div className="calc-body">
        <form className="calc-form card" onSubmit={onSubmit}>
          <h2>
            {meta.icon} คำนวณ{meta.title}
          </h2>
          <p className="muted small">{meta.hint}</p>

          {tab === 'concrete' && (
            <Field label="ปริมาตรคอนกรีต" unit="ลบ.ม. (คิว)">
              <input className="input" data-testid="calc-input-volume" type="number" min={0} step="any" inputMode="decimal"
                placeholder="เช่น 3" value={volume} onChange={(e) => setVolume(e.target.value)} />
            </Field>
          )}

          {tab === 'wall' && (
            <>
              <Field label="ชนิดอิฐ">
                <select className="select" data-testid="calc-wall-type" value={wallType} onChange={(e) => setWallType(e.target.value)}>
                  <option value="brick">อิฐมอญ (BRK-001)</option>
                  <option value="light">อิฐมวลเบา (BRK-002)</option>
                </select>
              </Field>
              <Field label="พื้นที่ผนัง" unit="ตร.ม.">
                <input className="input" data-testid="calc-input-area" type="number" min={0} step="any" inputMode="decimal"
                  placeholder="เช่น 10" value={wallArea} onChange={(e) => setWallArea(e.target.value)} />
              </Field>
            </>
          )}

          {tab === 'tile' && (
            <Field label="พื้นที่ปูกระเบื้อง" unit="ตร.ม.">
              <input className="input" data-testid="calc-input-area" type="number" min={0} step="any" inputMode="decimal"
                placeholder="เช่น 50" value={tileArea} onChange={(e) => setTileArea(e.target.value)} />
            </Field>
          )}

          {tab === 'paint' && (
            <>
              <Field label="ชนิดสี">
                <select className="select" data-testid="calc-paint-type" value={paintType} onChange={(e) => setPaintType(e.target.value)}>
                  <option value="interior">ภายใน (PNT-002)</option>
                  <option value="exterior">ภายนอก (PNT-001)</option>
                </select>
              </Field>
              <Field label="พื้นที่ทาสี" unit="ตร.ม.">
                <input className="input" data-testid="calc-input-area" type="number" min={0} step="any" inputMode="decimal"
                  placeholder="เช่น 120" value={paintArea} onChange={(e) => setPaintArea(e.target.value)} />
              </Field>
              <Field label="จำนวนเที่ยว" unit="เที่ยว">
                <input className="input" data-testid="calc-input-coats" type="number" min={1} step={1} inputMode="numeric"
                  value={coats} onChange={(e) => setCoats(e.target.value)} />
              </Field>
            </>
          )}

          {tab === 'rebar' && (
            <>
              <Field label="ขนาดเหล็ก">
                <select className="select" data-testid="calc-rebar-size" value={rebarSize} onChange={(e) => setRebarSize(e.target.value)}>
                  {REBAR_SIZES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="ความยาวรวม" unit="เมตร">
                <input className="input" data-testid="calc-input-length" type="number" min={0} step="any" inputMode="decimal"
                  placeholder="เช่น 100" value={length} onChange={(e) => setLength(e.target.value)} />
              </Field>
            </>
          )}

          {error && <div className="calc-msg err">{error}</div>}
          <button type="submit" className="btn calc-submit" data-testid="calc-submit" disabled={busy}>
            {busy ? 'กำลังคำนวณ…' : '🧮 คำนวณ'}
          </button>
        </form>

        <section className="calc-result card" aria-live="polite">
          <h2>วัสดุที่ต้องใช้</h2>
          {!result ? (
            <div className="calc-empty muted">กรอกข้อมูลแล้วกด “คำนวณ” — ผลลัพธ์ปัดขึ้นเป็นจำนวนเต็มเสมอ</div>
          ) : (
            <>
              {result.type === 'rebar' && (
                <div className="calc-extra">
                  <div>
                    <span className="muted small">จำนวนเส้น</span>
                    <b data-testid="calc-bars">{result.bars} เส้น</b>
                  </div>
                  <div>
                    <span className="muted small">น้ำหนักรวม</span>
                    <b data-testid="calc-weight">{formatBaht(result.weightKg ?? 0)} กก.</b>
                  </div>
                </div>
              )}
              <table className="tbl calc-tbl">
                <thead>
                  <tr>
                    <th>สินค้า</th>
                    <th className="r">จำนวน</th>
                    <th className="r">ราคา/หน่วย</th>
                    <th className="r">รวม</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((r) => (
                    <tr key={r.sku} data-testid="calc-row" data-sku={r.sku} data-qty={r.qty}>
                      <td>
                        <Link href={`/products/${r.sku}`} className="calc-sku">
                          {r.sku}
                        </Link>{' '}
                        {r.name || r.label}
                      </td>
                      <td className="r">
                        <b className="calc-qty">{r.qty.toLocaleString('th-TH')}</b> {r.unit}
                      </td>
                      <td className="r">{r.unitPrice != null ? formatBaht(r.unitPrice) : '–'}</td>
                      <td className="r">{r.lineTotal != null ? formatBaht(r.lineTotal) : '–'}</td>
                    </tr>
                  ))}
                </tbody>
                {result.estimate != null && (
                  <tfoot>
                    <tr>
                      <td colSpan={3} className="r">
                        ประมาณการ (ยังไม่รวม VAT/ค่าส่ง)
                      </td>
                      <td className="r">
                        <span className="price">฿{formatBaht(result.estimate)}</span>
                      </td>
                    </tr>
                  </tfoot>
                )}
              </table>
              <button
                type="button"
                className="btn calc-add"
                data-testid="calc-add-all"
                onClick={onAddAll}
                disabled={adding || !result.rows.some((r) => r.qty > 0)}
              >
                {adding ? 'กำลังเพิ่ม…' : '🛒 เพิ่มทั้งหมดลงตะกร้า'}
              </button>
              {addMsg && (
                <div className={`calc-msg ${addMsg.ok ? 'ok' : 'err'}`} role="status">
                  {addMsg.text}
                  {addMsg.ok && (
                    <>
                      {' '}
                      · <Link href="/cart">ไปที่ตะกร้า →</Link>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function Field({ label, unit, children }: { label: string; unit?: string; children: React.ReactNode }) {
  return (
    <label className="calc-field">
      <span className="calc-label">{label}</span>
      <span className="calc-control">
        {children}
        {unit && <span className="calc-unit">{unit}</span>}
      </span>
    </label>
  );
}
