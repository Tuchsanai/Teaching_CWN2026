# กับดักที่เจอจริง (รอบต้นแบบ 14 ขั้น) และวิธีเลี่ยง

| ระยะ | อาการที่เจอ | วิธีเลี่ยงในสกิล |
|---|---|---|
| B | ทีมเปิด `docs/` ไม่เจอเพราะโฟลเดอร์ทำงานของแผนยังไม่มีเอกสาร | คัดลอก `./docs` ไป `/workspace/plans/<plan>/app/docs/` ก่อน `run` |
| C | สถานะ `ok` แต่บล็อกโครงโปรเจกต์จบใน 0.8 นาทีและไฟล์ไม่ครบ | `done` ต้องตรวจได้ (คำสั่งที่ผ่าน/ไฟล์ที่ต้องมี) · อ่าน `TEST.md`/ไฟล์ผลก่อนเชื่อ |
| C | บล็อก review ไม่ได้ APPROVED ใน `max_rounds=2` ทำให้ 3 บล็อกถัดไปถูกบล็อก | ตั้ง `max_rounds: 3` ตั้งแต่แผน · รันต่อด้วยข้อที่ผู้ตรวจขอตรงตัว ไม่เขียนใหม่ |
| C | ผู้ทำ review แก้ไฟล์ของบล็อกอื่น ผู้ตรวจไม่ผ่าน | ระบุไฟล์ที่บล็อกแก้ได้ใน `output`/`detail` |
| C | `--resume` ใช้รายชื่อบัญชีของ run เดิม บัญชีที่เพิ่มใหม่ไม่ถูกเรียก | ใส่บัญชีทั้งหมดที่อาจใช้ตั้งแต่ run แรก |
| C | ทีมเขียนแค่ `evaluate.py` ไม่มีสคริปต์ Training | บล็อก Training ต้องมี `done` = "มี train.py และ evaluate.py รันได้กับ data.yaml ตัวอย่าง" · มี `scripts/train.py` สำรอง |
| C | ชื่อคลาสใน Dataset (`NO-Safety Vest`) ไม่ตรงกับ `classes.json` ของ train และ Worker | เทียบ `model.names` กับ `classes.json` ทั้งสองที่ก่อนเทรน/เปิด Worker |
| C | `data.yaml` ของ Roboflow ชี้ `../test/images` ที่ไม่มีจริง | สร้าง `data_fixed.yaml` แบบ path absolute ไม่แก้ไฟล์เดิม |
| C | Test Set มี Positive 25 / Negative 57 ไม่ถึง 100/100 ตามเกณฑ์ → ประกาศผ่านไม่ได้ | นับรูปตอนเตรียม Dataset แล้วแจ้งที่ G3 ว่าต้องหา Test Set เพิ่ม · รายงาน "ยังตัดสินไม่ได้" |
| C | offer ถูกคนอื่นเช่าก่อน / เครื่องค้าง `created` เกิน 5 นาที | poll มี timeout · ลบเครื่องค้างทันที · ลองไม่เกิน 3 offer |
| C | เครื่อง Vast เป็น container ใช้ docker compose ฝั่ง AI ไม่ได้ | เปิดบริการเป็น process ใน tmux ด้วยคำสั่งเดียวกับ `CMD` ของ Dockerfile |
| C | RabbitMQ จาก apt: `.erlang.cookie eacces` และอ่าน config ไม่ได้ | `runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq …` · `chmod 644` ไฟล์ config |
| C | เว็บโหมดจริงไม่รับ gateway `http://` | uvicorn TLS + ใบรับรองสร้างเอง (SAN = IP) ใส่ CA ใน `.env` ของเว็บ |
| C/D | GPU ~20 ms/รูป แต่ dispatcher ส่งทีละรูป + TLS ใหม่ทุกคำขอ → p95 เกิน SLO | ใส่ "ส่งพร้อมกัน/เชื่อมต่อซ้ำ" ใน `done` ของบล็อก dispatcher และวัด p95 ในขั้น deploy |
| D | Windows `localhost` ช้าคำขอละ ~2 วินาที (ลอง IPv6 ก่อน) | สคริปต์ใช้ `127.0.0.1` |
| D | ไม่มี mock-gateway ตอนทดสอบโหมดจริง → TC ของกติกาโมเดลถูกบล็อก พลาดบั๊ก BUG_MODE 1 ตัว | เปิด mock-gateway (profile test) คู่กันเสมอในระยะ D |
| D | ตัวคุมงบรูป GPU ของเทสต์นับรวมรูปของขั้นก่อน | แยกไฟล์นับงบตามขั้น |
| D | `fetch` ของ Node ใช้การเชื่อมต่อที่เว็บปิดแล้ว · หน้า poll ทำให้รอ "networkidle" ไม่จบ | ปิด keep-alive ในตัวช่วยส่งไฟล์ · รอแบบมีเพดานเวลา |
| ทุกระยะ | PowerShell 5.1 เปลี่ยนภาษาไทยใน pipe เป็น `?` | เขียน JSON ด้วย Write แล้ว pipe จาก Git Bash |
