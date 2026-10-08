"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, useApp } from "./AppProvider";
import { MusicToggle } from "./MusicToggle";
import { Icon } from "./Ornament";
import { LANGS, LANG_LABEL, type DictKey } from "@/lib/i18n";

const LINKS: { href: string; key: DictKey; id: string }[] = [
  { href: "/services", key: "nav_services", id: "services" },
  { href: "/packages/bangkok-relax", key: "nav_package", id: "package" },
  { href: "/therapists", key: "nav_therapists", id: "therapists" },
  { href: "/rooms/couple-suite", key: "nav_rooms", id: "rooms" },
  { href: "/gift-cards", key: "nav_gift", id: "gift" },
];
const HELPERS: { href: string; key: DictKey; id: string }[] = [
  { href: "/mood", key: "nav_mood", id: "mood" },
  { href: "/quiz", key: "nav_quiz", id: "quiz" },
  { href: "/skin", key: "nav_skin", id: "skin" },
];

export function Header() {
  const { t, lang, setLang, user, setUser } = useApp();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const overHero = pathname === "/";

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 40);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);
  useEffect(() => {
    document.body.classList.toggle("nav-open", open);
  }, [open]);

  const logout = async () => {
    await api("/api/auth/logout", { method: "POST" });
    setUser(null);
    router.push("/");
  };

  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <header className={`site-header ${overHero && !scrolled && !open ? "is-clear" : "is-solid"}`} data-testid="site-header">
      <a href="#main" className="skip-link">{t("skip")}</a>
      <div className="site-header__inner">
        <Link href="/" className="brand" data-testid="nav-home" aria-label={t("nav_home")}>
          <img src="/assets/brand/logo.png" alt={t("brandSub")} width={44} height={44} className="brand__logo" />
          <span className="brand__text">
            <span className="brand__name">{t("brand")}</span>
            <span className="brand__sub">{t("brandSub")}</span>
          </span>
        </Link>

        <nav className={`main-nav ${open ? "is-open" : ""}`} aria-label={t("nav_menu")} id="main-nav">
          <ul className="main-nav__list">
            {LINKS.map((l) => (
              <li key={l.href}>
                <Link href={l.href} className={`main-nav__link ${isActive(l.href) ? "is-active" : ""}`} data-testid={`nav-${l.id}`}>
                  {t(l.key)}
                </Link>
              </li>
            ))}
            <li className="main-nav__group">
              <span className="main-nav__group-label">{t("nav_helpers")}</span>
              <ul className="main-nav__sub">
                {HELPERS.map((l) => (
                  <li key={l.href}>
                    <Link href={l.href} className={`main-nav__link ${isActive(l.href) ? "is-active" : ""}`} data-testid={`nav-${l.id}`}>
                      {t(l.key)}
                    </Link>
                  </li>
                ))}
              </ul>
            </li>
            <li className="main-nav__account">
              {user ? (
                <>
                  <Link href="/account" className={`main-nav__link ${isActive("/account") ? "is-active" : ""}`} data-testid="nav-account">
                    <Icon name="user" size={18} /> {lang === "th" ? user.name : user.nameEn}
                  </Link>
                  <Link href="/wallet" className={`main-nav__link ${isActive("/wallet") ? "is-active" : ""}`} data-testid="nav-wallet">
                    {t("nav_wallet")}
                  </Link>
                  <button type="button" className="main-nav__link linklike" onClick={logout} data-testid="nav-logout">
                    {t("nav_logout")}
                  </button>
                </>
              ) : (
                <Link href="/login" className={`main-nav__link ${isActive("/login") ? "is-active" : ""}`} data-testid="nav-login">
                  <Icon name="user" size={18} /> {t("nav_login")}
                </Link>
              )}
            </li>
          </ul>
        </nav>

        <div className="header-tools">
          <div className="lang-switch" role="group" aria-label={t("lang_label")}>
            {LANGS.map((l) => (
              <button
                key={l}
                type="button"
                className={`lang-switch__btn ${lang === l ? "is-active" : ""}`}
                aria-pressed={lang === l}
                onClick={() => setLang(l)}
                data-testid={`lang-${l}`}
                lang={l === "zh" ? "zh-CN" : l}
              >
                {LANG_LABEL[l]}
              </button>
            ))}
          </div>
          <MusicToggle />
          <Link href="/book" className="btn btn--gold btn--sm header-book" data-testid="nav-book">
            {t("nav_book")}
          </Link>
          <button
            type="button"
            className="icon-btn nav-toggle"
            aria-expanded={open}
            aria-controls="main-nav"
            aria-label={open ? t("close") : t("nav_menu")}
            onClick={() => setOpen((o) => !o)}
            data-testid="nav-toggle"
          >
            <Icon name={open ? "close" : "menu"} />
          </button>
        </div>
      </div>
    </header>
  );
}
