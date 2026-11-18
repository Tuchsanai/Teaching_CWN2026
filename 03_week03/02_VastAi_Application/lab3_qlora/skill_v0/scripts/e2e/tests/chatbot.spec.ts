// รัน 26 เคสจาก cases.json — 1 เคส = 1 วิดีโอ + 1 ไฟล์ผล (out/answers/case<N>.json)
import fs from "node:fs";
import path from "node:path";
import type { Page } from "@playwright/test";
import { runChecks, type Check } from "./check";
import { ask, clickChip, expect, FINAL_HOLD, OUT_DIR, openChat, test } from "./helpers";

type Step = { type?: string; chip?: string };
type Booking = { name: string; phone: string; service: string; time: string };
type Case = {
  id: number;
  slug: string;
  action: string;
  steps: Step[];
  confirm?: string[];
  checks: Check[];
  booking?: Booking;
};
type Turn = { user: string; bot: string };

const cases: Case[] = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "cases.json"), "utf8")).cases;

/** ตรวจการ์ดจองสำเร็จ + แถวในหน้า /bookings — คืนเหตุผลที่ไม่ผ่าน และข้อมูลบนการ์ด */
async function checkBooking(page: Page, want: Booking) {
  const fails: string[] = [];
  const card = page.getByTestId("booking-card").last();
  if ((await page.getByTestId("booking-card").count()) === 0) {
    const err = page.getByTestId("booking-error").last();
    const why = (await err.count()) ? (await err.innerText()).trim() : "บอทไม่ได้ส่งข้อมูลการจองที่ครบ";
    await page.waitForTimeout(FINAL_HOLD);
    return { fails: [`ไม่เห็นการ์ดจองสำเร็จ (${why})`], shown: null };
  }

  const read = (id: string) => card.getByTestId(id).innerText();
  const shown = {
    id: await card.getAttribute("data-booking-id"),
    name: await read("booking-card-name"),
    phone: await read("booking-card-phone"),
    service: await read("booking-card-service"),
    time: await read("booking-card-time"),
  };
  if (!shown.name.includes(want.name)) fails.push(`การ์ด: ชื่อไม่ใช่ ${want.name}`);
  if (!shown.phone.replace(/\D/g, "").includes(want.phone)) fails.push(`การ์ด: เบอร์ไม่ใช่ ${want.phone}`);
  if (!shown.service.includes(want.service)) fails.push(`การ์ด: บริการไม่ใช่ ${want.service}`);
  if (!shown.time.includes(want.time)) fails.push(`การ์ด: วันเวลาไม่ใช่ ${want.time}`);
  await card.scrollIntoViewIfNeeded();
  await page.waitForTimeout(FINAL_HOLD); // ค้างให้อ่านการ์ด

  // หน้า /bookings ต้องมีแถวเดียวกัน (อ่านจาก PostgreSQL)
  await page.getByTestId("nav-bookings").click();
  const row = page.locator(`[data-testid="booking-row"][data-booking-id="${shown.id}"]`);
  if ((await row.count()) === 0) {
    await row.waitFor({ timeout: 15_000 }).catch(() => {});
  }
  if ((await row.count()) === 0) {
    fails.push("หน้ารายการจอง: ไม่มีแถวของการจองนี้");
  } else {
    const rowText = await row.innerText();
    if (!rowText.includes(want.name)) fails.push(`หน้ารายการจอง: แถวไม่มีชื่อ ${want.name}`);
    if (!rowText.includes(want.service)) fails.push(`หน้ารายการจอง: แถวไม่ใช่ ${want.service}`);
    if (!rowText.includes(want.time)) fails.push(`หน้ารายการจอง: แถวไม่ใช่เวลา ${want.time}`);
    await row.hover();
  }
  await page.waitForTimeout(2500);
  return { fails, shown };
}

for (const c of cases) {
  const name = `case${c.id}-${c.slug}`;

  test(`${name}: ${c.action}`, async ({ page }) => {
    const turns: Turn[] = [];
    const result = { id: c.id, name, passed: false, failures: [] as string[], turns, booking: null as unknown };

    const doStep = async (s: Step) => {
      const bot = s.chip ? await clickChip(page, s.chip) : await ask(page, s.type!);
      turns.push({ user: s.chip ? `[กดปุ่ม ${s.chip}]` : s.type!, bot });
    };

    try {
      await openChat(page);
      for (const s of c.steps) await doStep(s);

      if (c.booking) {
        // LLM จริงบางตัวขอให้ยืนยันก่อน -> ส่งข้อความยืนยันเพิ่มจนกว่าการ์ดจะขึ้น
        for (const msg of c.confirm ?? []) {
          if (await page.getByTestId("booking-card").count()) break;
          await doStep({ type: msg });
        }
        const b = await checkBooking(page, c.booking);
        result.booking = b.shown;
        result.failures.push(...b.fails);
      } else {
        await page.waitForTimeout(FINAL_HOLD); // ค้างให้อ่านคำตอบสุดท้าย
      }
      result.failures.push(...runChecks(c.checks, turns.map((t) => t.bot)));
    } catch (e) {
      result.failures.push("เทสต์หยุดกลางทาง: " + String((e as Error).message).split("\n")[0]);
    } finally {
      // บันทึกคำตอบจริงทุกข้อความ (ใช้ทำรายงาน) แม้เคสจะไม่ผ่าน
      result.passed = result.failures.length === 0;
      const dir = path.join(OUT_DIR, "answers");
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, `case${c.id}.json`), JSON.stringify(result, null, 2));
    }
    expect(result.failures, "เงื่อนไขที่ไม่ผ่าน").toEqual([]);
  });
}
