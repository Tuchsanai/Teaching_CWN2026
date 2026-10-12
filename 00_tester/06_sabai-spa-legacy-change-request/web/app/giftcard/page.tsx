import { GiftCardShop } from "@/components/GiftCardShop.tsx";
import { Orchid } from "@/components/ThaiOrnament.tsx";
import { asset } from "@/lib/assets.ts";
import { t } from "@/lib/i18n.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function GiftCardPage() {
  const lang = await getLang();
  return (
    <>
      <div className="page-head">
        <Orchid className="orn sway" size={40} />
        <h1>{t(lang, "gift.title")}</h1>
      </div>
      <GiftCardShop images={{ orchid: asset("gc-orchid"), lotus: asset("gc-lotus"), gold: asset("gc-gold") }} />
    </>
  );
}
