const ADD = 'ใส่ตะกร้า';
exports.ids = ['f_heading', 'f_items', 'f_price_format', 'f_search', 'f_search_empty', 'f_cart_count', 'f_cart_total', 'f_persist', 'f_clear'];
exports.run = async h => {
  const { page } = h;
  await h.run('f_heading', async () => (await page.locator('h1').first().innerText()).includes('สวนเล็ก') || 'h1 ไม่ใช่ชื่อร้าน');
  await h.run('f_items', async () => {
    const t = await h.text();
    const miss = ['มอนสเตอร่า', 'ไทรใบสัก', 'กระบองเพชร', 'พลูด่าง', 'ลิ้นมังกร', 'ยางอินเดีย'].filter(x => !t.includes(x));
    const n = await page.getByRole('button', { name: ADD }).count();
    return (miss.length === 0 && n === 6) || `ขาด ${miss.join(',')} · ปุ่ม ${n}`;
  });
  await h.run('f_price_format', async () => (await h.has(/฿\s*1,250/)) || 'ราคา 1250 ไม่มีจุลภาค (฿1,250)');
  const box = page.getByPlaceholder('ค้นหาต้นไม้');
  await h.run('f_search', async () => { await box.fill('พลู'); await h.settle();
    const t = await h.text(); return (t.includes('พลูด่าง') && !t.includes('มอนสเตอร่า') && !t.includes('ลิ้นมังกร')) || 'ค้น "พลู" แล้วยังเห็นสินค้าอื่น'; });
  await h.run('f_search_empty', async () => { await box.fill('กุหลาบ'); await h.settle();
    const t = await h.text(); const ok = t.includes('ไม่พบสินค้า') && !t.includes('พลูด่าง'); await box.fill(''); await h.settle();
    return (ok && (await h.text()).includes('มอนสเตอร่า')) || 'ค้นไม่เจอแล้วไม่ขึ้น "ไม่พบสินค้า" หรือล้างคำค้นแล้วสินค้าไม่กลับมา'; });
  await box.fill('').catch(() => {}); await h.settle();
  await h.clickInCard('มอนสเตอร่า', ADD); await h.clickInCard('กระบองเพชร', ADD);
  await h.run('f_cart_count', async () => (await h.has(/ตะกร้า\s*\(\s*2\s*\)/)) || 'ไม่พบ "ตะกร้า (2)"');
  await h.run('f_cart_total', async () => (await h.has(/รวม\s*:?\s*฿\s*1,370(?![\d,])/)) || 'ไม่พบ "รวม ฿1,370"');
  await h.reload();
  await h.run('f_persist', async () => ((await h.has(/ตะกร้า\s*\(\s*2\s*\)/)) && (await h.has(/รวม\s*:?\s*฿\s*1,370/))) || 'รีเฟรชแล้วตะกร้าหาย');
  await h.run('f_clear', async () => { await h.button('ล้างตะกร้า').click(); await h.settle(); await h.reload();
    return ((await h.has(/ตะกร้า\s*\(\s*0\s*\)/)) && (await h.has(/รวม\s*:?\s*฿\s*0(?![\d,])/))) || 'ล้างตะกร้าแล้วรีเฟรชไม่เป็น 0'; });
};

exports.smoke = async h => { await h.clickInCard('พลูด่าง', 'ใส่ตะกร้า'); return /ตะกร้า\s*\(\s*1\s*\)/.test(await h.text()); };
