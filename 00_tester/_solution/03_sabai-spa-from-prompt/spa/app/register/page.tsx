"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, useApp, useReady, type Member } from "@/components/AppProvider";
import { ThaiDivider } from "@/components/Ornament";
import { errorText } from "@/lib/i18n";

export default function RegisterPage() {
  const { t, lang, setUser } = useApp();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [month, setMonth] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  useReady(true);

  const months = Array.from({ length: 12 }, (_, i) =>
    new Intl.DateTimeFormat(lang === "th" ? "th-TH" : lang === "zh" ? "zh-CN" : "en-GB", { month: "long", timeZone: "UTC" }).format(new Date(Date.UTC(2024, i, 1))),
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    const r = await api<{ ok: boolean; user?: Member; error?: string }>("/api/auth/register", { method: "POST", json: { name, email, password, birthMonth: Number(month) } });
    setBusy(false);
    if (r.ok && r.user) {
      setUser(r.user);
      router.push("/account");
    } else setError(errorText(lang, r.error ?? "REGISTER_INVALID"));
  };

  return (
    <div className="auth-wrap">
      <div className="auth-wrap__media">
        <img src="/assets/treatments/aroma-oil.jpg" alt={t("brandSub")} />
        <div className="auth-wrap__quote"><p>{t("home_member_title")}</p><span>{t("home_member_lead")}</span></div>
      </div>
      <div className="auth-wrap__form">
        <div className="auth-card">
          <h1 className="center" style={{ fontSize: "2rem" }}>{t("register_title")}</h1>
          <ThaiDivider />
          <form className="card card--pad" onSubmit={submit} noValidate data-testid="register-form">
            <div className="field">
              <label htmlFor="r-name">{t("register_name")}</label>
              <input id="r-name" className="input" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" data-testid="register-name" />
            </div>
            <div className="field">
              <label htmlFor="r-email">{t("login_email")}</label>
              <input id="r-email" className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" data-testid="register-email" />
            </div>
            <div className="field">
              <label htmlFor="r-pw">{t("login_password")}</label>
              <input id="r-pw" className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" data-testid="register-password" />
              <span className="hint">{t("register_password_hint")}</span>
            </div>
            <div className="field">
              <label htmlFor="r-month">{t("register_birth_month")}</label>
              <select id="r-month" className="select" value={month} onChange={(e) => setMonth(e.target.value)} data-testid="register-birth-month">
                <option value="">—</option>
                {months.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>
            {error && <p className="alert alert--error" role="alert" data-testid="register-error">{error}</p>}
            <button type="submit" className="btn btn--gold btn--block btn--lg" disabled={busy} data-testid="register-submit">{t("register_submit")}</button>
            <p className="center mt-1 small">{t("register_have")} <Link href="/login">{t("nav_login")}</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
}
