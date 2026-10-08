import type { PoolClient } from "pg";
import { addDays, bkkDate, bkkInstant, bkkParts } from "../time";
import { COURSE_DAYS, COURSE_PRICE, COURSE_SESSIONS, GIFT_DAYS } from "../rules";
import { hashPassword } from "./password";

export const SEED_PASSWORD = "Sabai1234!";

type Svc = [slug: string, category: string, duration: number, price: number, herbs: string[], image: string, names: [string, string, string], descs: [string, string, string]];

export const SERVICES: Svc[] = [
  ["thai-massage", "massage", 60, 800, ["plai"], "/assets/treatments/thai-massage.jpg",
    ["นวดไทย", "Traditional Thai Massage", "传统泰式按摩"],
    ["นวดไทยแผนโบราณ กดจุดและยืดเหยียดตามแนวเส้นพลังงาน ช่วยคลายกล้ามเนื้อที่ตึงล้า", "Ancient pressure-point and stretching techniques along the energy lines to release tired, tight muscles.", "沿能量线进行古法指压与伸展，舒缓疲劳紧绷的肌肉。"]],
  ["herbal-compress", "massage", 60, 900, ["plai", "turmeric", "lemongrass", "kaffir-lime"], "/assets/treatments/herbal-compress.jpg",
    ["ประคบสมุนไพร", "Herbal Compress", "草药热敷"],
    ["ลูกประคบสมุนไพรสดนึ่งร้อน กดคลึงตามจุด ช่วยลดปวดเมื่อยและให้กลิ่นหอมผ่อนคลาย", "Freshly steamed herbal balls pressed along the body to ease aches with a calming aroma.", "新鲜蒸热的草药球沿身体按压，舒缓酸痛并带来宁静香气。"]],
  ["foot-reflexology", "massage", 60, 600, ["lemongrass"], "/assets/treatments/foot-reflexology.jpg",
    ["นวดเท้า", "Foot Reflexology", "足底反射按摩"],
    ["นวดกดจุดฝ่าเท้าที่เชื่อมโยงกับอวัยวะต่าง ๆ ช่วยให้เลือดไหลเวียนดีและหลับสบาย", "Pressure on reflex points of the feet to boost circulation and help you sleep well.", "按压足底反射区，促进血液循环，帮助安眠。"]],
  ["aroma-oil", "massage", 90, 1500, ["lemongrass", "kaffir-lime"], "/assets/treatments/aroma-oil.jpg",
    ["นวดน้ำมันอโรมา", "Aroma Oil Massage", "芳香精油按摩"],
    ["นวดน้ำมันหอมระเหยด้วยจังหวะยาวและนุ่มนวล ปลดปล่อยความเครียดทั้งกายและใจ", "Long, flowing strokes with warm aromatic oils to release stress from body and mind.", "以温热芳香精油进行绵长流畅的按摩，释放身心压力。"]],
  ["coconut-rice-scrub", "body", 90, 1400, ["thanaka", "turmeric"], "/assets/treatments/coconut-rice-scrub.jpg",
    ["ขัดผิวข้าวมะพร้าว", "Coconut Rice Scrub", "椰子米身体磨砂"],
    ["ขัดผิวด้วยข้าวไทยบดและน้ำมันมะพร้าว ผลัดเซลล์ผิวเก่า ให้ผิวนุ่มเนียนกระจ่างใส", "Ground Thai rice and coconut oil polish away dead skin for soft, radiant skin.", "以泰国米粉与椰子油去除老化角质，令肌肤柔滑透亮。"]],
  ["turmeric-facial", "facial", 60, 1200, ["turmeric", "thanaka"], "/assets/treatments/turmeric-facial.jpg",
    ["ทรีตเมนต์หน้าขมิ้น", "Turmeric Glow Facial", "姜黄焕亮面部护理"],
    ["มาสก์ขมิ้นและทานาคา ช่วยให้ผิวหน้าดูกระจ่างใส สม่ำเสมอ", "A turmeric and thanaka mask for a brighter, more even complexion.", "姜黄与黄香楝面膜，令肤色更透亮均匀。"]],
  ["aloe-hydrating-facial", "facial", 60, 1100, ["aloe-vera"], "/assets/treatments/aloe-hydrating-facial.jpg",
    ["ทรีตเมนต์หน้าว่านหางจระเข้", "Aloe Hydrating Facial", "芦荟保湿面部护理"],
    ["เจลว่านหางจระเข้สด เติมความชุ่มชื้นและปลอบประโลมผิวที่แดงหรือระคายเคือง", "Fresh aloe gel deeply hydrates and calms red or irritated skin.", "新鲜芦荟凝胶深层补水，舒缓泛红或敏感肌肤。"]],
  ["body-contouring", "body", 90, 1500, ["plai", "turmeric"], "/assets/treatments/body-contouring.jpg",
    ["กระชับสัดส่วน", "Body Contouring", "塑身紧致护理"],
    ["นวดกระชับสัดส่วนด้วยไพลและขมิ้น ช่วยให้ผิวกระชับ (มีคอร์ส 10 ครั้ง แถม 1)", "Firming massage with plai and turmeric for toned skin (course: 10 sessions + 1 free).", "以泰国姜与姜黄进行紧致按摩（课程：10 次赠 1 次）。"]],
  ["bangkok-relax", "package", 120, 2900, ["plai", "turmeric", "lemongrass"], "/assets/packages/hotel-transfer.jpg",
    ["แพ็กเกจ Bangkok Relax", "Bangkok Relax Package", "曼谷放松套餐 Bangkok Relax"],
    ["นวดไทย + ประคบสมุนไพร + รถรับส่งโรงแรม จบในการจองเดียว ราคาต่อคน", "Thai massage + herbal compress + hotel transfer in a single booking, priced per person.", "泰式按摩 + 草药热敷 + 酒店接送，一次预约全包，按人计价。"]],
];

type Ther = [id: number, names: [string, string, string], titles: [string, string, string], ratings: number[]];
export const THERAPISTS: Ther[] = [
  [1, ["มาลี", "Malee", "玛莉"], ["ผู้เชี่ยวชาญนวดไทย 20 ปี", "Thai massage master, 20 years", "泰式按摩大师，20 年经验"], [5, 5, 5, 5, 5, 5, 5, 5, 5, 4]], // 4.9
  [2, ["ปิยะดา", "Piyada", "碧雅达"], ["นวดน้ำมันอโรมา", "Aroma oil specialist", "芳香精油按摩"], [5, 4]], // 4.5
  [3, ["กานดา", "Kanda", "甘达"], ["ประคบสมุนไพรและขัดผิว", "Herbal compress & scrubs", "草药热敷与身体磨砂"], [5, 5, 4, 4, 4]], // 4.4
  [4, ["สมชาย", "Somchai", "颂猜"], ["นวดไทยและนวดเท้า", "Thai & foot massage", "泰式与足底按摩"], [5, 5, 4, 5, 5, 5, 4, 5, 5, 4]], // 4.7
  [5, ["ประภา", "Prapa", "帕帕"], ["กระชับสัดส่วนและทรีตเมนต์หน้า", "Body contouring & facials", "塑身与面部护理"], [5, 5, 5]], // 5.0
  [6, ["อรุณ", "Arun", "阿伦"], ["นักบำบัดใหม่ · นวดเท้า", "New therapist · foot reflexology", "新晋理疗师 · 足底按摩"], []], // no reviews (BR-10)
];

const REVIEW_TEXT: Record<number, [string, string, string][]> = {
  5: [
    ["มือหนักกำลังดี ตื่นมาตัวเบาเลยค่ะ", "Perfect pressure — I woke up feeling light.", "力度刚好，醒来浑身轻松。"],
    ["บริการประทับใจมาก จะกลับมาอีกแน่นอน", "Wonderful service, I will definitely be back.", "服务非常棒，一定会再来。"],
    ["ใส่ใจทุกรายละเอียด ห้องหอมและเงียบสงบ", "Attentive to every detail; calm, fragrant room.", "细致入微，房间安静又芳香。"],
    ["ปวดหลังหายเป็นปลิดทิ้ง ขอบคุณมากค่ะ", "My back pain is gone. Thank you!", "背痛一扫而空，非常感谢！"],
  ],
  4: [
    ["ดีมาก แต่อยากให้นวดนานกว่านี้อีกนิด", "Very good, I just wished it lasted longer.", "很好，只是希望时间再长一点。"],
    ["ผ่อนคลายดี ราคาเหมาะสม", "Relaxing and fairly priced.", "很放松，价格合理。"],
  ],
};
const AUTHORS = ["Ann", "Mei", "Li Wei", "Ploy", "James", "Yuki", "Nok", "Sarah", "Ken", "Fon"];

type Room = [slug: string, image: string, capacity: number, names: [string, string, string], descs: [string, string, string]];
export const ROOMS: Room[] = [
  ["couple-suite", "/assets/rooms/room-couple-suite.jpg", 2, ["Couple Suite", "Couple Suite", "情侣套房"],
    ["ห้องส่วนตัวสำหรับ 2 คน อ่างแช่ดอกไม้ วิวสวนเขตร้อน (มี 1 ห้อง)", "A private suite for two with a flower bath and tropical garden view (1 suite).", "双人私密套房，配花瓣浴缸与热带花园景观（仅 1 间）。"]],
  ["thai-massage-room", "/assets/rooms/room-thai-massage.jpg", 6, ["ห้องนวดไทย", "Thai Massage Hall", "泰式按摩厅"],
    ["ห้องนวดไทยแบบดั้งเดิม เบาะนวดผ้าไทย บรรยากาศไม้สัก", "Traditional Thai massage hall with Thai-silk mats and teak wood.", "传统泰式按摩厅，泰丝垫与柚木氛围。"]],
  ["herbal-steam", "/assets/rooms/room-herbal-steam.jpg", 4, ["ห้องอบสมุนไพร", "Herbal Steam Room", "草药蒸汽房"],
    ["อบไอน้ำสมุนไพรไทย ตะไคร้ มะกรูด และไพล", "Thai herbal steam with lemongrass, kaffir lime and plai.", "以香茅、青柠与泰国姜进行泰式草药蒸汽浴。"]],
];

export const HOTELS: [number, string, string, number][] = [
  [1, "Sukhumvit Garden Hotel", "素坤逸花园酒店", 3.0],
  [2, "Lumphini Park View Hotel", "伦披尼公园景观酒店", 5.0],
  [3, "Siam Square Boutique Hotel", "暹罗广场精品酒店", 5.1],
  [4, "Chatuchak Park Hotel", "乍都乍公园酒店", 12.0],
  [5, "Chao Phraya Riverside Hotel", "湄南河畔酒店", 15.0],
  [6, "Bang Na Lakeside Hotel", "邦纳湖畔酒店", 15.1],
  [7, "Suvarnabhumi Airport Hotel", "素万那普机场酒店", 20.0],
];

type SeedBooking = {
  userId: number | null;
  guestName?: string;
  service: string;
  duration: number;
  price: number;
  date: string;
  startMin: number;
  people: number;
  kind: "single" | "couple" | "group";
  therapists: number[];
  room?: string;
  courseId?: number;
  total: number;
};

async function insertBooking(c: PoolClient, b: SeedBooking): Promise<number> {
  const start = bkkInstant(b.date, b.startMin);
  const end = new Date(start.getTime() + b.duration * 60_000);
  const subtotal = b.price * b.people;
  const r = await c.query<{ id: number }>(
    `INSERT INTO bookings (user_id, guest_name, guest_phone, service_slug, kind, people, start_at, end_at, therapist_ids, room_slug,
       subtotal, tier_discount, course_id, course_covered, total, due, source)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$15,'seed') RETURNING id`,
    [b.userId, b.guestName ?? null, b.guestName ? "080-000-0000" : null, b.service, b.kind, b.people, start, end, b.therapists, b.room ?? null,
      subtotal, b.courseId ? 0 : subtotal - b.total, b.courseId ?? null, b.courseId ? subtotal : 0, b.total],
  );
  const id = r.rows[0].id;
  await c.query("UPDATE bookings SET code = $2 WHERE id = $1", [id, `SB${String(id).padStart(5, "0")}`]);
  for (const t of b.therapists) {
    await c.query("INSERT INTO booking_resources (booking_id, resource, start_at, end_at) VALUES ($1,$2,$3,$4)", [id, `T:${t}`, start, end]);
  }
  if (b.room) await c.query("INSERT INTO booking_resources (booking_id, resource, start_at, end_at) VALUES ($1,$2,$3,$4)", [id, `R:${b.room}`, start, end]);
  return id;
}

/** Inserts the full demo data set. "now" is the (possibly locked) current time — all seed dates are relative to it. */
export async function seedAll(c: PoolClient, now: Date): Promise<void> {
  const today = bkkDate(now);
  const nowP = bkkParts(now);

  for (const [i, s] of SERVICES.entries()) {
    await c.query(
      `INSERT INTO services (slug, sort, category, duration, price, herbs, image, is_package, name_th, name_en, name_zh, desc_th, desc_en, desc_zh)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)`,
      [s[0], i + 1, s[1], s[2], s[3], s[4], s[5], s[1] === "package", ...s[6], ...s[7]],
    );
  }

  for (const [id, n, t, ratings] of THERAPISTS) {
    await c.query(
      `INSERT INTO therapists (id, image, name_th, name_en, name_zh, title_th, title_en, title_zh) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [id, `/assets/therapists/therapist-${id}.jpg`, ...n, ...t],
    );
    for (const [k, rating] of ratings.entries()) {
      const pool = REVIEW_TEXT[rating] ?? REVIEW_TEXT[4];
      const txt = pool[(id + k) % pool.length];
      await c.query(
        `INSERT INTO reviews (therapist_id, author, rating, reviewed_on, text_th, text_en, text_zh) VALUES ($1,$2,$3,$4,$5,$6,$7)`,
        [id, AUTHORS[(id * 3 + k) % AUTHORS.length], rating, addDays(today, -(7 * (k + 1) + id)), ...txt],
      );
    }
  }

  for (const [i, r] of ROOMS.entries()) {
    await c.query(
      `INSERT INTO rooms (slug, sort, image, capacity, name_th, name_en, name_zh, desc_th, desc_en, desc_zh) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
      [r[0], i + 1, r[1], r[2], ...r[3], ...r[4]],
    );
  }

  for (const h of HOTELS) await c.query("INSERT INTO hotels (id, name, name_zh, distance_km) VALUES ($1,$2,$3,$4)", h);

  // ---- users (password Sabai1234! for all) ----
  const ins = async (email: string, name: string, nameEn: string, month: number, day: number, spent: number, points: number) => {
    const r = await c.query<{ id: number }>(
      `INSERT INTO users (email, password_hash, name, name_en, birth_month, birth_day, total_spent, points) VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id`,
      [email, hashPassword(SEED_PASSWORD), name, nameEn, month, day, spent, points],
    );
    return r.rows[0].id;
  };
  const nidaMonth = ((nowP.m + 5) % 12) + 1; // a month that is not "this month"
  const nida = await ins("nida@sabai.test", "นิดา", "Nida", nidaMonth, 12, 12_400, 124);
  const ton = await ins("ton@sabai.test", "ต้น", "Ton", nowP.m, nowP.d, 30_000, 250);
  await ins("new@sabai.test", "สมาชิกใหม่", "New Member", ((nowP.m + 2) % 12) + 1, 1, 0, 0);
  void ton;

  // ---- Nida: body-contouring course, 4 used of 11 (bought 60 days ago) ----
  const bought = addDays(today, -60);
  const course = await c.query<{ id: number }>(
    `INSERT INTO courses (user_id, service_slug, total_sessions, used_sessions, price, purchased_on, expires_on) VALUES ($1,'body-contouring',$2,4,$3,$4,$5) RETURNING id`,
    [nida, COURSE_SESSIONS, COURSE_PRICE, bought, addDays(bought, COURSE_DAYS)],
  );
  const courseId = course.rows[0].id;
  const waist = [82.0, 80.5, 79.0, 78.0];
  for (const [i, cm] of waist.entries()) {
    const d = addDays(bought, i * 14);
    await c.query("INSERT INTO waist_measurements (user_id, measured_on, cm) VALUES ($1,$2,$3)", [nida, d, cm]);
    await insertBooking(c, { userId: nida, service: "body-contouring", duration: 90, price: 1500, date: d, startMin: 11 * 60, people: 1, kind: "single", therapists: [5], courseId, total: 0 });
  }
  await insertBooking(c, { userId: nida, service: "aroma-oil", duration: 90, price: 1500, date: addDays(today, -75), startMin: 18 * 60, people: 1, kind: "single", therapists: [2], total: 1425 });
  await c.query("INSERT INTO body_photos (user_id, taken_on, kind, image) VALUES ($1,$2,'before',$3), ($1,$4,'after',$3)", [nida, bought, "/assets/treatments/body-contouring.jpg", addDays(bought, 42)]);

  // Nida's appointment tomorrow 15:00 (BR-09 cancel tests)
  await insertBooking(c, { userId: nida, service: "thai-massage", duration: 60, price: 800, date: addDays(today, 1), startMin: 15 * 60, people: 1, kind: "single", therapists: [1], total: 760 });

  // Example bookings on day +2 for overlap tests (BR-04, BR-06)
  await insertBooking(c, { userId: null, guestName: "Demo Guest A", service: "thai-massage", duration: 60, price: 800, date: addDays(today, 2), startMin: 14 * 60, people: 1, kind: "single", therapists: [1], total: 800 });
  await insertBooking(c, { userId: null, guestName: "Demo Couple", service: "aroma-oil", duration: 90, price: 1500, date: addDays(today, 2), startMin: 18 * 60, people: 2, kind: "couple", therapists: [2, 3], room: "couple-suite", total: 3000 });

  // ---- gift cards for BR-18 tests ----
  const gift = async (code: string, amount: number, design: string, daysAgo: number) => {
    const bought = addDays(today, -daysAgo);
    await c.query(
      `INSERT INTO gift_cards (code, amount, balance, design, channel, recipient, recipient_name, sender_name, message, purchased_on, expires_on)
       VALUES ($1,$2,$2,$3,'line','demo-line','Mom','Fon','Happy birthday',$4,$5)`,
      [code, amount, design, bought, addDays(bought, GIFT_DAYS)],
    );
  };
  await gift("GIFT-2000-ORCHID", 2000, "orchid", 10);
  await gift("GIFT-DAY365", 1000, "lotus", 365); // today is day 365 → still valid
  await gift("GIFT-DAY366", 1000, "gold", 366); // today is day 366 → expired
}
