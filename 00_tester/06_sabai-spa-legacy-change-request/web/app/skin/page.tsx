import { SkinAnalyzer } from "@/components/SkinAnalyzer.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { asset } from "@/lib/assets.ts";
import { t } from "@/lib/i18n.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function SkinPage() {
  const lang = await getLang();
  const services = Object.fromEntries((await listServices(lang)).map((s) => [s.code, s.name]));
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "skin.title")}</h1>
      </div>
      <SkinAnalyzer sample={asset("face-sample")} services={services} />
    </>
  );
}
