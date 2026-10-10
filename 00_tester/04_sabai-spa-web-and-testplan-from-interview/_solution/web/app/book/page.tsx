import { BookingWizard } from "@/components/BookingWizard.tsx";
import { Lotus, Orchid } from "@/components/ThaiOrnament.tsx";
import { asset } from "@/lib/assets.ts";
import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { t } from "@/lib/i18n.ts";
import { bookableRange } from "@/lib/rules/dates.ts";
import { BOOKING_TYPES, type BookingType } from "@/lib/rules/party.ts";
import { listHotels, listServices } from "@/lib/server/catalog.ts";
import { loadCustomer, wallet } from "@/lib/server/customer.ts";
import { getLang } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** จอง 4 ขั้น (FR-01–06, FR-14, FR-21–23, FR-31, FR-33) */
export default async function BookPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const lang = await getLang();
  const session = await getSession();
  const { today } = await clock();
  const services = await listServices(lang);
  const hotels = await listHotels(lang);
  const customer = session ? await loadCustomer(getPool(), session.uid) : null;
  const courses = customer ? (await wallet(getPool(), customer.id, today, lang)).courses : [];

  const reqType = (sp.type ?? "") as BookingType;
  const svc = services.find((s) => s.code === (sp.service ?? "").toUpperCase());
  const type: BookingType = BOOKING_TYPES.includes(reqType)
    ? reqType
    : svc?.kind === "package"
      ? "package"
      : svc?.kind === "course"
        ? "course"
        : "single";
  const fallback = services.find((s) => (type === "package" ? s.kind === "package" : type === "course" ? s.kind === "course" : s.kind === "single"));
  const people = Number(sp.people ?? (type === "couple" ? 2 : type === "group" ? 3 : 1)) || 1;

  return (
    <>
      <div className="page-head">
        <Orchid className="orn sway" size={44} />
        <h1>{t(lang, "book.title")}</h1>
        <Lotus className="orn" size={44} />
      </div>
      <BookingWizard
        services={services.map((s) => ({ code: s.code, name: s.name, kind: s.kind, durationMin: s.durationMin, priceSatang: s.priceSatang, herbs: s.herbs }))}
        hotels={hotels}
        user={customer ? { name: customer.name, phone: customer.phone ?? "" } : null}
        courses={courses.map((c) => ({ id: c.id, code: c.code ?? "", label: `${c.remainingLabel} · ${c.expired ? t(lang, "wallet.expired") : t(lang, "wallet.expires", { d: c.expiresLabel })}`, usable: c.usable }))}
        range={bookableRange(today)}
        initial={{ type, service: svc && svc.kind === fallback?.kind ? svc.code : (fallback?.code ?? "S01"), people }}
        panorama={asset("pano-couple")}
      />
    </>
  );
}
