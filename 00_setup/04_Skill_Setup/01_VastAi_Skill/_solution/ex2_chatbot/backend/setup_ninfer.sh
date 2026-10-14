#!/usr/bin/env bash
# setup_ninfer.sh — ติดตั้ง NInfer + โหลดโมเดล Qwen3.8-27B (NVFP4) บนเครื่อง RTX 5090
# รันซ้ำได้ (ขั้นที่เสร็จแล้วจะข้าม) · ใช้เวลารวม ~8-10 นาที (ทดสอบจริง: 483 วินาที)
# วิธีใช้:  bash setup_ninfer.sh
set -euo pipefail
DIR=/workspace/ninfer
MODEL=$DIR/models/qwen3_8_27b_nvfp4.ninfer
export DEBIAN_FRONTEND=noninteractive
mkdir -p /workspace && cd /workspace
t0=$(date +%s)

echo "== [1/3] ติดตั้งแพ็กเกจ (apt + hf CLI)"
if ! command -v ninja >/dev/null || ! pkg-config --exists libavcodec 2>/dev/null; then
  apt-get update -qq
  apt-get install -y -qq git cmake ninja-build pkg-config build-essential python3-pip \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libcurl4-openssl-dev >/dev/null
fi
command -v hf >/dev/null || pip install -q --break-system-packages -U "huggingface_hub[hf_xet]"

echo "== [2/3] โหลดโมเดล 22 GiB (ทำเบื้องหลังพร้อมกับ build)"
mkdir -p $DIR/models
if [ ! -f "$MODEL" ]; then
  ( s=$(date +%s)
    HF_XET_HIGH_PERFORMANCE=1 hf download neroued/Qwen3.8-27B-nvfp4-NInfer \
      qwen3_8_27b_nvfp4.ninfer --local-dir $DIR/models >/workspace/download.log 2>&1
    e=$(( $(date +%s) - s )); sz=$(stat -c %s "$MODEL")
    echo "download: ${e}s, $(( sz / 1048576 / (e>0?e:1) )) MiB/s" >> /workspace/download.log
  ) & DL=$!
else
  echo "   มีโมเดลแล้ว ข้าม"; DL=""
fi

echo "== [3/3] clone + build NInfer"
[ -d $DIR/.git ] || { tmp=$(mktemp -d); git clone -q https://github.com/Neroued/ninfer.git "$tmp/n"; cp -a "$tmp/n/." $DIR/; rm -rf "$tmp"; }
cd $DIR
if [ ! -x build/apps/ninfer-serve ]; then
  s=$(date +%s)
  cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release >/workspace/build.log 2>&1
  cmake --build build -j"$(nproc)" >>/workspace/build.log 2>&1 || { tail -30 /workspace/build.log; exit 1; }
  echo "build: $(( $(date +%s) - s ))s" | tee -a /workspace/build.log
fi

if [ -n "$DL" ]; then echo "   รอโมเดลโหลดเสร็จ..."; wait $DL || { tail -20 /workspace/download.log; exit 1; }; fi
tail -1 /workspace/download.log
ls -lh "$MODEL"
echo "== เสร็จ ($(( $(date +%s) - t0 ))s) — ต่อไป: bash start_server.sh"
