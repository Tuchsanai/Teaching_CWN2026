ทำครบข้อ 2.1–2.7 แล้ว เครื่อง `vapp-r-receipt` ยังเปิดอยู่และ AI server ใช้งานได้ ไม่ได้แตะเครื่องอื่นในบัญชี (`vapp-v-lab1`, `vapp-q-small`) และส่งอีเมลแจ้งก่อนเช่าเครื่องแล้ว

| หัวข้อ | สิ่งที่รายงาน |
|---|---|
| เครื่อง | RTX 4090 (24 GB) · $0.418/ชม. (รวม disk 60 GB) · Poland · instance <id> · ทดสอบความเร็วโหลดจาก Hugging Face ได้ ~75 MB/s (เกณฑ์ 20 MB/s) |
| เวลา | เตรียมเครื่อง 2.2 นาที · เทรน 5.9 นาที (351 วินาที) · วัดผล Base 1.2 นาที · วัดผล Fine-tuned 0.9 นาที |
| การเทรน | เทรน 8.72 M จาก 2,136 M พารามิเตอร์ (0.41%) · validation loss 0.2743 → 0.026 → 0.021 · VRAM สูงสุด 11.29 GB |
| ผล Base → Fine-tuned (Test Set 100 ใบ) | `json_ok_pct` 100.0 → 100.0 · `total_exact_pct` 89.5 → **96.8** · `item_f1_pct` 72.1 → **87.6** · `sec_per_receipt` 0.71 → 0.54 |
| AI server | เปิด `receipt-base` และ `receipt-ft` ที่ `http://203.0.113.10:41234` · ทดสอบจาก container `multi-account` เห็นทั้งสองโมเดล ถ้าไม่ส่ง key จะได้ 401 · เขียน `receipt.env` 4 บรรทัดแล้ว ทั้งใน container และที่ `lab4_vlm/web/receipt.env` (ไฟล์นี้อยู่ใน `.gitignore`) |
| ไฟล์ที่เก็บกลับ | `lab4_vlm/results/` มี `metrics.json` `metrics_base.json` `metrics_ft.json` `train_log.json` `pred_base.jsonl` `pred_ft.jsonl` `example_ids.json` `compare.png` `loss.png` `example_1..4.png` · `results/logs/` มี `setup.log` `train.log` · `lab4_vlm/adapter/` มี `adapter_model.safetensors` `adapter_config.json` `README.md` (34 MB) |

ตัวเลขทั้งหมดมาจาก `metrics.json` และ `train_log.json` ตามที่สูตรกำหนด

- **`total_exact_pct` ของ Base เป็น 89.5:** ตัวเลขนี้คิดจากทั้ง 100 ใบไม่ได้ (100 ใบจะได้ค่าลงตัวที่ทศนิยม .0) จึงน่าจะหารด้วยเฉพาะใบที่เฉลยมียอดรวม ผมยังไม่ได้ตรวจใน `receipt_common.py` ว่าเป็นอย่างนั้นจริงหรือไม่
- **เปิดเผยค่าแล้ว 1 อย่าง:** ตอนเช่าเครื่อง คำสั่ง `vastai create instance --raw` พิมพ์ `instance_api_key` ของเครื่องนี้ออกมาใน log ของคำสั่ง key นี้ใช้ได้กับเครื่องนี้เครื่องเดียว และจะหมดอายุเมื่อลบเครื่อง ส่วน `HF_TOKEN`, key ของ Vast.ai และ key ของ AI server ไม่ได้แสดงออกมา
- **ยังไม่ได้ commit:** ทั้งโฟลเดอร์ `lab4_vlm/` ยังไม่อยู่ใน git และน่าจะมี session อื่นกำลังเขียนอยู่ (มีการแก้ `report.py` ไม่กี่นาทีก่อนเริ่มรอบนี้) ถ้าต้องการให้ commit และ push ไฟล์ผลกับ adapter บอกได้เลย

**ค่าใช้จ่าย:** ตอนนี้เปิดมาราว 17 นาที คิดเป็นราว $0.12 เครื่องจะคิดเงิน $0.418/ชม. ไปจนกว่าจะลบ และเพดาน `MAX_HOURS=3` จะครบประมาณ 06:55 ขั้นต่อไปคือพรอมต์ที่ 2 (เปิดเว็บ) แล้วตามด้วยพรอมต์ที่ 3 (ลบเครื่องและส่งอีเมลแจ้งค่าใช้จ่าย)