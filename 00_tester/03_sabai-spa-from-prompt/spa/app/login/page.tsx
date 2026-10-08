"use client";

import Link from "next/link";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, useApp, useReady, type Member } from "@/components/AppProvider";
import { Icon, ThaiDivider } from "@/components/Ornament";
import { Loader } from "@/components/Shared";
import { errorText } from "@/lib/i18n";

const DEMO = [
  { email: "nida@sabai.test", id: "nida", label: "Gold · ฿12,400 · 124 pts" },
  { email: "ton@sabai.test", id: "ton", label: "Platinum · ฿30,000 · 250 pts" },
  { email: "new@sabai.test", id: "new", label: "Silver · ฿0 · 0 pts" },
];

export default function LoginPage() {
  return (
    <Suspense fallback={<Loader />}>
      <LoginInner />
    </Suspense>
  );
}

function LoginInner() {
  const { t, lang, setUser } = useApp();
  const router = useRouter();
  const sp = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  useReady(true);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    const r = await api<{ ok: boolean; user?: Member; error?: string }>("/api/auth/login", { method: "POST", json: { email, password } });
    setBusy(false);
    if (r.ok && r.user) {
      setUser(r.user);
      const next = sp.get("next");
      router.push(next && next.startsWith("/") && !next.startsWith("//") ? next : "/account");
    } else setError(errorText(lang, r.error ?? "LOGIN_FAILED"));
  };

  return (
    <div className="auth-wrap">
      <div className="auth-wrap__media">
        <img src="/assets/rooms/room-thai-massage.jpg" alt={t("brandSub")} />
        <div className="auth-wrap__quote">
          <p>Sabai Jai Wellness Spa</p>
          <span>{t("home_member_lead")}</span>
        </div>
      </div>
      <div className="auth-wrap__form">
        <div className="auth-card">
          <img src="/assets/brand/logo.png" alt={t("brandSub")} width={72} height={72} style={{ margin: "0 auto 8px", borderRadius: "50%" }} />
          <h1 className="center" style={{ fontSize: "2rem" }}>{t("login_title")}</h1>
          <p className="center muted">{t("login_lead")}</p>
          <ThaiDivider />
          <form className="card card--pad" onSubmit={submit} data-testid="login-form">
            <div className="field">
              <label htmlFor="email">{t("login_email")}</label>
              <input id="email" className="input" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} required data-testid="login-email" />
            </div>
            <div className="field">
              <label htmlFor="pw">{t("login_password")}</label>
              <input id="pw" className="input" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required data-testid="login-password" />
            </div>
            {error && <p className="alert alert--error" role="alert" data-testid="login-error">{error}</p>}
            <button type="submit" className="btn btn--gold btn--block btn--lg" disabled={busy} data-testid="login-submit">
              {t("login_submit")} <Icon name="arrow" />
            </button>
            <p className="center mt-1 small">
              {t("login_no_account")} <Link href="/register" data-testid="login-register-link">{t("login_register")}</Link>
            </p>
          </form>
          <div className="mt-2">
            <p className="label small">{t("login_demo")}</p>
            <div className="demo-users">
              {DEMO.map((d) => (
                <button key={d.id} type="button" className="demo-user" onClick={() => { setEmail(d.email); setPassword(""); }} data-testid={`login-demo-${d.id}`}>
                  <b>{d.email}</b>
                  <small>{d.label}</small>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
