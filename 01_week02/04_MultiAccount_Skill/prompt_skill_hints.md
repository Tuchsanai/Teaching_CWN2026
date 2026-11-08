# คำแนะนำสำหรับผู้สร้างสกิล (ข้อเท็จจริงที่วัดแล้ว + กับดัก)

> ใช้คู่กับ [`prompt_skill_spec.md`](prompt_skill_spec.md) ไฟล์นี้บอก **ข้อเท็จจริงที่วัดจากการรันจริง** (container `multi-account`, Claude Code 2.1.319, codex-cli 0.167.0, พ.ย. 2026) เพื่อไม่ต้องลองผิดลองถูกเอง ถ้าเวอร์ชันที่ใช้ให้ผลต่างจากนี้ ให้เชื่อผลตรวจจริงและบันทึกความต่างใน TEST-REPORT

## 1. สภาพแวดล้อมใน container

| เรื่อง | ข้อเท็จจริง |
|---|---|
| wrapper | `/usr/local/bin/yolo1–5` และ `cyolo1–5` (โค้ดร่วมอยู่ใน `/usr/local/lib/multi-account/`) อ่านได้ ไม่ต้องแก้ |
| `yoloN` ตั้งให้เอง | `CLAUDE_CONFIG_DIR=$BASE/.Claude/yoloN`, `IS_SANDBOX=1`, `--dangerously-skip-permissions`, `--mcp-config` จาก `$BASE/.Claude/shared/mcp/mcp.json` |
| `cyoloN` ตั้งให้เอง | `CODEX_HOME=$BASE/.Codex/cyoloN`, `--dangerously-bypass-approvals-and-sandbox`, `-c cli_auth_credentials_store="file"` |
| บัญชีที่ไม่มี wrapper (N > 5) | เรียก `claude` / `codex` ตรงด้วย env และ flag ชุดเดียวกัน |
| Python | 3.12 มีในทุก container ใช้ไลบรารีมาตรฐานพอ ไม่ต้อง pip |
| ไฟล์ที่ห้ามอ่าน | `.credentials.json`, `.claude.json` (Claude) · `auth.json` (Codex) · `auth status --json` มี email/orgId: อ่านแค่ `loggedIn`, `subscriptionType` |
| JupyterLab | สร้าง `.ipynb_checkpoints` ในโฟลเดอร์ที่เปิดดู สคริปต์ต้องไม่สะดุดกับโฟลเดอร์นี้ |

## 2. Claude Code (`yoloN`) — ค่าที่วัดได้

| การวัด | ผล |
|---|---|
| `haiku`/`low` "ตอบ OK" | ~3.3 s · input ~27.7k (ส่วนใหญ่เป็น cache) · output 4 · ~$0.003 ราคาตามรายการ |
| alias → รุ่นจริง (`modelUsage`) | `opus` → `claude-opus-5-5` · `sonnet` → `claude-sonnet-5-5` · `fable` → `claude-fable-5-1` · `haiku` → `claude-haiku-5-5` |
| บัญชีไม่ได้ล็อกอิน เรียกจริง | exit 1 · `is_error: true` · ~45 ms · tokens 0 |
| ล็อกอินแล้วแต่หมดอายุ | `auth status` = `loggedIn: true` แต่เรียกจริงได้ `is_error` + `Failed to authenticate: OAuth session expired and could not be refreshed` (~50 ms, tokens 0) |
| หลายงานพร้อมกันในบัญชีเดียว | 4 งาน/บัญชีพร้อมกันผ่าน เมื่อใส่ `--no-session-persistence` ทุกครั้ง |
| `--bare` | ใช้ไม่ได้ (ไม่อ่าน OAuth) |
| `--disable-slash-commands`, system prompt สั้น, cwd ว่าง | ไม่ทำให้เร็วขึ้น |
| effort | มีผลเฉพาะงานที่ต้องคิดจริง (นับเลข 1–1000 ที่เข้าเงื่อนไข เฉลย 401: `opus/low` ผิด `opus/max` ถูก) โจทย์ง่ายถูกทุกระดับ |
| reasoning tokens | `usage.output_tokens_details.thinking_tokens` (ถ้ามี) |

`/usage` (ส่งเป็น prompt กับ `-p` ไม่เรียกโมเดล ไม่เสียโทเค็น) ให้บรรทัดแบบนี้ เป็น **% ที่ใช้ไปแล้ว** และบางบัญชีไม่มีบรรทัด `Current session`:

```text
Current session: 0% used · resets Nov 8, 11:10am (Asia/Bangkok)
Current week (all models): 2% used · resets Nov 9, 1pm (Asia/Bangkok)
Current week (Fable): 1% used · resets Nov 9, 1pm (Asia/Bangkok)
```

## 3. Codex CLI (`cyoloN`) — ค่าที่วัดได้

| การวัด | ผล |
|---|---|
| `gpt-6.1-sol`/`low` "ตอบ OK" `--ephemeral` | 3–4 s · input 17,780 (cached 12,288) · output 5 |
| `--ephemeral` เทียบไม่ใส่ | ~12 s vs ~42 s ต่องาน (เร็วกว่า ~3.5 เท่า) |
| บัญชีไม่ได้ล็อกอิน | `login status` พิมพ์ `Not logged in` · `exec` retry 401 ราว 15 s แล้ว `turn.failed` exit 1 |
| หลายงานพร้อมกันในบัญชีเดียว | 6 งาน/บัญชีพร้อมกันผ่าน |
| stderr | บรรทัด `Reading additional input from stdin...` เป็นเรื่องปกติ · ห้ามใช้ `-o /dev/stdout` (คำตอบซ้ำ) |
| `input_tokens` ใน `turn.completed.usage` | รวม cached แล้ว |
| ผลแบบมีโครงสร้าง | `--output-schema <ไฟล์>` ต้องเป็น schema แบบ strict: ทุก property อยู่ใน `required` และ `additionalProperties: false` |

stdout ของ `--json` (JSONL):

```json
{"type":"thread.started","thread_id":"…"}
{"type":"turn.started"}
{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}
{"type":"turn.completed","usage":{"input_tokens":17780,"cached_input_tokens":12288,"cache_write_input_tokens":0,"output_tokens":5,"reasoning_output_tokens":0}}
```

เมื่อล้ม: `{"type":"error","message":"Reconnecting... n/5 (…401…)"}` ซ้ำหลายครั้ง แล้ว `{"type":"turn.failed","error":{"message":"…"}}`

**รุ่นและ effort** อยู่ใน `$CODEX_HOME/models_cache.json`: `models[].slug`, `supported_reasoning_levels[].effort`, `default_reasoning_level`, `visibility` (`hide` = ไม่ใช้) ห้ามพิมพ์ส่วน `identity` ตัวอย่างที่พบ: `gpt-6.1-sol` รองรับ low…ultra, `gpt-6-luna` สูงสุด max · `ultra` เป็นโหมดฝั่ง client ห้ามส่งเป็นค่า `reasoning.effort` · effort ที่รุ่นไม่รองรับ CLI อาจ HTTP 400 หรือลดเงียบ ๆ สคริปต์จึงต้องเลือกระดับเองก่อนเรียก

**โควตา** ไม่อยู่ใน stdout แต่อยู่ใน rollout ที่ไม่ใช่ ephemeral: `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl` event ที่ `payload.type == "token_count"`:

```json
{"primary":{"used_percent":1.0,"window_minutes":10080,"resets_at":1794633702},"secondary":null,
 "credits":{"has_credits":true,"balance":"…"},"plan_type":"…","rate_limit_reached_type":null}
```

`used_percent` = % ที่ใช้ไปแล้ว · window อาจเป็น `null` · `credits` แยกจาก subscription · งาน ephemeral ไม่อัปเดตไฟล์นี้ → รีเฟรชด้วยการเรียกสั้น 1 ครั้งแบบไม่ ephemeral (รุ่นถูกสุด `low`) แล้วอ่านใหม่ · รายงาน timestamp ของ event เสมอ

**สร้างภาพ** (Codex เท่านั้น): สั่ง "สร้างภาพ (image generation) … บันทึกเป็น PNG ที่ <absolute path> ตอบ path อย่างเดียว" ไฟล์ต้นฉบับอยู่ที่ `$CODEX_HOME/generated_images/<thread>/` แล้ว agent คัดลอกมา ใช้เวลา ~60–80 s ต่อภาพ · ทดสอบภาพ 8 เงื่อนไขกับ effort low→ultra ได้ครบ 8/8 ทุกระดับ แต่ระดับสูงช้ากว่า ~40% → ใช้ `low` · ภาพออกมาถูกเพราะ prompt แจกแจงทุกเงื่อนไขเป็นข้อ (จำนวน สี ตำแหน่ง ข้อความ) · ถ้าเนื้อหาภาพต้องคำนวณก่อน แยกเป็นงานก่อนหน้า

## 4. ความเร็ว: สิ่งที่วัดแล้ว

| เรื่อง | ผล |
|---|---|
| 12 งานสั้น `--per-account 1` vs `4` | 141 s → 48 s (เร็วขึ้น 2.9 เท่า) ถูก 12/12 |
| งานสั้นมาก | Claude `haiku` ~6 s/งาน · Codex ~12–16 s/งาน |
| ยัดข้อมูลยาวลง prompt / ไม่สั่งให้ใช้เชลล์คำนวณ | ช้ากว่าถึง 4 เท่าและเคยตอบผิด → ส่ง path + สั่งให้ใช้เชลล์ |
| ให้ worker เขียนไฟล์ผลเอง | อ่านยากและพลาดง่าย → อ่านผลจาก `result` / ไฟล์ `-o` แล้วสคริปต์เขียน `out/` เอง (ยกเว้นงานที่ต้องสร้างไฟล์จริง เช่น โค้ด) |
| งานแก้โค้ดพร้อมกัน | แยกโฟลเดอร์ทำงานต่องานเมื่อแก้ไฟล์เดียวกันได้ |
| งานภาพ | มักเป็นคอขวด ให้เริ่มก่อนงานอื่น |

## 5. บทเรียนจากการใช้งานจริงโดย Claude Code app (เป้าหมายการออกแบบ)

สังเกตจาก session ที่ Claude Code app บน host ใช้สกิลแบบนี้ทำงานทีม 4 ขั้น (เขียนขนาน 2 บัญชี → ตรวจ → แก้และทดสอบ → ตาราง + โควตา): ใช้ 16 คำสั่ง ล้ม 4 คำสั่ง 182 วินาที

| สิ่งที่ทำให้ช้าหรือล้ม | สิ่งที่สกิลควรทำ |
|---|---|
| ใช้ 5 คำสั่งแรกหา container ที่ถูก และเปิด `references/` อีก 2 ไฟล์ | `SKILL.md` ตอบงานทั่วไปได้เลย: ชื่อ container, path ของสคริปต์ และกราฟตัวอย่างพร้อมดัดแปลง |
| Git Bash แปลง `/root/...` ใน argument ของ `docker exec` เป็น path Windows | ตัวอย่างฝั่ง host ใช้รูปที่ไม่โดนแปลง เช่นห่อด้วย `sh -c '…'` หรือ `MSYS_NO_PATHCONV=1` และทดสอบจริงจาก Git Bash |
| `expect` แบบ regex เข้มเกินไป งานตรวจตอบถูกแต่ถูกตีว่าล้ม ต้องเขียนกราฟใหม่แล้วรันซ้ำเอง | เก็บคำตอบที่ไม่ผ่านรูปแบบไว้ บอกเหตุผล และมี `--resume` รันเฉพาะงานที่ล้ม · แนะนำ `text` กับคำตอบที่เป็นความเรียง |
| ต้องรันคำสั่งสถิติและโควตาแยก แล้วอ่าน ledger เอง | `run` พิมพ์ตารางสรุป + โควตาตอนจบ |
| haiku/low ตอบ "50 − 8 = 42" แทนค่าล้วน | ตัวตรวจ `int` / `number` รับรูปสมการบรรทัดเดียวที่ลงท้าย `= N` |
| haiku/low คำนวณผิดเมื่อคำสั่งรูปแบบซับซ้อน | คำสั่งรูปแบบสั้นและตรง ตรวจผลด้วยการคำนวณอิสระเสมอ |
| การตรวจความพร้อมถูกนับเป็นงานของลูกทีม จนบัญชีถูกหยุดก่อนเริ่มงาน | ไม่นับการตรวจความพร้อมในงบโทเค็นของลูกทีม |

อีก session หนึ่งให้ Claude Code app สาธิตการสลับหัวหน้าทีม (ตารางสูตรคูณแม่ 2–9 แบ่งให้ลูกทีม, งบหัวหน้าต่ำ, จำลองหัวหน้าล้ม, งบลูกทีมต่ำ): ใช้ 801 วินาที 24 คำสั่ง

| สิ่งที่ทำให้ช้าหรือล้ม | สิ่งที่สกิลควรทำ |
|---|---|
| เอกสารไม่บอกวิธีจำลอง app ต้องเปิดอ่านโค้ด `team.py` หลายร้อยบรรทัด | `SKILL.md` มีคำสั่งสาธิตพร้อมใช้ และ flag จำลองอยู่ใน `--help` |
| หัวหน้าทำงานทั้งหมดจบในรอบเดียว ผู้ควบคุมตรวจงบหลังจบรอบเท่านั้น จึงไม่เกิดการสลับเชิงรุก ต้องรันใหม่รอบที่ 2 | ตรวจงบหัวหน้าระหว่างรอบ (หลัง dispatch / checkpoint) หรือจำกัดงานต่อรอบ |
| ตรวจงบลูกทีมก่อนแจกงานเท่านั้น งานแรกจึงใช้เกินงบเสมอ | ตรวจทันทีที่งานจบ และบอกในเอกสารว่างานที่กำลังรันจะทำจนจบ |
| app รัน `lead` เป็นงานเบื้องหลังแล้วนั่งรอ (เวลาส่วนใหญ่หายไปกับการรอ) | `lead` จบเร็ว รัน foreground ได้ พิมพ์ความคืบหน้า และจบด้วยตารางสรุปที่ตอบคำถามผู้ใช้ได้เลย |

### รอบล่าสุด: สกิลที่สร้างจากสเปกนี้ ถูกใช้จริงโดย Claude Code app ตัวใหม่

| สิ่งที่ยังทำให้ช้าหรือล้ม | สิ่งที่สกิลควรทำ |
|---|---|
| `team.py check` คืน exit code 2 เมื่อบางบัญชีไม่ได้ล็อกอิน app จึงนับว่าคำสั่งล้ม | คืน 0 เมื่อคำสั่งทำงานสำเร็จ ให้ตารางบอกสถานะแทน |
| `team.py status` ก่อนมี run ใด ๆ ได้ Traceback | พิมพ์ "ยังไม่มี run" |
| app เขียนกราฟด้วย heredoc (`cat > g.json <<'EOF' {…}`) ถูกตัวตรวจสิทธิ์บล็อก ("brace with quote") เสีย 1–2 คำสั่งทุกครั้ง | `SKILL.md` บอกวิธีที่ผ่านแน่: เขียนไฟล์บน host ด้วย Write แล้ว `docker exec -i multi-account sh -c "python3 …/team.py run -" < ไฟล์` |
| งานสาธิตหัวหน้าทีมกับเป้าหมายของผู้ใช้เอง: `--demo` ใช้ได้แค่งานตัวอย่าง app จึง grep/sed โค้ด `team.py` 3 คำสั่งเพื่อหาว่าตั้งงบเท่าไร | ตัวจำลองทั้งชุดใช้กับ `--goal` ใดก็ได้ และ `SKILL.md` บอกค่าที่ทำให้เกิดครบทั้ง 3 เหตุการณ์ |
| `SKILL.md` ของ agent-team ยาว ~18 KB app อ่านนานขึ้นทุกครั้ง | สั้นลง (~10 KB) เก็บรายละเอียดใน `references/` |

## 6. งานที่จะใช้วัดสกิล

หลังสร้างเสร็จ สกิลจะถูกวัดโดย Claude Code app ตัวใหม่บน host ด้วยงานทีมจริงหลายแบบ (ทั้งงานในตัวอย่างและงานที่ไม่เคยเห็น) วัดจาก: ผลถูกต้อง · จำนวนคำสั่งของ app และคำสั่งที่ล้ม · เวลารวม · ไม่แตะ credential · ตัวเลขในสรุปมาจาก ledger จริง
