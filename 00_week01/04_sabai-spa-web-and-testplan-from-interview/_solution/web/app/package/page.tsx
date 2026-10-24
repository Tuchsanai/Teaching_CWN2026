import { PackageCalc } from "@/components/PackageCalc.tsx";
import { GoldDivider } from "@/components/ThaiOrnament.tsx";
import { serviceImage } from "@/lib/assets.ts";
import { t } from "@/lib/i18n.ts";
import { formatBaht } from "@/lib/money.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** หน้าแพ็กเกจ Bangkok Relax (FR-21) */
export default async function PackagePage() {
  const lang = await getLang();
  const p = (await listServices(lang)).find((s) => s.code === "P01")!;
  return (
    <article className="card svc-card" data-testid="package-card">
      <img src={serviceImage("P01")} alt={p.name} style={{ aspectRatio: "16 / 7" }} />
      <div className="body">
        <h1 data-testid="package-title">{t(lang, "package.title")}</h1>
        <p className="price" data-testid="package-price" data-amount={p.price}>
          {t(lang, "package.price", { p: formatBaht(p.priceSatang) })}
        </p>
        <h2 style={{ fontSize: "1.2rem" }}>{t(lang, "package.includes")}</h2>
        <ol data-testid="package-includes">
          <li data-testid="package-item-1">{t(lang, "package.item1")}</li>
          <li data-testid="package-item-2">{t(lang, "package.item2")}</li>
          <li data-testid="package-item-3">{t(lang, "package.item3")}</li>
        </ol>
        <p className="muted small">
          {p.durationMin} {t(lang, "common.minutes")} · {t(lang, "package.note")}
        </p>
        <div className="small">
          <strong>{t(lang, "common.herbs")}:</strong> {p.herbs.join(", ")}
        </div>
        <GoldDivider />
        <PackageCalc unitSatang={p.priceSatang} />
      </div>
    </article>
  );
}
