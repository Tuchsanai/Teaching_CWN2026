import { TransportCalc } from "@/components/TransportCalc.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { t } from "@/lib/i18n.ts";
import { listHotels } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function TransportPage() {
  const lang = await getLang();
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "transport.title")}</h1>
      </div>
      <TransportCalc hotels={await listHotels(lang)} />
    </>
  );
}
