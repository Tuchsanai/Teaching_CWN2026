"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { isLang, translate, type DictKey, type Lang } from "@/lib/i18n";

export type Member = {
  id: number;
  email: string;
  name: string;
  nameEn: string;
  birthMonth: number;
  totalSpent: number;
  points: number;
  tier: "silver" | "gold" | "platinum";
  tierPct: number;
  nextTier: "gold" | "platinum" | null;
  nextTierNeed: number;
  birthday: "eligible" | "used" | "not-month";
};

export type Hotel = { id: number; name: string; nameZh: string; distanceKm: number };
export type Config = { now: string; today: string; bookable: { from: string; to: string }; phone: string; hotels: Hotel[] };

type Ctx = {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (k: DictKey, vars?: Record<string, string | number>) => string;
  config: Config | null;
  refreshConfig: () => Promise<Config | null>;
  user: Member | null;
  userLoaded: boolean;
  refreshUser: () => Promise<Member | null>;
  setUser: (u: Member | null) => void;
};

const AppCtx = createContext<Ctx | null>(null);

export async function api<T = any>(path: string, init?: RequestInit & { json?: unknown }): Promise<T> {
  const { json, ...rest } = init ?? {};
  const res = await fetch(path, {
    ...rest,
    cache: "no-store",
    headers: { ...(json !== undefined ? { "Content-Type": "application/json" } : {}), ...(rest.headers ?? {}) },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  let data: any = null;
  try {
    data = await res.json();
  } catch {
    data = { ok: false, error: "SERVER" };
  }
  if (data && typeof data === "object" && !("status" in data)) data.status = res.status;
  return data as T;
}

export function AppProvider({ initialLang, children }: { initialLang: Lang; children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang);
  const [config, setConfig] = useState<Config | null>(null);
  const [user, setUser] = useState<Member | null>(null);
  const [userLoaded, setUserLoaded] = useState(false);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    document.cookie = `lang=${l}; path=/; max-age=31536000; samesite=lax`;
    try {
      localStorage.setItem("lang", l);
    } catch {
      /* storage may be blocked */
    }
    document.documentElement.lang = l === "zh" ? "zh-CN" : l;
  }, []);

  const t = useCallback((k: DictKey, vars?: Record<string, string | number>) => translate(lang, k, vars), [lang]);

  const refreshConfig = useCallback(async () => {
    const c = await api<Config & { ok: boolean }>("/api/config");
    if (c && c.ok) {
      setConfig(c);
      return c;
    }
    return null;
  }, []);

  const refreshUser = useCallback(async () => {
    const r = await api<{ ok: boolean; user: Member | null }>("/api/auth/me");
    const u = r && r.ok ? r.user : null;
    setUser(u);
    setUserLoaded(true);
    return u;
  }, []);

  useEffect(() => {
    refreshConfig();
    refreshUser();
    // FR-20: the cookie is the source of truth; fall back to localStorage if the cookie was cleared
    if (!/(?:^|;\s*)lang=/.test(document.cookie)) {
      try {
        const saved = localStorage.getItem("lang");
        if (isLang(saved)) setLang(saved);
      } catch {
        /* ignore */
      }
    }
  }, [refreshConfig, refreshUser, setLang]);

  const value = useMemo(
    () => ({ lang, setLang, t, config, refreshConfig, user, userLoaded, refreshUser, setUser }),
    [lang, setLang, t, config, refreshConfig, user, userLoaded, refreshUser],
  );
  return <AppCtx.Provider value={value}>{children}</AppCtx.Provider>;
}

export function useApp(): Ctx {
  const c = useContext(AppCtx);
  if (!c) throw new Error("useApp outside AppProvider");
  return c;
}

/** <html data-ready="true"> once the page has finished loading its data */
export function useReady(ready: boolean) {
  useEffect(() => {
    document.documentElement.dataset.ready = ready ? "true" : "false";
    return () => {
      document.documentElement.dataset.ready = "false";
    };
  }, [ready]);
}
