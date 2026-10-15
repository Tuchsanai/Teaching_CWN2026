# Backend: NInfer + Qwen บน Vast.ai RTX 5090

ไม่มีสคริปต์ให้รันเอง — ให้ `yolo1` (skill `vastai`) อ่าน **[NINFER_RECIPE.md](NINFER_RECIPE.md)** แล้วทำให้ทั้งหมด
(เช่าเครื่อง → build NInfer → โหลดโมเดล → เปิด API พอร์ต 8080 → ทดสอบ → เขียน `.env.vast`)

| ไฟล์ | ทำอะไร |
|:--|:--|
| `NINFER_RECIPE.md` | สูตรการทำงานสำหรับ AI: ตารางโมเดล Qwen ที่เลือกได้ · เงื่อนไขเครื่อง · คำสั่งอ้างอิง · กติกา |
| `.env.vast` | AI เขียนให้ตอนจบ (3 บรรทัด `LLM_BASE_URL` `LLM_MODEL` `LLM_API_KEY`) · ถูก ignore ห้าม commit |

## พรอมต์ (วางใน `yolo1` ที่ `/workspace`)

```text
ใช้ skill vastai ทำตาม 00_setup/04_Skill_Setup/01_VastAi_Skill/_solution/ex2_chatbot/backend/NINFER_RECIPE.md
MODEL=qwen3.8-27b-nvfp4 LABEL=ex2-ninfer-5090 MAX_DPH=1.20
```

ค่าที่ frontend ใช้: `LLM_BASE_URL=http://<ip>:<port>` · `LLM_MODEL=<ชื่อใน API ตามตาราง>` · `LLM_API_KEY=<key>`

> เลิกใช้แล้ว **destroy เครื่องทุกครั้ง** (stop ยังเสียค่า disk)
