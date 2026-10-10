"use client";

import { useRouter } from "next/navigation";
import { LANG_COOKIE, type Lang } from "@/lib/i18n.ts";
import { useI18n } from "./I18nProvider.tsx";

const LABELS: Record<Lang, string> = { th: "ไทย", en: "English", zh: "中文" };
// หน้า 中文 ต้องไม่มีอักษรไทย (NFR-06) ปุ่มภาษาไทยจึงแสดงชื่อเป็นภาษาจีน
const labelFor = (l: Lang, current: Lang) => (l === "th" && current === "zh" ? "泰语" : LABELS[l]);

/** FR-24 ปุ่มเลือกภาษาอยู่ทุกหน้า จำด้วย cookie lang */
export function LangSwitcher() {
  const { lang, t } = useI18n();
  const router = useRouter();
  const choose = (l: Lang) => {
    document.cookie = `${LANG_COOKIE}=${l}; path=/; max-age=31536000; samesite=lax`;
    document.documentElement.lang = l;
    router.refresh();
  };
  return (
    <div className="lang-switch" role="group" aria-label={t("lang.label")} data-testid="lang-switcher">
      {(Object.keys(LABELS) as Lang[]).map((l) => (
        <button
          key={l}
          type="button"
          lang={l}
          className={l === lang ? "active" : ""}
          aria-pressed={l === lang}
          onClick={() => choose(l)}
          data-testid={`lang-${l}`}
        >
          {labelFor(l, lang)}
        </button>
      ))}
    </div>
  );
}
