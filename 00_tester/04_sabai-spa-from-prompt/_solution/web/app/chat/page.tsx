import { ChatBox } from "@/components/ChatBox.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { t } from "@/lib/i18n.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

const GREETING = {
  th: "สวัสดีค่ะ ผู้ช่วยสบายใจ สปา ยินดีให้บริการ ถามเวลาเปิด ราคา หรือพิมพ์ \"จอง\" ได้เลยค่ะ",
  en: "Hello! I'm the Sabai Jai Spa assistant. Ask about opening hours, prices, or type \"book\".",
  zh: "您好！我是舒心水疗助手。可以询问营业时间、价格，或输入\"预约\"。",
};

export default async function ChatPage() {
  const lang = await getLang();
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "chat.title")}</h1>
      </div>
      <ChatBox greeting={GREETING[lang]} />
    </>
  );
}
