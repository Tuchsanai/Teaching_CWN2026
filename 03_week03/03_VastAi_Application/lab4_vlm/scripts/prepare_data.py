"""โหลด CORD-v2 จาก Hugging Face แล้วเตรียมเป็น ภาพ JPEG (ย่อด้านยาวไม่เกิน MAX_SIDE) + jsonl ต่อ split
ผล: <out>/{train,validation,test}.jsonl  แต่ละบรรทัด = {"id","image","target"}  และภาพใน <out>/images/"""
import argparse
import json
import os

from datasets import load_dataset

from receipt_common import MAX_SIDE, gt_to_target

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="data")
args = ap.parse_args()

os.makedirs(f"{args.out}/images", exist_ok=True)
ds = load_dataset("naver-clova-ix/cord-v2")  # ใช้ HF_TOKEN จาก environment ถ้ามี
for split in ("train", "validation", "test"):
    n_items = 0
    with open(f"{args.out}/{split}.jsonl", "w", encoding="utf-8") as f:
        for i, row in enumerate(ds[split]):
            img = row["image"].convert("RGB")
            img.thumbnail((MAX_SIDE, MAX_SIDE))  # ย่อเฉพาะภาพที่ใหญ่กว่า ไม่ขยายภาพเล็ก
            path = f"images/{split}_{i:03d}.jpg"
            img.save(f"{args.out}/{path}", quality=90)
            target = gt_to_target(json.loads(row["ground_truth"])["gt_parse"])
            n_items += len(target["items"])
            f.write(json.dumps({"id": f"{split}_{i:03d}", "image": path, "target": target}, ensure_ascii=False) + "\n")
    print(f"{split}: {len(ds[split])} ใบ · {n_items} รายการสินค้า")
