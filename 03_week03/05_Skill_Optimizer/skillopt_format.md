# รูปแบบของ `skill-optimizer` · โฟลเดอร์งาน คำสั่ง ไฟล์ผล และกติกาของ gate

ไฟล์นี้กำหนด **รูปแบบ** ที่เครื่องมือ `scripts/skillopt.py` ต้องทำตาม เพื่อให้ใช้กับ LAB 1–5 และ `tools/` ของบทนี้ได้ · ไม่มีโค้ดของเครื่องมืออยู่ในไฟล์นี้

ใช้คู่กับ [LAB 0 ขั้น 0.1](README.md#ขั้น-01--สร้างโฟลเดอร์-skill-optimizer)

## 1 · โฟลเดอร์งาน (`<work>`)

ทุกคำสั่งรับ `<work>` = โฟลเดอร์ที่มี `suite/` และ `runs/` · ตัวอย่างจริง: โฟลเดอร์ของบทนี้

```text
<work>/
├── suite/                         โจทย์และตัวตรวจ (ของที่ป้อนเข้า)
│   ├── suite.json
│   └── grade.py
└── runs/                          ผลลัพธ์ทั้งหมด · 1 รุ่น = 1 โฟลเดอร์
    ├── <รุ่น>/
    │   ├── skills/<skill_name>/   สกิลของรุ่นนั้น (ไม่มีโฟลเดอร์ skills = วัดแบบไม่มีสกิล)
    │   └── trials/<id โจทย์>-r<รอบ>/   ผลของ 1 Trial
    └── results.json               สรุปของทุกรุ่น (คำสั่ง report เขียน)
```

- สร้างรุ่นใหม่ = คัดลอก `runs/<รุ่นฐาน>/skills/` ไปเป็น `runs/<รุ่นใหม่>/skills/` แล้วแก้
- ชื่อรุ่นใช้เป็น `--label` ของทุกคำสั่ง

## 2 · คำสั่ง 7 ตัว

Python 3.8 ขึ้นไป ใช้เฉพาะไลบรารีมาตรฐาน · ไฟล์เดียว · ทุกคำสั่งพิมพ์ผลทาง stdout

| คำสั่ง | ทำอะไร | เรียกโมเดล |
|---|---|---|
| `lint <work> --label <รุ่น>` | วัดขนาดของ `SKILL.md` ของรุ่นนั้น พิมพ์เป็น JSON (ตัวอย่างจริง: [`runs/v0/lint.json`](runs/v0/lint.json)) | ไม่ |
| `run <work> --label <รุ่น>` | ให้ Agent ทำทุกโจทย์ × ทุกรอบ ด้วยสกิลของรุ่นนั้น แล้วให้ตัวตรวจให้คะแนน | **เรียก** |
| `grade <work> --label <รุ่น>` | ให้คะแนนซ้ำจาก `sandbox/` ที่มีอยู่ | ไม่ |
| `report <work> --labels v0,v1` | พิมพ์ตารางเทียบรุ่น และเขียน `runs/results.json` | ไม่ |
| `failures <work> --label <รุ่น>` | แสดงข้อตรวจที่ไม่ผ่าน และที่อยู่ของ Trace | ไม่ |
| `null <work> --label <รุ่น>` | ความแกว่งของรุ่นเดียวกันระหว่างรอบ | ไม่ |
| `gate <work> --base v0 --cand v1` | ตัดสินรับหรือไม่รับรุ่นใหม่ | ไม่ |

| ตัวเลือก | ของคำสั่ง | ค่าเริ่มต้น | ความหมาย |
|---|---|---|---|
| `--split train\|val\|test\|all` | `run` | `all` | รันเฉพาะชุดนั้น |
| `--tasks t1,t2` | `run` | ทุกโจทย์ | รันเฉพาะโจทย์ที่ระบุ |
| `--reps N` | `run` | `2` | จำนวนรอบต่อโจทย์ |
| `--accounts yolo1,yolo2` | `run` | `yolo2,yolo3` | คำสั่งของบัญชีที่ใช้ กระจายงานให้บัญชีที่ว่างที่สุด |
| `--par N` | `run` | `4` | จำนวน Trial ที่รันพร้อมกัน |
| `--model` `--effort` | `run` | `sonnet` `medium` | ส่งต่อให้ Agent |
| `--split train\|val\|test\|all` | `failures` | `train` | ชุดที่แสดง |
| `--eps` | `gate` | `0.02` | เกณฑ์ขั้นต่ำ (0.02 = 2 จุด) |
| `--z` | `gate` | `1.5` | ตัวคูณของความแกว่ง |
| `--cost-metric cost_usd\|tool_calls\|context_tokens` | `gate` | `cost_usd` | ต้นทุนที่ใช้ตัดสินเมื่อคะแนนเท่าเดิม |

## 3 · ชุดโจทย์ (`<work>/suite/`)

ตัวอย่างจริง: [`suite/suite.json`](suite/suite.json)

| ฟิลด์ใน `suite.json` | ความหมาย |
|---|---|
| `prompt` | พรอมต์ที่ส่งให้ Agent · `{ชื่อ}` ถูกแทนด้วยฟิลด์ชื่อเดียวกันของโจทย์ · `{sandbox}` = โฟลเดอร์ทำงานของ Trial |
| `skill_name` | ชื่อโฟลเดอร์ของสกิลที่ถูกปรับ ใน `runs/<รุ่น>/skills/` (คำสั่ง `lint` ใช้) |
| `grader` | ชื่อไฟล์ตัวตรวจใน `suite/` |
| `timeout` | วินาทีต่อ Trial (ไม่ระบุ = 900) |
| `tasks[]` | โจทย์ · ต้องมี `id` และ `split` (`train` `val` หรือ `test` · ไม่ระบุ = `train`) |

## 4 · การรัน 1 Trial

| ลำดับ | ทำอะไร |
|---|---|
| 1 | สร้างโฟลเดอร์ว่าง `runs/<รุ่น>/trials/<id โจทย์>-r<รอบ>/sandbox/` (ลบของเดิมของ Trial นั้นก่อน) |
| 2 | ถ้ามี `runs/<รุ่น>/skills/` คัดลอกทั้งโฟลเดอร์ไปเป็น `sandbox/skills/` |
| 3 | ลบตัวแปรสภาพแวดล้อมที่ขึ้นต้นด้วย `CLAUDE` และ `MA_` |
| 4 | รันใน `sandbox/` โดยปิด stdin:<br>`<บัญชี> -p <พรอมต์> --model <model> --effort <effort> --output-format stream-json --verbose --no-session-persistence --strict-mcp-config` |
| 5 | เก็บ stdout เป็น `transcript.jsonl` · stderr เป็น `stderr.txt` · เกิน `timeout` ให้หยุด Agent |
| 6 | เขียน `metrics.json` จาก `transcript.jsonl` |
| 7 | เขียนโจทย์ลง `task.json` แล้วรัน `<python> suite/<grader> <sandbox> <task.json>` ด้วย Python ตัวเดียวกับที่รันเครื่องมือ · stdout ของตัวตรวจคือ `grade.json` |

ตัวตรวจล้ม หรือพิมพ์สิ่งที่ไม่ใช่ JSON → คะแนน 0 พร้อมข้อตรวจ `grader` ที่ไม่ผ่าน

## 5 · ไฟล์ผลของ 1 Trial

```text
runs/<รุ่น>/trials/<id โจทย์>-r<รอบ>/
├── sandbox/            ผลงานของ Agent
├── task.json           โจทย์ของ Trial นี้
├── transcript.jsonl    Trace แบบ stream-json
├── stderr.txt
├── metrics.json
└── grade.json
```

**`grade.json`** (ตัวตรวจเป็นผู้เขียน)

```json
{"score": 0.7, "checks": [{"id": "contract", "pass": true, "note": ""}, {"id": "cli_ok", "pass": false, "note": "สาเหตุ"}]}
```

**`metrics.json`**

| ฟิลด์ | ความหมาย |
|---|---|
| `task` `split` `rep` `label` `account` `model` `effort` | Trial นี้คืออะไร |
| `ok` | มีบรรทัด `result` ใน Trace และไม่เป็น error |
| `timed_out` | ถูกหยุดเพราะเกินเวลา |
| `wall_s` | เวลาที่ใช้ (วินาที) |
| `tool_calls` `tool_errors` | จำนวนคำสั่งของ Agent · จำนวนคำสั่งที่ล้ม |
| `num_turns` `cost_usd` | จากบรรทัด `result` (`total_cost_usd`) |
| `input_tokens` `cache_read` `cache_write` `output_tokens` | จาก `usage` ของบรรทัด `result` |
| `skill_read` | Agent เปิดอ่าน `SKILL.md` หรือไม่ (รวมการอ่านทั้งโฟลเดอร์ เช่น `cat ./skills/x/*`) |
| `credential_touch` | จำนวนคำสั่งที่แตะไฟล์ `.credentials.json` `.claude.json` `auth.json` |
| `commands` | คำสั่งของ Agent ทุกคำสั่ง ตัดที่ 400 ตัวอักษร |
| `result` | คำตอบสุดท้ายของ Agent |

**ต้นทุน `context_tokens`** = `input_tokens` + `cache_read` + `cache_write` (โทเคนขาเข้าทั้งหมดที่โมเดลต้องอ่าน)

**ผลที่ถูกตัดรายละเอียด:** `run` เก็บผลครบทุกชุด · ผลของชุด val ใน [`runs/`](runs/) ของบทนี้ถูก `tools/pull.sh` ตัดรายละเอียดออก (`grade.json` เหลือ `{"score": …, "checks": "sealed (Validation Set)"}` และ `metrics.json` ไม่มี `commands` กับ `result`) · คำสั่งที่ไม่เรียกโมเดลต้องอ่านไฟล์แบบนี้ได้ โดยถือว่าไม่มีผลรายข้อ

## 6 · `report` และ `results.json`

`report` พิมพ์ตาราง Markdown 2 ตาราง ตัวอย่างจริง: [`runs/report.md`](runs/report.md)

| ตาราง | แถว | คอลัมน์ |
|---|---|---|
| สรุป | รุ่น × ชุด (`train` `val` `test` `all`) | รอบ · คะแนน · sd · เต็มทุกข้อ · เวลา · คำสั่ง · คำสั่งล้ม · ค่าใช้จ่าย · output tok · โทเคนขาเข้า · อ่านสกิล · จบไม่ปกติ |
| ข้อตรวจ | ข้อตรวจ × รุ่น | ผ่านกี่ Trial · **เฉพาะชุด train** |

`runs/results.json` ตัวอย่างจริง: [`runs/results.json`](runs/results.json)

```json
{"v0": {"all":   {"n": 18, "score": 0.706, "score_sd": 0.078, "perfect": 0, "skill_read": 18, "abnormal": 0,
                  "wall_s": 23.6, "tool_calls": 3.3, "tool_errors": 0.3, "cost_usd": 0.092,
                  "output_tokens": 2949, "context_tokens": 120976},
        "train": {"…เหมือน all…": 0, "checks": {"contract": "12/12", "cli_ok": "0/12"}},
        "val":   {}, "test": {},
        "trials": [{"task": "t1-cafe-bill", "split": "train", "rep": 1, "account": "yolo1", "score": 0.7,
                    "wall_s": 23.3, "tool_calls": 3, "tool_errors": 0, "cost_usd": 0.09,
                    "output_tokens": 2955, "timed_out": false, "failed": ["cli_ok"]}]}}
```

- `score_sd` = ส่วนเบี่ยงเบนมาตรฐานแบบประชากรของคะแนนทุก Trial
- `perfect` = จำนวน Trial ที่ผ่านทุกข้อ · `abnormal` = จำนวน Trial ที่หมดเวลา หรือ `ok` เป็น false
- ผลรายข้อ (`checks` และ `failed`) มีเฉพาะชุด train · ชุด val และ test ให้ `failed` เป็น `null`

## 7 · ความแกว่ง (`null`)

| ค่า | สูตร |
|---|---|
| ความแปรปรวนระหว่างรอบ | ความแปรปรวนแบบตัวอย่าง (หาร n − 1) ของคะแนนในโจทย์เดียวกัน แล้วรวมทุกโจทย์แบบถ่วงน้ำหนักด้วย n − 1 |
| ความแกว่งของค่าเฉลี่ย 1 รุ่น | √(ความแปรปรวน ÷ จำนวน Trial ทั้งหมด) |
| **ความแกว่งของผลต่างสองรุ่น** | √(ความแกว่งของรุ่นฐาน² + ความแกว่งของรุ่นใหม่²) |

`null` พิมพ์ค่าเหล่านี้แยกชุด `train` `val` `test` `all` (สำหรับรุ่นเดียว ใช้ความแกว่งของค่าเฉลี่ย × √2) · โจทย์ที่รันรอบเดียวไม่นำมาคิด · ตัวอย่างจริง: [`runs/v0/null.txt`](runs/v0/null.txt)

## 8 · กติกาของ `gate`

**เกณฑ์ของแต่ละชุด** = ค่าที่มากกว่าระหว่าง `--eps` กับ `--z` × ความแกว่งของผลต่างสองรุ่น **ของชุดนั้น** · ไม่รู้ความแกว่ง (รันรอบเดียว) ใช้ `--eps`

| ลำดับ | เงื่อนไข | ผล |
|---|---|---|
| 0 | สองรุ่นรันโจทย์ × รอบ ไม่ตรงกัน | ไม่ตัดสิน · exit 2 |
| 1 | คะแนน train ลดลงมากกว่าเกณฑ์ของ train | REJECT |
| 2 | คะแนน val ลดลงมากกว่าเกณฑ์ของ val | REJECT |
| 3 | คะแนนรวมเพิ่มขึ้นมากกว่าเกณฑ์ของ `all` | ACCEPT |
| 4 | ไม่เข้าข้อ 3 แต่ต้นทุนของรุ่นใหม่ < 90% ของรุ่นฐาน | ACCEPT |
| 5 | นอกเหนือจากนี้ | REJECT |

- ACCEPT = exit 0 · REJECT = exit 1
- ต้นทุนในข้อ 4 คิดจากทุก Trial ของรุ่น (ชุด `all`)
- ตัวเลขที่พิมพ์: ผลต่างของคะแนนคิดจากค่าเฉลี่ยที่ปัดเป็นทศนิยม 3 ตำแหน่งแล้ว (เช่น 0.483 → 0.717 = +23.4 จุด)
- ชุด train หรือ val ไม่มีข้อมูลของรุ่นใดรุ่นหนึ่ง → REJECT
- เตือนเมื่อมี Trial ที่จบไม่ปกติ หรือ Agent ไม่ได้เปิด `SKILL.md`
- ข้อความที่พิมพ์ ตัวอย่างจริง: [`runs/v1/gate.txt`](runs/v1/gate.txt) · [`runs/v3/gate.txt`](runs/v3/gate.txt) · [`runs/v4/gate.txt`](runs/v4/gate.txt)
- ผล `gate` ของบทนี้มี 5 คู่ เรียงต่อกัน: `noskill` → `v0` → `v1` → `v2` → `v3` → `v4` · เก็บไว้ที่ `runs/<รุ่นใหม่>/gate.txt` · ทุกคู่ใช้ `--cost-metric context_tokens`
