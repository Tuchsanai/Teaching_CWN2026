'use client';
// แถบเมนูหลังร้าน: ภาพรวม · คำสั่งซื้อ · สต็อก · เอกสาร RAG · RabbitMQ UI · ออกจากระบบ
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function AdminNav() {
  const path = usePathname();
  const onDocs = path?.startsWith('/admin/docs');

  async function logout() {
    await fetch('/api/admin/login', { method: 'DELETE' }).catch(() => {});
    window.location.href = '/admin';
  }

  return (
    <div className="adm-nav">
      <div className="adm-nav-title">
        <span className="adm-badge-brand">หลังร้าน</span>
        <b>{onDocs ? 'เอกสาร RAG' : 'ภาพรวมร้าน'}</b>
      </div>
      <nav>
        <Link href="/admin" className={!onDocs ? 'active' : ''}>
          📊 ภาพรวม
        </Link>
        {!onDocs && (
          <>
            <a href="#orders">🧾 คำสั่งซื้อ</a>
            <a href="#stock">📦 สต็อก</a>
          </>
        )}
        <Link href="/admin/docs" className={onDocs ? 'active' : ''}>
          📄 เอกสาร RAG
        </Link>
        <a href="http://localhost:15672" target="_blank" rel="noreferrer" title="guest / guest (ใช้ในเครื่องเท่านั้น)">
          🐇 RabbitMQ UI ↗
        </a>
        <button type="button" className="adm-link-btn" onClick={logout}>
          ออกจากระบบ
        </button>
      </nav>
    </div>
  );
}
