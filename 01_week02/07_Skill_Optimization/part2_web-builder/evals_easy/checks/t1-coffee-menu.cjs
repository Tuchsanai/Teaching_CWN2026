const ADD = 'เพิ่มลงตะกร้า';
exports.ids = ['f_heading', 'f_items', 'f_filter', 'f_cart_count', 'f_cart_total', 'f_persist', 'f_clear', 'f_clear_persist'];
exports.run = async h => {
  const { page } = h;
  await h.run('f_heading', async () => (await page.locator('h1').first().innerText()).includes('บ้านกาแฟ') || 'h1 ไม่ใช่ชื่อร้าน');
  await h.run('f_items', async () => {
    const t = await h.text();
    const miss = ['เอสเปรสโซ', 'ลาเต้ร้อน', 'คาปูชิโน', 'อเมริกาโน่เย็น', 'ชาไทยเย็น', 'โกโก้เย็น'].filter(x => !t.includes(x));
    const n = await page.getByRole('button', { name: ADD }).count();
    return (miss.length === 0 && n === 6) || `ขาด ${miss.join(',')} · ปุ่มเพิ่ม ${n}`;
  });
  await h.run('f_filter', async () => {
    await h.button('ร้อน').click(); await h.settle();
    let t = await h.text();
    if (t.includes('ชาไทยเย็น') || !t.includes('คาปูชิโน')) return 'กรอง "ร้อน" ไม่ถูก';
    await h.button('เย็น').click(); await h.settle();
    t = await h.text();
    if (t.includes('คาปูชิโน') || !t.includes('ชาไทยเย็น')) return 'กรอง "เย็น" ไม่ถูก';
    await h.button('ทั้งหมด').click(); await h.settle();
    t = await h.text();
    return (t.includes('คาปูชิโน') && t.includes('ชาไทยเย็น')) || 'กรอง "ทั้งหมด" ไม่ถูก';
  });
  await h.clickInCard('เอสเปรสโซ', ADD); await h.clickInCard('เอสเปรสโซ', ADD); await h.clickInCard('ชาไทยเย็น', ADD);
  await h.run('f_cart_count', async () => (await h.has(/ตะกร้า\s*\(\s*3\s*\)/)) || 'ไม่พบ "ตะกร้า (3)"');
  await h.run('f_cart_total', async () => (await h.has(/รวม\s*:?\s*฿\s*160(?![\d,])/)) || 'ไม่พบ "รวม ฿160"');
  await h.reload();
  await h.run('f_persist', async () => ((await h.has(/ตะกร้า\s*\(\s*3\s*\)/)) && (await h.has(/รวม\s*:?\s*฿\s*160(?![\d,])/))) || 'รีเฟรชแล้วตะกร้าหาย');
  await h.run('f_clear', async () => { await h.button('ล้างตะกร้า').click(); await h.settle();
    return ((await h.has(/ตะกร้า\s*\(\s*0\s*\)/)) && (await h.has(/รวม\s*:?\s*฿\s*0(?![\d,])/))) || 'ล้างแล้วไม่เป็น 0'; });
  await h.reload();
  await h.run('f_clear_persist', async () => (await h.has(/ตะกร้า\s*\(\s*0\s*\)/)) || 'ล้างแล้วรีเฟรช ของกลับมา');
};

exports.smoke = async h => { await h.clickInCard('ลาเต้ร้อน', 'เพิ่มลงตะกร้า'); return /ตะกร้า\s*\(\s*1\s*\)/.test(await h.text()); };
