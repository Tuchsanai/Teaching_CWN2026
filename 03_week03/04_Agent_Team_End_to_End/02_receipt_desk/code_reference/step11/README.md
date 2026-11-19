# code_step11 · ขึ้นระบบจริง (GPU e2e-receipt + เว็บบนเครื่องนี้)

| ไฟล์ | ใช้ทำอะไร | รันที่ |
|---|---|---|
| `gpu.sh` | `push` (ส่ง ./app/ai + svc.sh + secrets) · `start/stop/restart/status/log <svc…|all>` · `sh 'cmd'` | เครื่องนี้ (ผ่าน container multi-account) |
| `svc.sh` | คุมบริการทีละตัวด้วย tmux: `rabbitmq vllm0 vllm1 nginx gateway worker0 worker1` | เครื่อง GPU |
| `push_c.sh` | ส่วนของ `gpu.sh push` ที่รันใน container (เขียน secrets.env chmod 600, ไม่แสดง key) | container |
| `web.sh` | `env` (เขียน app/.env) · `up/down/ps/logs/status` · `mode mock|gateway` · `psql` / `rows` | เครื่องนี้ |
| `setup_apt.sh` · `setup_py.sh` | ติดตั้ง nginx + rabbitmq · venv แอป + vLLM + รวม LoRA (`setup_gpu.sh` = รุ่นแรกที่รวมทุกอย่าง) | เครื่อง GPU (tmux) |
| `merge_lora.py` | รวม LoRA ที่ดีที่สุดเข้ากับ Qwen3-VL-2B → `step11/merged` | เครื่อง GPU |
| `web_upload.mjs` | ส่งใบเสร็จผ่านหน้า `/upload` จริง (Playwright) | เครื่องนี้ |
| `watch_gateway.py` | เก็บคำตอบของ gateway (G4) ก่อน dispatcher ลบ | เครื่องนี้ |
| `compare_db_gateway.py` | เทียบยอดใน DB กับคำตอบ gateway และเฉลย → `results/deploy/e2e_check.json` | เครื่องนี้ |

ตัวอย่าง: `bash code_step11/gpu.sh stop worker1` · `bash code_step11/gpu.sh status all` · `bash code_step11/web.sh mode mock`
