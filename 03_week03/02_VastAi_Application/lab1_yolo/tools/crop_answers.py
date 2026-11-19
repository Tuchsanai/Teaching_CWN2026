#!/usr/bin/env python3
"""ตัดส่วนสำคัญของภาพหน้าจอคำตอบจริง เป็นสำเนาใน img/cNN-*.jpg (ไม่แก้พิกเซลในกรอบที่ตัด ภาพต้นฉบับไม่ถูกแตะ)

  python tools/crop_answers.py            (รันจากโฟลเดอร์ lab1_yolo)
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ชื่อไฟล์ใหม่ : (ภาพต้นฉบับ, (ซ้าย, บน, ขวา, ล่าง) เป็นพิกเซลของภาพต้นฉบับ)
CROPS = {
    "c01-step1": ("image/lab1-step1.png", (60, 828, 1710, 1012)),
    "c02-step2": ("image/lab1-step2.png", (70, 868, 1700, 1425)),
    "c03-step3": ("image/lab1-step3.png", (70, 835, 1705, 1265)),
    "c04-step4": ("image/lab1-step4.png", (70, 962, 1700, 1600)),
    "c05-step5": ("image/lab1-step5.png", (70, 975, 1700, 1520)),
    "c06-step6": ("image/lab1-step6.png", (70, 1855, 1700, 2310)),
    "c07-step7": ("image/lab1-step7.png", (70, 850, 1700, 1260)),
    "c08-step8": ("image/lab1-step8.png", (70, 1162, 1700, 1625)),
    "c09-step9": ("image/lab1-step9.png", (70, 848, 1250, 1338)),
    "c10-step10": ("image/lab1-step10.png", (70, 580, 1700, 897)),
    "c11-web-result": ("results/web/web_result_1.png", (590, 185, 1212, 1190)),
    "c12-web-history": ("results/web/web_history.png", (60, 80, 1220, 560)),
    "c13-noharhat": ("results/images/before_after_2.jpg", (644, 0, 1288, 680)),
}

if __name__ == "__main__":
    for name, (src, box) in CROPS.items():
        im = Image.open(os.path.join(ROOT, src)).convert("RGB").crop(box)
        out = os.path.join(ROOT, "img", name + ".jpg")
        im.save(out, quality=92)
        print(name, im.size)
