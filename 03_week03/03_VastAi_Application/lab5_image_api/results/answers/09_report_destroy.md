I've finished closing out LAB 5. The charts come from the real results, all files are back in the chapter folder, and the vapp-lab5 machine is deleted.

**What was done**
- **Report script:** wrote `lab5_image_api/code/report.py` and ran it on the machine. It read all 9 result files and created `metrics.json` plus 5 charts.
- **Files brought back:** saved to `lab5_image_api/results` (46 files) and `lab5_image_api/code` (12 files, including report.py). The machine's copies and the local copies match exactly (MD5 checksums, 0 mismatches).
- **Charts checked:** I opened all 5. The text is readable and the labels don't overlap.

## ความจุของแต่ละแบบ (SLO: p95 ≤ 500 ms, error < 1%)

| จำนวน GPU | สถาปัตยกรรม | รองรับผู้ใช้พร้อมกัน | Throughput สูงสุด | p95 ที่ N นั้น | เท่าของ 1 ใบ | Efficiency |
|---|---|---|---|---|---|---|
| 1 | ทีละคำขอ (base1) | 22 คน | 63 req/s | 368 ms | 0.21 (แบบพื้นฐาน = 1.00) | – |
| 1 | Micro-batching (batch1) | 52 คน | 157 req/s | 365 ms | 0.50 (2.4 เท่าของแบบพื้นฐาน) | – |
| 1 | Micro-batching + 4 process (gpu1) | 104 คน | 325 req/s | 497 ms | 1.00 (แถวอ้างอิง, 4.7 เท่าของแบบพื้นฐาน) | 100% |
| 2 | Micro-batching + 4 process ต่อใบ (gpu2) | **176 คน** | 651 req/s | 421 ms | **1.69** (Throughput 2.00) | **85%** (Throughput 100%) |

**1 ใบ 104 คน → 2 ใบ 176 คน (1.69 เท่า, efficiency 85%)**

ความจุของ gpu2 ตามกติกาแบบเข้มคือ 32 คน เพราะที่ N=64 รอบแรก p95 พุ่งขึ้นเป็น 1,752 ms ครั้งเดียว ซึ่งดูเป็นอาการชั่วคราว พอวัด N=64 ซ้ำอีก 3 รอบก็ผ่านทั้งหมด (p95 ประมาณ 147 ms) และระดับ N=128, 160, 176 ก็ผ่าน ผมจึงใช้ 176 คน ใน `metrics.json` เก็บไว้ทั้งสองค่า คือ `capacity_users_strict` = 32 และ `capacity_users` = 176

**ประมาณการ 3 ใบ (คำนวณ ไม่ใช่ผลวัด):** ใช้ค่าของ 1 ใบ × 3 × efficiency ที่วัดได้ตอน 2 ใบ
- ผู้ใช้พร้อมกันประมาณ 264 คน
- Throughput ประมาณ 976 req/s
- server ต้องใช้ CPU ประมาณ 18.5 core ซึ่งยังอยู่ในโควตาของเครื่องนี้ (ประมาณ 27 core)

**ผลการทดลองเสริม**
- **round-robin กับ least_conn เมื่อ replica เท่ากัน:** round-robin รับได้ 176 คน least_conn รับได้ 256 คน
- **เมื่อ replica ตัวที่ 2 ช้าลงรูปละ 40 ms:** round-robin รับได้ 32 คน (แบ่งงาน 50/50 ทำให้ตัวช้าลากทั้งระบบ) ส่วน least_conn รับได้ 72 คน (ย้ายงาน 79% ไปให้ GPU0)
- **replica ล่มกลางการยิงโหลด:**
  - ถ้า NGINX ไม่ส่งซ้ำ จะมี error 5,474 จาก 14,822 คำขอ (36.9%)
  - ถ้า NGINX ส่งซ้ำ ไม่มี error เลย (0 จาก 9,601 คำขอ)
  - การเปิด replica คืนใช้เวลาประมาณ 92 วินาที จึงกลับมารับงานไม่ทันภายใน 45 วินาทีที่ยิง

## กราฟ (อยู่ที่ `lab5_image_api/results/`)
- **ชุดหลัก**
  - `latency_p95_vs_users.png`: p95 เทียบ N ของทั้ง 4 แบบ พร้อมเส้น SLO และดาวที่จุดความจุ
  - `throughput_vs_users.png`: Throughput เทียบ N
  - `scaling_vs_gpus.png`: ความจุและ Throughput สูงสุดเทียบจำนวน GPU พร้อมเส้น ideal, efficiency และจุดประมาณการ 3 ใบ
- **ชุดเสริม**
  - `lb_rr_vs_least_conn.png`: round-robin เทียบ least_conn ทั้งตอน replica เท่ากันและตอนมีตัวช้า พร้อมสัดส่วนคำขอที่แต่ละ replica ได้
  - `failover_timeline.png`: Throughput รายวินาที แยกสีตาม replica และ error ทั้งรอบที่ส่งซ้ำและไม่ส่งซ้ำ
- ไฟล์อื่นในโฟลเดอร์เดียวกัน: `metrics.json` และ `dataset_samples.jpg`

## ค่าใช้จ่ายจริงของ vapp-lab5 (instance <id>, RTX 3090 × 2, California)

| รายการ | ค่า |
|---|---|
| อายุเครื่อง | 2 ชม. 40 นาที (9,601 วินาที) |
| ราคาต่อชั่วโมง | $0.395 (GPU $0.347 + disk $0.048) |
| ยอดที่ถูกคิดตามใบแจ้งหนี้ | **$1.011** (GPU 2.535 ชม. $0.879 + disk 2.669 ชม. $0.128 + ดาวน์โหลด $0.004) |
