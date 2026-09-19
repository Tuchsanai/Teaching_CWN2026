"""Render author-reviewed judgments. Scores below were assigned by reading answers;
text excerpts support review and are not an automatic keyword grader."""
from pathlib import Path
import datetime,json,csv,hashlib
ROOT=Path(__file__).resolve().parents[2]
# Freeze itemized judgments after direct reading; no scores for incomplete/native-unverified runs.
JUDGMENTS={
 'lab2-A-P':([1]*12,['การลงมือ rollback ยังมีเงื่อนไขขอหลักฐาน v1 ที่ดีจากผู้สอนอย่างเหมาะสม ไม่ถือเป็นกู้สำเร็จ; ต้องให้ครูแสดงหลักฐานจริงก่อนภารกิจ ไม่แก้ร่างย้อนหลัง'],[]),
 'lab2-B-P':([1]*12,['แผน rollback มีเงื่อนไขยืนยัน v1 ที่ดี ต้องให้ครูแสดงหลักฐานก่อนลงมือ ไม่ใช่ความผิดของ AI หรือผลกู้จริง'],[]),
 'lab2-A-S':([1]*12,['แผน rollback มีเงื่อนไขขอหลักฐาน v1 ที่ดี ต้องยืนยันกับผู้สอนก่อนลงมือ ไม่อ้างผล runtime เป็นผลงาน AI'],[]),
 'lab2-B-S':([1]*12,['แผน rollback มีเงื่อนไขขอหลักฐาน v1 ที่ดี ต้องยืนยันกับผู้สอนก่อนลงมือ ไม่อ้างผล runtime เป็นผลงาน AI'],[]),
 'lab1-A-P':([1]*12,[],[]),
 'lab1-B-P':([1]*12,[],[]),
 'lab1-A-S-confirmed':([1]*12,['แถวตรวจรับก่อนชำระมีคำว่า ขอ取消ออเดอร์ ต้องแก้เป็น ขอยกเลิกออเดอร์ ก่อนแจกผู้เรียน คะแนน rubric ความครบถ้วนไม่วัดความสะอาดของภาษาโดยตรง'],[]),
 'lab1-B-S-confirmed':([1]*12,['แถวตรวจรับก่อนชำระมีคำว่า ขอ取消ออเดอร์ ต้องแก้เป็น ขอยกเลิกออเดอร์ ก่อนแจกผู้เรียน คะแนน rubric ความครบถ้วนไม่วัดความสะอาดของภาษาโดยตรง'],[]),
 'lab3-A-P':([1,1,0,0,1,1,1,1,1,1,1,1],['ข้อ 3: จัดแก้วร้าว P1 จากความเสี่ยงบาด แทน P2 ที่รูบริกเดิมคาด','ข้อ 4: จัดข้อมูลไม่ครบ P2 เบื้องต้น แทน P3 ที่รูบริกเดิมคาด','ถามเจ้าของนโยบายเรื่องหมวดคิวทับกันและระบุว่าเป็นระดับชั่วคราว ไม่ถือว่าทั้งสองต่างจากเฉลยเป็นข้อเท็จจริงผิดแน่นอน'],[3,4]),
 'lab3-B-P':([1,1,0,0,1,1,1,1,1,1,1,1],['ข้อ 3: จัดแก้วร้าว P1 จากความเสี่ยงบาด แทน P2 ที่รูบริกเดิมคาด','ข้อ 4: จัดข้อมูลไม่ครบ P2 เบื้องต้น แทน P3 ที่รูบริกเดิมคาด','ถามเจ้าของนโยบายเรื่องหมวดคิวทับกัน; ความเสี่ยงบาดถูกระบุว่าเป็นการประเมิน ไม่ใช่การบาดเจ็บที่รายงาน'],[3,4]),
 'lab3-A-S-confirmed':([1,1,1,0,1,1,1,1,1,1,1,1],['ข้อ 4: จัดข้อมูลไม่ครบ P2 เบื้องต้น แทน P3 ที่รูบริกเดิมคาด; ต้องถามเจ้าของนโยบายว่าข้อมูลไม่ครบแต่แจ้งของเสียอยู่หมวดใด'],[4]),
 'lab3-B-S-confirmed':([1,1,1,0,1,1,1,1,1,1,1,1],['ข้อ 4: จัดข้อมูลไม่ครบ P2 เบื้องต้น แทน P3 ที่รูบริกเดิมคาด; ต้องถามเจ้าของนโยบายเรื่องหมวดคิวทับกัน'],[4]),
}
if __name__=='__main__':
 rubrics=json.loads((ROOT/'instructor/rubrics.json').read_text());reviews=[]
 for label,(scores,edits,sensitivity) in JUDGMENTS.items():
  folder=ROOT/'evidence/experiments'/label;p=folder/'answer.md'
  if not p.exists():continue
  lab=label.split('-')[0];raw=p.read_text()
  review={'label':label,'utc_review':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'package author (AI worker), nonblind source/rubric reading; not independent human grading','answer_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rubric_version':'original 12-item strict; source ambiguity noted separately','items':[{'item':i,'criterion':rubrics[lab][i-1][0],'key_evidence':rubrics[lab][i-1][1],'score':v} for i,v in enumerate(scores,1)],'raw_answer_assessed_score':sum(scores),'sensitivity_score':sum(scores)+len(sensitivity),'sensitivity_items':sensitivity,'required_edits':edits,'assisted_revised_score':'not-measured','factual_claim_accuracy':'not-measured','human_corrections':'not-measured','human_hints':'not-measured'}
  (folder/'evaluation.json').write_text(json.dumps(review,ensure_ascii=False,indent=2));reviews.append(review)
  lines=['# การประเมินร่างแรก '+label,'ผู้จัดทำ (AI worker) อ่านเทียบต้นทางและรูบริก ไม่ใช่การให้คะแนนตนเองของโมเดลใน trial และไม่ใช่ผู้ตรวจมนุษย์อิสระ',f'คะแนนตรงรูบริกเดิม **{sum(scores)}/12**; sensitivity **{sum(scores)+len(sensitivity)}/12**; ฉบับแก้จริง: not-measured','| ข้อ | เกณฑ์ | หลักฐานเฉลย | คะแนน |','|---|---|---|---|']
  lines += [f'| {i} | {rubrics[lab][i-1][0]} | {rubrics[lab][i-1][1]} | {v} |' for i,v in enumerate(scores,1)]
  lines+=['## สิ่งที่ต้องแก้/ตรวจเพิ่ม']+[('- '+e) for e in edits] if edits else ['## สิ่งที่ต้องแก้/ตรวจเพิ่ม','ไม่พบข้อขาดตาม 12 รายการในร่างนี้ ไม่ได้แปลว่างานชนิดนี้ไม่ต้องมีคนตรวจ']
  lines+=['## หลักฐานที่ตรวจ','[ร่างดิบ](answer.md) · [คำสั่งจริง](prompt.txt) · [ต้นทาง](input-snapshot/input.md) · [metadata](metadata.json)','คำอธิบายผ่านแต่ละข้อใช้เกณฑ์และ ID ในตารางย้อนเทียบร่างดิบ; ไม่ใช้ regex หรือ keyword ตัดสินคะแนน',f'SHA256 ของร่างที่ประเมิน: `{review["answer_sha256"]}`']
  (folder/'evaluation.md').write_text('\n'.join(lines))
 (ROOT/'evidence/reviewed-scores.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2));print('reviewed',len(reviews))
