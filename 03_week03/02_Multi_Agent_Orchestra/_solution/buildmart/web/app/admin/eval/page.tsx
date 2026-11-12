// /admin/eval (v3) — แดชบอร์ดผลประเมิน RAG (ตรวจสิทธิ์ที่ admin/layout.tsx)
import EvalDashboard from './EvalDashboard';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'ประเมิน RAG — หลังร้าน BuildMart' };

export default function EvalPage() {
  return <EvalDashboard />;
}
