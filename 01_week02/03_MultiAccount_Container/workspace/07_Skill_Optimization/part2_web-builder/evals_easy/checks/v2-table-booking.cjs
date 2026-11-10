exports.ids = ['f_labels', 'f_empty_name', 'f_bad_people', 'f_past_date', 'f_success', 'f_duplicate_slot', 'f_second', 'f_cancel', 'f_persist'];
exports.run = async h => {
  const { page } = h;
  const name = page.getByLabel('ชื่อผู้จอง'), people = page.getByLabel('จำนวนคน'), date = page.getByLabel('วันที่'), time = page.getByLabel('เวลา');
  const submit = async (n, p, d, t) => { await name.fill(n); await people.fill(p); await date.fill(d); await time.selectOption({ label: t }); await h.button('จองโต๊ะ').click(); await h.settle(); };
  const cnt = async n => new RegExp('การจอง\\s*' + n + '\\s*รายการ').test(await h.text());
  await h.run('f_labels', async () => { await name.fill('x'); await people.fill('2'); await date.fill('2031-03-10'); await time.selectOption({ label: '19:00' }); });
  await h.run('f_empty_name', async () => { await submit('  ', '2', '2031-03-10', '18:00');
    return ((await h.text()).includes('กรุณากรอกชื่อผู้จอง') && !(await cnt(1))) || 'ชื่อว่างแต่ไม่เตือน'; });
  await h.run('f_bad_people', async () => { await submit('วิชัย', '0', '2031-03-10', '18:00');
    if (!(await h.text()).includes('จำนวนคนต้องอยู่ระหว่าง 1 ถึง 10') || (await cnt(1))) return 'จำนวนคน 0 ไม่เตือน';
    await submit('วิชัย', '11', '2031-03-10', '18:00');
    return ((await h.text()).includes('จำนวนคนต้องอยู่ระหว่าง 1 ถึง 10') && !(await cnt(1))) || 'จำนวนคน 11 ไม่เตือน'; });
  await h.run('f_past_date', async () => { await submit('วิชัย', '4', '2020-01-01', '18:00');
    return ((await h.text()).includes('วันที่ต้องไม่ใช่วันที่ผ่านมาแล้ว') && !(await cnt(1))) || 'วันที่ในอดีตไม่เตือน'; });
  await h.run('f_success', async () => { await submit('วิชัย', '4', '2031-03-10', '18:00');
    const t = await h.text(); return (t.includes('จองสำเร็จ') && (await cnt(1)) && t.includes('วิชัย') && !t.includes('วันที่ต้องไม่ใช่วันที่ผ่านมาแล้ว')) || 'ข้อมูลถูกแต่ไม่สำเร็จ หรือข้อความเตือนเก่าค้าง'; });
  await h.run('f_duplicate_slot', async () => { await submit('มานี', '2', '2031-03-10', '18:00');
    return ((await h.text()).includes('เวลานี้ถูกจองแล้ว') && !(await cnt(2))) || 'จองวันและเวลาซ้ำได้'; });
  await h.run('f_second', async () => { await submit('มานี', '2', '2031-03-10', '19:00'); return (await cnt(2)) || 'จองรายการที่ 2 (คนละเวลา) ไม่ได้'; });
  await h.run('f_cancel', async () => { const ok = await h.clickInCard('วิชัย', 'ยกเลิก'); await h.settle();
    const t = await h.text(); return (ok && (await cnt(1)) && t.includes('มานี')) || 'กด "ยกเลิก" ของวิชัยแล้วรายการไม่ลด'; });
  await h.reload();
  await h.run('f_persist', async () => { const t = await h.text(); return ((await cnt(1)) && t.includes('มานี') && !/วิชัย/.test(t)) || 'รีเฟรชแล้วรายการไม่ตรง'; });
};

exports.addText = async (h, t) => { const p = h.page; await p.getByLabel('ชื่อผู้จอง').fill(t); await p.getByLabel('จำนวนคน').fill('2'); await p.getByLabel('วันที่').fill('2032-05-05'); await p.getByLabel('เวลา').selectOption({ label: '20:00' }); await h.button('จองโต๊ะ').click(); await h.settle(); };
exports.smoke = async h => { await exports.addText(h, 'ผู้ทดสอบ'); return /การจอง\s*1\s*รายการ/.test(await h.text()); };
exports.invalid = async h => { await h.button('จองโต๊ะ').click(); await h.settle(); return h.page.getByLabel('ชื่อผู้จอง'); };
