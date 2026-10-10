"use client";

import Link from "next/link";
import { useApp, useReady } from "@/components/AppProvider";

export default function NotFound() {
  const { t } = useApp();
  useReady(true);
  return (
    <div className="not-found" data-testid="not-found">
      <h1>{t("not_found_title")}</h1>
      <p className="muted">{t("not_found_lead")}</p>
      <Link href="/" className="btn btn--gold">{t("go_home")}</Link>
    </div>
  );
}
