'use client';
/**
 * ฟอร์มเข้าสู่ระบบ (W3 POST /api/auth/login)
 * testid: login-email-input · login-password-input · login-submit-button · login-error
 */
import { useState } from 'react';
import type { FormEvent } from 'react';
import { api, errorText } from '../_ui/api';
import { PAGE_ROLES, homeFor } from '../_ui/roles';
import type { Role } from '../_ui/roles';

/** next ต้องเป็น path ภายในเว็บ (กัน open redirect) และบทบาทนี้เปิดได้ ไม่เช่นนั้นไปหน้าแรกของบทบาท */
function target(next: string, role: Role): string {
  if (!/^\/[^/\\]/.test(next) || next.startsWith('/login')) return homeFor(role);
  const base = '/' + (next.split(/[?#]/)[0].split('/')[1] ?? '');
  const roles = (PAGE_ROLES as Record<string, readonly Role[]>)[base];
  // path ที่ไม่อยู่ในตาราง (เช่นหน้าของบล็อกอื่น) ให้หน้านั้นตรวจสิทธิ์เอง
  if (roles && !roles.includes(role)) return homeFor(role);
  return next;
}

export default function LoginForm({ next }: { next: string }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !password) {
      setError('กรุณากรอกอีเมลและรหัสผ่าน');
      return;
    }
    setBusy(true);
    const r = await api<{ user: { role: Role } }>('/api/auth/login', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), password }),
    });
    if (!r.ok) {
      setBusy(false);
      setError(r.error.error === 'invalid_credentials' ? 'อีเมลหรือรหัสผ่านไม่ถูกต้อง' : errorText(r.error));
      return;
    }
    // โหลดหน้าใหม่ทั้งหน้าเพื่อให้ layout อ่าน session และแสดงเมนูตามบทบาท
    window.location.href = target(next, r.data.user.role);
  }

  return (
    <form className="card" onSubmit={onSubmit} noValidate>
      <label className="field">
        อีเมล
        <input
          type="email"
          name="email"
          autoComplete="username"
          data-testid="login-email-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label className="field" style={{ marginTop: 10 }}>
        รหัสผ่าน
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          data-testid="login-password-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      {error ? (
        <div className="notice error" role="alert" data-testid="login-error">
          {error}
        </div>
      ) : null}
      <div style={{ marginTop: 12 }}>
        <button type="submit" data-testid="login-submit-button" disabled={busy}>
          {busy ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'}
        </button>
      </div>
    </form>
  );
}
