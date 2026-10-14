# Backend: NInfer + Qwen3.8-27B บน Vast.ai RTX 5090

| ไฟล์ | ทำอะไร |
|:--|:--|
| `setup_ninfer.sh` | ลงแพ็กเกจ → clone + build NInfer → โหลดโมเดล 22 GiB (รันซ้ำได้) |
| `start_server.sh` | เปิด `ninfer-serve` ที่พอร์ต 8080 แบบเบื้องหลัง พร้อม API key + CORS แล้วรอจน `/health` ผ่าน |

## 1) เช่าเครื่อง
RTX 5090 · image `nvidia/cuda:13.1.2-devel-ubuntu24.04` · disk 90 GB · เน็ต > 2000 Mbps ·
Docker options: `-p 8080:8080`

## 2) ในเครื่อง Vast (SSH เข้าไปแล้ว copy-paste)
```bash
mkdir -p /workspace && cd /workspace
# วางไฟล์ setup_ninfer.sh และ start_server.sh ไว้ที่ /workspace (scp หรือคัดลอกเนื้อหา)
bash setup_ninfer.sh                         # ~8-10 นาที (build ~7.5 นาที + โหลดโมเดลพร้อมกัน ~2 นาที)
NINFER_API_KEY=ตั้งรหัสลับเอง bash start_server.sh   # ~15 วินาที จน "พร้อมแล้ว!"
```
log: `tail -f /workspace/ninfer.log`

## 3) หา URL สาธารณะ
หน้า Vast → instance → ปุ่ม IP/port: ดู `public IP` และพอร์ตที่ map กับ `8080/tcp`
(เช่น `8080/tcp -> 41234`) → URL = `http://<public_ip>:<HostPort>`

## 4) ทดสอบจากเครื่องตัวเอง
```bash
URL=http://<public_ip>:<HostPort>; KEY=รหัสลับ
curl $URL/health
curl $URL/v1/models -H "Authorization: Bearer $KEY"
curl $URL/v1/chat/completions -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"qwen3.8-27b","max_tokens":200,"messages":[
       {"role":"system","content":"คุณคือพนักงานร้านนวดแผนไทย ตอบสุภาพ สั้น เป็นภาษาไทย"},
       {"role":"user","content":"สวัสดีค่ะ ร้านเปิดกี่โมง"}]}'
```
ใส่ `"stream":true` เพื่อรับแบบ SSE (ใช้ `curl -N`)

ค่าที่ frontend ใช้: `LLM_BASE_URL=http://<ip>:<port>` · `LLM_MODEL=qwen3.8-27b` · `LLM_API_KEY=<รหัสลับ>`

> เลิกใช้แล้ว **destroy เครื่องทุกครั้ง** (stop ยังเสียค่า disk)
