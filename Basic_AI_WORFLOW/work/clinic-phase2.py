from pathlib import Path
import json
p=Path(Path('work/clinic-current-run.txt').read_text()); v=json.loads((p/'verification-phase1.json').read_text()); assert v['automated_checks_pass']
with (p/'trace.md').open('a') as f:f.write('''
## Iteration 1 — Critic
- C1 PASS: เอกสารครบ As-Is, Findings, To-Be/Data Model, Mapping/Migration, Gap/Roll-out, Plan v1 และ Mockup สามส่วน; เปิดจริงทั้งจอ 1440 และ 390
- C2 PASS (อ่านเทียบข้อมูล): Findings เก้าประเภทอ้าง R1–R5 และผลกระทบ; วันที่ทุกแบบที่กำกวมเก็บ candidate; R2 เป็นหลักฐานประกอบ ไม่เหมารูปแบบทุกสาขา; ผล Python ยืนยันวันของ R5 สองแบบไม่ใช่พุธ
- C3 PASS: อ่านตรวจชื่อ NFC/trim/casefold และเบอร์ตัดขีด/ช่องว่าง พร้อมกรณี R1–R5 ให้คนยืนยัน; Mermaid สามบล็อก render จริง; UI เก็บ raw วันที่ แสดงสถานะรอยืนยันและไม่มี auto-merge; ผลเปิดเบราว์เซอร์และภาพใน verification-phase1.json
หยุดเฟสแรกเพราะผ่านครบ ไม่จำเป็นต้องแก้ให้ครบสามรอบ ผลตรวจความหมายเป็นการตรวจโดย Codex ในบทสนทนาเดียว

## เฟสสอง — รับ Change Request หลังตรวจเฟสแรก
เพิ่มความยินยอมและการจองเองผ่าน LINE OA ให้ C1 ครอบคลุมทั้งเอกสารและ Mockup
Critic ตรวจ baseline: C1 FAIL เพราะเฟสแรกยังไม่มีสองส่วนนี้; C2 และ C3 ของขอบเขตเดิมยังผ่าน จึงแก้เฉพาะส่วนที่ได้รับผลกระทบ

## Iteration 2 — Generator
เพิ่มกระบวนการและแบบจำลองความยินยอม/LINE, Impact/Reuse และ Plan v2 พร้อม Mockup สองส่วนใหม่ คงเอกสารและสามหน้าจอเฟสแรก รอตรวจซ้ำทั้งหมด
''')
cr='''# Change Request ของโจทย์คลินิก
เพิ่มการเก็บความยินยอมของคนไข้และการจองเองผ่าน LINE OA ในเอกสารและ mockup.html ตามโจทย์ที่อัปเดต ตรวจ baseline ก่อนแก้ คง raw และผลที่ผ่าน บันทึกผลกระทบ การใช้ผลงานเดิมต่อ และ Plan v1 → v2 ใช้ C1–C3 เดิมโดย C1 รวมข้อกำหนดใหม่ เก็บผลเฟสแรกแยกไว้ และตรวจด้วยหลักฐานใหม่ ไม่เชื่อมบริการจริง
'''
(p/'prompt-phase2.md').write_text(cr)
old=Path('lab-results/loop/3_clinic_migration/run-2026-09-17-074505/output.md').read_text()
extra=old[old.index('## ข้อกำหนดใหม่และขอบเขต'):]
extra+='''
## Mockup ส่วนเพิ่ม (updated: change request)

เพิ่มสองส่วนต่อท้ายสามส่วนเดิมใน mockup.html:
- ความยินยอม: วัตถุประสงค์ รุ่นข้อความ การตัดสินใจ เวลา และสถานะถอนตรงกับ ConsentRecord แสดงว่าเป็นข้อความตัวอย่างรอยืนยัน ไม่มีตัวเลือกที่ติ๊กไว้ล่วงหน้า
- จองผ่าน LINE OA: แสดงสถานะตัวตนตาม LineIdentity.verification_status, สาขา/บริการ/เวลา และสถานะ BookingRequest ก่อนสร้าง Appointment หน้าจอเป็นภาพจำลอง ไม่เชื่อม LINE จริง ไม่ผูกตัวตนจากชื่อแสดงผล

Impact (ผลกระทบ): เพิ่มหน้าจอสองส่วนและรายการทางลัด พร้อมตรวจความสอดคล้องกับแบบจำลองส่วนเพิ่ม
Reuse (นำผลงานเดิมมาใช้ต่อ): คงตารางนัดหมาย ฟอร์มเจ้าหน้าที่ และคิวตรวจข้อมูลของเฟสแรก เพราะข้อมูลใหม่ไม่ได้แก้ความกำกวมของ R1–R5
Plan v2 รวมงาน Mockup ส่วนเพิ่มและการตรวจภาพทั้งห้าส่วน เก็บ mockup-phase1.html เพื่อเปรียบเทียบ
'''
(p/'output.md').write_text((p/'output-phase1.md').read_text()+'\n'+extra)
html=(p/'mockup-phase1.html').read_text()
addition='''<section id="consent"><span class="count">04 / เพิ่มหลัง Change Request</span><h2>บันทึกความยินยอม</h2><p class="muted">ข้อมูลจำลอง · ConsentRecord · ข้อความและนโยบายรอยืนยัน</p><div class="grid"><div><h3>วัตถุประสงค์และรุ่นข้อความ</h3><p>รอผู้รับผิดชอบยืนยันวัตถุประสงค์<br>รุ่นข้อความ: รอยืนยัน<br>ไม่ถือข้อมูลเก่าว่าให้ความยินยอมแล้ว</p></div><div><h3>สถานะตัวอย่าง</h3><p>การตัดสินใจ: ยังไม่บันทึก<br>เวลาบันทึก: —<br>เวลาถอน: —</p></div></div><label><input type="checkbox" id="consent-choice"> ตัวอย่างตัวเลือกความยินยอม — ยังไม่เลือก</label><p class="warn">ข้อความนี้เป็นแบบจำลอง ต้องยืนยันนโยบายและผลของการให้ ไม่ให้ หรือถอนก่อนใช้งานจริง ไม่กำหนดเงื่อนไขปฏิเสธการรักษาเอง</p><button disabled>บันทึกการตัดสินใจ — ปุ่มจำลอง</button></section>
<section id="line-booking"><span class="count">05 / เพิ่มหลัง Change Request</span><h2>จองคิวด้วยตนเองผ่าน LINE OA</h2><p class="muted">หน้าจอจำลองสำหรับการออกแบบ · ไม่เชื่อม LINE จริง</p><div class="phone"><span class="tag">ตัวอย่างหน้าจอคนไข้</span><h3>เลือกนัดหมายของคุณ</h3><p class="warn">ตัวตน: รอยืนยันบัญชีกับคนไข้<br>ห้ามเชื่อมจากชื่อแสดงผลอย่างเดียว</p><label>สาขา<select><option>เลือกสาขา</option><option>ลาดกระบัง</option><option>บางนา</option><option>อ่อนนุช</option></select></label><label>บริการ<select><option>เลือกบริการ</option><option>ตรวจฟัน</option></select></label><label>วันและเวลา<input placeholder="เลือกหลังยืนยันตัวตน"></label><p>สถานะคำขอ: ยังไม่ส่ง<br>สถานะนัด: ยังไม่ยืนยัน</p><button disabled>ส่งคำขอจอง — ปุ่มจำลอง</button><p class="muted">ระบบจริงต้องตรวจเวลาว่างอีกครั้ง และป้องกันคำขอซ้ำก่อนยืนยันนัด</p></div></section>'''
html=html.replace('<!--PHASE2_NAV-->','<a href="#consent">04 ความยินยอม</a><a href="#line-booking">05 LINE OA</a>').replace('<!--PHASE2-->',addition)
(p/'mockup.html').write_text(html)
print('Phase 2 generated; phase 1 preserved.')
