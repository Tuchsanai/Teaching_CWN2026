"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

export function LoginForm({ next, testAccounts }: { next: string; testAccounts: { email: string; password: string; note: string }[] }) {
  const { t } = useI18n();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    const r = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    const j = await r.json();
    setBusy(false);
    if (!r.ok) {
      setErr(j.message);
      return;
    }
    router.push(j.user.role === "owner" && next === "/account" ? "/admin" : next);
    router.refresh();
  };

  return (
    <>
      <form className="card" onSubmit={submit} style={{ maxWidth: 480 }}>
        <div className="field">
          <label htmlFor="email">{t("login.email")}</label>
          <input id="email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} required data-testid="login-email" />
        </div>
        <div className="field">
          <label htmlFor="password">{t("login.password")}</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required data-testid="login-password" />
        </div>
        {err && (
          <div className="alert alert-error" role="alert" data-testid="login-error">
            {err}
          </div>
        )}
        <button type="submit" className="btn" disabled={busy} data-testid="login-submit">
          {t("login.submit")}
        </button>
      </form>
      {testAccounts.length > 0 && (
        <details className="card small" style={{ maxWidth: 480 }}>
          <summary>Test accounts</summary>
          <ul data-testid="test-accounts">
            {testAccounts.map((a) => (
              <li key={a.email}>
                <code>{a.email}</code> / <code>{a.password}</code> — {a.note}
              </li>
            ))}
          </ul>
        </details>
      )}
    </>
  );
}
