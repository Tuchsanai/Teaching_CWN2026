from pathlib import Path
import json,html,datetime
ROOT=Path(__file__).resolve().parents[2]
blocks=[]
for meta in sorted((ROOT/'evidence/experiments').glob('*/metadata.json')):
 d=json.loads(meta.read_text());folder=meta.parent;label=d['label'];review=json.loads((folder/'evaluation.json').read_text()) if (folder/'evaluation.json').exists() else None
 score=str(review['raw_answer_assessed_score'])+'/12' if review else ('ดู transfer-review (เกณฑ์ /4)' if d['variant']=='C' else 'not-measured')
 native='ไม่ใช้ (P)' if d['condition']=='P' else ('ยืนยันแล้ว' if d['native_read_confirmed'] else 'ยังยืนยันไม่ได้')
 rel='experiments/'+label+'/'
 blocks.append(f'''<article><h2>{html.escape(label)}</h2><p>UTC {d['utc_start']} · {d['seconds']} วินาที · native read: {native} · คะแนนร่างแรก: {score}</p><p><a href="{rel}prompt.txt">Prompt จริง</a> · <a href="{rel}input-snapshot/input.md">ต้นทาง</a> · <a href="{rel}metadata.json">metadata / usage</a> · <a href="{rel}events.jsonl">JSONL</a> · <a href="{rel}answer.md">คำตอบดิบ</a></p><details><summary>อ่านคำตอบดิบ</summary><pre>{html.escape((folder/'answer.md').read_text() if (folder/'answer.md').exists() else 'No answer file')}</pre></details>{'<details><summary>คะแนนรายข้อและสิ่งที่ต้องแก้</summary><pre>'+html.escape(json.dumps(review,ensure_ascii=False,indent=2))+'</pre></details>' if review else ('<p>ผล C แยกจาก A/B: <a href="transfer-review.html">อ่านผลการใช้ซ้ำ</a></p>' if d['variant']=='C' else '<p>ไม่ผ่านหลักฐาน native gate จึงไม่รวมเป็นผลเทียบหลัก</p>')}</article>''')
page='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>Week2 evidence viewer</title><style>*{box-sizing:border-box}body{background:#f3f0e8;color:#14213d;font:18px/1.7 Tahoma,sans-serif;margin:0}main{max-width:1100px;margin:auto;padding:24px}article{padding:24px;margin:24px 0;background:white;border:1px solid #dcd6c8;border-radius:18px}a{color:#2364aa}pre{font:15px/1.8 Tahoma,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:18px}summary{cursor:pointer}h1{font-size:36px}h2{font-size:26px}</style><main><p><a href="../index.html#pilot">← สไลด์</a> · <a href="summary.html">สรุปการประเมิน</a></p><h1>หลักฐานรอบทดลองจริง</h1><p>technical pilot ของผู้จัดทำ ไม่ใช่การศึกษาผู้เรียน · ไม่แทนค่าที่ไม่ได้วัดด้วยศูนย์</p>'''+''.join(blocks)+'</main></html>'
(ROOT/'evidence/index.html').write_text(page)
print('evidence viewer:',len(blocks),'runs')
