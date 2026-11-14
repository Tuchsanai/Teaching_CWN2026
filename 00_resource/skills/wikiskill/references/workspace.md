# workspace ของ `wikiskill` · โครง และไฟล์ที่แต่ละคำสั่งเขียน

`<work>` = โฟลเดอร์งานแบบ skill-optimizer (มี `suite/` และ `runs/`) · 1 การรัน = 1 workspace = `<work>/runs/<ws>/` · `NN` = เลขรอบ 2 หลัก

## โครง

```text
<work>/runs/<ws>/
├── state.json                       สถานะของวงรอบ: cfg · k · phase · r_best · history[] · baseline
├── raw/iter-NN/                     Raw Layer · เขียนครั้งเดียว
│   ├── traces/<id โจทย์>-r<รอบ>.md   Trace 1 ไฟล์ต่อ 1 Trial (ไม่เกิน 15,000 ตัวอักษร)
│   └── summary.md                   ตารางผลของทุก Trace + รายการข้อตรวจที่ไม่ผ่าน
├── wiki/                            Wiki Layer · สะสม ไม่ถูกย้อนกลับ (ไม่มีเมื่อ --no-wiki)
│   ├── index.md                     สารบัญ 1 บรรทัดต่อ pattern        (Maintainer กำหนด โปรแกรมเขียนทับทั้งไฟล์)
│   ├── log.md                       บันทึกรายรอบ                       (Maintainer กำหนด โปรแกรมต่อท้ายใต้หัวข้อของรอบ)
│   ├── skill-impact.md              ข้อเสนอ diff คะแนน ผลตัดสินทุกรอบ   (โปรแกรมเขียนเท่านั้น)
│   └── patterns/<ชื่อ>.md            1 หน้าต่อ 1 pattern                (Maintainer กำหนด โปรแกรมเขียน)
├── skills/<ชื่อ>/SKILL.md, PURPOSE.md   Skills Layer · ชุดสกิลที่ใช้งาน
├── history/iter-NN/                 หลักฐานของรอบ
│   ├── maintainer_input.md          ข้อความที่ส่งให้ Maintainer
│   ├── maintainer_transcript_<n>.jsonl   stdout ของการเรียกครั้งที่ n (stream-json)
│   ├── maintainer_output.json       คำตอบที่ใช้ได้
│   ├── proposer_view/               โฟลเดอร์ที่ Proposer เห็น: wiki/ traces/ skills/ summary.md (สำเนา)
│   ├── proposer_input.md            ข้อความที่ส่งให้ Proposer
│   ├── proposer_transcript_<n>.jsonl
│   ├── proposal.json                ข้อเสนอ
│   ├── proposal.diff                unified diff ของ SKILL.md (ไฟล์ว่างเมื่อเป็น no_action)
│   ├── candidate/skills/            ชุดสกิลที่เสนอ (S′) = สำเนาของ skills/ + ข้อเสนอ
│   ├── gate.json                    k · val_score · r_best_before · outcome · val_trials[]
│   ├── wiki/                        สำเนาของ wiki/ หลังตัดสิน
│   └── skills/                      สำเนาของ skills/ หลังตัดสิน
└── rollouts/                        โฟลเดอร์งานของ skill-optimizer ที่ใช้รัน Trial
    ├── suite/                       สำเนา suite.json และไฟล์ตัวตรวจ
    └── runs/<ป้าย>/                  skills/ (ถ้ามีสกิล) และ trials/<id โจทย์>-r<รอบ>/
```

ป้ายของ Trial: `k00-val` (baseline) · `kNN-train` (rollout) · `kNN-val` (gate)

## แต่ละคำสั่งอ่านและเขียนอะไร

| คำสั่ง | ต้องอยู่ที่ `phase` | อ่าน | เขียน | `phase` หลังเสร็จ |
|---|---|---|---|---|
| `init` | (ยังไม่มี `state.json`) | `<work>/suite/` | `state.json` · `raw/` `skills/` `history/` · `rollouts/suite/` `rollouts/runs/` · `wiki/index.md` `log.md` `skill-impact.md` `patterns/` | `init` |
| `baseline` | `init` | – | `rollouts/runs/k00-val/` · `state.json` (`baseline` `r_best`) | `gate` |
| `rollout` | `gate` | `skills/` | `rollouts/runs/kNN-train/` · `raw/iter-NN/traces/*.md` `summary.md` · `state.json` (เพิ่ม `k` และรายการใหม่ใน `history`) | `rollout` |
| `maintain` | `rollout` | `raw/iter-NN/traces/` · คะแนนของ Trial · `skills/` · `wiki/` | `history/iter-NN/maintainer_*` · `wiki/patterns/*` `index.md` `log.md` · `state.json` | `maintain` |
| `propose` | `maintain` | `wiki/` · `raw/iter-NN/` · `skills/` | `history/iter-NN/proposer_*` `proposal.json` `proposal.diff` `candidate/skills/` · `state.json` | `propose` |
| `gate` | `propose` | `proposal.json` `proposal.diff` `candidate/skills/` | `rollouts/runs/kNN-val/` · `skills/` (เฉพาะ ACCEPTED) · `wiki/skill-impact.md` · `history/iter-NN/gate.json` `wiki/` `skills/` · `state.json` | `gate` |
| `loop` | ใดก็ได้ | `state.json` | เรียกคำสั่งถัดไปซ้ำจน `phase` = `gate` และ (`R_best` = 100% หรือ `k` ≥ `iters`) แล้วพิมพ์ `status` · `--iters N` ถูกบันทึกลง `cfg.iters` | – |
| `status` | ใดก็ได้ | `state.json` · ชื่อโฟลเดอร์ใน `skills/` | – (พิมพ์อย่างเดียว) | – |

- เรียกผิดลำดับ: พิมพ์ขั้นถัดไป แล้ว exit 1 โดยไม่เรียกโมเดล · `baseline` ที่ทำไปแล้ว และ `rollout` เมื่อ `R_best` = 100% ไม่ทำอะไร แล้ว exit 0
- `--no-wiki`: ไม่มี `wiki/` · `maintain` เปลี่ยน `phase` อย่างเดียว · `proposer_view/` ไม่มี `wiki/` และใช้ `prompts/proposer_nowiki.md` · `gate` ไม่เขียน `skill-impact.md` และไม่มี `history/iter-NN/wiki/`

## ใครเปลี่ยนชั้นไหนได้

| ชั้น | เปลี่ยนโดย | เมื่อไร | ย้อนกลับ |
|---|---|---|---|
| `raw/` | `rollout` | 1 ครั้งต่อรอบ | ไม่มีคำสั่งใดกลับไปแก้ |
| `wiki/patterns/` `index.md` `log.md` | `maintain` | ก่อนรู้ผลของ gate | ไม่ย้อน |
| `wiki/skill-impact.md` | `gate` | ทุกผลตัดสิน (ACCEPTED · REJECTED · NO_ACTION) | ไม่ย้อน |
| `skills/` | `gate` | เฉพาะ ACCEPTED | REJECTED = คงชุดเดิม |

## สิ่งที่โปรแกรมทำกับคำตอบของโมเดล

**Wiki Maintainer** (JSON: `create_patterns` `update_patterns` `update_index` `append_log`)

- ชื่อไฟล์ pattern ผิดรูปแบบ ขาด `update_index` หรือ `append_log` หรือไม่ใช่ JSON object → เรียกใหม่พร้อมสาเหตุ ไม่เกิน 3 ครั้ง แล้ว exit 1 (wiki ไม่ถูกแก้)
- `create_patterns` ที่ชื่อซ้ำกับหน้าเดิม → ต่อท้ายหน้าเดิม และนับเป็นหน้าที่ถูกแก้
- `update_patterns` ที่ไม่มีไฟล์ หรือรายการแก้ที่หา `target` ไม่พบ → ข้ามรายการนั้น และจดใน `edits_skipped`
- `append_log` ถูกต่อท้ายใต้หัวข้อ `## Iteration <k> · Training <คะแนน>` · ถ้าโมเดลเขียนหัวข้อ `## Iteration …` นำมาเอง บรรทัดนั้นถูกตัดออก

**Skill Proposer** (JSON: `create` · `patch` · `no_action`)

- ไม่ใช่ `no_action` แต่เปิด Trace ไม่ถึง 4 ไฟล์ (นับในเซสชันนั้น) หรือ Apply ไม่ได้ → เรียกใหม่พร้อมสาเหตุ ไม่เกิน 3 ครั้ง แล้วถือเป็น `no_action`
- `patch`: รายการแก้ใช้ไม่ได้แม้รายการเดียว หรือ `SKILL.md` ไม่เปลี่ยน = ข้อเสนอใช้ไม่ได้

**รายการแก้** ใช้ร่วมกันทั้ง wiki และสกิล

| `op` | ผล |
|---|---|
| `append` | ต่อท้ายไฟล์ (เว้น 1 บรรทัดใหม่ก่อนเนื้อหา) |
| `replace` | แทน `target` ที่พบครั้งแรกด้วย `content` |
| `insert_after` | แทรก `content` เป็นบรรทัดใหม่ ต่อจากบรรทัดที่ `target` (ครั้งแรกที่พบ) จบ |

## การเรียกโมเดลของ Maintainer และ Proposer

- ใช้บัญชีตัวแรกของ `--accounts` · โฟลเดอร์ของบัญชี = `$WIKISKILL_ACCOUNT_ROOT/<บัญชี>` (ไม่ตั้ง = `~/ai-accounts/.Claude/<บัญชี>`)
- มีโฟลเดอร์ของบัญชี → เรียก `claude --dangerously-skip-permissions --disable-slash-commands -p …` โดยตั้ง `CLAUDE_CONFIG_DIR` · ไม่มี → เรียกคำสั่งของบัญชีแทน (`<บัญชี> -p …`)
- ตัวแปรสภาพแวดล้อมที่ขึ้นต้นด้วย `CLAUDE` และ `MA_` ถูกลบ · ตั้ง `IS_SANDBOX=1` · ข้อความของผู้ใช้ส่งทาง stdin · หมดเวลา 1,800 วินาที
- Maintainer: `--tools ""` · Proposer: `--tools Read` โฟลเดอร์ทำงาน = `proposer_view/`
- คำสั่งของบัญชีที่เป็นไฟล์ `.py` ถูกรันด้วย Python ตัวเดียวกับเครื่องมือ (ใช้กับ Agent จำลองตอนทดสอบโดยไม่เรียกโมเดล)

## ทดสอบโดยไม่เรียกโมเดล

| ทดสอบ | วิธี |
|---|---|
| `status` | รันกับ workspace ที่เก็บไว้ แล้วเทียบกับ `status.txt` ทุกตัวอักษร |
| Apply | เรียก `apply_proposal(<skills ก่อนรอบนั้น>, <proposal.json>, <โฟลเดอร์ชั่วคราว>)` แล้วเทียบกับ `candidate/skills/` และ `proposal.diff` ที่เก็บไว้ |
| วงรอบ | `init --skillopt <skillopt จำลอง> --accounts <agent จำลอง .py>` โดยตั้ง `WIKISKILL_ACCOUNT_ROOT` เป็นโฟลเดอร์ว่าง แล้วสั่ง `loop` |
