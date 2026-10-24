import Link from "next/link";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { serviceImage } from "@/lib/assets.ts";
import { t } from "@/lib/i18n.ts";
import { formatBaht } from "@/lib/money.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** รายการบริการ + สมุนไพร (FR-31) */
export default async function ServicesPage() {
  const lang = await getLang();
  const services = await listServices(lang);
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "services.title")}</h1>
      </div>
      <div className="grid">
        {services.map((s) => {
          const href = s.kind === "package" ? "/package" : s.kind === "course" ? "/wallet" : `/book?service=${s.code}`;
          return (
            <article key={s.code} className="card svc-card" data-testid={`service-card-${s.code}`}>
              <img src={serviceImage(s.code)} alt={s.name} loading="lazy" />
              <div className="body">
                <h2 className="h3" data-testid={`service-name-${s.code}`} style={{ fontSize: "1.2rem" }}>
                  {s.name}
                </h2>
                <div className="muted">
                  {s.durationMin} {t(lang, "common.minutes")}
                  {s.kind === "course" ? ` · ${t(lang, "services.course")}` : ""}
                </div>
                <div className="price" data-testid={`service-price-${s.code}`}>
                  {formatBaht(s.priceSatang)} {s.kind !== "course" && <span className="muted small">{t(lang, "common.perPerson")}</span>}
                </div>
                <div className="small muted">{t(lang, "common.herbs")}</div>
                <ul className="chips" data-testid={`service-herbs-${s.code}`}>
                  {s.herbs.map((h) => (
                    <li key={h}>{h}</li>
                  ))}
                </ul>
                <Link className="btn btn-sm" href={href} data-testid={`service-book-${s.code}`}>
                  {t(lang, "common.bookNow")}
                </Link>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}
