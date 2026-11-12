'use client';
// แถบเมนูหลังร้าน: ภาพรวม · คำสั่งซื้อ · สต็อก · เอกสาร RAG · ประเมิน RAG · Load test · RabbitMQ UI · ออกจากระบบ
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const TITLES: [string, string][] = [
  ['/admin/docs', 'เอกสาร RAG'],
  ['/admin/eval', 'ประเมิน RAG'],
  ['/admin/load', 'Load test'],
];

export default function AdminNav() {
  const path = usePathname() || '/admin';
  const sub = TITLES.find(([p]) => path.startsWith(p));
  const onHome = !sub;

  async function logout() {
    await fetch('/api/admin/login', { method: 'DELETE' }).catch(() => {});
    window.location.href = '/admin';
  }

  return (
    <div className="adm-nav">
      <div className="adm-nav-title">
        <span className="adm-badge-brand">หลังร้าน</span>
        <b>{sub ? sub[1] : 'ภาพรวมร้าน'}</b>
      </div>
      <nav>
        <Link href="/admin" className={onHome ? 'active' : ''}>
          📊 ภาพรวม
        </Link>
        {onHome && (
          <>
            <a href="#orders">🧾 คำสั่งซื้อ</a>
            <a href="#stock">📦 สต็อก</a>
          </>
        )}
        <Link href="/admin/docs" className={path.startsWith('/admin/docs') ? 'active' : ''}>
          📄 เอกสาร RAG
        </Link>
        <Link href="/admin/eval" className={path.startsWith('/admin/eval') ? 'active' : ''} data-testid="admin-nav-eval">
          🧪 ประเมิน RAG
        </Link>
        <Link href="/admin/load" className={path.startsWith('/admin/load') ? 'active' : ''} data-testid="admin-nav-load">
          ⚡ Load test
        </Link>
        <a href="http://localhost:15672" target="_blank" rel="noreferrer" title="guest / guest (ใช้ในเครื่องเท่านั้น)">
          🐇 RabbitMQ ↗
        </a>
        <button type="button" className="adm-link-btn" onClick={logout}>
          ออกจากระบบ
        </button>
      </nav>
    </div>
  );
}
