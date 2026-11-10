exports.ids = ['f_add_button', 'f_add_enter', 'f_no_blank', 'f_trim_clear', 'f_count', 'f_done', 'f_filter', 'f_delete', 'f_persist'];
exports.run = async h => {
  const { page } = h;
  const box = page.getByPlaceholder('เพิ่มงานใหม่');
  const left = async n => new RegExp('เหลือ\\s*' + n + '\\s*งาน').test(await h.text());
  await h.run('f_add_button', async () => { await box.fill('ซื้อนม'); await h.button('เพิ่ม').click(); await h.settle(); return (await h.text()).includes('ซื้อนม') || 'กด "เพิ่ม" แล้วไม่มีงาน'; });
  await h.run('f_add_enter', async () => { await box.fill('ส่งรายงาน'); await box.press('Enter'); await h.settle(); return (await h.text()).includes('ส่งรายงาน') || 'กด Enter แล้วไม่เพิ่ม'; });
  await h.run('f_no_blank', async () => { await box.fill('   '); await box.press('Enter'); await h.settle(); await box.fill(''); await h.button('เพิ่ม').click(); await h.settle();
    return (await left(2)) || 'งานว่างถูกเพิ่ม (ต้องเหลือ 2 งาน)'; });
  await h.run('f_trim_clear', async () => { await box.fill('  ล้างรถ  '); await box.press('Enter'); await h.settle();
    return ((await box.inputValue()) === '' && (await left(3))) || 'เพิ่มแล้วช่องไม่ล้าง หรือจำนวนไม่ถูก'; });
  await h.run('f_count', async () => (await left(3)) || 'ไม่พบ "เหลือ 3 งาน"');
  await h.run('f_done', async () => { await page.getByRole('checkbox').first().check(); await h.settle(); return (await left(2)) || 'ติ๊กเสร็จแล้วไม่เป็น "เหลือ 2 งาน"'; });
  await h.run('f_filter', async () => {
    await h.button('เสร็จแล้ว').click(); await h.settle(); let t = await h.text();
    if (!t.includes('ซื้อนม') || t.includes('ส่งรายงาน') || t.includes('ล้างรถ')) return 'กรอง "เสร็จแล้ว" ไม่ถูก';
    await h.button('ยังไม่เสร็จ').click(); await h.settle(); t = await h.text();
    if (t.includes('ซื้อนม') || !t.includes('ส่งรายงาน')) return 'กรอง "ยังไม่เสร็จ" ไม่ถูก';
    await h.button('ทั้งหมด').click(); await h.settle(); t = await h.text();
    return (t.includes('ซื้อนม') && t.includes('ล้างรถ')) || 'กรอง "ทั้งหมด" ไม่ถูก'; });
  await h.run('f_delete', async () => { const ok = await h.clickInCard('ส่งรายงาน', 'ลบ'); await h.settle();
    const t = await h.text(); return (ok && !t.includes('ส่งรายงาน') && (await left(1))) || 'ลบ "ส่งรายงาน" แล้วไม่หาย หรือจำนวนไม่ถูก'; });
  await h.reload();
  await h.run('f_persist', async () => { const t = await h.text();
    const checked = await page.getByRole('checkbox', { checked: true }).count();
    return (t.includes('ซื้อนม') && t.includes('ล้างรถ') && (await left(1)) && checked === 1) || `รีเฟรชแล้วงานหรือสถานะเสร็จหาย (ติ๊กอยู่ ${checked})`; });
};

exports.addText = async (h, t) => { const b = h.page.getByPlaceholder('เพิ่มงานใหม่'); await b.fill(t); await b.press('Enter'); await h.settle(); };
exports.smoke = async h => { await exports.addText(h, 'งานทดสอบ'); return (await h.text()).includes('งานทดสอบ'); };
