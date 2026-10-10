---
name: cyolo
description: เรียก OpenAI Codex CLI ผ่านบัญชี cyolo1 ถึง cyoloN ค่าเริ่มต้น gpt-6-astra และ high เลือกบัญชี โมเดล และ reasoning effort ได้ ตรวจโควตา แบ่งงานขนาน และส่งค่าข้ามบัญชีหรือข้าม CLI ไป yolo ใช้เมื่อผู้ใช้ขอ "เรียก cyoloN", "ใช้ codex อีก account", "ให้ gpt ทำ...", "เช็คโควตา codex" หรือเปรียบเทียบคำตอบข้ามบัญชี/ข้ามค่าย
argument-hint: "[-a <N>] [-m <model>] [-e <effort>] <prompt>"
allowed-tools: Bash(cyolo* *), Bash(codex *), Bash(env CODEX_HOME=/root/workspace/ai-accounts/.Codex/cyolo* codex *)
---

# ค่าเริ่มต้น

- ไม่ระบุรุ่นให้ใช้ `-m gpt-6-astra` ไม่ระบุ effort ให้ใช้ `high`
- ไม่ระบุบัญชีให้ใช้ `cyolo1`; เลือกบัญชีด้วย `-a <N>` หรือระบุ `cyoloN` ในคำสั่งของผู้ใช้ โดย N เป็นจำนวนเต็มบวก ไม่จำกัดสูงสุดที่ 5
- ต้องใส่ทั้งสอง flag เสมอ อย่าพึ่ง `config.toml` หรือ default ของโมเดล ซึ่งต่างกันตามรุ่น (ดูตารางด้านล่าง)
- ค่าที่ผู้ใช้ระบุเองมีสิทธิ์เหนือค่าเริ่มต้นเสมอ
- อ่าน `$ARGUMENTS`: `-a <N>`, `-m <model>`, `-e <effort>` ที่เหลือคือ prompt — ไม่มี prompt ให้ถามผู้ใช้ก่อน หากเลขบัญชีจาก `-a` ขัดกับบัญชีที่ผู้ใช้ระบุในข้อความ ให้ถามว่าต้องการบัญชีใดก่อนรัน

# เลือกบัญชี cyolo1 ถึง cyoloN

- รับ N เป็นเลขฐานสิบรูปแบบ `[1-9][0-9]*` เท่านั้น เช่น `1`, `5`, `12`; ไม่ส่งค่าอื่นไปประกอบคำสั่ง shell
- ใช้โปรไฟล์ `/root/workspace/ai-accounts/.Codex/cyolo<N>` ของบัญชีที่เลือกตลอดทั้งงาน รวม `models_cache.json` และ `sessions/` อย่าใช้ข้อมูลบัญชี 1 แทนบัญชีอื่น
- ตรวจว่าโฟลเดอร์โปรไฟล์มีอยู่ และตรวจสถานะด้วย `env CODEX_HOME=/root/workspace/ai-accounts/.Codex/cyolo<N> codex login status` ก่อนส่ง prompt; อ่านข้อความสถานะ ไม่อาศัย exit code อย่างเดียว ห้ามอ่านหรือส่งต่อ `auth.json`
- ถ้าโปรไฟล์ไม่มีหรือยังไม่ได้ล็อกอิน ให้แจ้งบัญชีและเหตุผลที่รันไม่ได้ ไม่สร้างบัญชี ไม่เริ่ม login และไม่สลับไปบัญชีอื่นเอง
- ตรวจคำสั่งด้วย `command -v cyolo<N>`; launcher ที่ตรวจบนเครื่องนี้รองรับชื่อ `cyolo1`–`cyolo5` เท่านั้น สำหรับ N มากกว่า 5 ให้ใช้ `env CODEX_HOME=... codex ...` ตามตัวอย่างด้านล่างกับโปรไฟล์ที่มีอยู่แล้ว แม้จะมี symlink ชื่อ `cyolo<N>` ก็ตาม เว้นแต่ตรวจแล้วว่า launcher รองรับชื่อนั้นจริง
- การเลือกบัญชีครั้งเดียวทำในสกิลนี้ได้โดยตรง ไม่ต้องเปลี่ยนไปใช้สกิลอื่น

# ค่าที่รองรับ

ตรวจจาก `/root/workspace/ai-accounts/.Codex/cyolo1/models_cache.json` (`fetched_at` 2026-09-30, `client_version: 0.159.2`, cyolo2 ตรงกัน) เฉพาะรุ่นที่ `visibility: list`:

| Model | Effort ที่รองรับใน Codex CLI | Effort เริ่มต้นของโมเดล |
| --- | --- | --- |
| `gpt-6.1-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `low` |
| `gpt-6-astra` — ค่าเริ่มต้นของสกิล สำหรับงานซับซ้อน | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `medium` |
| `gpt-6-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `medium` |
| `gpt-6-luna` | `low`, `medium`, `high`, `xhigh`, `max` | `medium` |
| `gpt-5.6-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `low` |
| `gpt-5.6-terra` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `medium` |
| `gpt-5.6-luna` | `low`, `medium`, `high`, `xhigh`, `max` | `medium` |
| `gpt-5.5` | `low`, `medium`, `high`, `xhigh` | `medium` |

`gpt-5.4-mini` และ `gpt-5.3-codex-spark` ไม่อยู่ใน cache ของ 0.159.2 แล้ว

- สกิลยังใช้ effort `high` เมื่อผู้ใช้ไม่ระบุ แม้ default ของโมเดลในตารางจะต่างกัน
- `ultra` เป็นโหมดฝั่ง Codex client: reasoning สูงสุดพร้อม automatic task delegation ตามคำอธิบายใน cache; ใช้เฉพาะรุ่นที่ประกาศรองรับ ส่วน [OpenAI Docs ของ GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) ระบุ API `reasoning.effort` ถึง `max` อย่านำ `ultra` ไปใช้เป็นค่า API โดยตรง
- `gpt-5.4` ไม่อยู่ใน cache รอบนี้ จึงไม่ยืนยันว่าใช้ได้กับบัญชีนี้; รุ่นที่ `visibility: hide` เช่น `gpt-reserve` และ `codex-auto-review` ไม่ใช่ตัวเลือกทั่วไปในตาราง
- ตารางนี้เป็น snapshot ของบัญชี 1; สำหรับบัญชีอื่น หรือเมื่อผู้ใช้ขอรุ่นใหม่หรือข้อมูลไม่ตรงกับ CLI ให้อ่าน `fetched_at`, `slug`, `visibility`, `supported_reasoning_levels` และ `default_reasoning_level` จาก `/root/workspace/ai-accounts/.Codex/cyolo<N>/models_cache.json` ของบัญชีที่เลือก อย่าเปลี่ยนรุ่นที่ผู้ใช้ระบุเองเงียบ ๆ และอย่าถือว่า cache เก่ายืนยันสิทธิ์เข้าถึงปัจจุบัน
- ค่าที่ไม่รองรับอาจได้ HTTP 400 เช่น `invalid_enum_value`, `unsupported_value` หรือ `not supported when using Codex with a ChatGPT account`; ตรวจรายการที่รองรับก่อนเรียก ไม่ส่งงานเพื่อเดาค่า effort
- ผลทดสอบเดิมบน CLI 0.152.1 พบว่า `ultra` บน `gpt-5.5` และ `gpt-5.6-luna` อาจ fallback เงียบ ๆ จึงอย่าใช้การไม่เกิด error เป็นหลักฐานว่ารองรับ และยอด `tokens used` อาจไม่รวมงานของ sub-agent

# การเรียกใช้งาน

```bash
cyolo<N> exec -m <model> -c model_reasoning_effort="<effort>" -o <outfile> "<prompt>" < /dev/null
```

แทน `<N>`, `<model>`, `<effort>`, `<outfile>` และ `<prompt>` ด้วยค่าจริงก่อนรัน ไม่พิมพ์วงเล็บมุมลง shell ค่าเริ่มต้นคือ `cyolo1`, `gpt-6-astra`, `high`

ถ้าไม่มี wrapper หรือ launcher ยังไม่รองรับเลขบัญชี ให้เรียกคำสั่งเทียบเท่าด้วยโปรไฟล์ที่เลือก:

```bash
env CODEX_HOME=/root/workspace/ai-accounts/.Codex/cyolo<N> codex --dangerously-bypass-approvals-and-sandbox exec -m <model> -c model_reasoning_effort="<effort>" -o <outfile> "<prompt>" < /dev/null
```

**ไม่มีคำสั่ง `cyolo` เปล่า ๆ ต้องมีเลขบัญชีเสมอ** และอย่าเรียก `codex` โดยไม่กำหนด `CODEX_HOME` เพราะจะใช้โปรไฟล์คนละชุด ตัวอย่าง `/cyolo -a 3 ช่วยสรุปโค้ดนี้` เลือกบัญชี 3 พร้อม `-m gpt-6-astra -c model_reasoning_effort="high"`; `/cyolo -a 12 -m gpt-6-astra -e max วิเคราะห์โค้ดนี้` เลือกโปรไฟล์บัญชี 12 ถ้ามีและล็อกอินแล้ว

ต้องมี `exec` เสมอ (รันเปล่าจะเปิด TUI ค้าง) และ `< /dev/null` เสมอ (ไม่งั้นค้างรอ stdin ไม่มีวันจบ) บรรทัด `Reading additional input from stdin...` เป็นเรื่องปกติ

- **`-o <file>` คือวิธีอ่านคำตอบที่ถูกต้อง** stdout ปกติมี banner + `tokens used` ปนมา และ **ห้ามใช้ `-o /dev/stdout`** คำตอบจะออกซ้ำสองรอบ (`42` กลายเป็น `4242`)
- `--json` ให้ JSONL: โทเคนอยู่ใน `turn.completed.usage.{input_tokens,cached_input_tokens,output_tokens,reasoning_output_tokens}` ส่วนงานล้มเหลวได้ `turn.failed.error.message`
- `--skip-git-repo-check` ไม่จำเป็นในการทดสอบเดิมผ่าน `cyolo1` นอก git repo; ใส่ได้เมื่อรันนอก repo เพื่อเลี่ยงการต้องเรียกงานซ้ำ
- ถ้าผู้ใช้ขอแบบไม่ bypass ให้ใช้ `env CODEX_HOME=/root/workspace/ai-accounts/.Codex/cyolo<N> codex exec --sandbox read-only` (หรือ `--sandbox workspace-write`) พร้อม flag model, effort, output และ prompt ตามปกติ

`cd` เข้าโฟลเดอร์เป้าหมายก่อนรัน เพราะ codex เขียนไฟล์ลง cwd งานทดลองให้รันใน scratchpad เมื่องานยังไม่จบ ให้ติดตาม process และ session ล่าสุดใน `/root/workspace/ai-accounts/.Codex/cyolo<N>/sessions/<YYYY>/<MM>/<DD>/` ของบัญชีที่เลือก; การมีไฟล์อย่างเดียวไม่ได้แปลว่างานยังรันอยู่

ก่อนรัน ให้แจ้งบัญชี model และ effort หลังรัน ให้สรุปผลสำเร็จหรือข้อผิดพลาด, ไฟล์ที่เปลี่ยน และ tokens ห้าม retry งานที่กินโทเคนโดยอัตโนมัติหลัง error

# ผลทดสอบ

codex-cli 0.152.1 — `cyolo1` ล็อกอินด้วยบัญชี ChatGPT ไว้แล้ว ไม่ต้องใช้ API key ถ้าพังให้เช็ค `env CODEX_HOME=/root/workspace/ai-accounts/.Codex/cyolo1 codex login status` (ต้องได้ `Logged in using ChatGPT`) แล้วให้ผู้ใช้รัน `! cyolo1 login` เอง — บัญชีที่ไม่ได้ล็อกอินพ่น `401 Unauthorized` + retry 5 ครั้ง แต่ **exit code ยังเป็น 0**

**effort มีผลจริง** โจทย์นับ `n ∈ 1..500 ที่เขียนเป็น a²+b² ได้` (เฉลย 177): `gpt-5.6-sol` + `low` → reasoning 803 โทเคน ตอบ **176 ผิด**, `+ max` → reasoning 3106 โทเคน ตอบ **177 ถูก** — โจทย์ง่ายจะถูกหมดทุก effort จึงเห็นผลเฉพาะงานที่ยากพอ

codex-cli 0.159.2 — ตรวจซ้ำ 2026-10-02: `cyolo1`/`cyolo2` `Logged in using ChatGPT`, `cyolo3`–`cyolo5` `Not logged in` ทดสอบด้วย `gpt-6-astra` / `low`:

- relay ข้าม CLI `cyolo1 → yolo2(opus/low) → cyolo2` = `42 → 142 → 426` ✅ โจทย์บรรทัดเดียวใช้ input ~17k (cached 12k) output 5 โทเคน
- fan-out ผสม yolo1/2/3 + cyolo1/2 บวกเลข 5 chunk ถูกทุก chunk ฝั่ง cyolo ใช้ 16.6–19.9s ต่อ job (1 command_execution ต่อ job)
- `cyolo2` เป็น orchestrator สั่ง `yolo1` + `cyolo1` ขนานผ่านเชลล์ได้ ผลรวมตรงเฉลย (72s) ส่วน orchestrator ฝั่ง yolo ทำงานเดียวกันได้ใน 27s — ดูหัวข้อ "กระจายงานข้าม CLI" ในสกิล [yolo](../yolo/SKILL.md)

codex ไม่รู้ว่าตัวเองถูกตั้ง effort ระดับไหน ถามมันไม่ได้ ยืนยันจากฝั่งคำสั่งเท่านั้น และรายงานของมันเชื่อไม่ได้ — ไฟล์ที่มันแก้ให้อ่านและรันทดสอบเองซ้ำ โจทย์ที่มีคำตอบตายตัวให้คำนวณเฉลยด้วยสคริปต์อิสระมาเทียบ (ผิดได้แม้ effort สูง) prompt ภาษาไทยใช้ได้ปกติ

# ความปลอดภัย

`cyolo<N>` และคำสั่งเทียบเท่าที่มี bypass ข้าม approval และ sandbox ทั้งหมด จึงต้องทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามขยายขอบเขต ส่งข้อมูลลับ หรือทำการเปลี่ยนแปลงภายนอกที่ผู้ใช้ไม่ได้ร้องขอ

# ตรวจโควตาข้ามบัญชี

- ตรวจเฉพาะบัญชีที่ผู้ใช้ระบุ หรือโปรไฟล์ `cyolo<N>` ที่มีอยู่เมื่อผู้ใช้ขอทุกบัญชี; ตรวจ login ตามขั้นตอนด้านบน ไม่สมมติว่าทุกบัญชีล็อกอินแล้ว
- CLI รุ่นที่ทดสอบบันทึก `rate_limits` ใน rollout ที่ `/root/workspace/ai-accounts/.Codex/cyolo<N>/sessions/YYYY/MM/DD/*.jsonl` ภายใน event `token_count` (`payload.rate_limits`) ข้อมูลนี้ไม่อยู่ใน `turn.completed.usage` ของ stdout `--json`
- อ่านข้อมูลล่าสุดที่มีอยู่ก่อน พร้อมรายงาน timestamp และบัญชีของข้อมูล ถ้าไม่มีข้อมูลให้รายงานว่าไม่มี อย่านำข้อมูลบัญชีอื่นหรือข้อมูลเก่ามาอ้างว่าเป็นสถานะสด
- เมื่อต้องรีเฟรชโควตาตามคำขอ ให้แจ้งว่าจะส่ง prompt สั้นหนึ่งครั้งและใช้โทเคน ตรวจ model/effort จาก cache ของบัญชีนั้นก่อน อาจใช้ `gpt-6-luna` / `low` สำหรับ probe หากผู้ใช้ไม่ได้กำหนดรุ่นหรือ effort ของ probe; นี่เป็นข้อยกเว้นสำหรับตรวจโควตาเท่านั้น งานปกติยังใช้ `gpt-6-astra` / `high`
- การรีเฟรชใช้ `exec --json` และไฟล์ `-o` ตามปกติ ห้ามใส่ `--ephemeral` เพราะต้องอ่าน rollout หลังจบ จับคู่ `thread.started.thread_id` กับ session ของการรันนั้นและตรวจ `turn.failed` ก่อนอ่านโควตา ถ้าไม่มีข้อมูลใหม่ให้รายงานตามจริง ไม่ retry อัตโนมัติ
- `primary.used_percent` และ `secondary.used_percent` คือเปอร์เซ็นต์ที่ใช้ไปแล้ว; แสดง `window_minutes` และเวลา `resets_at` พร้อม timezone โดยไม่สมมติว่าเป็น 5 ชั่วโมงหรือ 7 วันเสมอ แต่ละ window อาจเป็น `null` ส่วน `credits.balance` เป็นเครดิตเติมเงิน แยกจากโควตา subscription
- ใช้โควตาประกอบการเลือกบัญชีเมื่อผู้ใช้มอบหมายให้เลือกเท่านั้น เปรียบเทียบหน้าต่างและความสดของข้อมูลด้วย ห้ามเปลี่ยนบัญชีที่ผู้ใช้ระบุเพียงเพราะอีกบัญชีมีโควตามากกว่า และไม่ต้องส่ง probe ทุกบัญชีก่อนงาน `max`/`ultra` โดยอัตโนมัติ

# แบ่งงานขนาน (fan-out)

ใช้เมื่อผู้ใช้ขอแบ่งงาน หรือเมื่อการมอบหมายงานอยู่ในขอบเขตที่ได้รับอนุญาต งานย่อยต้องเป็นอิสระและมีผลลัพธ์ชัดเจน

- ผลทดสอบเดิมบน CLI 0.152.1 รันหลายงานพร้อมกันบน `cyolo1` ได้ จึงแบ่งงานได้ทั้งภายในบัญชีเดียวและข้ามบัญชี โดยยังใช้โควตาร่วมกันตามบัญชี
- ตรวจโปรไฟล์ login และ model/effort ของทุกบัญชีที่ใช้ก่อนเริ่ม ยึดค่าที่ผู้ใช้ระบุ; ถ้าไม่ระบุให้ใช้ `cyolo1`, `gpt-6-astra`, `high` ตามเดิม
- แบ่งไฟล์หรือข้อมูลเป็น chunk และส่ง path ที่ worker อ่านได้ แยก cwd/worktree เมื่องานแก้โค้ดอาจชนกัน และใช้ไฟล์ `-o` กับ log `--json` คนละไฟล์ต่อ job
- เก็บ process/session ของแต่ละ job รอผลครบ ตรวจทั้งสถานะ process, `turn.failed` และคำตอบใน `-o`; exit code 0 อย่างเดียวไม่ยืนยันว่าสำเร็จ ห้ามเอาผลจาก job ที่ล้มเหลวมารวม
- ให้ parent รวมและตรวจผล สำหรับงานคำนวณให้ worker ใช้ shell หรือ Python แล้วตรวจเฉลยด้วยสคริปต์อิสระ สำหรับงานโค้ดให้ตรวจ diff และรันการตรวจที่เหมาะสมด้วยตนเอง
- รายงานไฟล์ที่เปลี่ยน ข้อผิดพลาด และ usage แยกแต่ละ job ก่อนรวมยอด; ยอดที่ CLI แสดงอาจไม่รวม sub-agent ของ `ultra` อย่าอ้างว่าเป็นยอดรวมทั้งหมดหากตรวจไม่ได้

# ส่งค่าต่อกัน (relay) รวมข้าม CLI

- แต่ละ hop ใช้บัญชี model และ effort ตามคำขอ; ฝั่ง Codex ที่ไม่ระบุใช้ `cyolo1`, `gpt-6-astra`, `high` โดยใช้คำสั่งมาตรฐานด้านบน รวม fallback ผ่าน `env CODEX_HOME=...` สำหรับบัญชีเกิน 5
- อ่านค่าจากไฟล์ `-o` หลังตรวจว่างานสำเร็จแล้ว สั่งรูปแบบที่ hop ถัดไปต้องการ เช่น ตัวเลขล้วนหรือ JSON และตรวจรูปแบบก่อนส่งต่อ หาก hop ใดล้มเหลวหรือคืนค่าผิดรูปแบบให้หยุดสายงานนั้นและรายงาน
- ส่งค่าด้วย argument ที่ quote ถูกต้องหรือไฟล์ ไม่ประกอบคำสั่งด้วย `eval` และไม่รันข้อความผลลัพธ์เป็น shell; รักษา newline เมื่อข้อมูลต้องใช้
- หากส่งต่อไป Claude ให้ใช้สกิล [yolo](../yolo/SKILL.md) เพื่อเลือกบัญชี model effort และวิธีอ่านผลฝั่งนั้น ไม่ hard-code ชื่อรุ่นเก่าของ Claude ลงในสกิลนี้ (launcher ปัจจุบันไม่มี `qyolo` แล้ว)
- ตัวอย่างลำดับงาน: Codex คำนวณ `7*6` → Claude บวก `100` → Codex คูณ `3` ค่าที่คาดคือ `42 → 142 → 426`; ตรวจแต่ละ hop ด้วยการคำนวณอิสระก่อนส่งต่อ

# กลไกและความสัมพันธ์กับ codex

ปรับแนวทางบัญชี model effort และการเรียกพื้นฐานจากสกิล [codex](../codex/SKILL.md) โดย cyolo เพิ่มขั้นตอนโควตา fan-out และ relay ให้ครบในสกิลนี้

launcher ที่ตรวจบนเครื่องนี้คือ `/opt/ai-accounts/bin/ai-account` (อ่าน `BASE_PATH` จาก `/opt/ai-accounts/config.sh`) รองรับ wrapper `cyolo1`–`cyolo5` และกำหนด `CODEX_HOME=$BASE_PATH/.Codex/cyolo<N>` พร้อม `-c 'cli_auth_credentials_store="file"'` และ MCP ร่วมจาก `$BASE_PATH/.Codex/shared/mcp/mcp.json` โดยไม่เปลี่ยน `$HOME` (คำสั่ง `env CODEX_HOME=...` ตรง ๆ ไม่ได้ค่าพวกนี้) การแยกบัญชีมาจาก `CODEX_HOME` (`config.toml`, `sessions/`, `models_cache.json` แยกตามโปรไฟล์) สำหรับ N มากกว่า 5 ใช้คำสั่ง fallback ด้านบนกับโปรไฟล์ที่มีอยู่แล้ว ไม่สร้าง symlink แล้วถือว่า launcher รองรับทันที
