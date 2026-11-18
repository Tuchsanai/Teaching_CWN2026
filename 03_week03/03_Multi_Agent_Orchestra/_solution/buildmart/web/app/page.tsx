// หน้าแรก (v3) — hero 3D (Three.js) · หมวดสินค้าพร้อมภาพ · จุดเด่นร้าน · แนะนำน้องช่าง AI
import Link from 'next/link';
import CatImage from '@/components/CatImage';
import Hero3D from '@/components/Hero3D';
import OpenChatButton from '@/components/OpenChatButton';
import { CATEGORIES } from '@/lib/categories';

const FEATURES = [
  { ico: '🏷️', t: 'ยิ่งซื้อเยอะ ยิ่งถูก', d: '50 ชิ้นขึ้นไปลด 5% · 200 ชิ้นขึ้นไปลด 10% คิดแยกต่อรายการอัตโนมัติ' },
  { ico: '🚚', t: 'ส่งถึงหน้างาน', d: 'เลือกรถให้ตามน้ำหนัก กระบะ · 6 ล้อ · 10 ล้อ ส่งฟรีเมื่อยอดถึง 20,000 บาท' },
  { ico: '🏬', t: '3 สาขา สต็อกเรียลไทม์', d: 'ลาดกระบัง · บางนา · รังสิต ดูของคงเหลือแต่ละสาขาก่อนสั่ง' },
  { ico: '🧮', t: 'คำนวณวัสดุให้', d: 'คอนกรีต ผนัง กระเบื้อง สี เหล็กเส้น — ได้จำนวนแล้วใส่ตะกร้าได้ทันที' },
];

export default function HomePage() {
  return (
    <>
      <section className="hero3d" aria-label="บ้านช่าง BuildMart">
        <div className="hero3d-bg" style={{ backgroundImage: 'url(/img/hero-bg.webp), url(/img/hero-bg.png)' }} aria-hidden />
        <Hero3D />
        <div className="hero3d-shade" aria-hidden />
        <div className="hero3d-inner">
          <div className="hero3d-copy">
            <span className="eyebrow">
              <i>ใหม่</i> ถามน้องช่างด้วยเสียง · ตอบพร้อมอ้างอิงเอกสาร
            </span>
            <h1>
              วัสดุก่อสร้างครบ
              <br />
              <span className="glow">จบที่บ้านช่าง</span>
            </h1>
            <p className="lead">
              ปูน เหล็ก อิฐ กระเบื้อง สี ประปา ไฟฟ้า — ซื้อเยอะยิ่งถูก (50 ชิ้นขึ้นไปลด 5% · 200 ชิ้นขึ้นไปลด 10%) ส่งจาก 3 สาขา
              ลาดกระบัง · บางนา · รังสิต
            </p>
            <div className="actions">
              <Link href="/products" className="btn">
                ดูสินค้าทั้งหมด →
              </Link>
              <Link href="/calculator" className="btn secondary">
                🧮 คำนวณวัสดุ
              </Link>
              <OpenChatButton className="btn secondary" voice>
                🎙 คุยกับน้องช่าง
              </OpenChatButton>
            </div>
            <div className="hero-stats">
              <div className="hero-stat">
                <b>11</b>
                <span>หมวดวัสดุ</span>
              </div>
              <div className="hero-stat">
                <b>3</b>
                <span>สาขาพร้อมส่ง</span>
              </div>
              <div className="hero-stat">
                <b>−10%</b>
                <span>ราคาส่งสูงสุด</span>
              </div>
              <div className="hero-stat">
                <b>24 ชม.</b>
                <span>ผู้ช่วย AI</span>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-scroll" aria-hidden>
          SCROLL
        </div>
      </section>

      <h2 className="section-title reveal">หมวดสินค้า</h2>
      <p className="section-sub reveal">เลือกหมวดเพื่อดูสินค้า ราคาส่ง และสต็อกแต่ละสาขา</p>
      <div className="cat-grid reveal">
        {CATEGORIES.map((c) => (
          <Link
            key={c.name}
            href={`/products?category=${encodeURIComponent(c.name)}`}
            className="cat-tile tilt"
            data-testid="category-tile"
            data-category={c.name}
          >
            <CatImage category={c.name} className="cat-img" fallbackClassName="cat-fallback" />
            <span className="icon" aria-hidden>
              {c.icon}
            </span>
            <span className="label">{c.name}</span>
            <span className="go">ดูสินค้า →</span>
          </Link>
        ))}
      </div>

      <h2 className="section-title reveal">ทำไมช่างเลือกบ้านช่าง</h2>
      <div className="feature-grid reveal">
        {FEATURES.map((f) => (
          <div key={f.t} className="feature tilt">
            <div className="ico" aria-hidden>
              {f.ico}
            </div>
            <h3>{f.t}</h3>
            <p>{f.d}</p>
          </div>
        ))}
      </div>

      <section className="ai-band reveal" aria-label="น้องช่าง ผู้ช่วย AI">
        <div className="ai-band-copy">
          <span className="eyebrow">
            <i>AI</i> น้องช่าง · ผู้ช่วยหน้าร้าน
          </span>
          <h2>ถามด้วยเสียงได้เลย น้องช่างฟัง คิด แล้วตอบเป็นเสียง</h2>
          <p>
            ถามราคา สต็อก 3 สาขา วิธีใช้งานจากเอกสารสเปก ให้คำนวณวัสดุ ใส่ตะกร้า หรือออกใบเสนอราคา — ทุกคำตอบจากเอกสารมีป้ายอ้างอิงหน้า
            PDF ให้กดเปิดดูได้
          </p>
          <div className="ai-chips">
            <span className="ai-chip">🎙 พูดถามได้ (Whisper)</span>
            <span className="ai-chip">🔊 ตอบเป็นเสียง</span>
            <span className="ai-chip">📄 อ้างอิงเอกสาร (RAG + rerank)</span>
            <span className="ai-chip">🛒 ใส่ตะกร้าให้</span>
          </div>
          <div>
            <OpenChatButton voice>💬 เริ่มคุยกับน้องช่าง</OpenChatButton>
          </div>
        </div>
        <div className="ai-band-visual" aria-hidden>
          <span className="ring" />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/img/mascot.webp" alt="" loading="lazy" />
        </div>
      </section>
    </>
  );
}
