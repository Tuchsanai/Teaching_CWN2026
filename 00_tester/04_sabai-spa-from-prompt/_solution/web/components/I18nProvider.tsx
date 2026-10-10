"use client";

import { createContext, useContext, type ReactNode } from "react";
import { t as translate, type Lang } from "@/lib/i18n.ts";

const Ctx = createContext<Lang>("th");

export function I18nProvider({ lang, children }: { lang: Lang; children: ReactNode }) {
  return <Ctx.Provider value={lang}>{children}</Ctx.Provider>;
}

export function useI18n() {
  const lang = useContext(Ctx);
  return { lang, t: (key: string, vars?: Record<string, string | number>) => translate(lang, key, vars) };
}
