// /admin/docs (B3) — ตารางเอกสาร PDF ของ RAG + อัปโหลด/ลบ/ทำใหม่ (ตรวจสิทธิ์ที่ ../layout.tsx)
import DocsManager from './DocsManager';

export const dynamic = 'force-dynamic';

export default function AdminDocsPage() {
  return <DocsManager />;
}
