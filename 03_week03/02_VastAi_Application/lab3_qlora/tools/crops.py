#!/usr/bin/env python3
"""ตัดส่วนที่สำคัญของภาพหน้าจอ/ภาพผลจริง เป็นสำเนาใน img/cNN-*.jpg (ไม่แก้พิกเซลในส่วนที่ตัด · ไฟล์ต้นฉบับไม่ถูกแตะ)

  python tools/crops.py      (รันจากโฟลเดอร์ของบท)
"""
from PIL import Image

CROPS = [  # (ไฟล์ต้นฉบับ, ไฟล์ที่ได้, (ซ้าย, บน, ขวา, ล่าง) เป็นพิกเซลของต้นฉบับ)
    ("results/dataset_samples.jpg", "img/c21-dataset-top.jpg", (0, 0, 1700, 670)),
    ("results/dataset_samples.jpg", "img/c22-dataset-rows.jpg", (0, 470, 1700, 1045)),
    ("image/lab3-step1.png", "img/c23-step1-leak.jpg", (47, 3110, 1722, 3625)),
    ("image/lab3-step2.png", "img/c24-step2-table.jpg", (75, 935, 1700, 1570)),
    ("image/lab3-step3.png", "img/c25-step3-summary.jpg", (60, 1540, 1715, 1895)),
    ("image/lab3-step4.png", "img/c26-step4-table.jpg", (70, 1180, 1700, 1695)),
    ("image/lab3-step5.png", "img/c27-step5-examples.jpg", (70, 1870, 1705, 2240)),
    ("image/lab3-step8.png", "img/c28-step8-table.jpg", (75, 850, 1700, 1165)),
    ("image/lab3-step9.png", "img/c29-step9-skill.jpg", (70, 885, 1705, 1270)),
    ("image/lab3-step10.png", "img/c30-step10-table.jpg", (72, 530, 1695, 1228)),
    ("results/val_compare.png", "img/c31-e2e-chart.jpg", (0, 0, 480, 598)),
    ("results/web/demo_compare_discount.png", "img/c32-compare-answers.jpg", (0, 250, 1000, 650)),
]

if __name__ == "__main__":
    for src, out, box in CROPS:
        im = Image.open(src).convert("RGB")
        box = (box[0], box[1], min(box[2], im.width), min(box[3], im.height))
        im.crop(box).save(out, quality=92)
        print(out, box)
