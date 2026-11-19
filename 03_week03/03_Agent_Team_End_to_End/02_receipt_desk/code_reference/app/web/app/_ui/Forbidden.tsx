import Link from 'next/link';
import { homeFor } from './roles';
import type { PageUser } from './roles';

/** บทบาทนี้เปิดหน้านี้ไม่ได้ (DESIGN 9.1 ช่อง "—") — ไม่โหลดข้อมูลของหน้านั้นเลย */
export default function Forbidden({ user, page }: { user: PageUser; page: string }) {
  return (
    <main className="page">
      <div className="notice error" data-testid="page-forbidden" role="alert">
        บัญชี{user.roleLabel}ไม่มีสิทธิ์เปิดหน้า{page}
      </div>
      <p>
        <Link href={homeFor(user.role)}>กลับหน้าแรกของบัญชีนี้</Link>
      </p>
    </main>
  );
}
