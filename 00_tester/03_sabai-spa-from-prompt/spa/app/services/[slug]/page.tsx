"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useApp, useReady } from "@/components/AppProvider";
import { Icon, ThaiDivider } from "@/components/Ornament";
import { AllergyWarning, HERB_IMG, Loader, PageHead, svcName, useServices } from "@/components/Shared";
import { pick, type DictKey } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

export default function ServiceDetailPage() {
  const { t, lang } = useApp();
  const { slug } = useParams<{ slug: string }>();
  const services = useServices();
  useReady(!!services);
  const s = services?.find((x) => x.slug === slug);

  if (!services) return <Loader />;
  if (!s) {
    return (
      <div className="not-found">
        <h1>{t("service_not_found")}</h1>
        <Link href="/services" className="btn btn--green">{t("nav_services")}</Link>
      </div>
    );
  }
  return (
    <>
      <PageHead eyebrow={t(`cat_${s.category}` as DictKey)} title={svcName(s, lang)} lead={pick(s, "desc", lang)} image={s.image} />
      <section className="section">
        <div className="container split">
          <div className="split__media">
            <img src={s.image} alt={svcName(s, lang)} />
          </div>
          <div>
            <div className="row">
              <span className="badge badge--ok" data-testid="service-detail-duration"><Icon name="clock" size={14} /> {t("minutes", { n: s.duration })}</span>
              <span className="badge badge--muted" data-testid="service-detail-price">{formatBaht(s.price)}{s.is_package ? t("per_person") : ""}</span>
            </div>
            <h2 className="mt-2">{t("herbs_used")}</h2>
            <ThaiDivider className="mt-0" />
            <div className="grid grid--3" data-testid="service-detail-herbs" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 14 }}>
              {s.herbs.map((h) => (
                <div key={h} className="herb-card" data-herb={h}>
                  <img src={HERB_IMG[h]} alt={t(`herb_${h}` as DictKey)} width={96} height={96} />
                  <h3>{t(`herb_${h}` as DictKey)}</h3>
                  <p>{t(`herbdesc_${h}` as DictKey)}</p>
                </div>
              ))}
            </div>
            <div className="mt-2">
              <AllergyWarning />
            </div>
            <div className="row mt-2">
              <Link href={`/book?service=${s.slug}`} className="btn btn--gold btn--lg" data-testid="service-detail-book">
                {t("book_now")} <Icon name="arrow" />
              </Link>
              <Link href="/services" className="btn btn--ghost">{t("back")}</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
