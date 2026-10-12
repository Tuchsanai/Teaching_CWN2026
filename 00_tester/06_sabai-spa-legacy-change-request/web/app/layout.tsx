import "@fontsource/sarabun/400.css";
import "@fontsource/sarabun/600.css";
import "@fontsource/sarabun/700.css";
import "./globals.css";
import type { Metadata, Viewport } from "next";
import { cookies } from "next/headers";
import Link from "next/link";
import type { ReactNode } from "react";
import { I18nProvider } from "@/components/I18nProvider.tsx";
import { LangSwitcher } from "@/components/LangSwitcher.tsx";
import { LogoutButton } from "@/components/LogoutButton.tsx";
import { MusicToggle } from "@/components/MusicToggle.tsx";
import { NavMenu, type NavItem } from "@/components/NavMenu.tsx";
import { ReadyFlag } from "@/components/ReadyFlag.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { LANG_COOKIE, normalizeLang, SHOP_PHONE, t } from "@/lib/i18n.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "สบายใจ สปา · Sabai Jai Wellness Spa",
  description: "Contemporary Thai wellness spa · นวดไทย สมุนไพรไทย จองออนไลน์",
  icons: { icon: "/favicon.svg" },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#2f5530" };

export default async function RootLayout({ children }: { children: ReactNode }) {
  const lang = normalizeLang((await cookies()).get(LANG_COOKIE)?.value);
  const session = await getSession();
  const items: NavItem[] = [
    { href: "/", key: "nav.home", testid: "nav-home" },
    { href: "/services", key: "nav.services", testid: "nav-services" },
    { href: "/book", key: "nav.book", testid: "nav-book" },
    { href: "/package", key: "nav.package", testid: "nav-package" },
    { href: "/therapists", key: "nav.therapists", testid: "nav-therapists" },
    { href: "/giftcard", key: "nav.giftcard", testid: "nav-giftcard" },
    { href: "/transport", key: "nav.transport", testid: "nav-transport" },
    { href: "/chat", key: "nav.chat", testid: "nav-chat" },
    { href: "/quiz", key: "nav.quiz", testid: "nav-quiz" },
    { href: "/skin", key: "nav.skin", testid: "nav-skin" },
    ...(session ? [
      { href: "/account", key: "nav.account", testid: "nav-account" },
      { href: "/wallet", key: "nav.wallet", testid: "nav-wallet" },
    ] : []),
    ...(session?.role === "owner" ? [{ href: "/admin", key: "nav.admin", testid: "nav-admin" }] : []),
  ];

  return (
    <html lang={lang} data-ready="false">
      <body>
        <I18nProvider lang={lang}>
          <a className="skip-link" href="#main">
            {t(lang, "common.skip")}
          </a>
          <header className="site-header">
            <div className="header-row container">
              <Link href="/" className="brand" data-testid="brand-link">
                <Lotus size={34} className="brand-mark" />
                <span>{t(lang, "brand")}</span>
              </Link>
              <div className="header-tools">
                <MusicToggle />
                <LangSwitcher />
                {session ? (
                  <LogoutButton />
                ) : (
                  <Link href="/login" className="btn btn-ghost btn-sm" data-testid="nav-login">
                    {t(lang, "nav.login")}
                  </Link>
                )}
              </div>
            </div>
            <div className="container nav-row">
              <NavMenu items={items} />
            </div>
          </header>
          <main id="main" className="container main">
            {children}
          </main>
          <footer className="site-footer">
            <div className="container footer-row">
              <div>
                <strong>{t(lang, "brand")}</strong>
                <div>{t(lang, "footer.hours")}</div>
              </div>
              <div>
                {t(lang, "footer.phone")} <a href={`tel:${SHOP_PHONE}`} data-testid="footer-phone">{SHOP_PHONE}</a>
              </div>
            </div>
          </footer>
          <Link href="/chat" className="chat-fab" aria-label={t(lang, "nav.chat")} data-testid="chat-fab">
            <svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path d="M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H10l-4 4v-4H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z" fill="#23422a" />
              <circle cx="8.5" cy="10.5" r="1.3" fill="#f1e2bd" />
              <circle cx="12" cy="10.5" r="1.3" fill="#f1e2bd" />
              <circle cx="15.5" cy="10.5" r="1.3" fill="#f1e2bd" />
            </svg>
          </Link>
          <ReadyFlag />
        </I18nProvider>
      </body>
    </html>
  );
}
