# ตัวอย่างสรุปการส่งงาน

> ตัวอย่างประกอบการเรียนที่เรียบเรียงขึ้น ไม่ใช่ผลจากการรัน Fable/Astra จริง ใช้เทียบโครงสร้างและความครบถ้วน ไม่ใช่เฉลยตายตัว

บทบาทตามแผน: ผู้วิเคราะห์ yolo1 / Fable / medium และผู้ตรวจ cyolo1 / Astra / medium ตัวอย่างชุดนี้ไม่ได้เรียกโมเดลจริง จึงไม่มีชื่อโมเดลที่ยืนยันจาก CLI หรือ exit code จริง

| รอบ | ไฟล์เข้า | ไฟล์ผลตรวจ | สถานะการรันของตัวอย่าง |
|---|---|---|---|
| 1 | plan-v1.md และ review-task.txt | review-1.md | NOT RUN; exit code: ไม่มี |
| 2 | แผนทั้งสองฉบับ response.md review-1.md และ review-final-task.txt | review-final.md | NOT RUN; exit code: ไม่มี |

คำสั่งที่ผู้เรียนต้องบันทึกจากการรันของตนเอง:

```bash
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium -o review-1.md - < review-task.txt
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium -o review-final.md - < review-final-task.txt
```

แผนปรับเรื่องคิวชนตอนยืนยัน การรักษาคิวเดิมขณะรอเลื่อน และข้อมูลไม่ทราบในรายงาน ยังต้องถามระยะเวลานัด นโยบายรอ การรับลูกค้าไม่ได้นัด และผู้รับผิดชอบหลังนัด

เมื่อทำแล็บจริง ให้แทนสถานะ NOT RUN ด้วยผลจริง เก็บคำสั่ง เวลา/รอบ และ exit code ของตนเอง ห้ามนำตัวอย่างนี้ไปใช้เป็นหลักฐานรันผ่าน
