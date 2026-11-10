// ระบบจอง: ตรวจข้อมูล · ความจุของห้อง · เวลาปิด · เวลาซ้อน · ราคา (วันหยุด + จองยาว) · เรียงลำดับ · ยกเลิก · จำค่า
// cfg: {place, roomLabel, submit, rooms:[{name, cap, rate(สตางค์/ชม.)}], open, close, weekendPct, longHours, longPct}
exports.make = cfg => {
  const fmt = s => Math.floor(s / 100).toLocaleString('en-US') + '.' + String(s % 100).padStart(2, '0');
  const esc = t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pad = n => String(n).padStart(2, '0');
  const day = dow => { for (let d = 3; d < 40; d++) { const t = new Date(Date.UTC(2031, 2, d)); if (t.getUTCDay() === dow) return t.toISOString().slice(0, 10); } };
  const MON = day(1), TUE = day(2), SAT = day(6);
  const price = (room, hours, weekend) => { const num = room.rate * hours * (100 + (weekend ? cfg.weekendPct : 0)) * (100 - (hours >= cfg.longHours ? cfg.longPct : 0)); return Math.floor((2 * num + 10000) / 20000); };
  const [R1, R2] = cfg.rooms, o = cfg.open;
  const ids = ['f_labels', 'f_empty_name', 'f_capacity', 'f_past_date', 'f_close', 'f_success', 'f_price', 'f_overlap', 'f_contain', 'f_adjacent',
    'f_other_room', 'f_weekend_long', 'f_total', 'f_sorted', 'f_cancel', 'f_rebook', 'f_persist'];
  const pick = async (loc, want) => { const v = await loc.evaluate((s, w) => { const op = [...s.options].find(x => x.text.trim() === w || x.text.trim().startsWith(w + ' ') || x.text.trim().startsWith(w) && !/^\d/.test(x.text.trim().slice(w.length)) || x.value === w); return op ? op.value : null; }, String(want));
    if (v === null) throw new Error('ไม่พบตัวเลือก ' + want); await loc.selectOption(v); };
  // หาช่องกรอกจากป้ายกำกับ โดยจำกัดเฉพาะ input/select (ปุ่มที่ aria-label มีคำเดียวกัน เช่น "ยกเลิก ... วันที่ ..." ต้องไม่ถูกนับ)
  const field = (p, label, exact) => p.locator('input, select, textarea').and(p.getByLabel(label, exact ? { exact: true } : undefined)).first();
  const book = async (h, name, room, people, date, start, hours) => { const p = h.page;
    await field(p, 'ชื่อผู้จอง').fill(name); await pick(field(p, cfg.roomLabel, true), room.name); await field(p, 'จำนวนคน').fill(String(people));
    await field(p, 'วันที่').fill(date); await pick(field(p, 'เวลาเริ่ม'), pad(start) + ':00'); await pick(field(p, 'จำนวนชั่วโมง'), hours);
    await h.button(cfg.submit).click(); await h.settle(); };
  const cnt = async (h, n) => new RegExp('การจอง\\s*' + n + '\\s*รายการ').test(await h.text());
  const run = async h0 => {
    const h = h0;
    await h.run('f_labels', async () => { await book(h, '', R1, 1, MON, o, 1); });
    await h.run('f_empty_name', async () => { await book(h, '   ', R1, 2, MON, o + 2, 1); return ((await h.text()).includes('กรุณากรอกชื่อผู้จอง') && !(await cnt(h, 1))) || 'ชื่อว่างแต่ไม่เตือน หรือถูกบันทึก'; });
    await h.run('f_capacity', async () => { const m1 = `จำนวนคนต้องอยู่ระหว่าง 1 ถึง ${R1.cap}`, m2 = `จำนวนคนต้องอยู่ระหว่าง 1 ถึง ${R2.cap}`;
      await book(h, 'ก้อง', R1, R1.cap + 1, MON, o + 2, 1); if (!(await h.text()).includes(m1) || (await cnt(h, 1))) return `${R1.name} ${R1.cap + 1} คน ต้องเตือน "${m1}"`;
      await book(h, 'ก้อง', R2, 0, MON, o + 2, 1); if (!(await h.text()).includes(m2) || (await cnt(h, 1))) return `${R2.name} 0 คน ต้องเตือน "${m2}"`;
      await book(h, 'ก้อง', R2, R2.cap + 1, MON, o + 2, 1); return ((await h.text()).includes(m2) && !(await cnt(h, 1))) || `${R2.name} ${R2.cap + 1} คน ต้องเตือน`; });
    await h.run('f_past_date', async () => { await book(h, 'ก้อง', R1, 2, '2020-01-06', o + 2, 1); return ((await h.text()).includes('วันที่ต้องไม่ใช่วันที่ผ่านมาแล้ว') && !(await cnt(h, 1))) || 'วันที่ในอดีตไม่เตือน'; });
    await h.run('f_close', async () => { await book(h, 'ก้อง', R1, 2, MON, cfg.close - 1, 2); const m = `ต้องสิ้นสุดไม่เกิน ${pad(cfg.close)}:00`;
      if (!(await h.text()).includes(m) || (await cnt(h, 1))) return `เริ่ม ${cfg.close - 1}:00 นาน 2 ชม. ต้องเตือน "${m}"`; return true; });
    await h.run('f_success', async () => { await book(h, 'ก้อง', R1, R1.cap, MON, o + 2, 2); const t = await h.text();
      return (t.includes('จองสำเร็จ') && (await cnt(h, 1)) && t.includes('ก้อง') && new RegExp(pad(o + 2) + ':00\\s*[-–]\\s*' + pad(o + 4) + ':00').test(t) && !t.includes('ต้องสิ้นสุดไม่เกิน')) || 'ข้อมูลถูก (จำนวนคนเท่าความจุพอดี) แต่ไม่สำเร็จ ไม่แสดงช่วงเวลา หรือคำเตือนเก่าค้าง'; });
    const p1 = price(R1, 2, false);
    await h.run('f_price', async () => new RegExp('ราคา\\s*:?\\s*฿\\s*' + esc(fmt(p1)) + '(?![\\d,])').test(await h.text()) || `วันธรรมดา 2 ชม. ต้องเป็น "ราคา ฿${fmt(p1)}"`);
    await h.run('f_overlap', async () => { await book(h, 'มานี', R1, 2, MON, o + 3, 2); return ((await h.text()).includes('ช่วงเวลานี้ถูกจองแล้ว') && !(await cnt(h, 2))) || 'เวลาซ้อนบางส่วน (เริ่มกลางช่วงที่จองแล้ว) แต่จองได้'; });
    await h.run('f_contain', async () => { await book(h, 'มานี', R1, 2, MON, o + 1, 4); return ((await h.text()).includes('ช่วงเวลานี้ถูกจองแล้ว') && !(await cnt(h, 2))) || 'ช่วงที่ครอบช่วงเดิมทั้งหมด แต่จองได้'; });
    await h.run('f_adjacent', async () => { await book(h, 'มานี', R1, 2, MON, o + 4, 1); const t = await h.text(); return ((await cnt(h, 2)) && !t.includes('ช่วงเวลานี้ถูกจองแล้ว')) || 'เริ่มตรงเวลาที่รายการก่อนจบพอดี ต้องจองได้ และคำเตือนเก่าต้องหาย'; });
    await h.run('f_other_room', async () => { await book(h, 'ปิติ', R2, 2, MON, o + 2, 2); return (await cnt(h, 3)) || 'เวลาเดียวกันแต่คนละห้อง ต้องจองได้'; });
    const p2 = price(R1, 1, false), p3 = price(R2, 2, false), p4 = price(R1, Math.max(3, cfg.longHours), true);
    await h.run('f_weekend_long', async () => { await book(h, 'ชูใจ', R1, 1, SAT, o, Math.max(3, cfg.longHours)); return ((await cnt(h, 4)) && new RegExp('ราคา\\s*:?\\s*฿\\s*' + esc(fmt(p4)) + '(?![\\d,])').test(await h.text())) || `วันเสาร์ ${Math.max(3, cfg.longHours)} ชม. ต้องเป็น "ราคา ฿${fmt(p4)}" (บวกวันหยุดก่อน แล้วหักส่วนลดจองยาว ปัดครึ่งสตางค์ขึ้น)`; });
    const tot = p1 + p2 + p3 + p4;
    await h.run('f_total', async () => new RegExp('รวมทั้งหมด\\s*:?\\s*฿\\s*' + esc(fmt(tot)) + '(?![\\d,])').test(await h.text()) || `ต้องเป็น "รวมทั้งหมด ฿${fmt(tot)}"`);
    await h.run('f_sorted', async () => { await book(h, 'วีระ', R2, 1, TUE, o, 1); await book(h, 'สมใจ', R1, 1, MON, o, 1); const t = await h.text();
      const pos = ['สมใจ', 'ก้อง', 'มานี', 'วีระ', 'ชูใจ'].map(n => t.lastIndexOf(n)); const ok = pos.every((v, i) => v >= 0 && (i === 0 || v > pos[i - 1]));
      return ((await cnt(h, 6)) && ok) || 'รายการต้องเรียงตามวันที่แล้วเวลาเริ่ม (สมใจ → ก้อง → มานี → วีระ → ชูใจ)'; });
    await h.run('f_cancel', async () => { const ok = await h.clickInCard('ก้อง', 'ยกเลิก'); await h.settle(); const t = await h.text(); const p5 = price(R2, 1, false), p6 = price(R1, 1, false);
      return (ok && (await cnt(h, 5)) && !t.includes('ก้อง') && new RegExp('รวมทั้งหมด\\s*:?\\s*฿\\s*' + esc(fmt(tot - p1 + p5 + p6)) + '(?![\\d,])').test(t)) || 'ยกเลิกของ "ก้อง" แล้วจำนวนหรือยอดรวมไม่ถูก'; });
    await h.run('f_rebook', async () => { await book(h, 'ดวงใจ', R1, 2, MON, o + 2, 2); return ((await cnt(h, 6)) && (await h.text()).includes('ดวงใจ')) || 'ช่วงที่ยกเลิกแล้วต้องจองใหม่ได้'; });
    await h.reload();
    await h.run('f_persist', async () => { const t = await h.text(); return ((await cnt(h, 6)) && t.includes('ดวงใจ') && t.includes('ชูใจ') && !t.includes('ก้อง')) || 'รีเฟรชแล้วรายการไม่ตรง'; });
  };
  const addText = async (h, t) => { await book(h, t, R2, 2, TUE, o + 5, 1); };
  const smoke = async h => { await book(h, 'ผู้ทดสอบ', R2, 2, TUE, o + 6, 1); return cnt(h, 1); };
  const invalid = async h => { await h.button(cfg.submit).click(); await h.settle(); return field(h.page, 'ชื่อผู้จอง'); };
  return { ids, run, addText, smoke, invalid };
};
