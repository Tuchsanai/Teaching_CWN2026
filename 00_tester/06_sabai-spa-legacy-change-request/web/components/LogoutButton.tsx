"use client";

import { useRouter } from "next/navigation";
import { useI18n } from "./I18nProvider.tsx";

export function LogoutButton() {
  const { t } = useI18n();
  const router = useRouter();
  return (
    <button
      type="button"
      className="btn btn-ghost btn-sm"
      data-testid="logout-button"
      onClick={async () => {
        await fetch("/api/auth/logout", { method: "POST" });
        router.push("/");
        router.refresh();
      }}
    >
      {t("nav.logout")}
    </button>
  );
}
