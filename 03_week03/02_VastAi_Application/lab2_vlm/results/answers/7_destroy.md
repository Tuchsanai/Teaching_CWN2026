ปิด LAB 2 ครบทั้ง 3 ข้อแล้ว

**1. ผลใน `lab2_vlm/results` ครบ**
- `eval/metrics.json` มีผลวัดทั้งโมเดลตั้งต้น (base) และโมเดลที่ fine-tune แล้ว (ft) อย่างละ 100 ใบเสร็จ
  - ยอดรวมตรงทุกหลัก: 88.4% → 100%
  - item F1: 69.9% → 88.4%
- กราฟ: `train/loss_curve.png` และ `eval/images/base_vs_ft.png`
- ภาพตัวอย่าง: `eval/images/examples.jpg`, `dataset_samples.jpg` และภาพหน้าเว็บกับ GIF ใน `web/`
- LoRA adapter อยู่ใน `adapter/`: `adapter_model.safetensors` (≈34.9 MB), `adapter_config.json` และ README

**2. ลบเครื่อง vapp-lab2 แล้ว**
- ลบเครื่อง id <id> (RTX 4090 ×1) ด้วยคำสั่ง `vastai destroy instance` ผ่านสกิล vastai ใน container `multi-account`
- ตรวจรายการเครื่องในบัญชีซ้ำแล้ว ไม่มีป้าย vapp-lab2 ค้างอยู่

**3. ปิดเว็บแล้ว รายจ่ายยังอยู่**
- ใช้ `docker compose down` แบบไม่ใส่ `-v` จึงลบแค่ container และ network ของเว็บ
- volume `vapp-lab2_dbdata` ที่เก็บตาราง `expenses` ยังอยู่ รอบหน้าสั่ง `docker compose up -d` ข้อมูลเดิมก็กลับมา

---

### ค่าใช้จ่ายจริงของเครื่อง vapp-lab2
ตัวเลขมาจากใบแจ้งค่าใช้จ่ายของ Vast (`show invoices-v1`)

| รายการ | ค่า |
|---|---|
| อายุเครื่อง | ≈ 1.24 ชม. (ประมาณ 74 นาที) |
| ราคาต่อชั่วโมง | $0.398/ชม. (GPU $0.387 + disk 60 GB $0.011) |
| GPU | $0.476 (1.230 ชม. × $0.387) |
| Disk | $0.014 (1.238 ชม. × $0.011) |
| รับข้อมูลเข้าเครื่อง (download) | $0.038 (14.5 GB × $0.003/GB) |
| ส่งข้อมูลออกจากเครื่อง (upload) | $0.001 (0.2 GB × $0.006/GB) |
| **รวมที่ถูกคิด** | **$0.529** |

ค่าใช้จ่ายส่วนใหญ่ (≈ 90%) เป็นค่า GPU ส่วน 14.5 GB ที่รับเข้ามาคือค่าดาวน์โหลดโมเดลกับชุดข้อมูลลงเครื่อง
