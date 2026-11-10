exports.ids = ['f_labels', 'f_empty_name', 'f_bad_email', 'f_bad_phone', 'f_success', 'f_form_reset', 'f_phone_dash', 'f_duplicate', 'f_persist'];
exports.run = async h => {
  const { page } = h;
  const name = page.getByLabel('ชื่อ-นามสกุล'), email = page.getByLabel('อีเมล'), phone = page.getByLabel('เบอร์โทร'), round = page.getByLabel('รอบอบรม');
  const submit = async (n, e, p) => { await name.fill(n); await email.fill(e); await phone.fill(p); await h.button('สมัคร').click(); await h.settle(); };
  await h.run('f_labels', async () => { await name.fill('x'); await email.fill('x'); await phone.fill('1'); await round.selectOption({ label: 'รอบบ่าย' }); await name.fill(''); await email.fill(''); await phone.fill(''); });
  await h.run('f_empty_name', async () => { await submit('   ', 'a@b.co', '0812345678');
    const t = await h.text(); return (t.includes('กรุณากรอกชื่อ-นามสกุล') && !/ผู้สมัคร\s*1\s*คน/.test(t)) || 'ชื่อว่าง (ช่องว่างล้วน) แต่ไม่ขึ้นข้อความเตือน หรือถูกบันทึก'; });
  await h.run('f_bad_email', async () => { await submit('สมชาย ใจดี', 'somchai@', '0812345678');
    const t = await h.text(); return (t.includes('อีเมลไม่ถูกต้อง') && !/ผู้สมัคร\s*1\s*คน/.test(t)) || 'อีเมลผิดแต่ไม่ขึ้น "อีเมลไม่ถูกต้อง"'; });
  await h.run('f_bad_phone', async () => { await submit('สมชาย ใจดี', 'somchai@mail.com', '181234567');
    let t = await h.text(); if (!t.includes('เบอร์โทรไม่ถูกต้อง') || /ผู้สมัคร\s*1\s*คน/.test(t)) return 'เบอร์ 9 หลักแต่ไม่เตือน';
    await submit('สมชาย ใจดี', 'somchai@mail.com', '1812345678'); t = await h.text();
    return (t.includes('เบอร์โทรไม่ถูกต้อง') && !/ผู้สมัคร\s*1\s*คน/.test(t)) || 'เบอร์ไม่ขึ้นต้นด้วย 0 แต่ผ่าน'; });
  await h.run('f_success', async () => { await submit('สมชาย ใจดี', 'somchai@mail.com', '0812345678');
    const t = await h.text(); return (t.includes('สมัครสำเร็จ') && /ผู้สมัคร\s*1\s*คน/.test(t) && t.includes('สมชาย ใจดี') && !t.includes('เบอร์โทรไม่ถูกต้อง')) || 'ข้อมูลถูกแต่ไม่สำเร็จ หรือข้อความเตือนเก่ายังค้าง'; });
  await h.run('f_form_reset', async () => ((await name.inputValue()) === '' && (await email.inputValue()) === '') || 'สมัครแล้วฟอร์มไม่ล้าง');
  await h.run('f_phone_dash', async () => { await submit('สมหญิง รักเรียน', 'somying@mail.com', '081-234 5679');
    return (/ผู้สมัคร\s*2\s*คน/.test(await h.text())) || 'เบอร์ที่มีขีด/เว้นวรรคคั่น (081-234 5679) ไม่ผ่าน'; });
  await h.run('f_duplicate', async () => { await submit('คนซ้ำ', 'SOMCHAI@mail.com', '0899999999');
    const t = await h.text(); return (t.includes('อีเมลนี้สมัครแล้ว') && !/ผู้สมัคร\s*3\s*คน/.test(t)) || 'อีเมลซ้ำ (ต่างตัวพิมพ์) ไม่ถูกจับ'; });
  await h.reload();
  await h.run('f_persist', async () => { const t = await h.text(); return (/ผู้สมัคร\s*2\s*คน/.test(t) && t.includes('สมชาย ใจดี')) || 'รีเฟรชแล้วรายชื่อหาย'; });
};

exports.addText = async (h, t) => { const p = h.page; await p.getByLabel('ชื่อ-นามสกุล').fill(t); await p.getByLabel('อีเมล').fill('probe@mail.com'); await p.getByLabel('เบอร์โทร').fill('0811111111'); await h.button('สมัคร').click(); await h.settle(); };
exports.smoke = async h => { await exports.addText(h, 'ผู้ทดสอบ'); return /ผู้สมัคร\s*1\s*คน/.test(await h.text()); };
exports.invalid = async h => { await h.button('สมัคร').click(); await h.settle(); return h.page.getByLabel('ชื่อ-นามสกุล'); };
