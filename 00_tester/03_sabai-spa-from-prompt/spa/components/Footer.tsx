"use client";

import Link from "next/link";
import { useApp } from "./AppProvider";
import { Icon, ThaiDivider } from "./Ornament";

export function Footer() {
  const { t } = useApp();
  return (
    <footer className="site-footer" data-testid="site-footer">
      <div className="site-footer__pattern" aria-hidden="true" />
      <div className="container site-footer__grid">
        <div className="site-footer__brand">
          <img src="/assets/brand/logo.png" alt={t("brandSub")} width={64} height={64} />
          <p className="site-footer__name">{t("brand")}</p>
          <p className="site-footer__tagline">{t("footer_tagline")}</p>
        </div>
        <div>
          <h2 className="site-footer__h">{t("footer_explore")}</h2>
          <ul className="site-footer__links">
            <li><Link href="/services">{t("nav_services")}</Link></li>
            <li><Link href="/book">{t("nav_book")}</Link></li>
            <li><Link href="/packages/bangkok-relax">{t("nav_package")}</Link></li>
            <li><Link href="/therapists">{t("nav_therapists")}</Link></li>
            <li><Link href="/rooms/couple-suite">{t("nav_rooms")}</Link></li>
            <li><Link href="/gift-cards">{t("nav_gift")}</Link></li>
          </ul>
        </div>
        <div>
          <h2 className="site-footer__h">{t("nav_helpers")}</h2>
          <ul className="site-footer__links">
            <li><Link href="/mood">{t("nav_mood")}</Link></li>
            <li><Link href="/quiz">{t("nav_quiz")}</Link></li>
            <li><Link href="/skin">{t("nav_skin")}</Link></li>
            <li><Link href="/privacy" data-testid="footer-privacy">{t("nav_privacy")}</Link></li>
          </ul>
        </div>
        <div>
          <h2 className="site-footer__h">{t("footer_visit")}</h2>
          <ul className="site-footer__contact">
            <li><Icon name="clock" size={18} /> <span data-testid="footer-hours">{t("footer_hours")}</span></li>
            <li><Icon name="phone" size={18} /> <a href="tel:021234567">{t("footer_phone")}</a></li>
            <li><Icon name="pin" size={18} /> <span>{t("footer_address")}</span></li>
            <li><Icon name="shield" size={18} /> <Link href="/privacy">{t("footer_noface")}</Link></li>
          </ul>
        </div>
      </div>
      <ThaiDivider className="site-footer__divider" />
      <p className="site-footer__copy">© {t("brandSub")} · {t("footer_rights")}</p>
    </footer>
  );
}
