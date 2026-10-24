import { LoginForm } from "@/components/LoginForm.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { flags } from "@/lib/flags.ts";
import { t } from "@/lib/i18n.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

// บัญชีทดสอบแสดงเฉพาะโหมดทดสอบ (T2, A20)
const TEST_ACCOUNTS = [
  { email: "nida@sabai.test", password: "Nida@2026", note: "U01 Gold · course C01" },
  { email: "ton@sabai.test", password: "Ton@2026", note: "U02 Platinum · Oct birthday" },
  { email: "may@sabai.test", password: "May@2026", note: "U03 new member" },
  { email: "fon@sabai.test", password: "Fon@2026", note: "U04 Silver · 250 pts" },
  { email: "prae@sabai.test", password: "Prae@2026", note: "U05 birthday used" },
  { email: "vipa@sabai.test", password: "Vipa@2026", note: "U06 Platinum · 199 pts" },
  { email: "kan@sabai.test", password: "Kan@2026", note: "U07 Gold · course 1 left" },
  { email: "liwei@sabai.test", password: "LiWei@2026", note: "U08 tourist" },
  { email: "owner@sabai.test", password: "Owner@2026", note: "owner → /admin" },
];

export default async function LoginPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const lang = await getLang();
  const next = sp.next && sp.next.startsWith("/") && !sp.next.startsWith("//") ? sp.next : "/account";
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "login.title")}</h1>
      </div>
      <LoginForm next={next} testAccounts={flags.allowTestReset ? TEST_ACCOUNTS : []} />
    </>
  );
}
