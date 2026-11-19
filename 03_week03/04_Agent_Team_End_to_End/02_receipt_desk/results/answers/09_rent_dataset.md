## ขั้นที่ 9 · เช่าเครื่อง 2× RTX 3090 + โหลดโมเดลและ Dataset ใบเสร็จ

### 1. เช่าเครื่อง (ป้าย `e2e-receipt`)
- ค้นข้อเสนอ `gpu_name=RTX_3090 num_gpus=2 dph_total<=0.60 disk>=80 verified` เจอ 17 รายการ
- ครั้งที่ 1 (Bulgaria, $0.420/ชม., id 61387698): สถานะ running แต่ SSH key ไม่เข้าเครื่องเลย (Permission denied นานกว่า 6 นาที แม้ถอดแล้วผูก key ใหม่) → ทำลายทิ้ง
- ครั้งที่ 2 (Taiwan, $0.486/ชม., id 61388901): ยัง loading เกิน 5 นาที → ทำลายทิ้ง
- ครั้งที่ 3 (Japan, id **61389598**) running ภายใน ~1 นาที SSH เข้าได้ `nvidia-smi` เห็น RTX 3090 24 GB จำนวน 2 ใบ
  - เริ่มเช่า 2026-11-19 13:07:35 (เวลาไทย) · image `vastai/pytorch:cuda-13.0.3-auto` (PyTorch 2.14.1 + CUDA 13.0) · ดิสก์ 80 GB
  - SSH: `210.130.226.136:41519` (proxy `ssh3.vast.ai:18156`)
  - พอร์ตสาธารณะ: 8000/tcp → **41588** · 8080/tcp → **41457** (ไว้ใช้กับ API gateway และ load balancer ภายหลัง)
  - บันทึกไว้ที่ `/workspace/vastapp_lab/e2e_receipt/inst.json` (และสำเนาใน `./code_step09/inst.json`)

### 2. ดาวน์โหลดลงเครื่องที่เช่า (รันใน tmux)
- โมเดล `Qwen/Qwen3-VL-2B-Instruct` → `/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct` (4.27 GB)
- Dataset `naver-clova-ix/cord-v2` → `/workspace/e2e_receipt/data/cord-v2` (2.31 GB) คอลัมน์ `image`, `ground_truth`
- นับจากไฟล์จริง: Training 800 · Validation 100 · Test 100 (รวม 1,000 ใบ)

### 3. ภาพตัวอย่าง
`./results/dataset_samples.jpg`: ใบเสร็จ 6 ใบจาก Training Set (train[482], [121], [370], [72], [647], [322]) แต่ละใบวางรูปคู่กับ JSON เฉลย (`gt_parse`) และไฮไลต์ `total.total_price` เป็นสีแดง

### 4. อธิบาย label ของใบเสร็จ 1 ใบ (ใบที่ #3 = train[370])
`ground_truth` เป็นข้อความ JSON ส่วนที่ใช้คือ `gt_parse`:
```json
{
 "menu": [ {"nm": "CKM 1 OR", "cnt": "1", "price": "29,545"},
           {"nm": "Sundae",   "cnt": "1", "price": "8,182"} ],
 "sub_total": {"subtotal_price": "37,727", "tax_price": "3,773"},
 "total": {"total_price": "41,500", "cashprice": "51,500",
           "changeprice": "10,000", "menuqty_cnt": "2"}
}
```
| ช่อง | ความหมาย |
|---|---|
| `menu[]` | รายการสินค้าแต่ละบรรทัด |
| `menu.nm` | ชื่อสินค้า |
| `menu.cnt` | จำนวน (บางใบเขียน `x1`) |
| `menu.unitprice` | ราคาต่อหน่วย (มีในบางใบ) |
| `menu.price` | ราคาของบรรทัดนั้น (= ราคาแต่ละรายการ ตาม FR-03) |
| `sub_total.subtotal_price` | ยอดก่อนภาษี/ค่าบริการ (37,727) |
| `sub_total.tax_price` | ภาษี/ค่าบริการ (3,773) |
| `total.total_price` | **ยอดรวมที่ต้องจ่าย (41,500)** |
| `total.cashprice` / `creditcardprice` | เงินที่ลูกค้าจ่าย (เงินสด/บัตร) |
| `total.changeprice` | เงินทอน |
| `total.menuqty_cnt` | จำนวนชิ้นรวม |

- ช่องที่ Requirement ใช้ตัดสินคือ **`total.total_price`** = "ยอดรวม" ใน M1 (Exact Match หลังปัดทศนิยม 2 ตำแหน่ง), BR-04 (ความมั่นใจ < 0.90 → ติดธง), BR-05 (|ผลรวม `menu.price` − ยอดรวม| > 1.00 → ติดธง) และ BR-06
- ข้อควรระวัง: ตัวเลขเป็นสตริงรูปแบบอินโดนีเซีย (`41,500`, `28.000`, `118.000,00`) ต้องแปลงเป็นตัวเลขก่อนเทียบ และใบที่มีภาษีจะเห็นว่า ผลรวม `menu.price` (37,727) ≠ `total_price` (41,500) ซึ่งจะทำให้ BR-05 ติดธง
- CORD ไม่มีช่อง "ชื่อร้าน" และ "วันที่" ใน label (ส่วนหัวใบเสร็จถูกเบลอไว้) ดังนั้น 2 ใน 5 ช่องของ FR-03 ต้องหาข้อมูลจากแหล่งอื่นหรือตั้งเป็นข้อสมมติ

### ค่าใช้จ่ายจนถึงตอนนี้ (13:14 น.)
เครื่องปัจจุบัน ~$0.044 + ครั้งที่ 1 ~$0.063 + ครั้งที่ 2 ไม่เกิน ~$0.045 → **รวมประมาณ $0.15**

สคริปต์ทั้งหมดอยู่ที่ `./code_step09/` (rent.sh, poll_instance.sh, save_inst.py, remote_setup.sh, download_and_count.py, make_samples.py, vast.sh, remote.sh) ไม่มีการแสดงค่า key ใด ๆ และไม่ได้แตะเครื่องป้ายอื่น

### สรุป
| หัวข้อ | ผล |
|---|---|
| รุ่นและจำนวน GPU | NVIDIA RTX 3090 (24 GB) × 2 ใบ ในเครื่องเดียว (Japan, id 61389598) |
| ราคาต่อชั่วโมง | $0.414 (ไม่เกินเพดาน $0.60) · ค่าเช่ารวมถึงตอนนี้ ~$0.15 |
| จำนวนใบเสร็จแต่ละชุด | Training 800 · Validation 100 · Test 100 (รวม 1,000) |
| ช่องที่ใช้ตัดสินตาม Requirement | `total.total_price` (ยอดรวม: M1 Exact Match, BR-04, BR-05 เทียบกับผลรวม `menu.price`, BR-06) |
| สถานะเครื่อง | **ยังเปิดอยู่ (running)** ป้าย e2e-receipt กำลังคิดเงิน $0.414/ชม. มีโมเดลและ Dataset พร้อมใช้ในขั้นถัดไป |

เวลาที่ใช้: ~23 นาที
