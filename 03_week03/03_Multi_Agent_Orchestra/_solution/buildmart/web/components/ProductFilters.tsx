'use client';
// components/ProductFilters.tsx (B1) — แถบกรอง/เรียงสินค้า · เปลี่ยนค่าแล้วอัปเดต URL (หน้า /products render ใหม่จาก searchParams)
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useRef, useState, useTransition } from 'react';
import { CATEGORIES } from '@/lib/categories';

export default function ProductFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const [pending, startTransition] = useTransition();
  const [q, setQ] = useState(sp.get('q') || '');
  const [min, setMin] = useState(sp.get('min') || '');
  const [max, setMax] = useState(sp.get('max') || '');
  // select/checkbox เก็บค่าในเครื่องด้วย ให้ตอบสนองทันทีระหว่างรอหน้าโหลดใหม่
  const [category, setCategory] = useState(sp.get('category') || '');
  const [sort, setSort] = useState(sp.get('sort') || '');
  const [inStock, setInStock] = useState(!!sp.get('inStock'));
  const timer = useRef<ReturnType<typeof setTimeout>>();
  // query ล่าสุดที่สั่งไป (กันเปลี่ยนหลายช่องติดกันก่อน URL อัปเดตแล้วค่าหาย)
  const latest = useRef(new URLSearchParams(sp.toString()));

  // ค้นจาก header แล้ว URL เปลี่ยน → sync ช่องในแถบกรอง
  useEffect(() => {
    latest.current = new URLSearchParams(sp.toString());
    setQ(sp.get('q') || '');
    setMin(sp.get('min') || '');
    setMax(sp.get('max') || '');
    setCategory(sp.get('category') || '');
    setSort(sp.get('sort') || '');
    setInStock(!!sp.get('inStock'));
  }, [sp]);

  function apply(patch: Record<string, string | null>) {
    const next = new URLSearchParams(latest.current.toString());
    for (const [k, v] of Object.entries(patch)) {
      if (v === null || v === '') next.delete(k);
      else next.set(k, v);
    }
    next.delete('page'); // เปลี่ยนเงื่อนไข → กลับหน้า 1
    latest.current = next;
    const qs = next.toString();
    startTransition(() => router.push(qs ? `${pathname}?${qs}` : pathname, { scroll: false }));
  }

  function applyPriceLater(nextMin: string, nextMax: string) {
    clearTimeout(timer.current);
    timer.current = setTimeout(() => apply({ min: nextMin, max: nextMax }), 600);
  }

  const hasFilter = ['q', 'category', 'min', 'max', 'inStock', 'sort'].some((k) => sp.get(k));

  return (
    <form
      className={`pf-bar card${pending ? ' is-pending' : ''}`}
      onSubmit={(e) => {
        e.preventDefault();
        clearTimeout(timer.current);
        apply({ q: q.trim(), min, max });
      }}
    >
      <label className="pf-field pf-q">
        <span>คำค้น</span>
        <input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="ชื่อสินค้า หรือ SKU" />
      </label>
      <label className="pf-field">
        <span>หมวด</span>
        <select
          className="select"
          data-testid="filter-category"
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            apply({ category: e.target.value });
          }}
        >
          <option value="">ทุกหมวด</option>
          {CATEGORIES.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
      </label>
      <div className="pf-field">
        <span>ช่วงราคา (บาท)</span>
        <div className="pf-range">
          <input
            className="input"
            type="number"
            min={0}
            inputMode="decimal"
            data-testid="filter-min"
            placeholder="ต่ำสุด"
            value={min}
            onChange={(e) => {
              setMin(e.target.value);
              applyPriceLater(e.target.value, max);
            }}
          />
          <span className="muted">–</span>
          <input
            className="input"
            type="number"
            min={0}
            inputMode="decimal"
            data-testid="filter-max"
            placeholder="สูงสุด"
            value={max}
            onChange={(e) => {
              setMax(e.target.value);
              applyPriceLater(min, e.target.value);
            }}
          />
        </div>
      </div>
      <label className="pf-check">
        <input
          type="checkbox"
          data-testid="filter-instock"
          checked={inStock}
          onChange={(e) => {
            setInStock(e.target.checked);
            apply({ inStock: e.target.checked ? '1' : null });
          }}
        />
        <span>เฉพาะที่มีของ</span>
      </label>
      <label className="pf-field">
        <span>เรียงตาม</span>
        <select
          className="select"
          data-testid="sort-select"
          value={sort}
          onChange={(e) => {
            setSort(e.target.value);
            apply({ sort: e.target.value });
          }}
        >
          <option value="">แนะนำ (รหัสสินค้า)</option>
          <option value="price_asc">ราคา ต่ำ → สูง</option>
          <option value="price_desc">ราคา สูง → ต่ำ</option>
        </select>
      </label>
      <div className="pf-actions">
        <button type="submit" className="btn">
          ใช้ตัวกรอง
        </button>
        {hasFilter && (
          <button
            type="button"
            className="btn secondary"
            onClick={() => {
              latest.current = new URLSearchParams();
              startTransition(() => router.push(pathname, { scroll: false }));
            }}
          >
            ล้าง
          </button>
        )}
      </div>
    </form>
  );
}
