"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

export interface NavItem {
  href: string;
  key: string;
  testid: string;
}

export function NavMenu({ items }: { items: NavItem[] }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const path = usePathname();
  useEffect(() => setOpen(false), [path]);
  return (
    <>
      <button
        type="button"
        className="nav-toggle"
        aria-expanded={open}
        aria-controls="main-nav"
        onClick={() => setOpen((v) => !v)}
        data-testid="nav-toggle"
      >
        <span aria-hidden="true">☰</span> {t("nav.menu")}
      </button>
      <nav id="main-nav" className={`main-nav${open ? " open" : ""}`} aria-label={t("nav.menu")}>
        {items.map((it) => (
          <Link key={it.href} href={it.href} className={path === it.href ? "active" : ""} data-testid={it.testid}>
            {t(it.key)}
          </Link>
        ))}
      </nav>
    </>
  );
}
