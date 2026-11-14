# โครงของ 1 การรัน และไฟล์ที่แต่ละคำสั่งอ่านและเขียน

`<work>` = โฟลเดอร์ที่มี `bench/` และ `runs/` · `<run>` = `<work>/runs/<ชื่อ>/`

## 1 · สิ่งที่ผู้ใช้ส่ง (`<work>/bench/`)

| ไฟล์ | เนื้อหา |
|---|---|
| `instruction.md` | คำสั่งของผู้ใช้ 1 หน้า ต้องมี `<E> epochs · <N> samples per task` (ตัวคั่น `·` `x` หรือ `,`) · มีได้หลายไฟล์ เลือกด้วย `init --instruction` |
| `data/<data root>/` | ข้อมูลของ benchmark (โฟลเดอร์เดียวใต้ `data/`) |
| `split.json` | `{"train": [...], "validation": [...], "test": [...]}` |
| `benchmark_grader.py` | ตัวตรวจ: `grade(task, snapshot)` → 0–1 และรันได้ `python3 benchmark_grader.py <sandbox> <task.json>` พิมพ์ `{"score": …, "checks": […]}` |
| `solver_prompt.txt` | พรอมต์ของ Solver · `{brief}` ถูกแทนด้วยข้อความโจทย์ |

## 2 · โฟลเดอร์ของ 1 การรัน

```text
<run>/
├── RUN.json                 hash ของ instruction split grader · data (dir, files) · run_size
├── state.json               cfg · epochs · n · phase · k · session_id · session_cost · adapt · legs · turns
├── inputs/                  สำเนาตอน init: instruction.md split.json benchmark_grader.py
├── adapt/                   โต๊ะทำงานของ Benchmark Adaptor: setup/ reference/ work/ data/
├── setup/                   ที่ล็อกแล้ว: benchmark_plugin.py plugin_api.py benchmark_grader.py tasks.json freeze.json audit.md
├── reference/               สิ่งที่ Evolver อ่านได้เกี่ยวกับ benchmark
├── skills_v1/ … skills_vE/  ชุดสกิลหลังตาที่ K (เก็บทุกชุด)
├── evo/                     เครื่องของ Evolver (ข้อ 5)
├── turns/
│   ├── adaptor/             message.md system_append.md transcript.jsonl(.stderr) actions.md stats.json
│   ├── evolver_system_append.md
│   └── turn_K/              message.md transcript.jsonl(.stderr) actions.md stats.json
└── legs/                    โฟลเดอร์งานของ skillopt.py
    ├── <leg>.json           สรุปของ 1 leg (มีไฟล์นี้ = leg เสร็จ)
    ├── suite/               suite.json + สำเนาตัวตรวจจาก setup/
    └── runs/<leg>/          skills/ (ถ้ามีสกิล) และ trials/<id>-r<ครั้ง>/ (sandbox/ transcript.jsonl grade.json metrics.json task.json)
```

ชื่อ leg: `base_train` `base_val` `base_test` · `vK_val` `vK_train` (epoch สุดท้ายไม่มี `vK_train`) · `vE_test` · leg ของ `eval` ใช้ชื่อจาก `--label`

## 3 · ลำดับของขั้น (`state.phase`)

| `phase` ตอนนี้ | คำสั่งถัดไป | `phase` หลังทำเสร็จ |
|---|---|---|
| `init` | `adapt` | `adapt` |
| `adapt` | `base` | `base` |
| `base` | `turn` (`k` = 1) | `turn` |
| `turn` | `rollout` | `rollout` |
| `rollout` และ `k` < E | `turn` (`k` + 1) | `turn` |
| `rollout` และ `k` = E | `test` | `test` |
| `test` | (จบ) | – |

คำสั่งที่ถูกเรียกผิดลำดับ: บอกขั้นถัดไป แล้ว exit 1 โดยไม่เรียกโมเดล · `status` `noise` `audit` `eval` `export` ไม่เปลี่ยน `phase`

## 4 · แต่ละคำสั่งอ่านและเขียนอะไร

| คำสั่ง | อ่าน | เขียน | หยุด (exit 1) เมื่อ |
|---|---|---|---|
| `init` | `bench/*` | `inputs/` `RUN.json` `state.json` | มี `state.json` แล้ว · ไม่พบขนาดของการรัน · ไม่พบไฟล์ของผู้ใช้หรือ `skillopt.py` |
| `adapt` | `inputs/` · data root · `prompts/adaptor.md` | `adapt/` `turns/adaptor/` `setup/` `reference/` `state.adapt` | เซสชันจบไม่ปกติ · ไม่มี plug-in · import ต้องห้าม · การแบ่งชุดไม่ตรง · พบการรั่ว (`phase` ยังเป็น `init`) |
| `audit` | `reference/` `setup/tasks.json` `inputs/benchmark_grader.py` data root | – (พิมพ์รายงาน) | พบการรั่ว · hash ของ `setup/` ไม่ตรง |
| `base` | `setup/` | `legs/` (3 leg) `state.legs` | hash ไม่ตรง · `skillopt.py run` ล้ม · ผลไม่ครบ |
| `turn` | leg ของ Training ของ epoch K−1 · `skills_v(K−1)/` · `prompts/evolver_*.md` | `evo/` `turns/turn_K/` `turns/evolver_system_append.md` `skills_vK/` `state.turns` | เซสชันจบไม่ปกติและไม่ใช่เพราะหมดเวลา (`phase` ไม่เปลี่ยน รัน `turn` ซ้ำได้) |
| `rollout` | `skills_vK/` `setup/` | `legs/` (`vK_val` แล้ว `vK_train`) | เหมือน `base` |
| `test` | `skills_vE/` `setup/` | `legs/` (`vE_test`) | เหมือน `base` |
| `run` | `state.json` | ตามขั้นที่ทำ | ขั้นใดขั้นหนึ่งหยุด (สั่ง `run` ซ้ำเพื่อทำต่อ) |
| `status` `noise` | `state.json` เท่านั้น | – | ไม่พบการรัน |
| `eval` | ชุดสกิลที่ระบุ · `setup/` | `legs/` (`<ป้าย>`) `state.legs` | ชื่อป้ายซ้ำกับ leg ของวงรอบ · ไม่พบชุดสกิล |
| `export` | ทั้งการรัน | `<โฟลเดอร์>/<ชื่อ>/` (ลบของเดิมก่อน) | – |

rollout ที่ Solver ไม่ได้ทำงาน (`metrics.ok` เป็น false หรือหมดเวลา และ `tool_calls` = 0 เช่น บัญชีติดลิมิต) ใช้กับทุก leg (`base` `rollout` `test` `eval`): พิมพ์ชื่อ rollout บัญชี และข้อความ `result` แล้ว exit 1 โดยไม่เขียน `legs/<leg>.json` และไม่บันทึกลง `state.json` · สั่งคำสั่งเดิมซ้ำ = รัน leg นั้นใหม่ทั้ง leg

การทำต่อจากที่ค้าง: leg ที่มี `legs/<leg>.json` แล้วไม่รันซ้ำ · leg ที่ค้างกลางทางถูกลบแล้วรันใหม่ทั้ง leg · ตาของ Evolver ที่ล้มทำใหม่ทั้งตา (เซสชันเดิมถ้าไม่ใช่ตาแรก)

## 5 · เครื่องของ Evolver (`evo/` = `/evo`)

| โฟลเดอร์ | เนื้อหา | Evolver |
|---|---|---|
| `traces/epoch_K/<id>_s<i>.jsonl` | `transcript.jsonl` ของ rollout ครั้งที่ i ของชุด Training | อ่าน |
| `scores/epoch_K.json` | `{"<id>_s<i>": คะแนน}` · ตัวตรวจล้ม = `"grader_failed"` · ไม่มีผลรายข้อ | อ่าน |
| `solver_workspaces/epoch_K/<id>_s<i>/` | `sandbox/` ของ rollout นั้น ไม่รวม `skills/` และ `__pycache__` | อ่าน |
| `skills/epoch_K/` | ชุดสกิลที่ Solver ของ epoch K ใช้ (epoch 0 ว่าง) | อ่าน |
| `reference/` | สำเนาของ `reference/` (คัดลอกครั้งแรกครั้งเดียว) | อ่าน |
| `staging/` | ชุดสกิลที่กำลังเขียน คงอยู่ข้ามตา · ตอนจบตาที่ K ถูกคัดลอกเป็น `skills_vK/` เสมอ | เขียน |
| `evolver_workspace/` | บันทึกและสคริปต์ของ Evolver คงอยู่ข้ามตา | เขียน |

ก่อนตาที่ K โปรแกรมส่งเฉพาะผลของ leg `base_train` (K = 1) หรือ `v(K−1)_train` · ของ Validation และ Test ไม่ถูกส่งเข้า `evo/` เลย

## 6 · การเรียก Agent และการแยกเครื่อง

```text
claude --dangerously-skip-permissions --disable-slash-commands -p --append-system-prompt <prompt> --model <model> --effort <effort>
       --disallowedTools WebSearch,WebFetch --output-format stream-json --verbose --strict-mcp-config
       <--no-session-persistence | --session-id <uuid> | --resume <uuid>>
```

| เรื่อง | ค่า |
|---|---|
| บัญชี | ตัวแรกของ `--accounts` · โฟลเดอร์ของบัญชี = `$EVOSKILL_ACCOUNT_ROOT/<บัญชี>` (ไม่ตั้ง = `~/ai-accounts/.Claude/<บัญชี>`) → ตั้ง `CLAUDE_CONFIG_DIR` |
| ไม่มีโฟลเดอร์ของบัญชี | เรียกคำสั่งของบัญชีแทน `claude` ด้วยตัวเลือกชุดเดียวกันตั้งแต่ `-p` (ชื่อบัญชีเป็นคำสั่งที่มีช่องว่างได้) |
| ตัวแปรสภาพแวดล้อม | ลบตัวที่ขึ้นต้นด้วย `CLAUDE` และ `MA_` · ตั้ง `IS_SANDBOX=1` |
| ข้อความของผู้ใช้ | ส่งทาง stdin · stdout → `transcript.jsonl` · stderr → `transcript.jsonl.stderr` |
| หมดเวลา | Adaptor 1,800 วินาที · Evolver `turn-minutes` × 60 + 60 วินาที → ส่ง SIGTERM ให้ทั้งกลุ่ม process รอ 5 วินาที แล้ว SIGKILL (รวม process ใน session เดียวกันที่พบใน `/proc`) |
| Solver | เรียกโดย `skillopt.py run` ซึ่งหาคำสั่งของบัญชีจาก `PATH` |

**การแยกเครื่อง** (`unshare -m --propagation private bash -c <สคริปต์>`): ผูกโฟลเดอร์ที่อนุญาตตามตาราง → remount ส่วนที่อ่านอย่างเดียวเป็น read-only → แทน `/workspace` (และโฟลเดอร์งาน ถ้าอยู่นอก `/workspace`) ด้วย tmpfs ว่าง → `cd` ไปโฟลเดอร์ทำงาน → `exec` Agent

| Agent | bind | โฟลเดอร์ทำงาน |
|---|---|---|
| Benchmark Adaptor | `adapt/` → `/ba` (เขียนได้) · `adapt/data/` → `/data` (อ่านอย่างเดียว) | `/ba/work` |
| Evolver | `evo/` → `/evo` (เขียนได้) · `/evo/traces` `/evo/scores` `/evo/solver_workspaces` `/evo/skills` `/evo/reference` (อ่านอย่างเดียว) | `/evo` |

คำสั่ง `claude` และโฟลเดอร์ของบัญชีต้องอยู่นอกโฟลเดอร์ที่ถูกซ่อน (โปรแกรมตรวจก่อนเริ่ม) · จุด mount `/ba` `/data` `/evo` ถูกสร้างเป็นโฟลเดอร์ว่างบนเครื่องจริง

ไม่มีคำสั่ง `unshare` หรือตั้ง `EVOSKILL_NO_ISOLATION=1`: พิมพ์คำเตือน 1 บรรทัด รันในโฟลเดอร์จริง และส่ง path จริงทางตัวแปร `EVOSKILL_BA_DIR` `EVOSKILL_DATA_DIR` `EVOSKILL_EVO_DIR` (ใช้กับ Agent จำลองเท่านั้น)

## 7 · การตรวจการรั่วใน `reference/`

| ชื่อไฟล์หรือเนื้อหาต้องไม่มี | นับเป็น |
|---|---|
| id ของโจทย์ชุด validation หรือ test | ของชุดที่เก็บไว้ |
| 60 ตัวอักษรแรกของข้อความโจทย์ชุด validation หรือ test (ค้นทั้งรูปตามจริงและรูปที่ถูก escape แบบ JSON) | ของชุดที่เก็บไว้ |
| ค่าของ `function` ใน `<data root>/tasks/<id>.json` ของชุด validation หรือ test | ของชุดที่เก็บไว้ |
| ไฟล์ชื่อ `benchmark_grader.py` หรือบรรทัดของตัวตรวจยาว 40 ตัวอักษรขึ้นไป (ไม่นับบรรทัดที่มีในข้อมูลของผู้ใช้) | โค้ดของตัวตรวจ |

## 8 · `stats.json` ของ 1 ครั้งที่เรียก Agent

`ok` `tool_calls` `tools` `bash` `bash_python` `rerun_old_scripts` `subagents` `compactions` `touch` (นับการใช้เครื่องมือที่อ้างถึง `/evo/<โฟลเดอร์>`) `num_turns` `cost_usd` `output_tokens` `context_tokens` · ของ Evolver เพิ่ม `session_cost_usd` `k` `wall_s` `timed_out` `fresh_session` `session_id` `rollouts_given` `old_scripts` `skills` `skill_md_bytes` `skill_other_files` `skill_problems` `files_added` `files_removed` `files_changed` `workspace_files` · ของ Adaptor เพิ่ม `wall_s` และใน `state.adapt` มี `tasks` `reference` `audit_ok`

ค่าใช้จ่ายของ 1 ตา: เซสชันใหม่ = `total_cost_usd` · เซสชันที่ `--resume` = `total_cost_usd` (ยอดสะสม) ลบยอดสะสมของตาก่อน · ถ้ายอดที่รายงานต่ำกว่ายอดสะสมเดิม ถือว่าเป็นค่าของตานั้นเอง

## 9 · `export`

เก็บ: `RUN.json` `state.json` `inputs/instruction.md` · `status.txt` `noise.txt` · `setup/` 4 ไฟล์ (ไม่มีตัวตรวจ) · `reference/` `skills_v*/` `turns/` `evo/evolver_workspace/` `evo/scores/` · `legs/<leg>.json` · `legs/runs/<leg>/trials/<rollout>/` (`grade.json` `metrics.json` `sandbox/solve.py` `sandbox/test_solve.py`)

ไม่เก็บ: `.jsonl` `.stderr` `.pyc` `__pycache__` ไฟล์ใหญ่กว่า 400 KB · rollout ของชุด val เหลือ `{"score": …, "checks": "sealed (Validation Set)"}` · `metrics.json` ไม่มี `commands` และ `result` · ไม่มี `sandbox/`

## 10 · ทดสอบโดยไม่เรียกโมเดล

| ทดสอบ | วิธี |
|---|---|
| `status` และ `noise` | รันกับการรันที่เก็บไว้ แล้วเทียบกับ `status.txt` `noise.txt` ทุกตัวอักษร |
| ทั้งวงรอบ | `init --accounts "python3 fake_agent.py"` (ไม่มีโฟลเดอร์ของบัญชี = เรียกคำสั่งนั้น) + `EVOSKILL_NO_ISOLATION=1` · Agent จำลองแยกบทบาทจาก `--append-system-prompt` และตัวแปร `EVOSKILL_*_DIR` · Solver จำลองถูกเรียกโดย `skillopt.py run` จริง และตัวตรวจจริงให้คะแนน |
| การรั่ว | ให้ Adaptor จำลองคัดลอกโจทย์ของ Validation ลง `reference/` → `adapt` ต้องหยุดโดย `phase` ยังเป็น `init` |
| การล็อก | แก้ `setup/tasks.json` หลัง `adapt` → คำสั่งถัดไปต้องหยุดพร้อมบอกชื่อไฟล์ |

## 11 · ข้อจำกัดที่รู้

- ตาที่หมดเวลาถูกรับตามสภาพของ `staging/` และไม่มีบรรทัด `result` จึงไม่มีค่าใช้จ่ายของตานั้น (`cost_usd` = null)
- Agent เป็น root ใน namespace ของตัวเอง การแยกเครื่องกันการเห็นโดยไม่ตั้งใจ ไม่ได้กัน Agent ที่จงใจ unmount
- เครือข่ายไม่ถูกปิด (ปิดเฉพาะเครื่องมือ WebSearch และ WebFetch)
