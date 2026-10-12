// ข้อ 5 ชุด B · ทำซ้ำ exam/EX5-EVIDENCE.json ของผู้สอบบนระบบตั้งต้น (1 คะแนน)
//   env EVIDENCE = path ของไฟล์ (mount) · ระบบ = image ตั้งต้นของเครื่องตรวจ
import { readFileSync } from "node:fs";
import { Score, reset, login, me, USERS, SEED_NOW, expectEq, all } from "../lib.mjs";

const s = new Score(5, "evidence");
await s.check("B5-ev", "EX5-EVIDENCE.json ตรงกับที่เครื่องตรวจทำซ้ำบนระบบตั้งต้น", 1, async () => {
  const ev = JSON.parse(readFileSync(process.env.EVIDENCE, "utf8"));
  const code = String(ev.booking ?? "").trim().toUpperCase();
  const cust = String(ev.customer ?? "").trim().toUpperCase();
  if (!/^B\d+$/.test(code)) return `booking "${ev.booking}" ไม่ใช่รูปแบบ B??`;
  if (!USERS[cust] || cust === "OWNER") return `customer "${ev.customer}" ไม่ใช่ลูกค้าสมาชิก U01–U08`;
  await reset();
  const o = await login("OWNER");
  // หาวันนัดและยืนยันว่าเป็นนัดของลูกค้าคนนั้น · ยังไม่ถึงเวลาที่ now ของ seed
  const id = Number(code.slice(1));
  const mine = (await (await login(cust)).get("/api/me/bookings")).json;
  const list = mine.bookings ?? mine.items ?? mine;
  const bk = Array.isArray(list) ? list.find((b) => b.code === code || b.id === id) : null;
  if (!bk) return `${code} ไม่ใช่นัดของ ${cust}`;
  const start = bk.date && bk.time ? `${bk.date}T${bk.time}:00+07:00` : null;
  if (bk.status !== "confirmed") return `${code} สถานะ ${bk.status} (ต้องเป็นนัดที่ยืนยันแล้ว)`;
  if (start && new Date(start) <= new Date(SEED_NOW)) return `${code} ไม่ใช่นัดที่ยังไม่ถึงเวลา (${start})`;
  const before = await me(cust);
  const r = await o.post(`/api/admin/bookings/${id}/complete`, {});
  const after = { status: r.status, ...(await me(cust)) };
  await reset();
  const pick = (x) => ({ points: x?.points, lifetimeSpend: x?.lifetimeSpend, tier: x?.tier });
  return all(expectEq(pick(ev.before), before, "before"), expectEq({ status: ev.after?.status, ...pick(ev.after) }, after, "after"));
});
s.done();
