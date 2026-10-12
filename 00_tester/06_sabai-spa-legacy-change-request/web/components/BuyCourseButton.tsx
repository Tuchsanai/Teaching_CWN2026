"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

/** FR-13 ซื้อคอร์สกระชับสัดส่วน 10 แถม 1 */
export function BuyCourseButton() {
  const { t } = useI18n();
  const router = useRouter();
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  return (
    <div>
      <button
        type="button"
        className="btn btn-gold"
        disabled={busy}
        data-testid="buy-course"
        onClick={async () => {
          setBusy(true);
          const r = await fetch("/api/courses", { method: "POST" });
          const j = await r.json();
          setBusy(false);
          setMsg({ ok: r.status === 201, text: j.message });
          if (r.status === 201) router.refresh();
        }}
      >
        {t("wallet.buy")}
      </button>
      {msg && (
        <p className={`alert ${msg.ok ? "alert-ok" : "alert-error"}`} role="status" data-testid="buy-course-result">
          {msg.text}
        </p>
      )}
    </div>
  );
}
