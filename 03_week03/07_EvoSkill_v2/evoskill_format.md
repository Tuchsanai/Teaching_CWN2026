# รูปแบบของ `evoskill` · โฟลเดอร์งาน คำสั่ง ไฟล์ของ 1 การรัน และกติกาของวงรอบ

ไฟล์นี้กำหนด **รูปแบบ** ที่เครื่องมือ `scripts/evoskill.py` ต้องทำตาม เพื่อให้ใช้กับ LAB 1–7 และสคริปต์วาดภาพใน `tools/` ของบทนี้ได้ · ไม่มีโค้ดและไม่มี prompt ของเครื่องมืออยู่ในไฟล์นี้

ใช้คู่กับ [LAB 0 ขั้น 0.1](README.md#ขั้น-01--สร้างโฟลเดอร์-evoskill) · ที่มาคือเปเปอร์ EvoSkill v2 (arXiv:2610.25931) Section 3 และ Table 1

## 1 · โฟลเดอร์ของสกิล

```text
my-evoskill/
├── SKILL.md                    คู่มือที่ AI อ่าน: ใช้เมื่อไร · ตารางคำสั่ง · ขั้นตอน · ข้อห้าม
├── scripts/
│   ├── evoskill.py             โปรแกรมควบคุมการรัน (ไฟล์เดียว · Python 3.8 ขึ้นไป · ไลบรารีมาตรฐานเท่านั้น)
│   ├── plugin_api.py           รูปแบบของ 1 โจทย์ (class Task) ที่ plug-in ต้องคืน
│   └── plugin_skeleton.py      โครงเปล่าของ plug-in ให้ Benchmark Adaptor เติม
├── prompts/
│   ├── adaptor.md              ข้อความต่อท้าย system prompt ของ Benchmark Adaptor
│   ├── evolver_system.md       ข้อความต่อท้าย system prompt ของ Evolver
│   └── evolver_message.md      ข้อความประจำ epoch ที่ส่งให้ Evolver
└── references/
    ├── source.md               ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง
    └── workspace.md            โครงของ 1 การรัน และไฟล์ที่แต่ละคำสั่งอ่านและเขียน
```

- prompt ทั้ง 3 ไฟล์เขียนเป็นภาษาไทยด้วยถ้อยคำของตัวเอง · โปรแกรมหา prompt จากโฟลเดอร์ `prompts/` ที่อยู่ข้าง `scripts/`
- `plugin_api.py`: `class Task` (dataclass) มีฟิลด์ `id` · `split` (`"train"` `"validation"` `"test"`) · `instruction` (ข้อความโจทย์ที่ Solver ได้รับ) · `inputs` (list) · `answer_files` (list) · `grading` (dict ที่ตัวตรวจอ่าน) · `category` และเมธอด `to_dict()`

## 2 · โฟลเดอร์งาน (`<work>`) และการรัน

`<work>` = โฟลเดอร์ที่มี `bench/` และ `runs/` · ตัวอย่างจริง: โฟลเดอร์ของบทนี้ · **1 การรัน EvoSkill v2 = 1 โฟลเดอร์ `runs/<ชื่อ>/`**

```text
<work>/
├── bench/                              สิ่งที่ผู้ใช้ส่ง (ของที่ป้อนเข้า)
│   ├── instruction.md                  คำสั่งของผู้ใช้ 1 หน้า (มีได้หลายไฟล์ เลือกด้วย --instruction)
│   ├── data/<data root>/               ข้อมูลของ benchmark (โฟลเดอร์เดียวใต้ data/)
│   ├── split.json                      {"train": [...], "validation": [...], "test": [...]}
│   ├── benchmark_grader.py             ตัวตรวจของผู้ใช้ (ข้อ 6)
│   └── solver_prompt.txt               พรอมต์ของ Solver · {brief} ถูกแทนด้วยข้อความโจทย์
└── runs/<ชื่อ>/
    ├── RUN.json state.json             สิ่งที่ผู้ใช้ส่งมา (hash) · สถานะของการรัน (ข้อ 4)
    ├── inputs/                         สำเนาของ instruction.md split.json benchmark_grader.py ตอน init
    ├── adapt/                          โต๊ะทำงานของ Benchmark Adaptor: setup/ reference/ work/ data/
    ├── setup/                          ผลของ adapt ที่ถูกล็อก: benchmark_plugin.py plugin_api.py benchmark_grader.py tasks.json freeze.json audit.md
    ├── reference/                      สิ่งที่ Evolver อ่านได้เกี่ยวกับ benchmark
    ├── skills_v1/ … skills_vE/         ชุดสกิลหลังตาที่ K ของ Evolver (เก็บทุกชุด)
    ├── evo/                            "เครื่องของ Evolver" (ข้อ 8)
    ├── turns/adaptor/ · turns/turn_K/  สิ่งที่ Agent ได้รับและทำในแต่ละครั้ง (ข้อ 10)
    └── legs/                           โฟลเดอร์งานของ skill-optimizer ที่ใช้รัน rollout (ข้อ 6)
        ├── <leg>.json                  สรุปของ 1 leg
        ├── suite/                      suite.json และสำเนาตัวตรวจ
        └── runs/<leg>/                 skills/ และ trials/<id โจทย์>-r<ครั้ง>/ ของ leg นั้น
```

คำศัพท์: **rollout** = Solver ทำโจทย์ 1 ข้อ 1 ครั้ง · **epoch** = 1 รอบของวงรอบ (epoch 0 ไม่มีสกิล · epoch K ใช้ `skills_vK`) · **ตา (turn)** = Evolver ทำงาน 1 ครั้ง · **leg** = Solver ทำโจทย์ 1 ชุดด้วยชุดสกิล 1 ชุด

## 3 · คำสั่ง 12 ตัว

รูปแบบ: `python3 scripts/evoskill.py <คำสั่ง> <work> --run <ชื่อ>` · ทุกคำสั่งพิมพ์ผลทาง stdout · ข้อความผิดพลาดพิมพ์ทาง stderr แล้ว exit 1

| คำสั่ง | ทำอะไร | เรียกโมเดล |
|---|---|---|
| `init` | สร้างการรัน: คัดลอกสิ่งที่ผู้ใช้ส่งลง `inputs/` เขียน `RUN.json` และ `state.json` · ถ้ามี `state.json` อยู่แล้ว ไม่ทำอะไร แล้ว exit 1 | ไม่ |
| `adapt` | Benchmark Adaptor 1 เซสชัน → plug-in และ `reference/` แล้วโปรแกรมล็อกด้วย hash และตรวจการรั่ว (ข้อ 5) | **เรียก** 1 เซสชัน |
| `audit` | ตรวจ `reference/` ซ้ำ (ข้อ 5) · สะอาด exit 0 · พบการรั่ว exit 1 | ไม่ |
| `base` | epoch 0: Solver ทำโจทย์ทุกชุดโดยไม่มีสกิล → leg `base_train` `base_val` `base_test` | **เรียก** (rollout) |
| `turn` | ตาของ Evolver 1 ครั้ง → `skills_vK` (ข้อ 9) | **เรียก** 1 ตา |
| `rollout` | Solver ทำโจทย์ด้วย `skills_vK` → leg `vK_val` และ `vK_train` (epoch สุดท้ายไม่มี `vK_train`) | **เรียก** (rollout) |
| `test` | วัดชุดสกิลของ epoch สุดท้ายกับ Test Set 1 ครั้ง → leg `vE_test` | **เรียก** (rollout) |
| `run` | ทำทุกขั้นที่เหลือจนจบ (ทำต่อจากขั้นที่ค้าง) แล้วพิมพ์ `status` · `--stop-after adapt\|base\|turn\|rollout` หยุดหลังขั้นนั้น 1 ครั้ง | **เรียก** |
| `status` | ตารางสรุปของการรัน อ่านจาก `state.json` เท่านั้น (ข้อ 11) | ไม่ |
| `noise` | ความแกว่งของ rollout และผลของประตูรับแบบวัดครั้งเดียว อ่านจาก `state.json` เท่านั้น (ข้อ 12) | ไม่ |
| `eval` | วัดชุดสกิลใดก็ได้: `--label <ป้าย> --skills <v1\|v2\|… \| none \| โฟลเดอร์ skills> --split <train\|val\|test\|all> [--model M]` → leg ชื่อ `<ป้าย>` | **เรียก** (rollout) |
| `export` | เขียนสำเนาของการรันที่ตัดรายละเอียดแล้วไปที่ `--to <โฟลเดอร์>/<ชื่อ>/` (ข้อ 13) | ไม่ |

| ตัวเลือกของ `init` | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `--accounts yolo1,yolo2` | (ต้องระบุ) | คำสั่งของบัญชีที่ใช้ |
| `--instruction <ไฟล์>` | `<work>/bench/instruction.md` | คำสั่งของผู้ใช้ที่ส่งให้ Benchmark Adaptor |
| `--solver-model` `--solver-effort` | `sonnet` `medium` | โมเดลของ Solver |
| `--evolver-model` `--evolver-effort` | `sonnet` `high` | โมเดลของ Evolver |
| `--adaptor-model` | `sonnet` (effort `high` เสมอ) | โมเดลของ Benchmark Adaptor |
| `--par` | `6` | จำนวน rollout ที่รันพร้อมกัน |
| `--turn-minutes` | `30` | เวลาสูงสุดของ 1 ตาของ Evolver |
| `--fresh-session` | ปิด | การทดลองตัดส่วนประกอบ: Evolver เริ่มเซสชันใหม่ทุก epoch |
| `--skillopt <path>` | `../skill-optimizer/scripts/skillopt.py` นับจากโฟลเดอร์ของสกิลนี้ (ไม่พบให้ลอง `../my-skill-optimizer/…`) | ที่อยู่ของ `skillopt.py` ของบท 05 |

**ขนาดของการรัน** ไม่ใช่ตัวเลือก: `init` อ่านจากคำสั่งของผู้ใช้ ซึ่งต้องมีข้อความรูปแบบ `<E> epochs · <N> samples per task` (ตัวคั่นเป็น `·` `x` หรือ `,`) · ไม่พบ = บอกสาเหตุ แล้ว exit 1

`RUN.json`: `instruction` `split` `grader` (แต่ละตัวมี `file` และ `sha256`) · `data` (`dir` และจำนวนไฟล์ `files`) · `run_size` (`epochs` `samples_per_task`)

## 4 · `state.json` และลำดับของขั้น

`phase` บอกขั้นล่าสุดที่ทำเสร็จ · คำสั่งที่ถูกเรียกผิดลำดับต้องบอกว่าขั้นถัดไปคืออะไร แล้ว exit 1 โดยไม่เรียกโมเดล

| `phase` ตอนนี้ | คำสั่งถัดไป | `phase` หลังทำเสร็จ |
|---|---|---|
| `init` | `adapt` | `adapt` |
| `adapt` | `base` | `base` |
| `base` | `turn` (ตั้ง `k` = 1) | `turn` |
| `turn` | `rollout` | `rollout` |
| `rollout` และ `k` < จำนวน epoch | `turn` (เพิ่ม `k` ขึ้น 1) | `turn` |
| `rollout` และ `k` = จำนวน epoch | `test` | `test` |
| `test` | (จบ) | – |

ตัวอย่างจริง: [`runs/e1/state.json`](runs/e1/state.json) · คำสั่ง `status` และ `noise` ต้องอ่านไฟล์แบบนี้ได้

| ฟิลด์ | ความหมาย |
|---|---|
| `cfg` | `name` `accounts` `par` `solver_prompt` `solver_model` `solver_effort` `evolver_model` `evolver_effort` `adaptor_model` `turn_minutes` `fresh_session` และ path ที่โปรแกรมต้องใช้ (ข้อมูล · `skillopt`) |
| `epochs` `n` | จำนวน epoch (E) · จำนวนครั้งต่อโจทย์ (N) |
| `phase` `k` | ขั้นล่าสุดที่ทำเสร็จ · หมายเลข epoch ปัจจุบัน |
| `session_id` `session_cost` | เซสชันของ Evolver · ยอดสะสมของค่าใช้จ่ายในเซสชันนั้น |
| `adapt` | สถิติของ Benchmark Adaptor (แบบเดียวกับ 1 ตา ข้อ 10) + `tasks` (จำนวนโจทย์ต่อชุด) `reference` (`files` `answers` `leaks`) `audit_ok` |
| `legs` | `<leg>` → สรุปของ leg (ตารางถัดไป) |
| `turns` | รายการสถิติของแต่ละตา (ข้อ 10) |

| ฟิลด์ของ 1 leg | ความหมาย |
|---|---|
| `label` `split` `skills` `model` | ชื่อ leg · ชุด (`train` `validation` `test` `all`) · ชื่อสกิลที่ใช้ · โมเดลของ Solver |
| `n` `tasks` | จำนวน rollout · จำนวนโจทย์ |
| `score` | ค่าเฉลี่ยของคะแนนทุก rollout (0–1) |
| `by_task` | `<id โจทย์>` → คะแนนของแต่ละครั้ง เรียงตามครั้งที่ |
| `passes` | rollout ที่ผ่าน (คะแนน ≥ 0.999) |
| `pass3` `all3` `none3` `mixed` | โจทย์ที่ผ่านอย่างน้อย 1 ครั้ง · ผ่านทุกครั้ง · ไม่ผ่านเลย · ผ่านบางครั้ง |
| `cost_usd` `context_tokens` `tool_calls` `skill_read` | ค่าใช้จ่ายรวม · โทเคนขาเข้าเฉลี่ยต่อ rollout (`input_tokens` + `cache_read` + `cache_write`) · คำสั่งเฉลี่ยต่อ rollout · จำนวน rollout ที่เปิดอ่านสกิล |
| `grader_failed` | จำนวน rollout ที่ตัวตรวจเองล้ม (ข้อตรวจแรกชื่อ `grader`) |

## 5 · Benchmark Adaptor (`adapt`)

| ลำดับ | ทำอะไร |
|---|---|
| 1 | เตรียม `adapt/`: `setup/` (มี `plugin_api.py` `plugin_skeleton.py` และสำเนา `benchmark_grader.py`) · `reference/` (ว่าง) · `work/` (ว่าง) · `data/` (สำเนาของ data root และ `split.json`) |
| 2 | เรียก Benchmark Adaptor 1 เซสชัน (ข้อ 7): system prompt ต่อท้ายด้วย `prompts/adaptor.md` · ข้อความของผู้ใช้ = ไฟล์คำสั่งทั้งไฟล์ · มองเห็น `adapt/` ในชื่อ `/ba` (เขียนได้) และ `adapt/data/` ในชื่อ `/data` (อ่านอย่างเดียว) · โฟลเดอร์ทำงาน `/ba/work` |
| 3 | ไม่มี `/ba/setup/benchmark_plugin.py` หรือเซสชันจบไม่ปกติ = หยุด exit 1 |
| 4 | **ล็อก (freeze):** คัดลอก plug-in และ `plugin_api.py` ลง `setup/` · ตัวตรวจใน `setup/` คัดลอกจาก `inputs/` (ไม่ใช่สำเนาที่ Adaptor แตะได้) · plug-in ต้อง import ได้เฉพาะ `json` `os` `pathlib` `re` `typing` `dataclasses` `collections` `itertools` `functools` `plugin_api` |
| 5 | รัน `list_tasks(<data root>)` ใน process แยก → `setup/tasks.json` · id ต้องไม่ซ้ำ และการแบ่งชุดต้องตรงกับ `split.json` ของผู้ใช้ทุกข้อ ไม่ตรง = หยุด exit 1 |
| 6 | คัดลอก `adapt/reference/` เป็น `reference/` · เขียน `setup/freeze.json`: `frozen_at` · `sha256` ของ `benchmark_plugin.py` `benchmark_grader.py` `tasks.json` · `grader_unchanged_by_adaptor` · `tasks` (id ของแต่ละชุด) |
| 7 | ตรวจการรั่ว (ตารางล่าง) → `setup/audit.md` · พบการรั่ว = บันทึกผลแล้วหยุด exit 1 โดย `phase` ยังเป็น `init` (ต้องแก้คำสั่งของผู้ใช้ แล้วรัน `adapt` ใหม่) |

**ก่อนรันทุก leg และก่อนคำสั่ง `turn` `audit` `eval`** โปรแกรมคำนวณ hash ของ 3 ไฟล์ใน `setup/` ใหม่ ไม่ตรงกับ `freeze.json` = หยุด exit 1 พร้อมบอกชื่อไฟล์

| ตรวจการรั่ว: ไฟล์ใน `reference/` (ชื่อไฟล์หรือเนื้อหา) ต้องไม่มี | นับเป็น |
|---|---|
| id ของโจทย์ชุด validation หรือ test | ของชุดที่เก็บไว้ |
| 60 ตัวอักษรแรกของข้อความโจทย์ชุด validation หรือ test | ของชุดที่เก็บไว้ |
| ค่าของฟิลด์ `function` ในไฟล์โจทย์ (`<data root>/tasks/<id>.json`) ของชุด validation หรือ test | ของชุดที่เก็บไว้ |
| ไฟล์ชื่อ `benchmark_grader.py` หรือบรรทัดของตัวตรวจที่ยาว 40 ตัวอักษรขึ้นไป (ไม่นับบรรทัดที่มีอยู่ในข้อมูลของผู้ใช้อยู่แล้ว) | โค้ดของตัวตรวจ |

`audit.md` ตัวอย่างจริง: [`runs/e1/setup/audit.md`](runs/e1/setup/audit.md) · ตาราง `รายการ | ผล` 4 แถว (จำนวนไฟล์ · มีเฉลยอ้างอิงของชุด Training กี่ไฟล์ = ไฟล์ใต้ `answers/` · ของชุด Validation หรือ Test พบหรือไม่ · โค้ดของตัวตรวจพบหรือไม่) ตามด้วยรายชื่อไฟล์ทั้งหมด และรายการสิ่งที่รั่ว (ถ้ามี)

**สิ่งที่ `prompts/adaptor.md` ต้องบอก:** การรันแบบ skill evolution คืออะไร และ 3 ชุดโจทย์ใช้ทำอะไร · งาน 2 อย่าง (เขียน `benchmark_plugin.py` ลง `{setup_dir}/` และเติม `{reference_dir}/`) · กติกาของ plug-in (ข้อ 1 และลำดับ 4) · `reference/` ต้องมีทุกอย่างที่ผู้ใช้ส่งมาและ Evolver ใช้ได้ **ยกเว้น** ของชุด validation ของชุด test และตัวตรวจ (โค้ดและทุกอย่างที่อธิบายวิธีตรวจ) · ถ้าคำสั่งของผู้ใช้จำกัดมากกว่านี้ให้ทำตามผู้ใช้ · ให้ทดสอบ plug-in ก่อนจบ · โปรแกรมแทน `{setup_dir}` ด้วย `/ba/setup` และ `{reference_dir}` ด้วย `/ba/reference`

## 6 · Solver และตัวตรวจ (rollout)

EvoSkill ไม่รัน rollout เอง ใช้คำสั่ง `run` ของ `skill-optimizer` ที่สร้างใน [บท 05](../05_Skill_Optimizer/skillopt_format.md) กับโฟลเดอร์งาน `runs/<ชื่อ>/legs/` Solver จึงเป็นไพป์ไลน์เดียวกับบท 05 และ 06

| ลำดับ | ทำอะไร |
|---|---|
| 1 | ตรวจ hash ของ `setup/` (ข้อ 5) |
| 2 | เขียน `legs/suite/suite.json`: `name` · `skill_name` = `-` · `timeout` = 600 · `grader` = `benchmark_grader.py` · `prompt` = เนื้อหาของ `solver_prompt.txt` · `tasks` = โจทย์จาก `setup/tasks.json` ทุกข้อ (`id` · `split` โดย `validation` เขียนเป็น `val` · `brief` = `instruction` · `grading`) และคัดลอกตัวตรวจจาก `setup/` ไปไว้ข้างกัน |
| 3 | ลบ `legs/runs/<leg>/` เดิม · ถ้าชุดสกิลมีสกิลอย่างน้อย 1 ตัว (โฟลเดอร์ที่มี `SKILL.md`) คัดลอกทั้งชุดไปเป็น `legs/runs/<leg>/skills/` · ไม่มีสกิล = ไม่สร้างโฟลเดอร์ `skills` |
| 4 | รัน `<python> <skillopt.py> run <legs> --label <leg> --split <train\|val\|test\|all> --reps <N> --accounts <บัญชี คั่นด้วย ,> --par <par> --model <model> --effort <effort>` ด้วย Python ตัวเดียวกับที่รันเครื่องมือ |
| 5 | อ่าน `grade.json` และ `metrics.json` ของทุก rollout ใต้ `legs/runs/<leg>/trials/` → สรุปของ leg ลง `state.json` และ `legs/<leg>.json` · คำสั่ง `run` ล้ม หรือจำนวนผลไม่ครบ = หยุดพร้อมบอกสาเหตุ |

- leg ที่มี `legs/<leg>.json` อยู่แล้วถือว่าเสร็จ ไม่รันซ้ำ (รันต่อจากที่ค้างได้) · leg ที่ค้างกลางทางรันใหม่ทั้ง leg
- **rollout ที่ Solver ไม่ได้ทำงาน** = จบไม่ปกติ (`metrics.ok` เป็น false หรือหมดเวลา) และไม่มีคำสั่งเลย (`tool_calls` = 0) เช่น บัญชีติดลิมิตการใช้งาน: leg นั้นไม่ถือว่าเสร็จ · ไม่เขียน `legs/<leg>.json` และไม่บันทึกลง `state.json` · พิมพ์ชื่อ rollout บัญชี และข้อความ `result` ของแต่ละครั้ง แล้ว exit 1 · สั่งคำสั่งเดิมซ้ำ = รัน leg นั้นใหม่ทั้ง leg (คะแนน 0 ที่มาจากบัญชีใช้ไม่ได้ ต้องไม่ถูกนับเป็นผลของสกิล)
- Solver เห็นเฉพาะ `./skills` ใน sandbox ของตัวเอง ไม่เห็นเฉลย ตัวตรวจ และ `evo/`
- **ตัวตรวจของผู้ใช้** `benchmark_grader.py` มีฟังก์ชัน `grade(task, snapshot)` คืนคะแนน 0–1 และรันเป็นโปรแกรมได้ `python3 benchmark_grader.py <sandbox> <task.json>` พิมพ์ `{"score": …, "checks": […]}` (รูปแบบที่ `skillopt.py` ใช้) · ผลรายข้อ (`checks`) เป็นของผู้สอน **ห้ามส่งให้ Evolver**

## 7 · การเรียก Agent และการแยกเครื่อง

Benchmark Adaptor และ Evolver คือ Claude Code 1 เซสชัน ที่ใช้ system prompt เดิมของมัน แล้วต่อท้ายด้วย prompt ของเรา · ข้อความของผู้ใช้ส่งทาง stdin · stdout เก็บเป็น `transcript.jsonl` · stderr เป็น `transcript.jsonl.stderr`

```text
claude --dangerously-skip-permissions --disable-slash-commands -p --append-system-prompt <prompt> --model <model> --effort <effort>
       --disallowedTools WebSearch,WebFetch --output-format stream-json --verbose --strict-mcp-config
       <--no-session-persistence | --session-id <uuid> | --resume <uuid>>
```

| เงื่อนไข | ค่า |
|---|---|
| บัญชี | ตัวแรกของ `--accounts` |
| ตัวแปรสภาพแวดล้อม | ลบตัวที่ขึ้นต้นด้วย `CLAUDE` และ `MA_` · ตั้ง `IS_SANDBOX=1` · ตั้ง `CLAUDE_CONFIG_DIR=<โฟลเดอร์ของบัญชี>` เมื่อมีโฟลเดอร์นั้น |
| โฟลเดอร์ของบัญชี | `<root>/<ชื่อบัญชี>` โดย `<root>` = ตัวแปร `EVOSKILL_ACCOUNT_ROOT` (ไม่ตั้ง = `~/ai-accounts/.Claude`) |
| ไม่มีโฟลเดอร์ของบัญชี | เรียกคำสั่งของบัญชีแทน `claude …` ด้วยตัวเลือกชุดเดียวกันตั้งแต่ `-p` · ชื่อบัญชีเป็นคำสั่งที่มีช่องว่างได้ เช่น `python3 fake_agent.py` (ใช้ทดสอบด้วย Agent จำลอง) |
| เซสชัน | Adaptor: `--no-session-persistence` · Evolver ตาแรกของเซสชัน: `--session-id <uuid ใหม่>` · ตาถัดไป: `--resume <uuid เดิม>` |
| หมดเวลา | Adaptor 1,800 วินาที · Evolver `turn-minutes` × 60 + 60 วินาที แล้วหยุดทั้งกลุ่ม process |

**การแยกเครื่อง:** Agent ทั้งสองรันใน mount namespace ของตัวเอง (`unshare -m --propagation private`) · ผูก (bind mount) เฉพาะโฟลเดอร์ที่อนุญาตไปยัง path ที่ Agent เห็น ส่วนที่อ่านอย่างเดียว remount เป็น read-only · แล้วแทน `/workspace` ด้วย tmpfs ว่าง Agent จึงมองไม่เห็นตัวตรวจ ข้อมูลทั้งหมด และผลของ Validation กับ Test

| Agent | สิ่งที่เห็น |
|---|---|
| Benchmark Adaptor | `/ba` = `adapt/` (เขียนได้) · `/data` = `adapt/data/` (อ่านอย่างเดียว) |
| Evolver | `/evo` = `evo/` (เขียนได้) · `/evo/traces` `/evo/scores` `/evo/solver_workspaces` `/evo/skills` `/evo/reference` (อ่านอย่างเดียว) |

ไม่มีคำสั่ง `unshare` (เช่น ทดสอบบน Windows) หรือตั้งตัวแปร `EVOSKILL_NO_ISOLATION=1`: รัน Agent โดยไม่แยกเครื่อง พิมพ์คำเตือน 1 บรรทัด ให้โฟลเดอร์ทำงานเป็นโฟลเดอร์จริง และส่ง path จริงให้ Agent ทางตัวแปร `EVOSKILL_BA_DIR` `EVOSKILL_DATA_DIR` `EVOSKILL_EVO_DIR` (ใช้กับ Agent จำลองเท่านั้น ห้ามใช้วัดผลจริง)

## 8 · เครื่องของ Evolver (`evo/`)

ก่อนทุกตา โปรแกรมส่งผลของ **ชุด Training ของ epoch ก่อนหน้า** (epoch 0 = leg `base_train` · epoch K = leg `vK_train`) เข้า `evo/` · ของชุด Validation และ Test ไม่ถูกส่งเข้าไปเลย

| โฟลเดอร์ | เนื้อหา | Evolver |
|---|---|---|
| `traces/epoch_K/<id โจทย์>_s<i>.jsonl` | `transcript.jsonl` ของ rollout ครั้งที่ i | อ่าน |
| `scores/epoch_K.json` | `{"<id โจทย์>_s<i>": คะแนน}` · ตัวตรวจล้มให้ค่า `"grader_failed"` · **คะแนนอย่างเดียว ไม่มีผลรายข้อ** | อ่าน |
| `solver_workspaces/epoch_K/<id โจทย์>_s<i>/` | `sandbox/` ของ rollout นั้น ไม่รวม `skills/` และ `__pycache__` | อ่าน |
| `skills/epoch_K/` | ชุดสกิลที่ Solver ของ epoch K ใช้ (epoch 0 = โฟลเดอร์ว่าง) | อ่าน |
| `reference/` | สำเนาของ `reference/` (คัดลอกครั้งแรกครั้งเดียว) | อ่าน |
| `staging/` | ชุดสกิลที่กำลังเขียน · เริ่มว่าง แล้วคงอยู่ข้ามตา | เขียน |
| `evolver_workspace/` | บันทึกและสคริปต์ของ Evolver เอง คงอยู่ข้ามตา | เขียน |

## 9 · ตาของ Evolver (`turn`)

| ลำดับ | ทำอะไร |
|---|---|
| 1 | ส่งผลของ Training ของ epoch K−1 เข้า `evo/` (ข้อ 8) |
| 2 | เขียน `turns/turn_K/message.md` จาก `prompts/evolver_message.md`: แทน `{now}` (เวลา UTC ตอนนี้ `YYYY-MM-DD HH:MM`) `{deadline}` (ตอนนี้ + `turn-minutes`) `{k}` · system prompt ต่อท้ายด้วย `prompts/evolver_system.md` ซึ่งแทน `{n}` ด้วยจำนวนครั้งต่อโจทย์ แล้วบันทึกที่ `turns/evolver_system_append.md` |
| 3 | เรียก Evolver (ข้อ 7) โฟลเดอร์ทำงาน `/evo` · ตาที่ 1 หรือเมื่อใช้ `--fresh-session` = เซสชันใหม่ · นอกนั้นทำต่อในเซสชันเดิม |
| 4 | เซสชันจบไม่ปกติและไม่ใช่เพราะหมดเวลา = หยุด exit 1 โดยไม่เปลี่ยน `phase` (รัน `turn` ซ้ำเพื่อทำตานี้ใหม่) |
| 5 | **คัดลอก `evo/staging/` เป็น `skills_vK/` โดยไม่มีเงื่อนไข** (ไม่มีประตูรับ · หมดเวลาก็ใช้ตามสภาพที่เป็นอยู่) |
| 6 | เขียน `turns/turn_K/actions.md` และ `stats.json` (ข้อ 10) · ต่อท้าย `state.turns` · ตั้ง `k` และ `phase` |

**สิ่งที่ `prompts/evolver_system.md` ต้องบอก:** บทบาท (เขียนชุดสกิลให้ Solver ของ epoch ถัดไป) · เป้าหมาย (คะแนนสูงขึ้นกับโจทย์ที่ไม่เคยเห็น โจทย์ชุด train เป็นเพียงตัวอย่าง) · epoch 0 ไม่มีสกิล และ epoch K ใช้ชุดที่เขียนในตาที่ K · เซสชันนี้อยู่ตลอดการรัน · แผนที่ของ `/evo` ทั้ง 7 โฟลเดอร์ตามข้อ 8 · กติกาของ `staging/` (แก้ในที่เดิม · ไม่แก้ = Solver ใช้ชุดเดิม · สกิล 1 ตัว = `<ชื่อ>/SKILL.md` ที่ frontmatter มีเฉพาะ `name` กับ `description` · ไฟล์อื่นในโฟลเดอร์ถูกส่งไปกับสกิล) · บริบทอาจถูกย่ออัตโนมัติ จึงควรเก็บสิ่งสำคัญใน `evolver_workspace/` · path ใน trace เป็นของเครื่องของ Solver · เขียนสกิลเป็นภาษาไทย
**สิ่งที่ `prompts/evolver_message.md` ต้องบอก:** เวลาปัจจุบัน · เส้นตาย · หมายเลข epoch · ให้วิเคราะห์ rollout วินิจฉัยจุดพลาดที่สกิลแก้ได้ แล้วเขียน `skills_v{k}` ลง `/evo/staging/` · ข้อความสั้น 1 ย่อหน้า และ **ไม่บอกจำนวน epoch ทั้งหมด**
ทั้งสอง prompt **ไม่บอกวิธีวิเคราะห์** และไม่บอกอะไรเกี่ยวกับตัวตรวจ

## 10 · หลักฐานของแต่ละครั้ง (`turns/`)

`turns/adaptor/` และ `turns/turn_K/` มี `message.md` (ข้อความที่ส่ง) · `transcript.jsonl` · `actions.md` · `stats.json` · ของ Adaptor มี `system_append.md` ด้วย

**`actions.md`** = transcript ที่คนอ่านได้ ตามลำดับเวลา: ข้อความของ Agent ขึ้นต้นด้วย `**Agent พูด:**` (ของ subagent ใช้ `**subagent พูด:**`) · การใช้เครื่องมือเป็นหัวข้อ `### ขั้น <n> · <ชื่อเครื่องมือ>` ตามด้วยคำสั่งหรือไฟล์ที่เขียน (ตัดที่ 2,500 ตัวอักษร) และ `ผลที่ได้:` (ตัดที่ 1,200 ตัวอักษร) · ข้อความของ Agent ตัดที่ 1,500 ตัวอักษร · ตัวอย่างจริง: [`runs/e1/turns/turn_1/actions.md`](runs/e1/turns/turn_1/actions.md)

| ฟิลด์ของ `stats.json` | ความหมาย |
|---|---|
| `ok` | มีบรรทัด `result` และไม่เป็น error |
| `tool_calls` `tools` | จำนวนการใช้เครื่องมือทั้งหมด · แยกตามชื่อเครื่องมือ |
| `bash` `bash_python` | จำนวนคำสั่ง Bash · จำนวนที่เรียก `python` หรือ `python3` |
| `rerun_old_scripts` | จำนวนคำสั่ง Bash ที่เรียกสคริปต์ (`.py` `.sh`) ซึ่งมีอยู่ใน `evolver_workspace/` ก่อนเริ่มตานี้ |
| `subagents` `compactions` | จำนวนครั้งที่เรียก subagent (เครื่องมือ `Task` หรือ `Agent`) · จำนวนครั้งที่บริบทถูกย่อ |
| `touch` | จำนวนการใช้เครื่องมือที่อ้างถึงแต่ละโฟลเดอร์ของ `/evo` (7 คีย์ตามข้อ 8) |
| `num_turns` `output_tokens` `context_tokens` | จากบรรทัด `result` · `context_tokens` = `input_tokens` + `cache_read_input_tokens` + `cache_creation_input_tokens` |
| `cost_usd` `session_cost_usd` | ค่าใช้จ่ายของตานี้ · ยอดสะสมของเซสชัน (`total_cost_usd` ของเซสชันที่ `--resume` เป็นยอดสะสม ค่าของ 1 ตา = ผลต่างจากตาก่อน) |
| `k` `wall_s` `timed_out` `fresh_session` `session_id` `rollouts_given` `old_scripts` | ตาที่ · เวลา · หมดเวลาหรือไม่ · เป็นเซสชันใหม่หรือไม่ · เซสชัน · จำนวน rollout ที่ส่งให้ · จำนวนสคริปต์เดิมใน `evolver_workspace/` |
| `skills` `skill_md_bytes` `skill_other_files` `skill_problems` | ชื่อสกิลใน `skills_vK` · ขนาดรวมของ `SKILL.md` · ไฟล์อื่นในชุด · สกิลที่ไม่มี `description` ใน frontmatter |
| `files_added` `files_changed` `files_removed` | ไฟล์ใน `staging/` ที่ต่างจากก่อนเริ่มตา |
| `workspace_files` | ไฟล์ใน `evolver_workspace/` เมื่อจบตา |

## 11 · ข้อความของ `status`

ตัวอย่างจริง: [`runs/e1/status.txt`](runs/e1/status.txt) (เซสชันเดียว) · [`runs/f1/status.txt`](runs/f1/status.txt) (`--fresh-session`) · ต้องพิมพ์ตรงกันทุกตัวอักษรเมื่ออ่าน `state.json` เดียวกัน รวมบรรทัดว่างบรรทัดแรก

```text
(บรรทัดว่าง)
การรัน <name> · <E> epochs · <N> samples per task · Solver <model>/<effort> · Evolver <model>/<effort> · <เซสชันเดียวตลอดการรัน|เซสชันใหม่ทุก epoch>
Benchmark Adaptor: โจทย์ train <n> · validation <n> · test <n> · reference/ <n> ไฟล์ (เฉลยของ Training <n> ไฟล์) · ตรวจการรั่ว: <สะอาด|พบการรั่ว> · $<0.00>
(บรรทัดว่าง)
| epoch | ชุดสกิลที่ Solver ใช้ | SKILL.md | ไฟล์อื่น | Training คะแนน (ผ่าน) | Validation คะแนน (ผ่าน) | ตาของ Evolver (นาที) | เครื่องมือ | Bash | รันสคริปต์เดิมซ้ำ | ย่อบริบท | ค่าใช้จ่าย |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | (ไม่มีสกิล) | - | - | <%> (<ผ่าน>/<n>) | <%> (<ผ่าน>/<n>) | - | - | - | - | - | - |
| <k> | <ชื่อสกิล คั่นด้วย ", " หรือ (ว่าง)> | <0.0> KB | <n> | <%> (<ผ่าน>/<n>) | <%> (<ผ่าน>/<n>) | <0.0> | <n> | <n> | <n> | <n> | $<0.00> |
(บรรทัดว่าง)
| Test Set (held-out) | คะแนน | pass@1 (rollout ที่ผ่าน) | pass@3 (ผ่านอย่างน้อย 1 ครั้ง) | all@3 (ผ่านทุกครั้ง) |
|---|---|---|---|---|
| ไม่มีสกิล | <%> | <n>/<n> | <n>/<n> | <n>/<n> |
| skills_v<E> (epoch สุดท้าย) | <%> | <n>/<n> | <n>/<n> | <n>/<n> |
(บรรทัดว่าง)
รวม: rollout ของ Solver <n> ครั้ง ($<0.00>) · Evolver <n> ตา ($<0.00>) · Benchmark Adaptor $<0.00>
Test Set: คะแนนเพิ่ม <+0.0> จุด · pass rate เพิ่ม <+0.0> จุด · ต้นทุนของ Evolver ต่อ 1 จุดที่เพิ่ม: คะแนน <$0.000|ไม่เพิ่ม> · pass rate <$0.000|ไม่เพิ่ม>
สถานะ: <จบแล้ว (วัด Test Set แล้ว)|ยังไม่จบ · ขั้นถัดไป: <ขั้น> (epoch <k>)>
```

- `<%>` = ร้อยละ ทศนิยม 1 ตำแหน่ง · leg ที่ยังไม่มีพิมพ์ `-` · KB = ไบต์ ÷ 1024 · นาที = วินาที ÷ 60
- บรรทัด Benchmark Adaptor ตาราง Test Set และบรรทัด `Test Set:` พิมพ์เมื่อมีข้อมูลนั้นแล้วเท่านั้น (ตาราง Test Set พิมพ์เมื่อมี `base_test` · แถวที่สองเมื่อมี `v<E>_test`)
- rollout ที่นับ = ทุก leg ใน `state.legs` · pass rate = `passes` ÷ `n` · "ต้นทุนต่อ 1 จุด" = ค่าใช้จ่ายรวมของ Evolver ÷ จุดที่เพิ่ม
- `(epoch <k>)` ท้ายบรรทัดสถานะ = `k` + 1 เมื่อขั้นถัดไปคือ `turn` นอกนั้น = `k`

## 12 · ข้อความของ `noise`

ตัวอย่างจริง: [`runs/e1/noise.txt`](runs/e1/noise.txt) · [`runs/e2/noise.txt`](runs/e2/noise.txt) · ต้องพิมพ์ตรงกันทุกตัวอักษร

| ส่วน | เนื้อหา |
|---|---|
| ตารางที่ 1 | 1 แถวต่อ leg เรียงตาม `base_train` `base_val` `base_test` แล้ว `v1_train` `v1_val` `v1_test` `v2_…` (เฉพาะที่มี) ตามด้วย leg อื่นเรียงตามชื่อ · คอลัมน์: ชุดสกิล · จำนวนโจทย์ · ผ่าน N/N (`all3`) · ผ่าน 0/N (`none3`) · ผ่านบางครั้ง (`mixed`) · จำนวนโจทย์ที่คะแนนของแต่ละครั้งไม่เท่ากัน |
| ตารางที่ 2 | ประตูรับแบบ "วัดโจทย์ละ 1 ครั้ง รับเมื่อคะแนนสูงกว่าเดิม": แยก Training และ Validation · เทียบชุดสกิลที่ติดกัน (ไม่มีสกิล → v1 → v2 …) · จับคู่ครั้งที่ i ของชุดเดิมกับครั้งที่ j ของชุดใหม่ทุกแบบ (N × N คู่) โดยคะแนนของ 1 ครั้ง = ค่าเฉลี่ยของทุกโจทย์ในครั้งนั้น · นับ รับ (สูงกว่า) · เสมอ · ต่ำกว่า (ถือว่าเท่ากันเมื่อต่างไม่เกิน 1e-9) |

## 13 · `export` (สำเนาที่เก็บลงเครื่อง)

`export <work> --run <ชื่อ> --to <โฟลเดอร์>` เขียน `<โฟลเดอร์>/<ชื่อ>/` (ลบของเดิมก่อน) · นี่คือสิ่งที่เก็บใน [`runs/`](runs/) ของบทนี้

| เก็บ | รายละเอียด |
|---|---|
| `RUN.json` `state.json` `inputs/instruction.md` | – |
| `status.txt` `noise.txt` | ผลของคำสั่ง `status` และ `noise` |
| `setup/` | `benchmark_plugin.py` `tasks.json` `freeze.json` `audit.md` (ไม่เก็บตัวตรวจ) |
| `reference/` · `skills_v*/` · `turns/` · `evo/evolver_workspace/` · `evo/scores/` | ทั้งโฟลเดอร์ |
| `legs/<leg>.json` | ทุก leg |
| `legs/runs/<leg>/trials/<rollout>/` | `grade.json` `metrics.json` และ `sandbox/solve.py` `sandbox/test_solve.py` |

| ไม่เก็บ | รายละเอียด |
|---|---|
| Trace ดิบ | ไฟล์ `.jsonl` `.stderr` `.pyc` · โฟลเดอร์ `__pycache__` · ไฟล์ที่ใหญ่กว่า 400 KB |
| รายละเอียดของ Validation Set | rollout ของชุด val: `grade.json` เหลือ `{"score": …, "checks": "sealed (Validation Set)"}` · `metrics.json` ไม่มี `commands` และ `result` · ไม่มี `sandbox/` |
