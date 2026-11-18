#!/usr/bin/env bash
# รัน train.py แบบทนการหลุด: ถ้า process ตายให้รันใหม่ (สูงสุด 5 ครั้ง) train.py จะเทรนต่อจาก checkpoint ล่าสุดเอง
# ใช้บนเครื่องเช่า:  cd /workspace/lab3/code && setsid nohup bash run_train.sh --epochs 3 > ../results/logs/train.log 2>&1 &
# อาร์กิวเมนต์ทั้งหมดส่งต่อให้ train.py (เช่น --epochs 1 --model Qwen/Qwen3-4B-Instruct-2507 --out_dir ../results)
cd "$(dirname "$0")"
for try in 1 2 3 4 5; do
  echo "=== attempt $try $(date '+%F %T') ==="
  python train.py --data_dir ../data --out_dir ../results "$@" && { echo TRAIN_OK; exit 0; }
  sleep 10
done
echo TRAIN_FAILED
exit 1
