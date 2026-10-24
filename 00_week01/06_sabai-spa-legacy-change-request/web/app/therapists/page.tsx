import { TherapistList } from "@/components/TherapistList.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { therapistImage } from "@/lib/assets.ts";
import { t } from "@/lib/i18n.ts";
import { listServices, listTherapists } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function TherapistsPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const lang = await getLang();
  const services = await listServices(lang);
  const list = await listTherapists(lang);
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "therapists.title")}</h1>
      </div>
      <TherapistList
        initialFilter={sp.min === "4.5"}
        items={list.map((x) => ({
          code: x.code,
          name: x.name,
          rating: x.rating,
          reviewCount: x.reviewCount,
          passes45: x.passes45,
          services: x.services,
          serviceNames: x.services.map((c) => services.find((s) => s.code === c)?.name ?? c),
          image: therapistImage(x.code),
        }))}
      />
    </>
  );
}
