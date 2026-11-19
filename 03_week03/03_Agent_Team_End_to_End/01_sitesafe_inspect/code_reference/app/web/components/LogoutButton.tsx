'use client';

import { useState } from 'react';

export default function LogoutButton() {
  const [busy, setBusy] = useState(false);
  async function logout() {
    setBusy(true);
    try {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
    } catch {
      /* the cookie is cleared by the server; go to the login page either way */
    }
    window.location.assign('/login');
  }
  return (
    <button type="button" className="secondary" data-testid="nav-logout" onClick={logout} disabled={busy}>
      ออกจากระบบ
    </button>
  );
}
