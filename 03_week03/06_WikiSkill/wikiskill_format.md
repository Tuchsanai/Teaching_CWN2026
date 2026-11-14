# รูปแบบของ `wikiskill` · โฟลเดอร์งาน คำสั่ง ไฟล์ของ 3 ชั้น และกติกาของวงรอบ

ไฟล์นี้กำหนด **รูปแบบ** ที่เครื่องมือ `scripts/wikiskill.py` ต้องทำตาม เพื่อให้ใช้กับ LAB 1–5 และสคริปต์วาดภาพใน `tools/` ของบทนี้ได้ · ไม่มีโค้ดและไม่มี prompt ของเครื่องมืออยู่ในไฟล์นี้

ใช้คู่กับ [LAB 0 ขั้น 0.1](README.md#ขั้น-01--สร้างโฟลเดอร์-wikiskill) · เลขบรรทัดที่อ้างคือ Algorithm 1 ของเปเปอร์ WikiSkill (arXiv:2608.27454 ภาคผนวก A.1)

## 1 · โฟลเดอร์ของสกิล

```text
my-wikiskill/
├── SKILL.md                  คู่มือที่ AI อ่าน: ใช้เมื่อไร · ตารางคำสั่ง · ขั้นตอน · ข้อห้าม
├── scripts/wikiskill.py      โปรแกรมของวงรอบ (ไฟล์เดียว · Python 3.8 ขึ้นไป · ไลบรารีมาตรฐานเท่านั้น)
├── prompts/
│   ├── maintainer.md         system prompt ของ Wiki Maintainer
│   ├── proposer.md           system prompt ของ Skill Proposer
│   └── proposer_nowiki.md    system prompt ของ Skill Proposer เมื่อไม่ใช้ wiki (`--no-wiki`)
└── references/
    ├── source.md             ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง
    └── workspace.md          โครงของ workspace และไฟล์ที่แต่ละคำสั่งเขียน
```

- prompt ทั้ง 3 ไฟล์เขียนด้วยถ้อยคำของตัวเอง (ห้ามคัดลอก prompt ในภาคผนวก E ของเปเปอร์) · ใน prompt ใช้ `{task_desc}` แทนคำอธิบายงาน โปรแกรมแทนค่าให้ตอนเรียกโมเดล
- โปรแกรมหา prompt จากโฟลเดอร์ `prompts/` ที่อยู่ข้าง `scripts/`

## 2 · โฟลเดอร์งาน (`<work>`) และ workspace

`<work>` = โฟลเดอร์งานรูปแบบเดียวกับ `skill-optimizer` ของ [บท 05](../05_Skill_Optimizer/skillopt_format.md) (มี `suite/` และ `runs/`) · **1 การรัน WikiSkill = 1 workspace = `runs/<ws>/`**

```text
<work>/
├── suite/                              โจทย์และตัวตรวจ (ของที่ป้อนเข้า)
└── runs/<ws>/
    ├── state.json                      สถานะของวงรอบ (ข้อ 4)
    ├── raw/iter-NN/                    Raw Layer · เขียนครั้งเดียว ไม่แก้
    │   ├── traces/<id โจทย์>-r<รอบ>.md   Trace ของ Training 1 ไฟล์ต่อ 1 Trial
    │   └── summary.md                  ตารางผลของทุก Trace ในรอบนั้น
    ├── wiki/                           Wiki Layer · สะสม ไม่ถูกย้อนกลับ
    │   ├── index.md                    สารบัญ 1 บรรทัดต่อ 1 pattern        (Wiki Maintainer เขียน)
    │   ├── log.md                      บันทึกของแต่ละรอบ                    (Wiki Maintainer เขียน โปรแกรมต่อท้ายให้)
    │   ├── skill-impact.md             ข้อเสนอ diff คะแนน และผลตัดสินทุกรอบ   (โปรแกรมเขียน)
    │   └── patterns/<ชื่อ>.md           1 หน้าต่อ 1 pattern                  (Wiki Maintainer เขียน)
    ├── skills/<ชื่อ>/                   Skills Layer · ชุดสกิลที่ใช้งาน ย้อนกลับได้
    │   ├── SKILL.md
    │   └── PURPOSE.md
    ├── history/iter-NN/                หลักฐานของแต่ละรอบ (ข้อ 7–9)
    └── rollouts/                       โฟลเดอร์งานของ skill-optimizer ที่ใช้รัน Trial (ข้อ 5)
        ├── suite/                      สำเนา suite.json และไฟล์ตัวตรวจ
        └── runs/<ป้าย>/                 skills/ และ trials/ ของ Trial ชุดนั้น
```

- `runs/<ws>/skills/` อยู่ตำแหน่งเดียวกับสกิลของ 1 รุ่นใน skill-optimizer จึงวัดชุดสกิลของ workspace ได้ด้วย `skillopt.py run <work> --label <ws>` โดยตรง (ผลไปอยู่ที่ `runs/<ws>/trials/`)
- `NN` = เลขรอบ 2 หลัก (`01` `02` …)

## 3 · คำสั่ง 8 ตัว

รูปแบบ: `python3 scripts/wikiskill.py <คำสั่ง> <work> --ws <ชื่อ workspace>` · ทุกคำสั่งพิมพ์ผลทาง stdout

| คำสั่ง | Algorithm 1 | ทำอะไร | เรียกโมเดล |
|---|---|---|---|
| `init` | บรรทัด 2 | สร้าง workspace: ชุดสกิลว่าง wiki ว่าง · ถ้ามี `state.json` อยู่แล้ว ไม่ทำอะไร แล้ว exit 1 | ไม่ |
| `baseline` | บรรทัด 3 | วัด Validation ด้วยชุดสกิลว่าง → `R_best` | **เรียก** (Trial) |
| `rollout` | บรรทัด 8 | Inference Agent ทำโจทย์ Training ด้วยชุดสกิลปัจจุบัน → `raw/iter-NN/` | **เรียก** (Trial) |
| `maintain` | บรรทัด 9–10 | Wiki Maintainer สรุป Trace ที่สุ่มมาลง `wiki/` | **เรียก** 1 ครั้ง |
| `propose` | บรรทัด 11–12 | Skill Proposer อ่าน wiki และ Trace แล้วเสนอแก้สกิล 1 ตัว → `history/iter-NN/candidate/` | **เรียก** 1 เซสชัน |
| `gate` | บรรทัด 13–19 | วัด Validation ของชุดสกิลที่เสนอ → รับ หรือ ย้อนกลับ · จดผลลง `wiki/skill-impact.md` | **เรียก** (Trial) |
| `loop` | บรรทัด 3–20 | ทำต่อจากขั้นที่ค้างจนวงรอบหยุด แล้วพิมพ์ `status` · มี `--iters N` ใช้แทนค่าของ `init` ได้ (บันทึกลง `cfg.iters`) | **เรียก** |
| `status` | – | ตารางสรุปทุกรอบ อ่านจาก `state.json` และชื่อโฟลเดอร์ใน `skills/` เท่านั้น | ไม่ |

| ตัวเลือกของ `init` | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `--accounts yolo1,yolo2` | (ต้องระบุ) | คำสั่งของบัญชีที่ใช้ |
| `--iters` | `8` | จำนวนรอบสูงสุด (K) |
| `--reps` | `3` | จำนวนรอบต่อโจทย์ของทุกการวัด |
| `--par` | `6` | จำนวน Trial ที่รันพร้อมกัน |
| `--model` `--effort` | `sonnet` `medium` | โมเดลของ Inference Agent |
| `--opt-model` `--opt-effort` | `sonnet` `high` | โมเดลของ Wiki Maintainer และ Skill Proposer |
| `--task-desc "…"` | `เขียนโค้ด Python ตามโจทย์ (ตัวตรวจอัตโนมัติให้คะแนนผลงาน)` | คำอธิบายงาน ใส่แทน `{task_desc}` ใน prompt |
| `--no-wiki` | ปิด | การทดลองตัดส่วนประกอบ (ข้อ 10) |
| `--skillopt <path>` | `../skill-optimizer/scripts/skillopt.py` นับจากโฟลเดอร์ของสกิลนี้ | ที่อยู่ของ `skillopt.py` |

`init` สร้าง: `raw/` `skills/` `history/` `rollouts/suite/` (คัดลอก `suite.json` และไฟล์ตัวตรวจที่ระบุในฟิลด์ `grader` จาก `<work>/suite/`) `rollouts/runs/` และ wiki ตั้งต้น 3 ไฟล์

| ไฟล์ | เนื้อหาตั้งต้น |
|---|---|
| `wiki/index.md` | `# Wiki Index` บรรทัดว่าง `ยังไม่มี pattern` |
| `wiki/log.md` | `# Evolution Log` |
| `wiki/skill-impact.md` | `# Skill Impact` บรรทัดว่าง `บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ` |

## 4 · `state.json` และลำดับของขั้น

`phase` บอกขั้นล่าสุดที่ทำเสร็จ · คำสั่งที่ถูกเรียกผิดลำดับต้องบอกว่าขั้นถัดไปคืออะไร แล้ว exit 1 โดยไม่เรียกโมเดล

| `phase` ตอนนี้ | คำสั่งถัดไป | `phase` หลังทำเสร็จ |
|---|---|---|
| `init` | `baseline` | `gate` |
| `gate` | `rollout` (เพิ่ม `k` ขึ้น 1) | `rollout` |
| `rollout` | `maintain` | `maintain` |
| `maintain` | `propose` | `propose` |
| `propose` | `gate` | `gate` |

- `baseline` ที่ทำไปแล้ว และ `rollout` เมื่อ `R_best` = 100% ไม่ทำอะไร แล้ว exit 0
- `loop` หยุดเมื่อ `phase` = `gate` และ (`R_best` = 100% หรือ `k` ≥ จำนวนรอบสูงสุด)

```json
{"cfg": {"name": "w1", "skillopt": "/…/skillopt.py", "accounts": ["yolo1"], "iters": 8, "reps": 3, "par": 6,
         "model": "sonnet", "effort": "medium", "opt_model": "sonnet", "opt_effort": "high",
         "task_desc": "…", "use_wiki": true},
 "k": 1, "phase": "gate", "r_best": 1.0,
 "baseline": {"trials": 6, "cost_usd": 0.5, "context_tokens": 83000, "tool_calls": 2.2, "skill_read": 0, "val_score": 0.433},
 "history": [{"k": 1, "skills_in": [], "train_score": 0.442, "train_perfect": 0, "train_n": 12,
              "train_checks": {"contract": "12/12", "cli_ok": "0/12"},
              "train": {"trials": 12, "cost_usd": 1.0, "context_tokens": 83000, "tool_calls": 2.2, "skill_read": 0},
              "sampled": {"fail": ["t4-cashback-r1"], "pass": []},
              "patterns_created": ["a.md"], "patterns_updated": [], "edits_skipped": [], "patterns_total": 5,
              "maintainer": {"calls": 1, "tool_calls": 0, "cost_usd": 0.1, "wall_s": 76.0, "output_tokens": 4000, "context_tokens": 30000},
              "proposal": {"action": "create", "name": "x", "rationale": "…"},
              "proposer": {"attempts": 1, "reads": ["wiki/patterns/a.md", "traces/t4-cashback-r1.md"], "traces_read": 4,
                           "patterns_read": 3, "calls": 8, "cost_usd": 0.2, "wall_s": 60.0, "context_tokens": 200000},
              "val_score": 1.0, "r_best_before": 0.433, "accepted": true, "outcome": "ACCEPTED", "r_best_after": 1.0,
              "skills_out": ["x"], "val": {"trials": 6, "cost_usd": 0.5, "context_tokens": 120000, "tool_calls": 3.0, "skill_read": 6}}]}
```

| ฟิลด์ | ความหมาย |
|---|---|
| `train_score` `val_score` `r_best` | ค่าเฉลี่ยของคะแนนทุก Trial (0–1) |
| `train_perfect` | จำนวน Trial ที่คะแนน ≥ 0.999 |
| `train_checks` | ข้อตรวจ → `ผ่าน/ทั้งหมด` ของ Training ในรอบนั้น |
| `trials` `cost_usd` `context_tokens` `tool_calls` `skill_read` | จำนวน Trial · ค่าใช้จ่ายรวม · โทเคนขาเข้าเฉลี่ยต่อ Trial · คำสั่งเฉลี่ยต่อ Trial · จำนวน Trial ที่เปิดอ่านสกิล |
| `maintainer.calls` `proposer.calls` | `num_turns` ของการเรียกโมเดล (ของ Proposer รวมทุกครั้งที่ลองใหม่) |
| `outcome` | `ACCEPTED` · `REJECTED` · `NO_ACTION` |
| `r_best` | `null` จนกว่าจะทำ `baseline` |
| `cfg.skillopt` | path เต็มของ `skillopt.py` |
| เมื่อมีการเรียกใหม่ | `maintainer`: `calls` และโทเคนเป็นของครั้งสุดท้าย · `cost_usd` และ `wall_s` รวมทุกครั้ง · `proposer`: รวมทุกครั้ง ส่วน `reads` เป็นของครั้งสุดท้าย |

**โทเคนขาเข้า (`context_tokens`)** = `input_tokens` + `cache_read` + `cache_write`

## 5 · การรัน Trial (Inference Agent)

WikiSkill ไม่รัน Trial เอง ใช้คำสั่ง `run` ของ skill-optimizer กับโฟลเดอร์งาน `runs/<ws>/rollouts/` Agent จึงได้โจทย์ ตัวตรวจ และพรอมต์ชุดเดียวกับบท 05

| เมื่อไร | ป้าย | ชุด | ชุดสกิลที่ใช้ |
|---|---|---|---|
| `baseline` | `k00-val` | `val` | ว่าง |
| `rollout` รอบ k | `kNN-train` | `train` | `runs/<ws>/skills/` |
| `gate` รอบ k | `kNN-val` | `val` | `history/iter-NN/candidate/skills/` |

| ลำดับ | ทำอะไร |
|---|---|
| 1 | ลบ `rollouts/runs/<ป้าย>/` เดิม แล้วสร้างใหม่ |
| 2 | ถ้าชุดสกิลมีสกิลอย่างน้อย 1 ตัว (โฟลเดอร์ที่มี `SKILL.md`) คัดลอกไปเป็น `rollouts/runs/<ป้าย>/skills/` · ไม่มีสกิล = ไม่สร้างโฟลเดอร์ `skills` |
| 3 | รัน `<python> <skillopt.py> run <rollouts> --label <ป้าย> --split <ชุด> --reps <reps> --accounts <บัญชี คั่นด้วย ,> --par <par> --model <model> --effort <effort>` ด้วย Python ตัวเดียวกับที่รันเครื่องมือ |
| 4 | อ่าน `grade.json` และ `metrics.json` ของทุก Trial ใต้ `rollouts/runs/<ป้าย>/trials/` · คำสั่ง `run` ล้ม หรือไม่มีผล ให้หยุดพร้อมบอกสาเหตุ |

Inference Agent เห็นเฉพาะ `./skills` ใน sandbox ของตัวเอง ไม่เห็น `wiki/` และ `raw/`

## 6 · Raw Layer (`rollout` เขียน)

**Trace** `raw/iter-NN/traces/<id โจทย์>-r<รอบ>.md` สร้างจาก `transcript.jsonl` `grade.json` `metrics.json` `task.json` ของ Trial · `trace_id` = `<id โจทย์>-r<รอบ>`

```text
# Trace <trace_id> · iteration <k>

- ผล: **PASS|FAIL** · คะแนน 0.70 (ผ่าน 7 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่|ไม่

## โจทย์                        ข้อความโจทย์ (ฟิลด์ brief ของ task.json)
## ผลของตัวตรวจ (Grader)        1 บรรทัดต่อข้อตรวจ: - ✓ `id` หรือ - ✗ `id`: ข้อความของตัวตรวจ
## สิ่งที่ Agent ทำ              ตามลำดับเวลา: ข้อความที่ Agent พูด · ### ขั้น n · <ชื่อเครื่องมือ> · คำสั่งหรือไฟล์ที่เขียน · ผลที่ได้
## คำตอบสุดท้ายของ Agent
```

- PASS = คะแนน ≥ 0.999
- 1 Trace ยาวไม่เกิน 15,000 ตัวอักษร: ตัดคำสั่งและผลของแต่ละขั้นให้สั้นลงก่อน แล้วจึงตัดท้าย

**`summary.md`**: บรรทัดคะแนนเฉลี่ยและจำนวน Trace ที่ผ่านครบ · ตาราง `trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน` · รายการ `- <trace_id> · `<ข้อตรวจ>`: <ข้อความของตัวตรวจ>` ของทุกข้อที่ไม่ผ่าน (ไม่มีข้อที่ไม่ผ่าน พิมพ์ `- (ไม่มี)`)

## 7 · Wiki Maintainer (`maintain`)

| ลำดับ | ทำอะไร |
|---|---|
| 1 | สุ่ม Trace ของรอบนี้แบบแบ่งชั้น: ที่ไม่ผ่านไม่เกิน **5** + ที่ผ่านไม่เกิน **3** (วิธีสุ่มอยู่ใต้ตาราง) |
| 2 | ประกอบข้อความ: เลขรอบและคะแนน Training · `SKILL.md` ของสกิลที่ใช้งาน · wiki ปัจจุบันทุกไฟล์ · Trace ที่สุ่มมา (แต่ละไฟล์ครอบด้วย `<trace id="…">`) → บันทึกที่ `history/iter-NN/maintainer_input.md` (ตัวอย่างจริง: [`runs/w1/history/iter-01/maintainer_input.md`](runs/w1/history/iter-01/maintainer_input.md)) |
| 3 | เรียกโมเดล 1 ครั้ง ไม่มีเครื่องมือ (ข้อ 11) |
| 4 | คำตอบต้องเป็น JSON object ตามตารางล่าง · ใช้ไม่ได้ให้เรียกใหม่พร้อมบอกสาเหตุ ไม่เกิน 3 ครั้ง · ครบ 3 ครั้งแล้วยังใช้ไม่ได้ exit 1 |
| 5 | บันทึกคำตอบที่ `history/iter-NN/maintainer_output.json` แล้วโปรแกรมเป็นผู้เขียนไฟล์ wiki |

**วิธีสุ่ม** (รันซ้ำแล้วได้ชุดเดิม): ใช้ `random.Random(k)` โดย k = เลขรอบ · กลุ่มที่ไม่ผ่านเรียงตาม (คะแนน, ค่าสุ่ม) · กลุ่มที่ผ่านเรียงตามค่าสุ่ม · ในแต่ละกลุ่มหยิบวนทีละโจทย์ โจทย์ละ 1 Trace ต่อรอบวน (เริ่มจากโจทย์ที่ Trace แรกคะแนนต่ำสุด) จนครบจำนวน

| ฟิลด์ของคำตอบ | โปรแกรมทำอะไร |
|---|---|
| `create_patterns`: `[{"name": "x.md", "content": "…"}]` | สร้าง `wiki/patterns/x.md` · ถ้ามีไฟล์ชื่อนี้อยู่แล้ว ต่อท้ายไฟล์เดิมโดยเว้น 1 บรรทัด (นับเป็นหน้าที่ถูกแก้) |
| `update_patterns`: `[{"name": "x.md", "edits": […]}]` | แก้หน้าเดิมด้วยรายการแก้ (ตารางถัดไป) · ไม่มีไฟล์ หรือรายการแก้ใดใช้ไม่ได้ = ข้ามเฉพาะรายการนั้น และจดสาเหตุใน `edits_skipped` |
| `update_index`: ข้อความ (ต้องมี) | เขียนทับ `wiki/index.md` ทั้งไฟล์ |
| `append_log`: ข้อความ (ต้องมี) | ต่อท้าย `wiki/log.md` ใต้หัวข้อ `## Iteration <k> · Training <คะแนน>` ที่โปรแกรมเขียน · ถ้าข้อความขึ้นต้นด้วยหัวข้อ Iteration ของตัวเอง ให้ตัดบรรทัดนั้นออก |

| รายการแก้ (`edits`) | ผล |
|---|---|
| `{"op": "append", "content": "…"}` | ต่อท้ายไฟล์ ขึ้นบรรทัดใหม่ 1 ครั้ง (ไม่เว้นบรรทัด) |
| `{"op": "replace", "target": "…", "content": "…"}` | แทนข้อความ `target` ที่พบครั้งแรก |
| `{"op": "insert_after", "target": "…", "content": "…"}` | แทรกเป็นบรรทัดใหม่ ต่อจากท้ายบรรทัดที่ `target` (ที่พบครั้งแรก) จบ |

- `target` ต้องตรงกับข้อความเดิมทุกตัวอักษร · ไม่พบ = รายการนั้นใช้ไม่ได้
- ชื่อไฟล์ pattern: ตัวอักษรอังกฤษ ตัวเลข `.` `_` `-` เท่านั้น ลงท้าย `.md` · ชื่อผิดรูปแบบ (เช่น มีตัวอักษรไทย) = คำตอบใช้ไม่ได้ ให้เรียกใหม่ตามลำดับ 4 และ prompt ต้องบอกกติกานี้
- prompt ของ Maintainer ต้องกำหนดให้หน้า pattern มี อาการ · สาเหตุ · หลักฐาน (trace id) · วิธีแก้ และให้บรรทัดใน index บอกปัญหา สาเหตุ และวิธีแก้พอที่ผู้อ่านตัดสินได้ว่าจะเปิดหน้านั้นหรือไม่

## 8 · Skill Proposer (`propose`)

| ลำดับ | ทำอะไร |
|---|---|
| 1 | สร้างโฟลเดอร์ที่ Proposer มองเห็น `history/iter-NN/proposer_view/`: สำเนาของ `wiki/` · `traces/` (ทุก Trace ของรอบนี้) · `skills/` (ชุดสกิลที่ใช้งาน) · `summary.md` |
| 2 | ประกอบข้อความ: เลขรอบ · `R_best` · เนื้อหาของ `wiki/index.md` และ `wiki/skill-impact.md` · `summary.md` · รายชื่อสกิลที่ใช้งาน → บันทึกที่ `history/iter-NN/proposer_input.md` (ตัวอย่างจริง: [`runs/w1/history/iter-01/proposer_input.md`](runs/w1/history/iter-01/proposer_input.md)) |
| 3 | เรียกโมเดล 1 เซสชัน มีเครื่องมือ `Read` อย่างเดียว โฟลเดอร์ทำงานคือ `proposer_view/` (ข้อ 11) · Proposer เปิดไฟล์เองเท่าที่ต้องการ (ReAct) แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย |
| 4 | ตรวจข้อเสนอ: ถ้าไม่ใช่ `no_action` ต้องเปิด Trace แล้วอย่างน้อย **4** ไฟล์ในเซสชันนั้น (นับไฟล์ที่ไม่ซ้ำใต้ `traces/` · รอบที่มี Trace น้อยกว่า 4 ใช้จำนวนที่มี) และต้องนำไปสร้างชุดสกิลที่เสนอได้ (ลำดับ 5) · ใช้ไม่ได้ให้เรียกใหม่พร้อมบอกสาเหตุ ไม่เกิน 3 ครั้ง · ครบแล้วยังใช้ไม่ได้ ถือเป็น `no_action` ที่ `rationale` บอกสาเหตุล่าสุด |
| 5 | Apply (บรรทัด 12): คัดลอก `skills/` ไปเป็น `history/iter-NN/candidate/skills/` แล้วทำตามข้อเสนอ · **ยังไม่แตะ `skills/` ที่ใช้งาน** |
| 6 | บันทึก `history/iter-NN/proposal.json` (ข้อเสนอ) และ `proposal.diff` (unified diff ของ `SKILL.md` ก่อนและหลัง หัวไฟล์ `a/skills/<ชื่อ>/SKILL.md` `b/skills/<ชื่อ>/SKILL.md` · `no_action` = ไฟล์ว่าง) |

| ข้อเสนอ | ฟิลด์ | Apply ทำอะไร |
|---|---|---|
| `{"action": "create", …}` | `name` · `skill_md` (ทั้งไฟล์ ต้องขึ้นต้นด้วย YAML frontmatter `---`) · `purpose_md` · `rationale` | เขียน `candidate/skills/<name>/SKILL.md` และ `PURPOSE.md` (แทนของเดิมถ้าชื่อซ้ำ) |
| `{"action": "patch", …}` | `name` (สกิลที่มีอยู่) · `edits` (รายการแก้แบบเดียวกับข้อ 7) · `purpose_append` · `rationale` | แก้ `SKILL.md` ตามรายการแก้ · ต่อท้าย `PURPOSE.md` โดยเว้น 1 บรรทัด · รายการแก้ใช้ไม่ได้แม้รายการเดียว หรือ `SKILL.md` ไม่เปลี่ยน = ข้อเสนอใช้ไม่ได้ |
| `{"action": "no_action", …}` | `rationale` | ไม่เปลี่ยนอะไร |

ข้อเสนอ 1 ครั้งเปลี่ยนสกิลได้ตัวเดียว · ชื่อสกิลใช้ตัวอักษรอังกฤษ ตัวเลข `.` `_` `-` เท่านั้น

## 9 · Gating and Rollback (`gate`)

| ลำดับ | ทำอะไร |
|---|---|
| 1 | `no_action` → ไม่วัด · ผล `NO_ACTION` |
| 2 | นอกนั้น วัด Validation ของ `candidate/skills/` (ป้าย `kNN-val`) |
| 3 | **รับเมื่อคะแนน Validation > `R_best` เท่านั้น** (เท่ากัน = ไม่รับ) → `ACCEPTED`: แทน `skills/` ด้วยชุดที่เสนอ และตั้ง `R_best` ใหม่ · ไม่เช่นนั้น `REJECTED`: `skills/` คงเดิม |
| 4 | **ทุกผลตัดสิน** ต่อท้าย `wiki/skill-impact.md` (รูปแบบด้านล่าง) · wiki ไม่ถูกย้อนกลับ |
| 5 | เก็บสำเนา `wiki/` และ `skills/` หลังตัดสินไว้ที่ `history/iter-NN/wiki/` และ `history/iter-NN/skills/` · เขียน `history/iter-NN/gate.json`: `k` `val_score` `r_best_before` `outcome` `val_trials` (`trace_id` และ `score` ของแต่ละ Trial) |

```text
## Iteration <k> · <action> `<ชื่อสกิล หรือ ->` · <ACCEPTED|REJECTED|NO_ACTION>

- Validation ของสกิลที่เสนอ: <คะแนน หรือ (ไม่ได้วัด)> · R_best ก่อนหน้า: <คะแนน> -> <รับ (R_best ใหม่ <คะแนน>) | ไม่รับ ย้อนกลับไปใช้ชุดสกิลเดิม | ไม่มีข้อเสนอ ใช้ชุดสกิลเดิม>
- เหตุผลของข้อเสนอ: <rationale>

Diff ของ SKILL.md ที่เสนอ:

(บล็อก ```diff ที่มีเนื้อหาของ proposal.diff · เมื่อเป็น no_action ไม่มีทั้งบรรทัดหัวและบล็อกนี้)
```

## 10 · `--no-wiki` (การทดลองตัดส่วนประกอบ)

| ส่วน | เมื่อใช้ `--no-wiki` |
|---|---|
| `init` | ไม่สร้างโฟลเดอร์ `wiki/` |
| `maintain` | ไม่เรียกโมเดล เปลี่ยน `phase` อย่างเดียว |
| `propose` | `proposer_view/` ไม่มี `wiki/` · ข้อความไม่มี index และ skill-impact · ใช้ `prompts/proposer_nowiki.md` |
| `gate` | ไม่เขียน `wiki/skill-impact.md` และไม่มี `history/iter-NN/wiki/` |

## 11 · การเรียกโมเดลของ Wiki Maintainer และ Skill Proposer

ใช้บัญชีตัวแรกของ `--accounts` · ข้อความของผู้ใช้ส่งทาง stdin · stdout เก็บเป็น `history/iter-NN/maintainer_transcript_<ครั้งที่>.jsonl` หรือ `proposer_transcript_<ครั้งที่>.jsonl`

```text
claude --dangerously-skip-permissions --disable-slash-commands -p --system-prompt <prompt> --model <opt-model> --effort <opt-effort>
       --output-format stream-json --verbose --no-session-persistence --strict-mcp-config --tools <"" หรือ Read>
```

| เงื่อนไข | ค่า |
|---|---|
| ตัวแปรสภาพแวดล้อม | ลบตัวที่ขึ้นต้นด้วย `CLAUDE` และ `MA_` · ตั้ง `IS_SANDBOX=1` ทุกครั้ง · ตั้ง `CLAUDE_CONFIG_DIR=<โฟลเดอร์ของบัญชี>` เมื่อมีโฟลเดอร์นั้น |
| โฟลเดอร์ของบัญชี | `<root>/<ชื่อบัญชี>` โดย `<root>` = ตัวแปร `WIKISKILL_ACCOUNT_ROOT` (ไม่ตั้ง = `~/ai-accounts/.Claude`) |
| ไม่มีโฟลเดอร์ของบัญชี | เรียกคำสั่งของบัญชีแทน `claude …` (เช่น `yolo1 -p --system-prompt …`) ด้วยตัวเลือกชุดเดียวกันตั้งแต่ `-p` · คำสั่งของบัญชีที่เป็นไฟล์ `.py` ให้รันด้วย Python ตัวเดียวกับเครื่องมือ (ใช้ทดสอบด้วย Agent จำลอง) |
| `--tools` | Maintainer: `""` (ไม่มีเครื่องมือ) · Proposer: `Read` |
| หมดเวลา | 1,800 วินาทีต่อการเรียก 1 ครั้ง |

เหตุผลที่เรียก `claude` ตรง ๆ: คำสั่งของบัญชี (`yolo1` …) แนบ MCP มาด้วยทุกครั้ง เมื่อใช้ร่วมกับ `--tools` เครื่องมือ MCP ทั้งหมดจะถูกโหลดเข้าบริบท ราว 108,000 โทเคนต่อการเรียก

ค่าที่อ่านจากบรรทัด `result` ของ Trace: `result` (คำตอบ) · `num_turns` · `total_cost_usd` · `usage` (`input_tokens` `cache_read_input_tokens` `cache_creation_input_tokens` `output_tokens`) · ไฟล์ที่ Proposer เปิด อ่านจาก `tool_use` ที่ชื่อ `Read` (ตัดส่วนของ path จนถึง `proposer_view/` ออก)

## 12 · ข้อความของ `status`

ตัวอย่างจริง: [`runs/w1/status.txt`](runs/w1/status.txt) · ต้องพิมพ์ตรงกันทุกตัวอักษรเมื่ออ่าน `state.json` เดียวกัน

```text
(บรรทัดว่าง)
workspace <name> · โมเดลที่ทำโจทย์ <model>/<effort> · โมเดลของ Maintainer และ Proposer <opt_model>/<opt_effort> · wiki: <ใช้|ไม่ใช้>
Baseline Validation (ชุดสกิลว่าง): <%> · R_best ตอนนี้: <%> · สกิลที่ใช้งาน: <ชื่อโฟลเดอร์ใน skills/ ที่มี SKILL.md คั่นด้วย ", " หรือ (ไม่มี)>
(บรรทัดว่าง)
| รอบ | Training (สกิลก่อนแก้) | pattern ใหม่ | pattern ที่แก้ | pattern รวม | Proposer อ่าน (pattern/Trace) | ข้อเสนอ | Validation | R_best ก่อน | ผล |
|---|---|---|---|---|---|---|---|---|---|
| <k> | <%> (<ผ่านครบ>/<จำนวน Trial>) | <n> | <n> | <n> | <n>/<n> | <action> `<ชื่อ หรือ ->` | <%> | <%> | <outcome> |
(บรรทัดว่าง)
รวม: Trial ของ Inference Agent <n> ครั้ง ($<0.00>) · การเรียกโมเดลของ Maintainer + Proposer <n> ครั้ง ($<0.00>)
สถานะ: <ข้อความ>
```

- `<%>` = ร้อยละ ทศนิยม 1 ตำแหน่ง เช่น `43.3%` · ค่าที่ยังไม่มี (เช่น รอบที่ยังไม่ถึงขั้นนั้น หรือ `--no-wiki`) พิมพ์ `-` · ผลที่ยังไม่ตัดสินพิมพ์ `(ยังไม่ตัดสิน)`
- Trial ที่นับ = baseline + Training และ Validation ของทุกรอบ · จำนวนการเรียกโมเดล = 1 ต่อรอบที่ Maintainer ทำงาน + `proposer.calls` ของทุกรอบ
- `สถานะ:` มี 3 แบบ: `หยุดแล้ว เพราะ R_best = 100% ที่รอบ <k> (หยุดก่อนครบ <iters> รอบ)` (เมื่อ k < iters) · `หยุดแล้ว เพราะครบ <iters> รอบ` · `ยังไม่จบ (รอบ <k> · ขั้นล่าสุด <phase>)`
- `--no-wiki`: คอลัมน์ pattern ทั้ง 3 พิมพ์ `-` และคอลัมน์ Proposer อ่าน พิมพ์ `-/<จำนวน Trace>`
- ยังไม่ได้วัด baseline: พิมพ์บรรทัด workspace แล้ว `ยังไม่ได้วัด baseline`
