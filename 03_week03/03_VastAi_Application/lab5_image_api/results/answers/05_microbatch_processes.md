Both runs are complete. Micro-batching alone took capacity from 18 to 52 concurrent users (2.9×), and Micro-batching + 4 processes reached 104 users (5.8×). To get these numbers I had to fix a bug in `server.py` first (details below).

## เทียบ 3 แบบ (GPU RTX 3090 ใบเดียวกัน · SLO p95 ≤ 500 ms, error < 1%)

| | ทีละคำขอ (base1) | Micro-batching (batch1) | Micro-batching + 4 process (gpu1) |
|---|---|---|---|
| รองรับผู้ใช้พร้อมกัน | **18 คน** | **52 คน** | **104 คน** |
| Throughput สูงสุด | 39.5 req/s | 157.3 req/s | 325.1 req/s |
| p95 ที่ N นั้น | 479 ms | 365 ms | 497 ms |
| batch เฉลี่ย (ที่ N นั้น) | 1 | 27.3 | 15.1 |
| GPU utilization | 13% | 36% | 78% (สูงสุด 89%) |
| CPU ของ server | 1.24 core | 2.06 core | 6.13 core (4 process) |
| กี่เท่าของ Baseline (ผู้ใช้ / throughput) | 1× / 1× | **2.9× / 4.0×** | **5.8× / 8.2×** |

ทุกระดับไม่มี error เลย (0%) ตัวเลข "ที่ N นั้น" อ่านจากระดับที่ผ่านเกณฑ์สุดท้าย ส่วน Throughput สูงสุดเป็นค่าสูงสุดของทุกระดับที่ยิง

## คอขวดของแต่ละแบบ
- **ทีละคำขอ:** คอขวดคือการประมวลผลเรียงทีละรูปใน process เดียว แต่ละรูปใช้ GPU ราว 24 ms แต่ทั้งระบบตันที่ประมาณ 39 req/s ขณะที่ GPU ทำงานแค่ 13% เพราะคำขอต้องรอคิวต่อกันทีละรูป
- **Micro-batching:** การรวมรูปเป็น batch ละ 27–32 รูปทำให้ throughput เพิ่ม 4 เท่า คอขวดย้ายไปที่ CPU ของ Python process เดียว (ใช้ได้ทีละ core เพราะ GIL) ซึ่งต้องอ่าน multipart, ถอดรหัส JPEG, ทำ letterbox และแปลงผลกลับเอง ตัวชี้คือ CPU ค้างอยู่ราว 2 core, throughput แบนที่ 147–157 req/s ตั้งแต่ N=64 และ GPU ยังว่างกว่า 60%
- **Micro-batching + 4 process:** 4 process แบ่งงาน CPU กันทำ คอขวดจึงย้ายไปที่ GPU ซึ่งใช้งาน 78–89% และ throughput เริ่มแบนที่ประมาณ 310–325 req/s นอกจากนี้ cgroup throttling เพิ่มจาก 81 เป็น 315 ครั้งระหว่างรอบนี้ แปลว่าโควตา CPU ราว 26 core ของ container เริ่มตึงด้วย

## ต้องแก้ `server.py` ก่อนวัด
รอบแรกของ batch1 ได้แค่ **4 คน** (แย่กว่า Baseline) ผมตรวจดูแล้วพบว่าเป็นบั๊ก ไม่ใช่ผลของ batching
- **สาเหตุ:** cuDNN เก็บแผนการคำนวณแยกตาม thread และขนาด batch แต่ `asyncio.to_thread` ส่งงานไปคนละ thread ทุกครั้ง แต่ละคู่ thread × ขนาด batch ที่ไม่เคยเจอจึงต้องสร้างแผนใหม่ครั้งละประมาณ 2.65 วินาที (ทดสอบแยกแล้วได้ผลตรงกัน) และ warmup อุ่นไว้ให้แค่ thread เดียว
- **การแก้:** ให้ `run_model` และ `warmup` ทำงานบน thread เฉพาะเพียงตัวเดียว (`ThreadPoolExecutor(max_workers=1)`) แก้ไป 4 บรรทัด ตัวเปิดระบบ (`cluster.sh`) และตัวยิงโหลด (`loadgen.py`) ไม่ได้แตะ
- ต้นฉบับเก็บไว้เป็น `server.py.orig` ทั้งบนเครื่องและใน container (`/workspace/vastapp_lab/lab5_image_api/code`) ผลรอบที่ผิดเก็บไว้เป็น `batch1_try1` และ `batch1_try2`
- **ผลต่อ base1:** base1 วัดด้วย server ตัวเดิมที่มีบั๊ก แต่โดนน้อยเพราะใช้ batch ขนาด 1 อย่างเดียว เห็นเป็นแค่ p99 กระโดดเป็นครั้งคราว ถ้าวัด base1 ใหม่ด้วย server ที่แก้แล้วอาจได้มากกว่า 18 เล็กน้อย ซึ่งจะทำให้ตัวคูณในตารางลดลงนิดหน่อย

## สถานะเครื่อง
เครื่อง **vapp-lab5** (id <id>, RTX 3090 × 2) **ยังเปิดอยู่** ราคา $0.395/ชม. ระบบที่ค้างอยู่เป็นแบบ gpu1 (replica 1 · 4 process · batch 32) ผลทั้งหมดอยู่ใน `/workspace/lab5/results/` (`batch1.json/.log` และ `gpu1.json/.log`)
