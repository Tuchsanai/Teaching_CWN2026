'use client';
// ฟอร์มเข้าสู่ระบบหลังร้าน (รหัสผ่านจาก env ADMIN_PASSWORD · ค่า dev admin1234)
import { useState } from 'react';

export default function AdminLogin() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const r = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ password }),
      });
      if (r.ok) {
        window.location.reload();
        return;
      }
      setError((await r.json().catch(() => ({}))).error || 'เข้าสู่ระบบไม่สำเร็จ');
    } catch {
      setError('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้');
    }
    setBusy(false);
  }

  return (
    <div className="adm-login">
      <form className="card" onSubmit={submit}>
        <div className="adm-login-icon" aria-hidden>
          🔐
        </div>
        <h1>หลังร้าน BuildMart</h1>
        <p className="muted">สำหรับพนักงานร้านเท่านั้น · กรอกรหัสผ่านเพื่อจัดการสต็อก คำสั่งซื้อ และเอกสาร</p>
        <label htmlFor="admin-password">รหัสผ่าน</label>
        <input
          id="admin-password"
          className="input"
          type="password"
          autoFocus
          autoComplete="current-password"
          data-testid="admin-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />
        {error && (
          <div className="adm-error" role="alert">
            {error}
          </div>
        )}
        <button className="btn" type="submit" data-testid="admin-login" disabled={busy || !password}>
          {busy ? 'กำลังตรวจสอบ…' : 'เข้าสู่ระบบ'}
        </button>
      </form>
    </div>
  );
}
