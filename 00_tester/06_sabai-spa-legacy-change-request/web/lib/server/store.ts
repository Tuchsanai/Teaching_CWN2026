// ซื้อ Gift Card (FR-19) · ตรวจยอดบัตร (FR-20) · ซื้อคอร์ส (FR-13) · รูป before/after (FR-18)
import { randomBytes } from "node:crypto";
import { clock } from "../clock.ts";
import { fromSatang, query, toSatang, withTx } from "../db.ts";
import { formatDate, t, type Lang } from "../i18n.ts";
import { formatBaht, toBaht } from "../money.ts";
import { COURSE_PRICE, COURSE_SESSIONS, courseExpiry } from "../rules/course.ts";
import { GC_CHANNELS, GC_DESIGNS, giftCardExpiry, giftCardStatus, isValidFaceValue } from "../rules/giftcard.ts";
import type { Session } from "../session.ts";
import { ApiError } from "./http.ts";

function newCode(): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = randomBytes(6);
  return "SABAI-" + Array.from(bytes, (b) => alphabet[b % alphabet.length]).join("");
}

export async function buyGiftCard(body: Record<string, unknown>, session: Session | null, lang: Lang) {
  const value = typeof body.value === "number" ? body.value : typeof body.value === "string" && body.value.trim() !== "" ? Number(body.value) : NaN;
  if (!isValidFaceValue(value)) throw new ApiError(422, "GC_VALUE");
  const design = String(body.design ?? "");
  const channel = String(body.channel ?? "");
  const recipient = String(body.recipient ?? "").trim();
  const message = String(body.message ?? "").trim().slice(0, 300) || null;
  if (!(GC_DESIGNS as readonly string[]).includes(design) || !(GC_CHANNELS as readonly string[]).includes(channel) || !recipient) {
    throw new ApiError(422, "GC_FIELDS");
  }
  const { today } = await clock();
  const expiresOn = giftCardExpiry(today);
  const code = newCode();
  const r = await query(
    `INSERT INTO gift_card (code, buyer_id, face_value, balance, design, channel, recipient, message, purchased_on, expires_on)
     VALUES ($1, $2, $3, $3, $4, $5, $6, $7, $8, $9) RETURNING id`,
    [code, session?.uid ?? null, fromSatang(value * 100), design, channel, recipient.slice(0, 160), message, today, expiresOn],
  );
  const channelLabel = t(lang, `channel.${channel}`);
  return {
    id: r.rows[0].id,
    code,
    value,
    valueLabel: formatBaht(value * 100),
    design,
    channel,
    recipient,
    purchasedOn: today,
    expiresOn,
    expiresLabel: t(lang, "gift.expires", { d: formatDate(expiresOn, lang) }),
    simulated: true,
    sentMessage: t(lang, "gift.sent", { channel: channelLabel, to: recipient }),
    preview: t(lang, "gift.previewText", { v: formatBaht(value * 100), code, d: formatDate(expiresOn, lang) }) + (message ? ` · “${message}”` : ""),
  };
}

export async function giftCardInfo(code: string, lang: Lang) {
  const r = await query("SELECT * FROM gift_card WHERE code = $1", [code.trim().toUpperCase()]);
  const g = r.rows[0];
  if (!g) throw new ApiError(404, "GC_NOT_FOUND");
  const { today } = await clock();
  const balance = toSatang(g.balance);
  const status = giftCardStatus(today, g.expires_on, balance);
  return {
    code: g.code,
    faceValue: toBaht(toSatang(g.face_value)),
    balance: toBaht(balance),
    balanceLabel: formatBaht(balance),
    design: g.design,
    channel: g.channel,
    purchasedOn: g.purchased_on,
    expiresOn: g.expires_on,
    expiresLabel: t(lang, "gift.expires", { d: formatDate(g.expires_on, lang) }),
    status,
    message: status === "expired" ? t(lang, "err.GC_EXPIRED") : status === "empty" ? t(lang, "err.GC_EMPTY") : t(lang, "gift.ok"),
  };
}

export async function buyCourse(session: Session | null, lang: Lang) {
  if (!session) throw new ApiError(401, "LOGIN_REQUIRED");
  const { today } = await clock();
  const expiresOn = courseExpiry(today);
  return withTx(async (c) => {
    const k = await c.query("SELECT id FROM service WHERE code = 'K01'");
    const r = await c.query(
      `INSERT INTO course_purchase (customer_id, service_id, price, total_sessions, used_sessions, reserved_sessions, purchased_on, expires_on)
       VALUES ($1, $2, $3, $4, 0, 0, $5, $6) RETURNING id`,
      [session.uid, k.rows[0].id, fromSatang(COURSE_PRICE), COURSE_SESSIONS, today, expiresOn],
    );
    const id: number = r.rows[0].id;
    const code = `C${String(id).padStart(2, "0")}`;
    await c.query("UPDATE course_purchase SET code = $1 WHERE id = $2", [code, id]);
    // ยอดสะสมนับการซื้อคอร์ส (A10)
    await c.query("UPDATE customer SET lifetime_spend = lifetime_spend + $1 WHERE id = $2", [fromSatang(COURSE_PRICE), session.uid]);
    return {
      id,
      code,
      price: toBaht(COURSE_PRICE),
      total: COURSE_SESSIONS,
      remaining: COURSE_SESSIONS,
      purchasedOn: today,
      expiresOn,
      message: t(lang, "wallet.bought", { d: formatDate(expiresOn, lang) }),
    };
  });
}

export async function photoForViewer(photoId: number, session: Session | null) {
  if (!session) throw new ApiError(401, "LOGIN_REQUIRED");
  const r = await query(
    `SELECT bp.storage_key, cp.customer_id FROM body_photo bp JOIN course_purchase cp ON cp.id = bp.course_purchase_id WHERE bp.id = $1`,
    [photoId],
  );
  const row = r.rows[0];
  if (!row) throw new ApiError(404, "NOT_FOUND");
  if (row.customer_id !== session.uid) throw new ApiError(403, "FORBIDDEN");
  return String(row.storage_key);
}
