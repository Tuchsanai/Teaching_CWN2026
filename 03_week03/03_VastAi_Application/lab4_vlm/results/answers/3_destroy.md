ลบเครื่อง `vapp-r-receipt` แล้ว ค่าใช้จ่ายจริงจากใบแจ้งหนี้ของ Vast.ai คือ **$0.149**

**ก่อนลบ:** ไฟล์ตามข้อ 2.7 อยู่ครบในโฟลเดอร์ปัจจุบัน คือ `results/` (metrics, pred, ภาพ, `train_log.json`) และ `results/logs/` (`setup.log`, `train.log`) กับ `adapter/` (`adapter_model.safetensors`, `adapter_config.json`)

| หัวข้อ | ผล |
|---|---|
| เครื่องที่ลบ | `<id>` · ป้าย `vapp-r-receipt` · RTX 4090 · Poland · `dph_total` $0.418/ชม. |
| เวลาที่เปิด | ราว 22 นาที (`duration` 1,315 วินาที · ใบแจ้งหนี้คิด 0.366 ชม.) |
| คำสั่งลบ | `vastai destroy instance <id> -y` แล้วตรวจ `vastai show instances` ว่าไม่มีป้ายนี้เหลือ |
| ค่าใช้จ่ายจริง | **$0.149** จาก `vastai show invoices-v1 --charges`: GPU $0.142 (0.354 ชม. × $0.401) · disk $0.006 · ดาวน์โหลด 10.8 GB $0.001 · อัปโหลด $0.000 |
| ค่าประมาณ (เทียบ) | 0.365 ชม. × $0.418 ≈ $0.153 ใกล้กับยอดจริง |
| เว็บ | `docker compose down -v` ใน `lab4_vlm/web/` แล้ว ลบทั้ง container, volume `vapp-lab4_pgdata` และ network |

ในบัญชียังมีอีก 2 เครื่องที่ป้ายไม่ตรงกับงานนี้ จึงไม่ได้แตะ ทั้งสองเครื่องยังคิดเงินอยู่:
- `vapp-q-small`: RTX 3090 · $0.214/ชม. · running
- `vapp-v-lab2-dev`: RTX 4090 · $1.83/ชม. · loading

ถ้าจะปิดเครื่องไหนด้วย บอกได้เลย

ไฟล์ `lab4_vlm/web/receipt.env` ยังอยู่ แต่ใช้ไม่ได้แล้วเพราะ server ถูกลบไป และ key ในไฟล์ก็ใช้ไม่ได้แล้วเช่นกัน