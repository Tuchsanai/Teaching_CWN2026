# Multi-Account AI CLI Setup บน Ubuntu — สื่อการสอน

หลักสูตรเชิงปฏิบัติ: ติดตั้งและใช้งาน **Claude Code, Codex CLI และ Qwen Code หลาย account พร้อมกัน**
บนเครื่อง Ubuntu เดียว โดยแยก credential / config / session ออกจากกัน **100%**

---

## 0. ภาพรวมหลักสูตร

| หัวข้อ | รายละเอียด |
|---|---|
| กลุ่มเป้าหมาย | Dev / DevOps ที่ใช้ AI CLI มากกว่า 1 บัญชี (งานส่วนตัว + งานลูกค้า + งานทีม) |
| ความรู้พื้นฐาน | Linux shell พื้นฐาน, environment variable, สิทธิ์ไฟล์ (chmod), Node.js/npm เบื้องต้น |
| ระยะเวลา | 6 ชั่วโมง (บรรยาย 2 ชม. + Lab 3.5 ชม. + ตรวจรับ 0.5 ชม.) |
| รูปแบบ | สอนแบบ **ปัญหานำ → แนวคิด → สาธิต → Lab → จุดตรวจ** |
| ผลลัพธ์ | ผู้เรียนได้ installer ที่รันซ้ำได้ + คำสั่ง `yolo1..5`, `cyolo1..5`, `qyolo1..3` ใช้งานจริง |

### ผลลัพธ์การเรียนรู้ (Learning Outcomes)

จบหลักสูตรแล้วผู้เรียนต้อง:

1. **อธิบาย** ได้ว่าทำไม config root ต่อ CLI จึงเป็นวิธีที่ถูกต้องกว่าการสลับ `$HOME`
2. **ระบุ** กลไก official ของแต่ละ CLI สำหรับกำหนด config root ได้ พร้อมบอกแหล่งอ้างอิง
3. **เขียน** wrapper script ที่ส่งต่อ argument และตั้ง env ได้ถูกต้อง
4. **จัดการ** credential อย่างปลอดภัย (สิทธิ์ 600, ไม่รั่วผ่าน process list / log)
5. **ออกแบบ** shared skills/MCP ที่แก้ที่เดียวแล้วทุก account เห็น
6. **เขียน** installer ที่ idempotent (รันซ้ำไม่ทำลายของเดิม)
7. **ทดสอบและรายงานผล** ตามจริงในรูปแบบ PASS / FAIL / SKIP

### แผนการสอน (Teaching Sequence)

ลำดับนี้ออกแบบให้ **แต่ละ Module ใช้ผลลัพธ์ของ Module ก่อนหน้า** — ห้ามข้ามลำดับ

```
M0  เตรียมเครื่อง + ตรวจเวอร์ชันจริง         (30 นาที)  ── พื้นฐาน
     │
M1  ปัญหา: ทำไม account ชนกัน                (20 นาที)  ── แรงจูงใจ
     │
M2  ตัวแปรกลาง + โครงสร้างไดเรกทอรี          (30 นาที)  ── โครงกระดูก
     │
M3  Config root ต่อ CLI (หัวใจของหลักสูตร)   (60 นาที)  ── แกนหลัก
     │
M4  Wrapper commands yolo / cyolo / qyolo     (45 นาที)  ── ใช้งานได้จริง
     │
M5  Qwen credential + ความปลอดภัย             (45 นาที)  ── ของยาก
     │
M6  Shared Skills / MCP                       (45 นาที)  ── ต่อยอด
     │
M7  Installer ที่รันซ้ำได้                    (45 นาที)  ── รวมร่าง
     │
M8  ทดสอบ + ตรวจรับ + รายงาน                 (30 นาที)  ── ปิดจ๊อบ
```

**เหตุผลของลำดับนี้:** M1 สร้างแรงจูงใจก่อนสอนวิธีแก้ · M2 วางโครงให้ทุก Module หลังอ้างอิงได้
· M3 เป็นแนวคิดแกน ถ้าไม่เข้าใจ M4–M7 จะกลายเป็นการ copy-paste · M7 เอาทุกอย่างมาห่อรวม
จึงต้องอยู่หลังสุดก่อนทดสอบ

---

## Module 0 — เตรียมเครื่องและตรวจสอบเวอร์ชันจริง

> **กฎเหล็กของทั้งหลักสูตร: ห้ามเดา env / path / endpoint / model / flag**
> ทุกค่าต้องยืนยันจาก `--help` ของเวอร์ชันที่ติดตั้งจริง หรือ official docs
> ถ้า docs กับ CLI ไม่ตรงกัน → **รายงานความต่าง แล้วใช้ค่าที่ CLI จริงยืนยัน**

### จุดประสงค์
ผู้เรียนตรวจสอบสภาพเครื่องและจดเวอร์ชันจริงของ CLI ทั้งสามตัวได้

### Lab 0
```bash
# ตรวจ OS และ shell
lsb_release -a ; echo $SHELL ; node -v ; npm -v

# ตรวจว่าติดตั้ง CLI แล้วหรือยัง + จดเวอร์ชัน
claude --version ; codex --version ; qwen --version

# อ่าน help เพื่อหา flag/env ที่ใช้จริง (จดใส่ตารางด้านล่าง)
claude --help | less
codex --help | less
qwen  --help | less
```

### ใบจดบันทึก (ให้ผู้เรียนกรอกเอง — ห้ามลอกจากสไลด์)

| CLI | เวอร์ชันจริง | env กำหนด config root | flag skip permission | หมายเหตุ/ข้อจำกัด |
|---|---|---|---|---|
| Claude Code | | `CLAUDE_CONFIG_DIR` | `--dangerously-skip-permissions` | |
| Codex CLI | | `CODEX_HOME` | (bypass approval/sandbox — ยืนยันจาก help) | |
| Qwen Code | | *ต้องยืนยันจาก docs ล่าสุด* | (ยืนยันจาก help) | |

### แหล่งอ้างอิงทางการ
- https://code.claude.com/docs/
- https://github.com/openai/codex
- https://docs.qwencloud.com/developer-guides/clients-and-developer-tools/qwen-code

### จุดตรวจ M0
- [ ] จดเวอร์ชันครบ 3 CLI
- [ ] ระบุกลไก config root ของแต่ละ CLI ได้ พร้อมลิงก์อ้างอิง
- [ ] CLI ตัวใดไม่มีกลไก official → **เขียนข้อจำกัดไว้ชัดเจน** ไม่หาทางลัด

---

## Module 1 — ปัญหา: ทำไมหลาย account ถึงชนกัน

### จุดประสงค์
ผู้เรียนอธิบายอาการชนของ credential/session ได้ และบอกได้ว่าทำไม "สลับ `$HOME`" เป็นทางแก้ที่ผิด

### สาธิตให้เห็นปัญหา (Demo — 5 นาที)
เปิด CLI ตัวเดียวกันสอง terminal ด้วย account ต่างกัน แล้วให้ผู้เรียนสังเกต:
- login ตัวที่สอง **เขียนทับ** credential ตัวแรก
- session / history ปนกัน
- cache ใช้ร่วมกัน → พฤติกรรมไม่แน่นอน

### แนวคิดหลัก
สิ่งที่ต้องแยกให้ครบมี **5 อย่าง**: `credential` · `config` · `session` · `history` · `cache`
แยกไม่ครบข้อใดข้อหนึ่ง = ยังชนอยู่

### กับดักที่พบบ่อย
| วิธีที่คนมักทำ | ทำไมถึงพัง |
|---|---|
| `HOME=/path/to/acc1 claude` | พัง Git, SSH, npm cache และ tool อื่นทั้งเครื่อง |
| สลับไฟล์ credential ไปมาด้วย script | เปิดพร้อมกันไม่ได้ และมีโอกาสไฟล์หาย |
| ใช้ Docker แยกทุก account | ได้ผลแต่หนักเกินความจำเป็นสำหรับงาน CLI |

### คำถามชวนคิด
> ถ้าเปลี่ยน `$HOME` แล้ว `git commit` จะใช้ identity ของใคร? และ `~/.ssh` จะยังหาเจอไหม?

### จุดตรวจ M1
- [ ] อธิบายได้ว่าต้องแยกอะไรบ้าง 5 อย่าง
- [ ] อธิบายผลเสียของการเปลี่ยน `$HOME` ได้อย่างน้อย 2 ข้อ

---

## Module 2 — ตัวแปรตั้งค่ากลางและโครงสร้างไดเรกทอรี

### จุดประสงค์
ผู้เรียนวางโครงสร้างไดเรกทอรีจากตัวแปรกลางตัวเดียวได้

### หลักการ: Single Source of Truth
**แก้ที่เดียว ที่อื่นอ้างอิงตัวแปรนี้เท่านั้น** — ห้าม hard-code path ซ้ำที่ใดในระบบ

```bash
BASE_PATH="/root/workspace"
```

### โครงสร้างเป้าหมาย
```
$BASE_PATH/
├── .Claude/          yolo1..yolo5    + shared/{skills,mcp}
├── .Codex/           cyolo1..cyolo5  + shared/{skills,mcp}
└── .Qwen/            qyolo1..qyolo3  + shared/{skills,mcp}
```

### ตารางคำสั่งเป้าหมาย
| คำสั่ง | CLI | ผูกกับบัญชี | หมายเหตุ |
|---|---|---|---|
| `yolo1` .. `yolo5` | Claude Code | Anthropic account | |
| `cyolo1` .. `cyolo5` | Codex CLI | OpenAI account | |
| `qyolo1` .. `qyolo3` | Qwen Code | QwenCloud account | **เรียก Qwen Code โดยตรง** ห้ามผ่าน Claude Code/Codex |

### Lab 2
```bash
BASE_PATH="/root/workspace"
mkdir -p "$BASE_PATH"/.Claude/{yolo1,yolo2,yolo3,yolo4,yolo5,shared/{skills,mcp}}
mkdir -p "$BASE_PATH"/.Codex/{cyolo1,cyolo2,cyolo3,cyolo4,cyolo5,shared/{skills,mcp}}
mkdir -p "$BASE_PATH"/.Qwen/{qyolo1,qyolo2,qyolo3,shared/{skills,mcp}}
tree -L 2 "$BASE_PATH"/.Claude "$BASE_PATH"/.Codex "$BASE_PATH"/.Qwen
```

### จุดตรวจ M2
- [ ] โครงสร้างครบตามผัง
- [ ] ค้นทั้งโปรเจกต์แล้ว **ไม่มี path ที่ hard-code** นอกจากตัวแปร `BASE_PATH`

---

## Module 3 — Config Root ต่อ CLI *(หัวใจของหลักสูตร)*

### จุดประสงค์
ผู้เรียนใช้กลไก official ของแต่ละ CLI ชี้ config root ไปยังโฟลเดอร์ของแต่ละ account ได้

### กฎ 3 ข้อของการทำ Isolation
1. **แยกครบ 5 อย่าง** — credential / config / session / history / cache เปิดพร้อมกันต้องไม่ชน
2. **ห้ามเปลี่ยน `$HOME`** — ใช้กลไก official ต่อ CLI เท่านั้น
   - Claude Code → `CLAUDE_CONFIG_DIR`
   - Codex CLI → `CODEX_HOME`
   - Qwen Code → ตาม docs ล่าสุด (ยืนยันก่อนใช้)
   - CLI ใดไม่มีกลไก official → **ระบุข้อจำกัดให้ชัด และทำเฉพาะเท่าที่รองรับจริง**
3. **ห้ามแก้ของเดิมโดยไม่จำเป็น** — `.bashrc`, Git config, SSH config, project environment

### สาธิต
```bash
CLAUDE_CONFIG_DIR="$BASE_PATH/.Claude/yolo1" claude --version
CODEX_HOME="$BASE_PATH/.Codex/cyolo1"        codex --version
```

### Lab 3 — พิสูจน์ว่าแยกกันจริง
```bash
# terminal 1
CLAUDE_CONFIG_DIR="$BASE_PATH/.Claude/yolo1" claude
# terminal 2 (พร้อมกัน)
CLAUDE_CONFIG_DIR="$BASE_PATH/.Claude/yolo2" claude

# ตรวจว่าไฟล์ credential เกิดแยกกันจริง
find "$BASE_PATH/.Claude/yolo1" "$BASE_PATH/.Claude/yolo2" -maxdepth 2 -type f
```

### กับดักที่พบบ่อย
- ตั้ง env ใน `.bashrc` แบบ global → ทุก account กลายเป็นตัวเดียวกัน (**ผิดกฎข้อ 3**)
- ตั้ง env แล้วไม่ `export` ให้ subprocess เห็น
- เชื่อว่า Qwen ใช้ env ชื่อเดียวกับ Claude/Codex → **ต้องเช็ค docs เสมอ**

### จุดตรวจ M3
- [ ] `yolo1` และ `yolo2` เปิดพร้อมกันได้ ไม่แย่ง credential กัน
- [ ] `.bashrc` / Git config / SSH config **ไม่ถูกแก้**
- [ ] ระบุกลไกที่ใช้ของทั้ง 3 CLI ได้ พร้อมข้อจำกัดของตัวที่ไม่รองรับ

---

## Module 4 — Wrapper Commands

### จุดประสงค์
ผู้เรียนเขียน wrapper ที่ผูก account + ส่งต่อ argument + เปิดโหมด skip permission ได้

### ข้อกำหนด
ทุกคำสั่งต้อง **ส่งต่อ `"$@"`** และรันแบบ skip permissions ด้วย flag ล่าสุดของแต่ละ CLI

| Wrapper | รูปแบบคำสั่งจริง |
|---|---|
| `yoloN` | `claude --dangerously-skip-permissions "$@"` |
| `cyoloN` | `codex` + flag bypass approval/sandbox + `"$@"` |
| `qyoloN` | `qwen` + flag permission/approval ที่รองรับ + `"$@"` |

> ⚠️ **สอนเรื่องความเสี่ยงตรงนี้ด้วย:** skip permissions = CLI ทำงานได้โดยไม่ถามยืนยัน
> ต้องอธิบายให้ผู้เรียนเข้าใจว่าเหมาะกับ sandbox/งานที่ควบคุมได้เท่านั้น

### แม่แบบ wrapper (`yolo1`)
```bash
#!/usr/bin/env bash
set -euo pipefail
BASE_PATH="/root/workspace"                       # อ้างอิงตัวแปรกลางเสมอ
export CLAUDE_CONFIG_DIR="$BASE_PATH/.Claude/yolo1"
exec claude --dangerously-skip-permissions "$@"   # exec = ไม่เหลือ process ซ้อน
```

### Lab 4
1. สร้าง `yolo1`, `yolo2`, `cyolo1` ตามแม่แบบ
2. `chmod +x` และวางในตำแหน่งที่อยู่ใน `PATH`
3. ทดสอบส่งต่อ argument: `yolo1 --version` และ `yolo1 -p "hello"`

### จุดตรวจ M4
- [ ] `yolo1 --version` แสดงผลถูก (แปลว่า `"$@"` ส่งต่อจริง)
- [ ] เปิด `yolo1` กับ `yolo2` พร้อมกันได้
- [ ] ใช้ `exec` และมี `set -euo pipefail`

---

## Module 5 — Qwen Credential และความปลอดภัย

### จุดประสงค์
ผู้เรียนรับ API key อย่างปลอดภัยและจับคู่ plan กับ endpoint/model ได้ถูกต้อง

### 5.1 เลือก plan ตอนใช้ `qyoloN` ครั้งแรก
ให้ผู้ใช้เลือก 1 ใน 4 แล้วกรอก API key แบบ **ซ่อนตัวอักษร**:

| Plan | endpoint | credential variable | default model |
|---|---|---|---|
| Token Plan Personal | *ตาม docs* | *ตาม docs* | *ตาม docs* |
| Token Plan Team | *ตาม docs* | *ตาม docs* | *ตาม docs* |
| Coding Plan | *ตาม docs* | *ตาม docs* | *ตาม docs* |
| Pay-as-you-go | *ตาม docs* | *ตาม docs* | *ตาม docs* |

> ค่าทั้ง 3 คอลัมน์ **ต้องตรงกับ plan ตาม docs** — ห้ามเดา ห้ามใช้ข้าม plan
> (ให้ผู้เรียนเปิด docs กรอกตารางนี้เองใน Lab)

### 5.2 กฎการเก็บ key
- เก็บแยกใน `$BASE_PATH/.Qwen/qyoloN` สิทธิ์ **600**
- ❌ ห้ามฝังใน source / template / ไฟล์ที่แจกจ่าย
- ❌ ห้ามส่งผ่าน command-line argument
- ❌ ห้ามแสดงใน terminal / process list / log
- ❌ ห้ามใช้ key เดียวข้ามหลาย account โดยไม่แจ้งเจ้าของ credential

### Lab 5 — รับ key แบบไม่รั่ว
```bash
read -rsp "Qwen API key: " QWEN_KEY ; echo      # -s = ไม่ echo ตัวอักษร
umask 077
printf '%s\n' "$QWEN_KEY" > "$BASE_PATH/.Qwen/qyolo1/credential"
chmod 600 "$BASE_PATH/.Qwen/qyolo1/credential"
unset QWEN_KEY

# พิสูจน์ว่าไม่รั่ว: ต้องไม่เห็น key ใน process list
qyolo1 & sleep 1 ; ps aux | grep -i qwen ; kill %1
```

### จุดตรวจ M5
- [ ] ไฟล์ credential สิทธิ์ `600` จริง (`ls -l`)
- [ ] `ps aux` และ log **ไม่ปรากฏ key**
- [ ] plan ↔ endpoint ↔ model จับคู่ตรงตาม docs

---

## Module 6 — Shared Skills และ MCP

### จุดประสงค์
ผู้เรียนตั้ง shared source ให้ **แก้ครั้งเดียว ทุก account ของ CLI นั้นเห็น**

### หลักการ
แต่ละ CLI ใช้ `<tool>/shared` เป็น source เดียว
- **Skills** → symlink หรือกลไก discovery ทางการของ CLI นั้น
- **MCP** → ถ้า CLI ไม่มี config include ให้ใช้วิธี sync
  ส่วนใดไม่รองรับ → **ระบุให้ชัดและทำเท่าที่รองรับจริง**

### Lab 6
```bash
# ตัวอย่าง: symlink skills เข้าทุก account ของ Claude
for d in "$BASE_PATH"/.Claude/yolo*; do
  ln -sfn "$BASE_PATH/.Claude/shared/skills" "$d/skills"
done

# ทดสอบ: เพิ่ม skill 1 ตัวใน shared แล้วเช็คว่าทุก account เห็น
```

### จุดตรวจ M6
- [ ] เพิ่ม Skill 1 ตัวใน shared ของแต่ละ CLI → ทุก account ของ CLI นั้นเห็น
- [ ] เพิ่ม MCP 1 ตัวใน shared → ทุก account ที่เกี่ยวข้องเห็น
- [ ] เขียนบันทึกข้อจำกัดของ CLI ที่รองรับไม่ครบ

---

## Module 7 — Installer ที่รันซ้ำได้ (Idempotent)

### จุดประสงค์
ผู้เรียนรวมทุก Module เป็น installer เดียวที่รันซ้ำได้อย่างปลอดภัย

### ข้อกำหนด
1. **รันซ้ำได้โดยไม่ลบ/เขียนทับ credential และ config เดิม**
2. เลือกวิธีติดตั้งและการจัดวางไฟล์เองได้ แต่ต้อง **อธิบายเหตุผลสั้น ๆ**

### เทคนิค idempotent ที่ควรสอน
| งาน | คำสั่งที่ปลอดภัย |
|---|---|
| สร้างโฟลเดอร์ | `mkdir -p` |
| สร้าง symlink | `ln -sfn` |
| เขียนไฟล์ credential | เช็ค `[ -f "$f" ] \|\| ...` **ก่อนเขียนเสมอ** |
| เขียน wrapper | เขียนทับได้ (เป็น generated file ไม่มี secret) |

### Lab 7
1. เขียน `install.sh` ครอบคลุม M2–M6
2. รันรอบที่ 1 → ตรวจผล
3. รันรอบที่ 2 → **credential และ config เดิมต้องอยู่ครบ ไม่ถูกแตะ**

### จุดตรวจ M7
- [ ] รันรอบที่ 2 แล้ว credential เดิมยังอยู่ (เทียบ checksum ก่อน/หลัง)
- [ ] อธิบายเหตุผลของการจัดวางไฟล์ที่เลือกได้

---

## Module 8 — ทดสอบและตรวจรับ

> **รายงานตามจริงเท่านั้น: PASS / FAIL / SKIP** — ห้ามเขียน PASS ถ้ายังไม่ได้ทดสอบจริง

| # | รายการทดสอบ | ผล |
|---|---|---|
| 1 | `yolo1`/`yolo2` login คนละ account, `cyolo1`/`cyolo2` login คนละ account, `qyolo1`/`qyolo2` ใส่ key ต่างกัน → เปิดพร้อมกัน ไม่ชน | ☐ |
| 2 | Qwen key ไม่ปรากฏใน argument / process list / log | ☐ |
| 3 | เพิ่ม Skill และ MCP อย่างละ 1 ใน shared ของแต่ละ CLI → ทุก account ที่เกี่ยวข้องเห็น | ☐ |
| 4 | รัน installer รอบ 2 → ไม่ทำลายของเดิม | ☐ |
| 5 | Git / SSH ยังทำงานปกติ | ☐ |
| 6 | เทสต์ที่ต้องใช้ credential จริง → ให้เจ้าของ credential เป็นผู้รัน (มิฉะนั้นรายงาน **SKIP**) | ☐ |

### สิ่งที่ต้องส่งพร้อมรายงาน
- **config root** ของแต่ละ CLI
- **ตำแหน่ง credential** ของแต่ละ account
- **shared source** ของแต่ละ CLI
- **ข้อจำกัด** ที่พบของแต่ละ CLI (ตัวไหนไม่รองรับอะไร)

---

## ภาคผนวก A — ตารางสรุปสำหรับผู้สอน (Cheat Sheet)

| Module | แนวคิดที่ต้องได้ | Lab ส่งอะไร | เวลา |
|---|---|---|---|
| M0 | ห้ามเดา — ยืนยันจาก `--help`/docs | ตารางเวอร์ชัน + env | 30' |
| M1 | แยก 5 อย่าง, ห้ามแตะ `$HOME` | คำอธิบายปัญหา | 20' |
| M2 | Single source of truth | โครงสร้างไดเรกทอรี | 30' |
| M3 | Config root ต่อ CLI | 2 account เปิดพร้อมกัน | 60' |
| M4 | `"$@"` + `exec` + skip permission | wrapper 3 ตัว | 45' |
| M5 | Secret hygiene | credential 600 + พิสูจน์ไม่รั่ว | 45' |
| M6 | Shared source เดียว | symlink/sync ทำงาน | 45' |
| M7 | Idempotency | `install.sh` | 45' |
| M8 | รายงานตามจริง | ตารางผลทดสอบ | 30' |

## ภาคผนวก B — Troubleshooting

| อาการ | สาเหตุที่พบบ่อย | ทางแก้ |
|---|---|---|
| account ยังชนกัน | env ไม่ถูก `export` หรือชี้ path ผิด | `echo $CLAUDE_CONFIG_DIR` ใน wrapper |
| wrapper ไม่รับ argument | ลืม `"$@"` หรือใส่ `$@` ไม่มี quote | ใส่ `"$@"` ท้ายคำสั่ง |
| key โผล่ใน `ps` | ส่ง key ผ่าน argument | เปลี่ยนเป็นอ่านจากไฟล์ 600 |
| installer รอบ 2 ลบ credential | ใช้ `>` เขียนทับตรง ๆ | เช็ค `[ -f ]` ก่อนเขียน |
| Git/SSH พัง | ไปเปลี่ยน `$HOME` | เลิกใช้วิธีนั้น กลับไปใช้ config root |

## ภาคผนวก C — สเปกต้นฉบับ

ข้อกำหนดตั้งต้นเก็บไว้ที่ `readme.original.md` (ไฟล์เดิมก่อนจัดเรียงใหม่)
เนื้อหาถูกกระจายเข้าสู่ Module ตามนี้:

| ข้อกำหนดเดิม | อยู่ใน Module |
|---|---|
| ตัวแปร `BASE_PATH`, โครงสร้าง, รายการคำสั่ง | M2 |
| Isolation ข้อ 1–3 | M1, M3 |
| Wrapper ข้อ 4 | M4 |
| Qwen credential ข้อ 5–7 | M5 |
| Skills/MCP ข้อ 8 | M6 |
| Installer ข้อ 9–10 | M7 |
| Docs ข้อ 11 | M0 (ยกขึ้นเป็นกฎเหล็กของทั้งหลักสูตร) |
| รายการทดสอบ | M8 |
