'use client';
// components/Header.tsx (A) — โลโก้ · ช่องค้นหา · เมนู · ตัวเลขตะกร้า
// อัปเดตตัวเลขตะกร้าจากที่ไหนก็ได้: window.dispatchEvent(new CustomEvent('bm:cart', { detail: { count } }))
// (ไม่ส่ง detail → header ดึง /api/cart/count ใหม่เอง)
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Header() {
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    let alive = true;
    const refresh = () =>
      fetch('/api/cart/count', { cache: 'no-store' })
        .then((r) => r.json())
        .then((j) => alive && setCount(Number(j.count) || 0))
        .catch(() => {});
    const onCart = (e: Event) => {
      const c = (e as CustomEvent).detail?.count;
      if (typeof c === 'number') setCount(c);
      else refresh();
    };
    refresh();
    window.addEventListener('bm:cart', onCart);
    window.addEventListener('focus', refresh);
    return () => {
      alive = false;
      window.removeEventListener('bm:cart', onCart);
      window.removeEventListener('focus', refresh);
    };
  }, []);

  return (
    <header className="site-header">
      <div className="container bar">
        <Link href="/" className="logo" aria-label="บ้านช่าง BuildMart หน้าแรก">
          <span className="mark" aria-hidden>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M3 11 12 4l9 7v9H3z" fill="#fff" />
              <rect x="9" y="13" width="6" height="7" fill="#F26B1D" />
            </svg>
          </span>
          <span className="name">
            บ้านช่าง <b>BuildMart</b>
          </span>
        </Link>
        <form className="search" action="/products" method="get" role="search">
          <input name="q" data-testid="search-input" placeholder="ค้นหาสินค้า เช่น ปูน, DB12, สี" aria-label="ค้นหาสินค้า" />
          <button type="submit" data-testid="search-btn">
            ค้นหา
          </button>
        </form>
        <nav className="nav" aria-label="เมนูหลัก">
          <Link href="/products">สินค้า</Link>
          <Link href="/calculator">คำนวณวัสดุ</Link>
          <Link href="/cart" className="cart">
            🛒 ตะกร้า
            <span className="cart-badge" data-testid="nav-cart-count">
              {count}
            </span>
          </Link>
          <Link href="/track">ติดตามคำสั่งซื้อ</Link>
          <Link href="/admin">หลังร้าน</Link>
        </nav>
      </div>
    </header>
  );
}
