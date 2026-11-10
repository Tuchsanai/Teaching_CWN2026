// ร้านค้า: ตะกร้า · จำนวนต่อรายการ · โค้ดส่วนลด 2 แบบ · ค่าส่ง · เลขที่ออเดอร์ · เงินคิดเป็นสตางค์ (จำนวนเต็ม) ทั้งหมด
// cfg: {shop, add, items:[{name, price(สตางค์)}], maxQty, pct:{code, pct}, fixed:{code, off, min}, ship, free}
exports.make = cfg => {
  const fmt = s => (s < 0 ? '-' : '') + Math.floor(Math.abs(s) / 100).toLocaleString('en-US') + '.' + String(Math.abs(s) % 100).padStart(2, '0');
  const esc = t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = (label, s, minus) => new RegExp(esc(label) + '\\s*:?\\s*' + (minus ? '[-−–]?\\s*' : '') + '฿\\s*' + esc(fmt(s)) + '(?![\\d,])');
  const half = (num, den) => Math.floor((2 * num + den) / (2 * den));          // ปัดครึ่งขึ้นด้วยจำนวนเต็ม
  const I = cfg.items, P = n => I.find(i => i.name === n).price;
  const pctOff = sub => half(sub * cfg.pct.pct, 100);
  const ship = (sub, off) => sub === 0 ? 0 : (sub - off >= cfg.free ? 0 : cfg.ship);
  const ids = ['f_items', 'f_add', 'f_plus_minus', 'f_remove_at_zero', 'f_max_qty', 'f_empty', 'f_ship_fee', 'f_ship_free', 'f_pct_round',
    'f_ship_after_discount', 'f_fixed_min', 'f_fixed_ok', 'f_replace', 'f_unknown', 'f_auto_drop', 'f_remove_code', 'f_persist', 'f_order', 'f_order_seq', 'f_thousands'];
  const run = async h0 => {
    const add = async (h, name, n = 1) => { for (let k = 0; k < n; k++) await h.clickInCard(name, cfg.add); };
    const plus = (h, name) => h.page.getByRole('button', { name: 'เพิ่ม ' + name, exact: true }).first();
    const minus = (h, name) => h.page.getByRole('button', { name: 'ลด ' + name, exact: true }).first();
    const code = async (h, c) => { await h.page.locator('input').and(h.page.getByLabel('โค้ดส่วนลด')).first().fill(c); await h.button('ใช้โค้ด').click(); await h.settle(); };
    const sums = async (h, sub, off) => { const t = await h.text(); const sh = ship(sub, off); const bad = [];
      if (!re('ยอดสินค้า', sub).test(t)) bad.push('ยอดสินค้า ฿' + fmt(sub));
      if (!re('ส่วนลด', off, true).test(t)) bad.push('ส่วนลด -฿' + fmt(off));
      if (!re('ค่าส่ง', sh).test(t)) bad.push('ค่าส่ง ฿' + fmt(sh));
      if (!re('ยอดสุทธิ', sub - off + sh).test(t)) bad.push('ยอดสุทธิ ฿' + fmt(sub - off + sh));
      return bad.length ? 'ไม่พบ ' + bad.join(' · ') : true; };
    const count = async (h, n) => new RegExp('ตะกร้า\\s*\\(\\s*' + n + '\\s*\\)').test(await h.text());
    const [A, B, C] = I.map(i => i.name);   // A = รายการที่ราคามีเศษ .50 · C = รายการแพงสุด
    let h = h0;
    await h.run('f_items', async () => { const t = await h.text(); const miss = I.filter(i => !t.includes(i.name) || !t.includes('฿' + fmt(i.price))).map(i => i.name + ' ฿' + fmt(i.price));
      const n = await h.page.getByRole('button', { name: cfg.add }).count(); return (miss.length === 0 && n === I.length) || `ไม่พบ ${miss.join(', ')} · ปุ่ม "${cfg.add}" ${n}`; });
    await h.run('f_empty', async () => { const t = await h.text(); const dis = await h.button('สั่งซื้อ').isDisabled();
      const s = await sums(h, 0, 0); return (t.includes('ตะกร้าว่าง') && dis && s === true) || `ตะกร้าเปล่า: ${t.includes('ตะกร้าว่าง') ? '' : 'ไม่มี "ตะกร้าว่าง" '}${dis ? '' : 'ปุ่มสั่งซื้อยังกดได้ '}${s === true ? '' : s}`; });
    await h.run('f_add', async () => { await add(h, A, 2); await add(h, B, 1); const s = await sums(h, 2 * P(A) + P(B), 0);
      return ((await count(h, 3)) && s === true && !(await h.text()).includes('ตะกร้าว่าง')) || 'เพิ่ม 3 ชิ้น: ' + (s === true ? 'จำนวนในตะกร้าไม่ถูก หรือ "ตะกร้าว่าง" ยังอยู่' : s); });
    await h.run('f_plus_minus', async () => { await plus(h, B).click(); await plus(h, B).click(); await minus(h, A).click(); await h.settle();
      const s = await sums(h, P(A) + 3 * P(B), 0); return ((await count(h, 4)) && s === true) || 'ปุ่ม เพิ่ม/ลด: ' + (s === true ? 'จำนวนไม่ถูก' : s); });
    await h.run('f_remove_at_zero', async () => { await minus(h, A).click(); await h.settle(); const gone = (await minus(h, A).count()) === 0;
      const s = await sums(h, 3 * P(B), 0); return (gone && (await count(h, 3)) && s === true) || 'ลดจนเหลือ 0: ' + (gone ? (s === true ? 'จำนวนไม่ถูก' : s) : 'รายการยังอยู่ในตะกร้า'); });
    h = await h0.fresh();
    await h0.run('f_max_qty', async () => { await add(h, B, 1); for (let k = 0; k < cfg.maxQty + 2; k++) await plus(h, B).click(); await h.settle();
      const t = await h.text(); return ((await count(h, cfg.maxQty)) && t.includes(`สั่งได้สูงสุด ${cfg.maxQty} ชิ้นต่อรายการ`)) || `กดเกิน ${cfg.maxQty} ชิ้น: จำนวนเกิน หรือไม่มีข้อความเตือน`; });
    await h0.run('f_thousands', async () => { await add(h, C, 1); for (let k = 0; k < cfg.maxQty - 1; k++) await plus(h, C).click(); await h.settle();
      return await sums(h, cfg.maxQty * (P(B) + P(C)), 0); });
    h = await h0.fresh();
    await h0.run('f_ship_fee', async () => { await add(h, A, 1); return await sums(h, P(A), 0); });
    await h0.run('f_pct_round', async () => { await code(h, '  ' + cfg.pct.code.toLowerCase() + ' '); const s = await sums(h, P(A), pctOff(P(A)));
      return s === true || `โค้ด ${cfg.pct.code} (พิมพ์เล็ก มีช่องว่าง) กับยอด ฿${fmt(P(A))} ต้องลด ฿${fmt(pctOff(P(A)))} (ครึ่งสตางค์ปัดขึ้น) · ` + s; });
    await h0.run('f_remove_code', async () => { await h.button('ลบโค้ด').click(); await h.settle(); return await sums(h, P(A), 0); });
    h = await h0.fresh();
    const X = cfg.freeCart;       // ตะกร้าที่ยอดสินค้าเท่ากับเกณฑ์ส่งฟรีพอดี
    const subX = X.reduce((s, [n, q]) => s + P(n) * q, 0);
    await h0.run('f_ship_free', async () => { for (const [n, q] of X) await add(h, n, q); return subX === cfg.free ? await sums(h, subX, 0) : 'cfg ผิด'; });
    await h0.run('f_ship_after_discount', async () => { await code(h, cfg.pct.code); const s = await sums(h, subX, pctOff(subX));
      return s === true || 'ยอดหลังหักส่วนลดต่ำกว่าเกณฑ์ส่งฟรี ต้องคิดค่าส่ง · ' + s; });
    h = await h0.fresh();
    await h0.run('f_fixed_min', async () => { await add(h, B, 1); await code(h, cfg.fixed.code); const s = await sums(h, P(B), 0);
      return (s === true && (await h.text()).includes('โค้ดนี้ใช้ได้เมื่อยอดสินค้าตั้งแต่ ฿' + fmt(cfg.fixed.min))) || 'ยอดไม่ถึงขั้นต่ำ: ต้องไม่ลดและมีข้อความบอกขั้นต่ำ · ' + (s === true ? '' : s); });
    const Y = cfg.minCart, subY = Y.reduce((s, [n, q]) => s + P(n) * q, 0);   // ยอดสินค้าเท่ากับขั้นต่ำของโค้ดพอดี (รวม B 1 ชิ้นที่เพิ่มไปแล้ว)
    await h0.run('f_fixed_ok', async () => { for (const [n, q] of Y) await add(h, n, n === B ? q - 1 : q); await code(h, cfg.fixed.code); return subY === cfg.fixed.min ? await sums(h, subY, cfg.fixed.off) : 'cfg ผิด'; });
    await h0.run('f_unknown', async () => { await code(h, 'NOPE999'); const s = await sums(h, subY, cfg.fixed.off);
      return ((await h.text()).includes('ไม่พบโค้ดส่วนลด') && s === true) || 'โค้ดที่ไม่มี: ต้องขึ้น "ไม่พบโค้ดส่วนลด" และโค้ดเดิมยังอยู่ · ' + (s === true ? '' : s); });
    await h0.run('f_replace', async () => { await code(h, cfg.pct.code); return await sums(h, subY, pctOff(subY)); });
    await h0.run('f_auto_drop', async () => { await code(h, cfg.fixed.code); const s1 = await sums(h, subY, cfg.fixed.off); if (s1 !== true) return 'ใส่โค้ดลดคงที่อีกครั้งไม่ได้ · ' + s1;
      const [n] = Y[Y.length - 1]; await minus(h, n).click(); await h.settle(); const s = await sums(h, subY - P(n), 0);
      return s === true || 'ลดของจนยอดต่ำกว่าขั้นต่ำ ส่วนลดต้องหายเอง · ' + s; });
    h = await h0.fresh();
    await add(h, A, 2); await add(h, C, 1); await code(h, cfg.pct.code);
    const subZ = 2 * P(A) + P(C), offZ = pctOff(subZ);
    await h.reload();
    await h0.run('f_persist', async () => { const s = await sums(h, subZ, offZ); return ((await count(h, 3)) && s === true) || 'รีเฟรชแล้วตะกร้าหรือโค้ดหาย · ' + (s === true ? '' : s); });
    await h0.run('f_order', async () => { await h.button('สั่งซื้อ').click(); await h.settle(); const t = await h.text(); const s = await sums(h, 0, 0);
      return (/สั่งซื้อสำเร็จ\s*เลขที่ออเดอร์\s*#0001(?!\d)/.test(t) && ((await count(h, 0)) || t.includes('ตะกร้าว่าง')) && s === true) || 'สั่งซื้อ: ต้องขึ้น "สั่งซื้อสำเร็จ เลขที่ออเดอร์ #0001" และตะกร้ากับโค้ดถูกล้าง · ' + (s === true ? '' : s); });
    await h0.run('f_order_seq', async () => { await h.reload(); await add(h, B, 1); await h.button('สั่งซื้อ').click(); await h.settle();
      return /เลขที่ออเดอร์\s*#0002(?!\d)/.test(await h.text()) || 'ออเดอร์ถัดไปหลังรีเฟรชต้องเป็น #0002'; });
  };
  const smoke = async h => { await h.clickInCard(I[1].name, cfg.add); return new RegExp('ตะกร้า\\s*\\(\\s*1\\s*\\)').test(await h.text()); };
  return { ids, run, smoke };
};
