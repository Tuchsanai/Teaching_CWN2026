#!/bin/bash
# Deploy Clef-NVFP4 (vLLM) บน Vast.ai RTX 5090 ด้วยคำสั่งเดียว — ดูรายละเอียดใน DEPLOY.md
#
#   bash server/deploy_vast.sh                 # เช่า + deploy + รอจน server พร้อม
#   MAX_DPH=0.8 MIN_INET=1000 bash server/deploy_vast.sh
#
# ต้องมี: /root/workspace/DGX_2024/.env (VAST_API_KEY, VAST_SSH_KEY_FILE) และ clef/.env (CLEF_API_KEY)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"            # clef/server
CLEF_DIR="$(dirname "$HERE")"                    # clef
export VASTAI_ENV="${VASTAI_ENV:-/root/workspace/DGX_2024/.env}"
export VAST_LOADING_GRACE="${VAST_LOADING_GRACE:-1000}"   # image vLLM ~11 GB pull นาน — ค่า default 420 s สั้นไป
LABEL="${LABEL:-clef-5090-$(date +%m%d%H%M)}"            # notebook หา instance จาก prefix "clef-5090"
MAX_DPH="${MAX_DPH:-0.70}"
MIN_INET="${MIN_INET:-2000}"
IMAGE="${IMAGE:-vllm/vllm-openai:cu129-nightly-ac9126e58aa7bbab1856ba6593ba4d5003fea516}"
SKILL_MD="${SKILL_MD:-/root/workspace/ai-accounts/.Claude/yolo3/skills/vastai/SKILL.md}"
VAST=/tmp/vast.py
LOG="$(mktemp -d)"

step(){ echo -e "\n\033[1;36m== $*\033[0m"; }

step "0. ตรวจเครื่องมือฝั่ง local"
python -c "import vastai" 2>/dev/null || pip install -q 'vastai~=1.8'
[ -f "$VAST" ] || sed -n '/^cat > \/tmp\/vast.py/,/^VASTPY/p' "$SKILL_MD" | sed '1d;$d' > "$VAST"
python "$VAST" env >/dev/null || { echo "อ่าน $VASTAI_ENV ไม่ได้"; exit 1; }
python "$VAST" keys >/dev/null || { echo "SSH key ยังไม่ผูกกับบัญชี: python $VAST keys --attach"; exit 1; }
grep -q '^CLEF_API_KEY=' "$CLEF_DIR/.env" 2>/dev/null || {
  umask 077; echo "CLEF_API_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(32))')" >> "$CLEF_DIR/.env"
  echo "สร้าง CLEF_API_KEY ใหม่ใน $CLEF_DIR/.env"; }
python "$VAST" sweep || true

step "1. เช่า RTX 5090 (เน็ต > $MIN_INET Mbps, ≤ \$$MAX_DPH/hr, ตัดประเทศจีนอัตโนมัติ)"
for i in 1 2 3; do       # offer หายระหว่าง search→create บ่อย → ลองใหม่สูงสุด 3 รอบ
  if python "$VAST" rent --label "$LABEL" --gpu RTX_5090 --min-inet "$MIN_INET" --max-dph "$MAX_DPH" \
       --min-cuda 12.9 --disk 80 --image "$IMAGE" --env "-p 8000:8000" --timeout 1500 > "$LOG/rent.json" 2> "$LOG/rent.log"; then break; fi
  grep -q "created instance" "$LOG/rent.log" && break
  echo "rent รอบ $i ไม่สำเร็จ: $(grep ERROR "$LOG/rent.log" | tail -1)"; sleep 20
done
ID=$(python -c "import json;print(json.load(open('$LOG/rent.json'))['instance_id'])" 2>/dev/null || true)
[ -n "$ID" ] && python -c "import json,sys;sys.exit(0 if json.load(open('$LOG/rent.json'))['ok'] else 1)" \
  || { tail -5 "$LOG/rent.log"; echo "เช่าไม่สำเร็จ — ลองเพิ่ม MAX_DPH หรือลด MIN_INET"; exit 1; }
echo "instance $ID พร้อม (log: $LOG)"

step "2. เช็คว่าเข้า HuggingFace ได้ (ต้องได้ 200)"
python "$VAST" run --id "$ID" --cmd 'curl -s -o /dev/null -m 15 -w "huggingface %{http_code}  %{speed_download} B/s\n" -L https://huggingface.co/simonlehmann/clef-NVFP4/resolve/main/model-00002-of-00002.safetensors' 2>/dev/null | tail -1

step "3. ส่งไฟล์ server + start"
umask 077; { grep '^CLEF_API_KEY=' "$CLEF_DIR/.env"; echo "CLEF_GPU_UTIL=0.88"; echo "CLEF_MAX_MODEL_LEN=16384"; echo "CLEF_MAX_NUM_SEQS=4"; } > "$LOG/server.env"
for f in "$HERE/server.py" "$HERE/start.sh" "$LOG/server.env"; do
  python "$VAST" push --id "$ID" --src "$f" --dst /workspace/ >/dev/null 2>&1 || { echo "push $f ล้มเหลว"; exit 1; }
done
rm -f "$LOG/server.env"
python "$VAST" run --id "$ID" --cmd '(setsid nohup bash /workspace/start.sh > /workspace/start.log 2>&1 < /dev/null &); echo started'

step "4. รอโหลดโมเดล (23 GB) + vLLM compile (~6–8 นาที)"
python "$VAST" watch --id "$ID" --file /workspace/server.log --ready "Application startup complete" \
  --alive uvicorn --every 20 --timeout 2400 | tail -1

step "5. Direct URL"
URL=$(python - "$ID" <<'EOF'
import sys
exec(open('/tmp/vast.py').read().split('# ===== argparse')[0])
r = client().show_instance(id=int(sys.argv[1]))
print(f"http://{r['public_ipaddr'].strip()}:{r['ports']['8000/tcp'][0]['HostPort']}")
EOF
)
curl -s -m 10 "$URL/health"; echo
echo -e "\nCLEF URL: $URL   (label $LABEL, instance $ID)"
echo "notebook หา URL นี้เองจาก label — หรือใส่ CLEF_BASE_URL=$URL ใน clef/.env"
echo "เลิกใช้แล้วลบเครื่อง: python $VAST destroy --id $ID --yes"
