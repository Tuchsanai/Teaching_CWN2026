import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="page">
      <div className="card" data-testid="page-not-found">
        <h1>ไม่พบข้อมูล</h1>
        <p className="muted">ไม่พบหน้าหรือข้อมูลที่ต้องการ หรือบัญชีนี้ไม่มีสิทธิ์เห็นข้อมูลนี้</p>
        <Link href="/">กลับหน้าแรก</Link>
      </div>
    </main>
  );
}
