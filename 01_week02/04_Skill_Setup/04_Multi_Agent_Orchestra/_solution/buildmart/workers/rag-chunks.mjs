// workers/rag-chunks.mjs — ดูผลการดึงข้อความ + chunk ของ PDF (ไม่แตะ DB/embedder)
// รัน: docker compose -p buildmart exec rag-worker node rag-chunks.mjs /app/docs/BM-DS-CEM.pdf [--units]
import { readFileSync } from 'node:fs';
import { extractDocument, buildChunks } from './lib/pdf.js';

const file = process.argv[2];
if (!file) {
  console.error('usage: node rag-chunks.mjs <file.pdf> [--units]');
  process.exit(2);
}
const doc = await extractDocument(readFileSync(file));
console.log(`# ${doc.title} · ${doc.pages} หน้า · ${doc.tagged ? 'Tagged PDF (ใช้โครงสร้าง)' : 'ไม่มีโครงสร้าง (ใช้พิกัด)'}`);
if (process.argv.includes('--units')) {
  for (const u of doc.units) console.log(JSON.stringify(u));
  process.exit(0);
}
const chunks = buildChunks(doc.units);
chunks.forEach((c, i) => console.log(`\n--- chunk ${i} · หน้า ${c.page} · ${c.content.length} ตัวอักษร\n${c.content}`));
console.log(`\nรวม ${chunks.length} chunks`);
