// workers/rag-selftest.mjs — ทดสอบ Hybrid RAG กับ DB ที่รันอยู่ (เอกสาร 6 ไฟล์ต้อง ready แล้ว)
// รัน: docker compose -p buildmart exec rag-worker node rag-selftest.mjs
//   - คำถามเอกสาร R01–R06, R08 (BUILDMART ข้อ 7 · R07 = ไฟล์อัปโหลด ทดสอบแยก): ไฟล์ที่ถูกต้องต้องอยู่อันดับ 1 (ยอมอันดับ 2 แต่เตือน)
//     และข้อความสำคัญต้องอยู่ใน chunk ที่คืนมา
//   - คำถามทั่วไป (ไม่เกี่ยวกับเอกสาร): ดูค่า vecSim เพื่อเลือกเกณฑ์แสดงป้ายอ้างอิง (CITE_MIN_VECSIM)
import { pool } from './lib/db.js';
import { hybridSearch, CITE_MIN_VECSIM, CITE_MIN_KW, isCiteworthy } from './lib/rag-search.js';

const DOC_CASES = [
  { id: 'R01', q: 'ปูนซีเมนต์เก็บได้นานแค่ไหนครับ', file: 'BM-DS-CEM.pdf', fact: '3 เดือน' },
  { id: 'R02', q: 'สีทาภายนอกรับประกันกี่ปี', file: 'BM-DS-PNT.pdf', fact: '8 ปี' },
  { id: 'R03', q: 'กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม', file: 'BM-DS-TIL.pdf', fact: /0\.5%|R10/ },
  { id: 'R04', q: 'ซื้อปูนไปแล้วเปิดถุง ขอคืนได้ไหม', file: 'BM-POLICY.pdf', fact: 'คืนไม่ได้' },
  { id: 'R05', q: 'ทาบเหล็ก DB12 ต้องยาวเท่าไร', file: 'BM-DS-STL.pdf', fact: '48 ซม.' },
  { id: 'R06', q: 'สาย THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ แล้วเบรกเกอร์ 16A ราคาเท่าไร', file: 'BM-DS-ELC-PIP.pdf', fact: '16–20 A' },
  // R08: ตอบจากตารางหัว 2 ชั้น (ขนาดกระเบื้อง × ฟันเกรียง) — chunk ของแถวต้องมีหัวคอลัมน์ติดมาด้วย
  { id: 'R08', q: 'ปูกระเบื้อง 60x60 ด้วยปูนกาว ต้องใช้เกรียงฟันกี่มิล และใช้ปูนกาวกี่กิโลต่อตารางเมตร', file: 'BM-DS-CEM.pdf', fact: /60x60.*10 มม.*5.5/ },
  // เพิ่มเติม (ถามแบบอื่น / อังกฤษ)
  { id: 'X01', q: 'คอนกรีตต้องบ่มกี่วัน', file: 'BM-DS-CEM.pdf', fact: '7 วัน' },
  { id: 'X02', q: 'ผนังปูนใหม่ต้องรอกี่วันก่อนทาสีรองพื้น', file: 'BM-DS-PNT.pdf', fact: '28 วัน' },
  { id: 'X03', q: 'สมาชิก BuildMart Pro ได้แต้มยังไง', file: 'BM-POLICY.pdf', fact: '100 บาท' },
  { id: 'X04', q: 'ท่อ PVC ชั้น 8.5 ใช้กับน้ำอะไร', file: 'BM-DS-ELC-PIP.pdf', fact: 'น้ำทิ้ง' },
  { id: 'X05', q: 'How long can cement be stored?', file: 'BM-DS-CEM.pdf', fact: '3 เดือน' },
];
const GENERAL = [
  'ร้านเปิดกี่โมงครับ',
  'ปูนซีเมนต์ถุงละเท่าไร',
  'มีสาขาที่ไหนบ้าง',
  'ค่าส่งคิดยังไง',
  'คูปอง BUILD5 ใช้ยังไง',
  'ขอเบอร์โทรสาขาบางนา',
  'สวัสดีครับ',
  'เทคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง',
  'ใครเป็นนายกรัฐมนตรี',
  'What time do you open?',
];

const hasFact = (rows, fact) => rows.some((r) => (fact instanceof RegExp ? fact.test(r.content) : r.content.includes(fact)));
let fail = 0;
const citeDoc = [];
const citeGen = [];
const docTop = [];
console.log('— คำถามเอกสาร —');
for (const c of DOC_CASES) {
  const rows = await hybridSearch(pool, c.q, 4);
  const rank = rows.findIndex((r) => r.filename === c.file) + 1;
  const fact = hasFact(rows, c.fact);
  const ok = rank === 1 && fact;
  const warn = rank === 2 && fact;
  if (!ok && !warn) fail++;
  citeDoc.push([c.id, rows.slice(0, 2).some(isCiteworthy) && rows.slice(0, 2).find(isCiteworthy).filename === c.file]);
  if (c.id.startsWith('R')) docTop.push(rows[0]?.vecSim ?? 0); // เกณฑ์ cite คิดจาก R01–R08
  console.log(
    `${ok ? 'PASS' : warn ? 'WARN' : 'FAIL'} ${c.id} rank=${rank || '-'} fact=${fact ? 'y' : 'n'} ` +
      `top=${rows.map((r) => `${r.filename}#p${r.page}(v${r.vecSim.toFixed(3)} k${r.kwScore})`).join(' ')}  « ${c.q}`,
  );
}
console.log('\n— คำถามทั่วไป (ไม่ควรมีป้ายอ้างอิง) —');
const genTop = [];
for (const q of GENERAL) {
  const rows = await hybridSearch(pool, q, 4);
  const v = Math.max(0, ...rows.map((r) => r.vecSim));
  genTop.push(v);
  citeGen.push([q, rows.slice(0, 2).some(isCiteworthy)]);
  console.log(`maxVecSim=${v.toFixed(3)} top=${rows.slice(0, 2).map((r) => `${r.filename}#p${r.page}(v${r.vecSim.toFixed(3)} k${r.kwScore})`).join(" ")}  « ${q}`);
}
const docMin = Math.min(...docTop);
const genMax = Math.max(...genTop);
console.log(`\nvecSim อันดับ 1 ของ R01–R08: min=${docMin.toFixed(3)} max=${Math.max(...docTop).toFixed(3)}`);
console.log(`vecSim สูงสุดของคำถามทั่วไป:     max=${genMax.toFixed(3)} min=${Math.min(...genTop).toFixed(3)}`);
console.log(`เกณฑ์แนะนำ (กึ่งกลาง) ≈ ${((docMin + genMax) / 2).toFixed(3)} · ค่าที่ใช้ใน rag-search.js CITE_MIN_VECSIM = ${CITE_MIN_VECSIM}`);
const sep = genTop.filter((v) => v >= CITE_MIN_VECSIM).length;
console.log(`คำถามทั่วไปที่ vecSim ≥ เกณฑ์: ${sep}/${GENERAL.length} · คำถามเอกสารที่ < เกณฑ์: ${docTop.filter((v) => v < CITE_MIN_VECSIM).length}/${docTop.length}`);
console.log(`
กฎ cite (vecSim ≥ ${CITE_MIN_VECSIM} และ kwScore ≥ ${CITE_MIN_KW}, อันดับ 1–2):`);
const missDoc = citeDoc.filter(([, ok]) => !ok).map(([id]) => id);
const falseGen = citeGen.filter(([, c]) => c).map(([q]) => q);
console.log(`  คำถามเอกสารที่ได้ cite ไฟล์ถูก: ${citeDoc.length - missDoc.length}/${citeDoc.length}${missDoc.length ? ' · พลาด: ' + missDoc.join(', ') : ''}`);
console.log(`  คำถามทั่วไปที่ได้ cite (ไม่ควรมี): ${falseGen.length}/${citeGen.length}${falseGen.length ? ' · ' + falseGen.join(' | ') : ''}`);
await pool.end();
console.log(fail ? `\nFAILED ${fail}` : '\nALL OK');
process.exit(fail ? 1 : 0);
