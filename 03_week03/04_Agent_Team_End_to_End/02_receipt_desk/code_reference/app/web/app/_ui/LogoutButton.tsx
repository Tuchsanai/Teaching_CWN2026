'use client';
import { useState } from 'react';

/** ปุ่มออกจากระบบ (W4) → กลับไป /login */
export default function LogoutButton() {
  const [busy, setBusy] = useState(false);
  async function onClick() {
    setBusy(true);
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
    } finally {
      window.location.href = '/login';
    }
  }
  return (
    <button type="button" className="secondary" data-testid="logout-button" onClick={onClick} disabled={busy}>
      ออกจากระบบ
    </button>
  );
}
