import { randomBytes } from "node:crypto";
import { q1 } from "@/lib/server/db";
import { currentUser } from "@/lib/server/auth";
import { getNow } from "@/lib/server/clock";
import { body, fail, handle, json } from "@/lib/server/http";
import { addDays, bkkDate } from "@/lib/time";
import { GIFT_CHANNELS, GIFT_DAYS, GIFT_DESIGNS, GIFT_MAX, GIFT_MIN } from "@/lib/rules";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
function giftCode(): string {
  const bytes = randomBytes(8);
  return "GC-" + Array.from(bytes, (b) => ALPHABET[b % ALPHABET.length]).join("");
}

/** FR-16 / BR-17: buy a gift card. Delivery by LINE / email is simulated only (nothing is sent). */
export async function POST(req: Request) {
  return handle(async () => {
    const b = await body<{ amount?: number | string; design?: string; channel?: string; recipient?: string; recipientName?: string; senderName?: string; message?: string }>(req);
    const amount = Number(b.amount);
    if (!Number.isInteger(amount) || amount < GIFT_MIN || amount > GIFT_MAX) return fail("GIFT_AMOUNT");
    if (!GIFT_DESIGNS.includes(b.design as (typeof GIFT_DESIGNS)[number])) return fail("GIFT_DESIGN");
    if (!GIFT_CHANNELS.includes(b.channel as (typeof GIFT_CHANNELS)[number])) return fail("GIFT_CHANNEL");
    const recipient = String(b.recipient ?? "").trim();
    if (!recipient || (b.channel === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient))) return fail("GIFT_RECIPIENT");
    const u = await currentUser();
    const today = bkkDate(await getNow());
    const expires = addDays(today, GIFT_DAYS);
    const code = giftCode();
    await q1(
      `INSERT INTO gift_cards (code, amount, balance, design, channel, recipient, recipient_name, sender_name, message, buyer_user_id, purchased_on, expires_on)
       VALUES ($1,$2,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)`,
      [code, amount, b.design, b.channel, recipient.slice(0, 120), String(b.recipientName ?? "").slice(0, 60), String(b.senderName ?? "").slice(0, 60),
        String(b.message ?? "").slice(0, 300), u?.id ?? null, today, expires],
    );
    return json({
      ok: true,
      giftCard: { code, amount, balance: amount, design: b.design, channel: b.channel, recipient, recipientName: b.recipientName ?? "", senderName: b.senderName ?? "", message: b.message ?? "", purchasedOn: today, expiresOn: expires },
      delivery: { simulated: true, sent: false, channel: b.channel, to: recipient },
    }, 201);
  });
}
