import Link from 'next/link';

export default function ProductNotFound() {
  return (
    <div className="card" style={{ textAlign: 'center', padding: 40 }}>
      <div style={{ fontSize: 42 }}>📦</div>
      <h1>ไม่พบสินค้านี้</h1>
      <p className="muted">รหัสสินค้าอาจไม่ถูกต้อง หรือสินค้าถูกนำออกจากร้านแล้ว</p>
      <Link className="btn" href="/products">
        กลับไปดูสินค้าทั้งหมด
      </Link>
    </div>
  );
}
