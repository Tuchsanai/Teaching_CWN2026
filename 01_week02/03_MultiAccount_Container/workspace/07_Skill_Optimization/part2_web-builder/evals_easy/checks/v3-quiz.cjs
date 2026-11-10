exports.ids = ['f_heading', 'f_questions', 'f_incomplete', 'f_score', 'f_best', 'f_retry', 'f_perfect', 'f_best_keeps_max', 'f_persist'];
// คำตอบที่ถูก: ข้อ 1 Dockerfile · ข้อ 2 docker ps · ข้อ 3 -p · ข้อ 4 docker compose up
exports.run = async h => {
  const { page } = h;
  const pick = async l => { await page.getByLabel(l, { exact: true }).first().check(); };
  const sub = async () => { await h.button('ส่งคำตอบ').click(); await h.settle(); };
  await h.run('f_heading', async () => (await page.locator('h1').first().innerText()).includes('ควิซ Docker') || 'h1 ไม่ถูก');
  await h.run('f_questions', async () => { const n = await page.getByRole('radio').count(); return n === 12 || `ตัวเลือกแบบ radio ${n} (ต้อง 12)`; });
  await h.run('f_incomplete', async () => { await pick('Dockerfile'); await sub();
    const t = await h.text(); return (t.includes('กรุณาตอบให้ครบทุกข้อ') && !/คะแนน\s*\d\s*\/\s*4/.test(t.replace(/คะแนนสูงสุด\s*\d\s*\/\s*4/, ''))) || 'ตอบไม่ครบแต่ไม่เตือน หรือให้คะแนนเลย'; });
  await h.run('f_score', async () => { await pick('Dockerfile'); await pick('docker ps'); await pick('-v'); await pick('docker compose down'); await sub();
    const t = (await h.text()).replace(/คะแนนสูงสุด\s*\d\s*\/\s*4/, ''); return (/คะแนน\s*:?\s*2\s*\/\s*4/.test(t) && !t.includes('กรุณาตอบให้ครบทุกข้อ')) || 'ถูก 2 ข้อแต่ไม่ขึ้น "คะแนน 2/4" หรือคำเตือนเก่าค้าง'; });
  await h.run('f_best', async () => (await h.has(/คะแนนสูงสุด\s*:?\s*2\s*\/\s*4/)) || 'ไม่พบ "คะแนนสูงสุด 2/4"');
  await h.run('f_retry', async () => { await h.button('ทำใหม่').click(); await h.settle();
    const c = await page.getByRole('radio', { checked: true }).count(); const t = (await h.text()).replace(/คะแนนสูงสุด\s*\d\s*\/\s*4/, '');
    return (c === 0 && !/คะแนน\s*:?\s*\d\s*\/\s*4/.test(t)) || 'กด "ทำใหม่" แล้วคำตอบหรือคะแนนเดิมยังอยู่'; });
  await h.run('f_perfect', async () => { await pick('Dockerfile'); await pick('docker ps'); await pick('-p'); await pick('docker compose up'); await sub();
    return (await h.has(/คะแนนสูงสุด\s*:?\s*4\s*\/\s*4/)) || 'ถูกหมดแต่คะแนนสูงสุดไม่เป็น 4/4'; });
  await h.run('f_best_keeps_max', async () => { await h.button('ทำใหม่').click(); await h.settle();
    await pick('docker-compose.yml'); await pick('docker ls'); await pick('-v'); await pick('docker compose down'); await sub();
    const t = await h.text(); return (/คะแนนสูงสุด\s*:?\s*4\s*\/\s*4/.test(t) && /คะแนน\s*:?\s*0\s*\/\s*4/.test(t.replace(/คะแนนสูงสุด\s*:?\s*\d\s*\/\s*4/, ''))) || 'ทำรอบใหม่ได้ 0 แล้วคะแนนสูงสุดลดลง หรือไม่แสดง 0/4'; });
  await h.reload();
  await h.run('f_persist', async () => (await h.has(/คะแนนสูงสุด\s*:?\s*4\s*\/\s*4/)) || 'รีเฟรชแล้วคะแนนสูงสุดหาย');
};

exports.smoke = async h => { const p = h.page; for (const l of ['Dockerfile', 'docker ps', '-p', 'docker compose up']) await p.getByLabel(l, { exact: true }).first().check(); await h.button('ส่งคำตอบ').click(); await h.settle(); return /คะแนนสูงสุด\s*:?\s*4\s*\/\s*4/.test(await h.text()); };
