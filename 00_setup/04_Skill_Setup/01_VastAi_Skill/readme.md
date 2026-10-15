# LAB 04.1 · เช่า GPU บน Vast.ai ด้วย skill `vastai` (ก๊อปวางทีละขั้น)

LAB นี้ให้ AI (`yolo1`) **เช่า GPU จริงบน Vast.ai ให้เรา** ด้วย skill `vastai` แค่พิมพ์ภาษาไทย
แบบฝึกหัด 1 เช่า RTX 4090 → ssh เข้าไปดู GPU → ลบเครื่อง · แบบฝึกหัด 2 ทำแชทบอทร้านนวดแผนไทยที่ใช้ AI บน RTX 5090

**ต้องมีก่อน:**
- [LAB 03](../../03_MultiAccount_Container/README.md) — container `multi-account-devtool` ใช้งานได้ และล็อกอิน `yolo1` แล้ว
- [LAB 04](../00_Setup_Skill/readme.md) — ติดตั้ง skill `vastai` `yolo` `cyolo` ใน `shared` แล้ว
- บัญชี [Vast.ai](https://cloud.vast.ai/) ที่เติมเครดิตแล้ว (แนะนำ $5–10 พอสำหรับทั้ง LAB)
- Docker Desktop (Engine running) และ Git Bash บน Windows

**เวลา:** แบบฝึกหัด 1 ~45 นาที · แบบฝึกหัด 2 ~60 นาที
**ค่าใช้จ่ายจริง (ทดสอบ 14 ต.ค. 2026):** แบบฝึกหัด 1 ≈ $0.22 · แบบฝึกหัด 2 ≈ $0.91/ชม. × เวลาที่เปิดเครื่อง

> ⚠️ **เสียเงินจริง** — ทุกครั้งที่ทดลองเสร็จ ต้องสั่ง **ลบเครื่อง (destroy)** แล้วเช็คหน้าเว็บ Instances ว่าว่าง

### หลักการ: ตัวแปร 2 ตัวใน `.env`

![ภาพรวม 4 ขั้น: 1 เว็บ cloud.vast.ai ให้ API Key (คัดลอกค่า) และ SSH Key (ใส่ .pub บนเว็บ), 2 ไฟล์ .env มี 2 บรรทัด VAST_API_KEY และ VAST_SSH_KEY_FILE=Devtool_SSH/devtoolSSH, 3 docker run --env-file .env โหลดเป็นตัวแปร environment ใน container multi-account-devtool ให้ yolo1 และ skill vastai อ่าน, 4 skill ใช้ API Key สั่งเช่า/ลบเครื่อง และใช้ SSH Key ssh เข้าเครื่อง RTX 4090 บน Vast.ai](image/vast-flow-env.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): **สีส้ม = API Key** · **สีฟ้า = SSH Key** ตามเส้นสีจากซ้ายไปขวาได้เลย*

| ตัวแปรใน `.env` | ได้มาจากไหน | skill `vastai` เอาไปทำอะไร |
|---|---|---|
| 🟠 `VAST_API_KEY` | เว็บ Vast.ai → Keys → **API Keys** → + New → คัดลอก (ขั้นที่ 3) | ยืนยันตัวตนกับบัญชีเรา เพื่อ**สั่งเช่า / ลบเครื่อง / ดูบิล** (ตัดเงินจากเครดิต) |
| 🔵 `VAST_SSH_KEY_FILE` | path ของ **private key** ใน repo = `Devtool_SSH/devtoolSSH` (ส่วน `.pub` เอาไปใส่บนเว็บในขั้นที่ 2) | ใช้ **ssh / scp เข้าเครื่อง**ที่เช่ามา |

ลำดับการทำงาน: ใส่ค่าใน `.env` → `docker run --env-file .env` **โหลดค่าเป็นตัวแปร environment** ใน container `multi-account-devtool` → `yolo1` ที่มี skill `vastai` อ่านตัวแปร 2 ตัวนี้ไปเช่าเครื่องให้เรา

สัญลักษณ์: 🖥️ = พิมพ์ใน shell (กรอบ `bash`) · 💬 = วางในช่องแชทของ AI (กรอบ `text` ให้คัดลอกทั้งกรอบ)

---

## ส่วนที่ 1 · ตั้งค่าบนเว็บ Vast.ai (~10 นาที)

![เตรียมบัญชี Vast.ai 4 ขั้น: 1 สมัครบัญชีที่ cloud.vast.ai, 2 Billing เติมเครดิต $5–10 ทำเองห้ามให้ AI กรอกบัตร, 3 Keys → SSH Keys → + New วาง .pub, 4 Keys → API Keys → + New คัดลอกทันทีเพราะเห็นครั้งเดียว ได้กุญแจ 2 ดอกไปใส่ในไฟล์ .env](image/vast-signup-steps.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): 4 ขั้นในส่วนนี้ ภาพจริงของแต่ละขั้นมี**วงกลมสีแดงพร้อมเลขลำดับ** บอกว่าต้องกดตรงไหน*

### ขั้นที่ 1 · สมัครและเติมเครดิต

1. สมัครที่ https://cloud.vast.ai/ (มุมขวาบน **Sign Up** · ยืนยันอีเมล)
2. เมนูซ้าย **Billing** → กด **Add Credit** → เติม $5–10 — **ทำเองเท่านั้น ห้ามให้ AI กรอกข้อมูลบัตร**

![หน้า Billing: วงกลม 1 ที่เมนู Billing ด้านซ้าย, วงกลม 2 ที่ปุ่ม Add Credit ในการ์ด Credit Balance ยอดเงินและข้อมูลบัตรถูกเบลอ](image/vast-02-billing.png)
*ภาพจริง: ยอดเครดิต ข้อมูลบัตร และอีเมลถูกเบลอไว้*

### ขั้นที่ 2 · ใส่ SSH Key (public key)

1. 🖥️ เปิด Git Bash ที่โฟลเดอร์ repo (`Teaching` หรือ `Teaching_CWN2026`) แล้วแสดง **public key** (`.pub` แชร์ได้ ไม่ใช่ความลับ):

   ```bash
   cat Devtool_SSH/devtoolSSH.pub
   ```

   คัดลอกทั้งบรรทัดที่ขึ้นต้นด้วย `ssh-ed25519 AAAA…` (ไฟล์เดียวกันมีสำเนาใน `01_VastAi_Skill/Devtool_SSH/` ด้วย)
2. เปิด https://cloud.vast.ai/manage-keys/ → ทำตามเลข **①–⑤** ในภาพ

![หน้า Manage Keys: วงกลม 1 เมนู Keys ด้านซ้าย, วงกลม 2 แท็บ SSH Keys, วงกลม 3 ปุ่ม + New มุมขวา](image/vast-03-keys-ssh-before.png)
*ภาพจริง: ① เมนู **Keys** → ② แท็บ **SSH Keys** → ③ **+ New** · key ที่ใส่ที่นี่จะถูกใส่ให้เครื่องที่เช่าใหม่ทุกเครื่องอัตโนมัติ*

![หน้าต่าง Add SSH Key: วงกลม 4 ช่องวาง public key จากคำสั่ง cat Devtool_SSH/devtoolSSH.pub, วงกลม 5 ปุ่ม Save](image/vast-04-keys-ssh-add.png)
*ภาพจริง: ④ วางบรรทัด `ssh-ed25519 AAAA…` ที่คัดลอกมา → ⑤ **Save** · key ใหม่ไม่ถูกใส่ให้เครื่องที่เช่าไว้ก่อนแล้ว*

![หลัง Save ตาราง SSH Keys มีแถวใหม่ ssh-ed25519 ... devtools-lab วงกลมสีเขียว](image/vast-05-keys-ssh-after.png)
*ภาพจริง: ✔ มีแถว `… devtools-lab` = ใส่ SSH Key สำเร็จ*

### ขั้นที่ 3 · สร้าง API Key

ทำตามเลข **①–⑧** ในภาพ 3 ภาพนี้

![แท็บ API Keys: วงกลม 1 เมนู Keys, วงกลม 2 แท็บ API Keys, วงกลม 3 ปุ่ม + New](image/vast-06-keys-api-tab.png)
*ภาพจริง: ① เมนู **Keys** → ② แท็บ **API Keys** → ③ **+ New***

![หน้าต่าง Create API Key: วงกลม 4 ช่อง Name ใส่ devtools-lab, วงกลม 5 ช่อง Billing/Earning Write ที่ต้องเอาติ๊กออก, วงกลม 6 ปุ่ม Save](image/vast-07-keys-api-create.png)
*ภาพจริง: ④ ชื่อ `devtools-lab` → ⑤ **เอาติ๊กออกที่ Billing/Earning → Write** (ช่องอื่นติ๊กไว้ตามเดิม) → ⑥ **Save** · AI เช่า/ลบเครื่องและดูบิลได้ แต่แก้การเงินในบัญชีไม่ได้*

![หน้าต่าง API key created successfully: วงกลม 7 ปุ่มคัดลอก key, วงกลม 8 ปุ่ม Close หลังวาง key ลง .env](image/vast-08-keys-api-created.png)
*ภาพจริง: ⑦ กดคัดลอก 📋 **ทันที** (เห็นได้ครั้งเดียว ปิดแล้วดูอีกไม่ได้ ต้องสร้างใหม่) → ⑧ วางลง `.env` ในส่วนที่ 2 แล้วค่อยกด **Close** · key ในภาพถูกเบลอไว้ อย่าแคปหน้าจอนี้ให้คนอื่นเห็น*

---

## ส่วนที่ 2 · ใส่ค่าในไฟล์ `.env` (~3 นาที)

🖥️ Git Bash ที่โฟลเดอร์ repo:

```bash
cp .env_example .env
notepad .env
```

แก้ 3 บรรทัดของ vastai ให้เป็นแบบนี้ (แทน `<key>` ด้วย API key ที่คัดลอกมา) แล้วกด Save:

```text
VAST_API_KEY=<key>
VAST_SSH_KEY_FILE=Devtool_SSH/devtoolSSH
VAST_HTTP_TIMEOUT=20
```

ตัวหลักคือ 🟠 `VAST_API_KEY` กับ 🔵 `VAST_SSH_KEY_FILE` (ดูตารางในหัวข้อ "หลักการ" ด้านบน) · `VAST_HTTP_TIMEOUT` = รอ API ของ Vast ได้นานสุดกี่วินาที ใช้ค่านี้ได้เลย

> ⚠️ **3 กับดักที่เจอจริง**
> 1. **ห้ามใส่เครื่องหมายคำพูด** `"..."` ครอบ key — `docker --env-file` เก็บ `"` ไว้เป็นส่วนหนึ่งของค่า → skill ฟ้อง `Invalid user key`
> 2. **ห้ามเขียน `# comment` ต่อท้ายบรรทัดค่า** — เหตุผลเดียวกัน comment จะกลายเป็นส่วนหนึ่งของค่า (เขียน comment ไว้บรรทัดของมันเองได้)
> 3. **ห้ามเปิด `.env` ใน JupyterLab** — JupyterLab จะสร้าง `.ipynb_checkpoints/.env-checkpoint` ซึ่งเป็น**สำเนาความลับ**ของเรา แก้ด้วย Notepad บน Windows เท่านั้น

`VAST_SSH_KEY_FILE` เป็น path สัมพัทธ์ = อิงโฟลเดอร์ที่มี `.env` (ใน container คือ `/workspace/Devtool_SSH/devtoolSSH`) · `.env` ถูก ignore ใน `.gitignore` แล้ว ไม่ถูก commit

---

## ส่วนที่ 3 · เปิด container ให้เห็นโฟลเดอร์ repo ที่ `/workspace` (~5 นาที)

คำสั่ง `docker run` ในขั้นนี้ทำ 2 อย่าง:
- `--env-file .env` → **โหลด `VAST_API_KEY` และ `VAST_SSH_KEY_FILE` เป็นตัวแปร environment** ของ container (ขั้นที่ 3 ในภาพหลักการ)
- `-v <REPO>:/workspace` → โฟลเดอร์ repo บน Windows กับ `/workspace` ใน container คือ**โฟลเดอร์เดียวกัน** — skill จึงหาไฟล์ `Devtool_SSH/devtoolSSH` เจอ

### ขั้นที่ 4 · สร้าง container ใหม่ (ไม่หายล็อกอิน)

💬 เปิด **Claude Code บน Windows ที่โฟลเดอร์ repo** (`Teaching`) → วางพรอมต์นี้ → อนุญาตคำสั่ง `docker` เมื่อถูกถาม

```text
เตรียม container `multi-account-devtool` ให้เห็นโฟลเดอร์ปัจจุบันที่ /workspace:

1. ถ้ามี container `multi-account-devtool` อยู่แล้ว ให้ลบด้วย `docker rm -f multi-account-devtool`
   (ห้ามลบ volume `ai-accounts` เด็ดขาด เพราะเก็บการล็อกอินและ skill ของทุกบัญชี)
2. ตรวจ port <SSH_PORT>=2223 และ <JUPYTER_PORT>=8886 ถ้าชน ให้ใช้ port ว่างถัดไป
3. ต้องมีไฟล์ `.env` ในโฟลเดอร์ปัจจุบัน ถ้าไม่มีให้หยุดและบอกฉัน (ห้ามแสดงค่าในไฟล์ แสดงได้เฉพาะชื่อตัวแปร)
4. รัน (แทน <ENV_FILE> ด้วย path เต็มของ .env และ <REPO> ด้วย path เต็มของโฟลเดอร์ปัจจุบัน):

docker run -dit --name multi-account-devtool --hostname multi-account-devtool --privileged \
  -p <SSH_PORT>:22 -p <JUPYTER_PORT>:8888 \
  --env-file "<ENV_FILE>" \
  -v ai-accounts:/root/ai-accounts \
  -v "<REPO>":/workspace \
  tuchsanai/multi-account-devtool:2569_1

5. รอจน `docker logs multi-account-devtool` มีบรรทัดที่มีข้อความ `jupyter lab :8888`
6. ตรวจ skill:
docker exec multi-account-devtool bash -lc 'B=$HOME/ai-accounts; for t in .Claude .Codex; do for s in vastai yolo cyolo; do [ -d $B/$t/shared/skills/$s ] && echo "$t/$s OK" || echo "$t/$s MISSING"; done; done'
   ถ้ามี MISSING ให้เตือนฉันว่า "⚠️ ยังไม่ได้ติดตั้ง skill: <รายชื่อ>" ห้ามติดตั้ง skill เอง
7. ตรวจว่า `docker exec multi-account-devtool ls /workspace` เห็นไฟล์ .env และโฟลเดอร์ Devtool_SSH
8. ตรวจว่าตัวแปรถูกโหลดเข้า container (แสดงแค่ OK/MISSING ไม่แสดงค่า):
docker exec multi-account-devtool bash -lc 'for v in VAST_API_KEY VAST_SSH_KEY_FILE; do [ -n "${!v}" ] && echo "$v OK" || echo "$v MISSING"; done'
9. ห้ามล็อกอินแทนฉัน ห้ามพิมพ์ค่าใน .env สรุปเป็นภาษาไทย: คำเตือน (ถ้ามี) ไว้บนสุด, port ที่ใช้,
   URL http://localhost:<JUPYTER_PORT>/lab/tree/workspace, ผลตรวจ skill 6 บรรทัด, ผลตรวจ /workspace, ผลตรวจตัวแปร 2 บรรทัด
```

<details>
<summary>คำสั่ง <code>docker run</code> แบบพิมพ์เอง (อ้างอิง — ใช้แทนพรอมต์ได้)</summary>

🖥️ Git Bash ที่โฟลเดอร์ repo (`$(pwd -W)` = path เต็มของโฟลเดอร์ปัจจุบันแบบ Windows):

```bash
docker rm -f multi-account-devtool
docker run -dit --name multi-account-devtool --hostname multi-account-devtool --privileged \
  -p 2223:22 -p 8886:8888 \
  --env-file "$(pwd -W)/.env" \
  -v ai-accounts:/root/ai-accounts \
  -v "$(pwd -W)":/workspace \
  tuchsanai/multi-account-devtool:2569_1
```

</details>

**ผลที่ควรได้:** skill `OK` ครบ 6 บรรทัด · `/workspace` เห็น `.env` กับ `Devtool_SSH` · `VAST_API_KEY OK` และ `VAST_SSH_KEY_FILE OK`

### ขั้นที่ 5 · เปิด Terminal ใน JupyterLab แล้วติดตั้ง vastai SDK

1. เปิด **http://localhost:8886/lab/tree/workspace** (ใช้ port อื่น? เปลี่ยน `8886`)
2. แถบไฟล์ซ้ายต้องเขียน `/ workspace /` → ในแท็บ **Launcher** กด **Terminal**

![JupyterLab: วงกลม 1 แถบไฟล์เขียน / workspace /, วงกลม ! ไฟล์ .env ห้ามดับเบิลคลิก, วงกลม 2 ปุ่ม Terminal ในหมวด Other](image/vast-10-jupyter-workspace.png)
*ภาพจริง: ① ต้องเห็น `/ workspace /` (= โฟลเดอร์ repo บน Windows) → ② กด **Terminal** · ❗ ห้ามดับเบิลคลิก `.env`*

3. 🖥️ ใน Terminal (ทำครั้งเดียวต่อ container ใหม่ — **ใช้เวลา ~5–12 นาที** เพราะดาวน์โหลดจาก PyPI ช้า รอจนขึ้น prompt ใหม่):

   ```bash
   pip install 'vastai~=1.8'
   ```

---

## แบบฝึกหัด 1 · เช่า RTX 4090 → ssh → ลบเครื่อง (~30 นาที · ≈ $0.22)

![นักศึกษาพิมพ์ yolo1 บอกช่วยเช่า RTX 4090 หน่อย หุ่นยนต์ skill vastai ถือกุญแจไปที่ Vast.ai การ์ด RTX 4090 running เชื่อมด้วย ssh แมวถือป้ายเสร็จแล้วลบเครื่อง](image/cartoon-ex1-overview.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): สั่งเช่าด้วยภาษาไทย → ssh เข้าไปใช้ → เสร็จแล้วลบเครื่อง*

![วงจรชีวิต instance: rent และ loading เริ่มคิดเงิน, running คิด GPU + disk, stopped คิด disk อย่างเดียว, destroy หยุดจ่าย ทดลองเสร็จต้อง destroy ทุกครั้ง](image/vast-concept-lifecycle.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): **stop ≠ destroy** — stopped ยังเสียค่า disk · destroy เท่านั้นที่หยุดจ่ายทั้งหมด*

### ขั้นที่ 6 · ตรวจความพร้อม

🖥️ ใน Terminal ที่ `/workspace` พิมพ์ `yolo1` แล้ว 💬 วาง:

```text
ใช้ skill vastai ตรวจความพร้อมก่อนเช่า (env, keys, เครดิต) ตอบเป็นตารางสั้น ๆ
```

![yolo1 ตอบตารางความพร้อม: VAST_API_KEY โหลดจาก environment, SSH private key Devtool_SSH/devtoolSSH อ่านได้, ผูกคีย์กับบัญชี registered true, เครดิต (เบลอ), เครื่องที่เปิดค้าง 0, เพดานราคา $0.25/ชม.](image/vast-11-yolo1-check.png)
*ภาพจริง: ✅ ครบทุกข้อสำคัญ — API key, SSH key อ่านได้, key ผูกกับบัญชีแล้ว, เครดิตพอ, ไม่มีเครื่องค้าง · ⚠️ `VAST_LABEL_PREFIX` และ `chmod 600` เป็นคำแนะนำเสริม ข้ามได้*

### ขั้นที่ 7 · สั่งเช่า RTX 4090

💬 วาง:

```text
ใช้ skill vastai เช่า RTX 4090 1 เครื่อง ตั้งชื่อ lab-4090 แล้วบอกคำสั่ง ssh เข้าเครื่อง
```

skill จะ**ถามขอขึ้นเพดานราคา** เพราะเพดานเริ่มต้น (`VAST_MAX_DPH` $0.20–0.25/ชม.) ถูกกว่าราคา 4090 ในตลาด (~$0.37–0.70/ชม.) → เลือกข้อ **(Recommended)** แล้วกด Enter

![skill หา offer RTX 4090 ไม่ได้ในเพดาน $0.45 แล้วขึ้นคำถามเพดานราคา: 1 เช่าที่ ≤ $0.70/ชม. (Recommended), 2 ยังไม่เช่า, 3 เปลี่ยน GPU](image/vast-12-yolo1-price-ask.png)
*ภาพจริง: skill ไม่ขึ้นราคาเอง ต้องถามเราก่อนเสมอ — เลือก 1 (Recommended)*

ระหว่างรอ (รวม ~15 นาที) อาจเห็น: offer แรกหายไป (`no_such_ask`) แล้ว skill ลองตัวใหม่เอง · เครื่องที่ไม่พร้อมถูกลบแล้วเช่าใหม่ให้อัตโนมัติ — **ปกติ ไม่ต้องทำอะไร**

![yolo1 สรุป: RTX 4090 24 GB, ราคา $0.696/ชม. (GPU $0.667 + storage $0.030), California US, คำสั่ง SSH แบบ direct และ proxy ที่ใช้ -i /workspace/Devtool_SSH/devtoolSSH](image/vast-15-yolo1-rented.png)
*ภาพจริง: ได้ราคา/ที่ตั้ง และ**คำสั่ง ssh 2 แบบ** (direct เร็วกว่า · proxy ใช้ตอน direct หลุด) — IP/port เบลอไว้*

### ขั้นที่ 8 · ดูเครื่องบนหน้าเว็บ

เปิด https://cloud.vast.ai/instances/ → เห็นแท็บ `lab-4090`, ป้าย **lab-4090**, ราคา `$/hr` และสถานะ running

![หน้า Instances: 1x RTX 4090 ราคา $0.697/hr วงกลมเขียวที่ป้าย lab-4090 และวงกลม 1 ที่ปุ่ม >_Connect](image/vast-13-console-instance.png)
*ภาพจริง: ✔ ป้าย `lab-4090` = เครื่องที่ AI เช่าให้ (`$0.697/hr`, `Status: success, running`) → ① กด **>_Connect***

กดปุ่ม **>_Connect** → เห็นคำสั่ง ssh แบบเดียวกับที่ `yolo1` บอก

![หน้าต่าง Terminal Connections มี Direct SSH Connect และ Proxy SSH Connect ขึ้นต้นด้วย ssh -p](image/vast-14-console-connect.png)
*ภาพจริง: คำสั่ง ssh จากเว็บ (เบลอไว้) — ใช้ของ `yolo1` สะดวกกว่าเพราะใส่ `-i` key ให้แล้ว*

### ขั้นที่ 9 · ssh เข้าไปดู GPU

1. ใน JupyterLab กด **+** → **Terminal** (เปิด Terminal ที่ 2 · ปล่อย `yolo1` ไว้ใน Terminal แรก)
2. 🖥️ คัดลอกคำสั่ง **direct** ที่ `yolo1` พิมพ์ (`ssh -i /workspace/Devtool_SSH/devtoolSSH …`) แล้ว**เติม ` nvidia-smi` ต่อท้าย** → Enter
3. ถ้าถาม `Are you sure you want to continue connecting?` ให้พิมพ์ `yes` (ถามครั้งแรกครั้งเดียว)

**หน้าตาคำสั่งเต็ม** (ตัวอย่าง — **IP และ port ของคุณจะไม่เหมือนนี้** ให้ใช้ค่าที่ `yolo1` บอก):

```bash
# direct (เร็วกว่า) — ต่อตรงไปที่ IP ของเครื่อง
ssh -i /workspace/Devtool_SSH/devtoolSSH -p 41234 root@203.0.113.25 -o StrictHostKeyChecking=accept-new nvidia-smi

# proxy (ใช้ตอน direct ต่อไม่ได้) — ผ่านเซิร์ฟเวอร์กลางของ Vast
ssh -i /workspace/Devtool_SSH/devtoolSSH -p 13478 root@ssh5.vast.ai -o StrictHostKeyChecking=accept-new nvidia-smi
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| `-i /workspace/Devtool_SSH/devtoolSSH` | 🔵 private key = ค่าจาก `VAST_SSH_KEY_FILE` (คู่กับ `.pub` ที่ใส่บนเว็บในขั้นที่ 2) |
| `-p 41234` | port ของเครื่องที่เช่า (Vast สุ่มให้ — ทุกเครื่องไม่เหมือนกัน) |
| `root@203.0.113.25` | ล็อกอินเป็น `root` ที่ IP ของเครื่อง (proxy ใช้ `sshN.vast.ai` แทน) |
| `-o StrictHostKeyChecking=accept-new` | ยอมรับเครื่องใหม่อัตโนมัติ ไม่ต้องพิมพ์ `yes` |
| `nvidia-smi` | คำสั่งที่จะรัน**บนเครื่องที่เช่า** แล้วออกทันที (ไม่ใส่ = เข้าไปค้างใน shell ของเครื่องนั้น พิมพ์ `exit` เพื่อออก) |

**ผลที่ควรได้** (ผลจริงจากเครื่อง RTX 4090 วันที่ 14 ต.ค. 2026 · IP/port ในบรรทัดแรกเปลี่ยนเป็นค่าตัวอย่าง):

```text
Warning: Permanently added '[203.0.113.25]:41234' (ED25519) to the list of known hosts.
Welcome to vast.ai. If authentication fails, try again after a few seconds, and double check your ssh key.
Have fun!
Wed Oct 14 14:38:31 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.173.02             Driver Version: 580.173.02     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4090        On  |   00000000:E1:00.0 Off |                  Off |
| 30%   38C    P8             12W /  450W |       4MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

![Terminal ที่ 2 รัน ssh -i /workspace/Devtool_SSH/devtoolSSH ... nvidia-smi แสดง NVIDIA GeForce RTX 4090 หน่วยความจำ 4MiB / 24564MiB CUDA 13.0](image/vast-16-ssh-nvidia-smi.png)
*ภาพจริง: `NVIDIA GeForce RTX 4090 … 24564MiB` = เราใช้ GPU บนเครื่องที่เช่ามาได้จริง (IP/port ในภาพเบลอไว้)*

> `Connection refused` ตอนเพิ่งเช่าเสร็จ = เครื่องยังบูตไม่เสร็จ รอ 1–2 นาทีแล้วลองใหม่ หรือใช้คำสั่ง proxy

### ขั้นที่ 10 · ลบเครื่องและสรุปค่าใช้จ่าย (ห้ามข้าม!)

💬 กลับไป Terminal แรก (`yolo1`) วาง:

```text
ใช้ skill vastai ลบเครื่อง lab-4090 แล้วสรุปค่าใช้จ่าย
```

![yolo1 destroy เครื่อง lab-4090 แล้วตรวจว่าหายจากบัญชีจริง ตารางค่าใช้จ่าย ชม. GPU 0.321, GPU $0.214, storage $0.010, download $0.000, รวม $0.224 เวลาประมาณ 20 นาที](image/vast-17-yolo1-destroy-bill.png)
*ภาพจริง: ลบแล้วและยืนยันว่า "หายจาก show_instances() แล้ว" · **ค่าใช้จ่ายจริง $0.224 สำหรับ ~20 นาที** (GPU $0.214 + storage $0.010) · ยอดอาจอัปเดตช้า ~10 นาที*

เปิดหน้าเว็บ Instances อีกครั้ง → ต้อง**ไม่มี** `lab-4090` แล้ว

---

## แบบฝึกหัด 2 · แชทบอทร้าน "สบายใจ นวดแผนไทย" (~60 นาที)

![ลูกค้าถามราคานวดไทยเท่าไหร่ ผ่านแชทบนแล็ปท็อป ส่งคำถามไปยัง Qwen บน RTX 5090 ใน Vast.ai แล้วได้คำตอบกลับ ฝั่งเครื่องเรามี Next.js และ PostgreSQL บน Docker หุ่นยนต์ Playwright ทดสอบและได้ GIF](image/cartoon-ex2-overview.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): หน้าเว็บ + ฐานข้อมูลอยู่บนเครื่องเรา · สมอง AI อยู่บน GPU ที่เช่า*

| ส่วน | อยู่ที่ไหน | ทำอะไร |
|---|---|---|
| **frontend** | Docker บน Windows · http://localhost:3300 | หน้าแชท Next.js + PostgreSQL เก็บการจองคิว |
| **backend** | Vast.ai RTX 5090 · พอร์ต 8080 | [NInfer](https://github.com/Neroued/ninfer) รันโมเดล Qwen (เลือกได้ 5 ตัว ดูตารางด้านล่าง) เป็น API แบบ OpenAI พร้อม API key |

> ทำไม RTX 5090: NInfer รองรับเฉพาะ RTX 5090 (CUDA 13.1) · ต้องการเน็ต > 2500 Mbps เพื่อโหลดโมเดล 22 GB ให้เร็ว
> อยากลองโดยไม่เสียเงิน: ข้ามไป 4.2 แล้วใช้ **โหมด mock** (ไม่ต้องใช้ GPU)

### 4.0 · รู้จักโมเดลก่อนใช้ (~10 นาที อ่านอย่างเดียว)

ก่อนสั่ง AI เช่าเครื่อง มาดูก่อนว่า "สมอง" ของแชทบอทคืออะไร มีให้เลือกกี่ตัว ต่างกันอย่างไร และถ้าอยากเปลี่ยนต้องแก้ตรงไหน

#### ① ไฟล์ `.ninfer` คืออะไร

![ไฟล์ .ninfer คืออะไร: Qwen ต้นฉบับ BF16 27B พารามิเตอร์ × 16 bit ≈ 54 GB ใหญ่เกิน GPU 32 GB → บีบอัดเหลือ ~4 bit → กระเป๋า .ninfer ไฟล์เดียว 16–22 GB มี config, น้ำหนักโมเดล, MTP, Vision, chat template → NInfer (C++/CUDA) บน RTX 5090 32 GB → API แบบ OpenAI :8080 → หน้าแชท](image/ex2-model-ninfer.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo)*

- **Qwen** คือโมเดลภาษาของ Alibaba ที่เปิดให้ดาวน์โหลดฟรี ตัวที่ใช้มี **27 พันล้านพารามิเตอร์ (27B)** ไฟล์ต้นฉบับ (BF16, 16 bit ต่อค่า) ใหญ่ ~54 GB **ใส่ GPU 32 GB ไม่ได้**
- จึงต้อง**บีบอัด (quantize)** ให้แต่ละค่าเหลือ ~4 bit แล้วแพ็กทุกอย่างที่ต้องใช้ไว้ใน**ไฟล์เดียว** = ไฟล์ `.ninfer` (16–22 GB)
- **NInfer** คือโปรแกรมรันโมเดล (C++/CUDA) ที่เขียนมาให้เร็วที่สุด**เฉพาะ RTX 5090** อ่านไฟล์ `.ninfer` แล้วเปิดเป็น API แบบเดียวกับ OpenAI ที่พอร์ต 8080 → หน้าแชทของเราเรียกใช้ได้เลย
- ไฟล์ `.ninfer` ใช้ได้กับ NInfer เท่านั้น (เปิดด้วย Ollama / vLLM ไม่ได้) · ผู้แปลงไฟล์คือ [Hugging Face `neroued`](https://huggingface.co/neroued) มี Qwen ให้เลือก **5 ไฟล์**

#### ② ข้างในโมเดล 27B มีอะไร

![ข้างใน Qwen 27B Dense 64 ชั้น: คำถาม → token → Embedding คำศัพท์ 248k → ×16 รอบ ของ Gated DeltaNet 3 ชั้น + Full Attention 1 ชั้น (แต่ละชั้นมี FFN) → Output head → คำถัดไป · MTP head เดาล่วงหน้า 3 คำ ตอบเร็วขึ้น ~2–3 เท่า · Vision encoder ไม่ได้ใช้ใน LAB](image/ex2-model-arch.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo) · ตัวเลขจาก `config.json` ของ Qwen*

โมเดลตอบทีละ **token** (คำหรือส่วนของคำ): ข้อความผ่าน 64 ชั้นแล้วได้ token ถัดไป 1 ตัว วนซ้ำจนจบคำตอบ

| ส่วน | ทำอะไร |
|---|---|
| **Embedding** | แปลง token (คำศัพท์ 248,320 คำ รองรับภาษาไทย) เป็นตัวเลข |
| **Gated DeltaNet** 48 ชั้น | attention แบบ "จำย่อ" เก็บความจำขนาดคงที่ → เร็วและไม่กิน VRAM แม้บทสนทนายาว |
| **Full Attention** 16 ชั้น | มองย้อนทุกคำก่อนหน้า → แม่นยำ แต่ต้องเก็บ **KV cache** (ยิ่งคุยยาวยิ่งใช้ VRAM) · วางสลับ 3:1 กับ DeltaNet |
| **FFN** ทุกชั้น | ส่วน "ความรู้" ของโมเดล = น้ำหนักส่วนใหญ่ของไฟล์ |
| **MTP head** | เดาล่วงหน้า 3 token แล้วตรวจทีเดียว (`--spec mtp --draft-tokens 3`) → ตอบเร็วขึ้น ~2–3 เท่า |
| **Vision** | อ่านภาพ/วิดีโอได้ แต่ LAB นี้ไม่ได้เปิด (ไม่โหลดเข้า VRAM) |

#### ③ Dense กับ MoE ต่างกันอย่างไร

![Dense vs MoE: Dense 27B ทุกคำผ่าน FFN ก้อนเดียว ใช้ครบ 27B ~205 token/วินาที · MoE 35B-A3B มี Router เลือก 8 จากผู้เชี่ยวชาญ 256 ตัว + shared expert ใช้จริง ~3B ต่อคำ ~677 token/วินาที เร็วกว่า ~3 เท่า แต่ต้องเก็บครบ 35B ใน VRAM ไฟล์ 21.2 GiB](image/ex2-model-moe.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo) · ความเร็วจาก model card (ตอบ 1 คน, MTP=3)*

- **Dense (`27b`)** ทุก token ใช้น้ำหนักครบ 27B → แม่นและสม่ำเสมอ แต่คำนวณเยอะ
- **MoE (`35b-a3b`)** มี "ผู้เชี่ยวชาญ" 256 ตัวต่อชั้น (40 ชั้น) แต่ละ token ให้ **Router เลือกใช้แค่ 8 ตัว** + 1 ตัวที่ใช้ร่วม → คำนวณจริงแค่ **~3B (A3B = Active 3B)** → **ตอบเร็วกว่า ~3 เท่า** แต่ต้องเก็บครบทั้ง 35B ไว้ใน VRAM

#### ④ บีบอัดแบบ Q4/Q5 กับ NVFP4

![บีบโมเดลให้เล็ก: BF16 ต้นฉบับ 16 bit 54 GB · groupwise-int Q4/Q5 จำนวนเต็ม 4–5 bit + ตัวคูณทุกกลุ่ม · NVFP4 ทศนิยม 4 bit + ตัวคูณ FP8 ทุก 16 ค่า Tensor Core ของ RTX 5090 คำนวณได้ตรง ๆ · bit น้อย = ไฟล์เล็ก เร็วขึ้น แต่ความแม่นอาจลดนิดหน่อย](image/ex2-model-quant.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo)*

| วิธี | ชื่อไฟล์ | หลักการ | จุดเด่น |
|---|---|---|---|
| **groupwise-int (Q4/Q5)** | ไม่มีคำต่อท้าย เช่น `qwen3.6-27b` | เก็บเป็นจำนวนเต็ม 4–5 bit + ตัวคูณ 1 ค่าต่อกลุ่ม | ไฟล์เล็ก ความแม่นใกล้ต้นฉบับ |
| **NVFP4** | ลงท้าย `-nvfp4` | เก็บเป็นทศนิยม 4 bit + ตัวคูณ FP8 ทุก 16 ค่า (บางส่วนใช้ FP8) | GPU รุ่น Blackwell (RTX 5090) คำนวณได้ตรง ๆ → **อ่าน prompt ยาวเร็วมาก** |

#### ⑤ เทียบ 5 โมเดล: ความแม่น · ความเร็ว · VRAM

![กราฟเทียบ 5 โมเดล: GPQA-Diamond, AIME 2026, ความเร็ว token/วินาที และขนาดไฟล์ ≈ VRAM โดย qwen3.8-27b-nvfp4 (ค่าเริ่มต้น) GPQA 90.4% AIME 96.7% 205 tok/s 22.1 GiB](image/ex2-model-compare.png)
*กราฟจากตัวเลขใน model card ของ `neroued` บน Hugging Face (ตรวจ 15 ต.ค. 2026)*

| `MODEL=` (ใส่ในพรอมต์) | โครงสร้าง · บีบอัด | ขนาดไฟล์ | VRAM ที่ใช้ | GPQA-Diamond | AIME 2025 | AIME 2026 | IFBench | ความเร็ว (tok/s) | `LLM_MODEL` |
|---|---|---|---|---|---|---|---|---|---|
| `qwen3.8-27b-nvfp4` ⭐ | Dense 27B · NVFP4+FP8 | 22.1 GiB | **~24 GB** (วัดจริง) | **90.4%** | 96.7% | 96.7% | 77.0% | 205 | `qwen3.8-27b` |
| `qwen3.8-27b` | Dense 27B · Q4/Q5 | 19.0 GiB | ~21 GB | 87.4% | 96.7% | 96.7% | **77.7%** | – | `qwen3.8-27b` |
| `qwen3.6-27b` | Dense 27B · Q4/Q5 | 16.3 GiB | ~19 GB | 86.9% | 86.7% | 93.3% | – | 167 | `qwen3.6-27b` |
| `qwen3.6-27b-nvfp4` | Dense 27B · NVFP4 | 17.1 GiB | ~20 GB | 84.3% | 93.3% | 93.3% | – | 220 | `qwen3.6-27b` |
| `qwen3.6-35b-a3b` | MoE 35B (ใช้ 3B) · Q4–Q6 | 21.2 GiB | ~23 GB | 85.3% | 90.0% | 90.0% | – | **677** | `qwen3.6-35b-a3b` |

ตัววัด (benchmark) คืออะไร — ทุกตัวเป็น **accuracy (% ตอบถูก)** แบบ 0-shot (ไม่ให้ตัวอย่างก่อน) ตรวจคำตอบด้วยกฎอัตโนมัติ:

| ตัววัด | วัดอะไร |
|---|---|
| **GPQA-Diamond** | ข้อสอบวิทยาศาสตร์ (ฟิสิกส์ เคมี ชีวะ) ระดับปริญญาเอก แบบเลือกตอบ |
| **AIME 2025 / 2026** | ข้อสอบคณิตศาสตร์แข่งขันระดับมัธยมของอเมริกา (30 ข้อ/ปี) วัดการคิดหลายขั้น |
| **IFBench** | ทำตามคำสั่งได้เป๊ะไหม เช่น "ตอบไม่เกิน 3 บรรทัด" — สำคัญกับแชทบอท |
| **ความเร็ว** | token/วินาที ตอนตอบลูกค้า 1 คน (งานเขียนโค้ด, เปิด MTP=3) · "–" = ไม่มีใน model card |

- VRAM "~" = ประมาณจากขนาดไฟล์ + KV cache (`--max-context 16384`) ยังไม่ได้วัดจริง · RTX 5090 มี 32 GB **ใส่ได้ทุกตัว** · AI จะรายงานค่าจริงจาก `nvidia-smi` ตอนจบ
- **ค่าเริ่มต้นใช้ `qwen3.8-27b-nvfp4`** เพราะแม่นที่สุดและทดสอบใน LAB แล้ว · อยากได้ตอบไวสุด → `qwen3.6-35b-a3b` · อยากโหลดไวสุด → `qwen3.6-27b`
- ในแชทจริงเราวัดได้ ~113 tok/s (`qwen3.8-27b-nvfp4`) — ต่ำกว่าตาราง เพราะคำตอบสั้นและรวมเวลาเริ่มต้น

#### ⑥ อยากเปลี่ยนโมเดล แก้ตรงไหน

![อยากเปลี่ยนโมเดล แก้ตรงไหน: 1 พรอมต์ MODEL=qwen3.6-35b-a3b (แก้ตรงนี้ที่เดียว) → 2 NINFER_RECIPE.md ตารางโมเดล ได้ HF repo ไฟล์ .ninfer LLM_MODEL → 3 RTX 5090 hf download และ ninfer-serve → 4 .env.vast LLM_MODEL=qwen3.6-35b-a3b → 5 หน้าแชท :3300 docker compose up -d --build web · ข้อ 2–4 AI ทำให้เอง](image/ex2-model-switch.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo)*

**เราแก้แค่ค่า `MODEL=` ในพรอมต์** — ที่เหลือ AI อ่านจากตารางใน [NINFER_RECIPE.md](_solution/ex2_chatbot/backend/NINFER_RECIPE.md) แล้วทำเอง

| อยากทำอะไร | แก้ตรงไหน |
|---|---|
| เลือกโมเดลตั้งแต่แรก | แก้ `MODEL=` ในพรอมต์ข้อ 4.1 |
| เปลี่ยนโมเดลบนเครื่องที่เช่าอยู่ | ใช้พรอมต์ "เปลี่ยนโมเดล" ท้ายข้อ 4.1 แล้วทำ 4.2 ใหม่ |
| ยอมจ่ายแพงขึ้น / ตั้งชื่อเครื่องอื่น | แก้ `MAX_DPH=` / `LABEL=` ในพรอมต์ |
| ปรับการทำงานของ server (context ยาวขึ้น, รับลูกค้าพร้อมกันมากขึ้น) | แก้ตาราง flag ใน `NINFER_RECIPE.md` ข้อ 2.3 |
| เพิ่มโมเดลใหม่ที่ `neroued` เพิ่งปล่อย | เพิ่มแถวในตาราง `NINFER_RECIPE.md` ข้อ 1 (repo · ไฟล์ · ชื่อใน API) |

### 4.1 · backend — ให้ yolo1 เช่า RTX 5090 และเปิด AI server

![yolo1 สั่ง skill vastai เช่า RTX 5090 แล้วติดตั้ง NInfer และโหลดโมเดล Qwen เปิด API ที่พอร์ต 8080](image/cartoon-ex2-backend.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): พรอมต์เดียว — เช่า 5090 → build NInfer + โหลดโมเดล → เปิด API พอร์ต 8080 → เขียนค่าเชื่อมต่อลง `.env.vast`*

![หน้า Instances: 1x RTX 5090 Verified ราคา $0.909/hr Max CUDA 13.1 เน็ต 5438/4839 Mbps disk 90 GB ป้าย ex2-ninfer-5090 running nvidia/cuda_13.1.2-devel-ubuntu24.04](image/ex2-vast-5090-console.png)
*ภาพจริง: เครื่อง backend ที่ได้ — RTX 5090, CUDA 13.1, เน็ต ~5000 Mbps, disk 90 GB, `$0.909/hr`*

🖥️ Terminal ที่ `/workspace` → `yolo1` → 💬 วาง (อยากใช้โมเดลอื่น แก้แค่ `MODEL=` ตามตารางข้อ 4.0 ⑤):

```text
ใช้ skill vastai ทำตาม 00_setup/04_Skill_Setup/01_VastAi_Skill/_solution/ex2_chatbot/backend/NINFER_RECIPE.md
MODEL=qwen3.8-27b-nvfp4 LABEL=ex2-ninfer-5090 MAX_DPH=1.20
```

ไฟล์ `NINFER_RECIPE.md` คือ "สูตร" ที่บอก AI ว่าต้องเช่าเครื่องแบบไหน ติดตั้งอะไร เปิด server ด้วยค่าอะไร ทดสอบอย่างไร และเขียนผลลง `.env.vast` — **ไม่มีสคริปต์ให้เรารันเอง** AI สร้างคำสั่งและรันบนเครื่องที่เช่าให้ทั้งหมด

**ผลจริงที่ได้ (14 ต.ค. 2026):** build NInfer 448 วินาที พร้อมกับโหลดโมเดล 128 วินาที (setup รวม ~8 นาที) · server พร้อมใน 14 วินาที · $0.91/ชม. · ตอบภาษาไทยใน 1.2 วินาที (~113 token/วินาที)

ไฟล์ `backend/.env.vast` อยู่ใน repo บน Windows ด้วย (โฟลเดอร์เดียวกัน) และถูก ignore ไม่ถูก commit — ห้ามเปิดใน JupyterLab

**เปลี่ยนโมเดลภายหลัง** (ใช้เครื่องเดิม ไม่ต้องเช่า/build ใหม่ · ~3–5 นาที) 💬 วางใน `yolo1`:

```text
ใช้ skill vastai ทำตาม NINFER_RECIPE.md ข้อ 3 (เปลี่ยนโมเดล) ในโฟลเดอร์ 00_setup/04_Skill_Setup/01_VastAi_Skill/_solution/ex2_chatbot/backend
เครื่อง LABEL=ex2-ninfer-5090 เปลี่ยนเป็น MODEL=qwen3.6-35b-a3b
```

AI จะแก้ `LLM_MODEL=` ใน `.env.vast` ให้ (URL และ key เดิม) → จากนั้นทำ 4.2 โหมด AI จริงอีกครั้ง หน้าแชทจะใช้โมเดลใหม่

### 4.2 · frontend — เปิดหน้าแชทบนเครื่องเรา

🖥️ Git Bash **บน Windows** ที่โฟลเดอร์ `00_setup/04_Skill_Setup/01_VastAi_Skill/_solution/ex2_chatbot/frontend` (Docker Desktop ต้องเปิดอยู่):

**โหมด AI จริง** (ใช้ค่าจาก `backend/.env.vast`):

```bash
grep -v '^LLM_\(BASE_URL\|MODEL\|API_KEY\)=' .env.example > .env
grep '^LLM_' ../backend/.env.vast >> .env
docker compose up -d --build
```

**โหมด mock** (ฝึกได้ไม่ต้องมี GPU · บอทตอบจากคำตอบสำเร็จรูป):

```bash
cp .env.example .env
docker compose --profile mock up -d --build
```

ครั้งแรก build ~2–5 นาที แล้วเปิด:
- หน้าแชท: **http://localhost:3300** → กดปุ่ม 📅 จองคิว หรือพิมพ์ `จอง นวดไทย ชื่อสมชาย เบอร์ 081-234-5678 วันที่ 2026-10-20 เวลา 14:00`
- รายการจอง: **http://localhost:3300/bookings**

🖥️ ดูว่าการจองเข้า PostgreSQL จริง:

```bash
docker compose exec db psql -U massage -d massage_shop -c "SELECT * FROM bookings;"
```

### 4.3 · ทดสอบอัตโนมัติด้วย Playwright (7 เคส)

![หุ่นยนต์ Playwright ถือโทรโข่งและป้ายเคส 1-7 หน้าจอแชทจองสำเร็จ แมวกอด PostgreSQL ติ๊กถูก ฟิล์ม GIF และ MP4](image/cartoon-ex2-test.png)
*ภาพแนวคิด (Imagegen ด้วย cyolo): Playwright เปิดเบราว์เซอร์คุยกับบอทแทนเรา 7 เคส แล้วอัดเป็น GIF/MP4*

🖥️ Git Bash บน Windows ที่โฟลเดอร์ `_solution/ex2_chatbot/e2e` (ต้องมี Node.js และหน้าแชทเปิดอยู่ที่ :3300):

```bash
npm install
npx playwright install chromium
npx playwright test
```

อยากเห็นเบราว์เซอร์ทำงานใส่ `--headed` · ดูรายงาน `npx playwright show-report` · (ไม่บังคับ) แปลงวิดีโอเป็น GIF/MP4: `node make-media.mjs` (ต้องมี ffmpeg)

**ผลจริงกับโมเดลบน RTX 5090** (MP4 ถ้ามี — ไฟล์ `.mp4` ไม่ถูกเก็บใน git):

| เคส | ทดสอบ | ผล |
|---|---|---|
| 1 | ทักทาย + ถามเวลาเปิดปิด ([MP4](image/ex2/ex2-case1-hours.mp4)) | ![เคส 1 ถามเวลาเปิดปิด](image/ex2/ex2-case1-hours.gif) |
| 2 | กดปุ่ม "ดูราคา" ([MP4](image/ex2/ex2-case2-price.mp4)) | ![เคส 2 ดูราคา](image/ex2/ex2-case2-price.gif) |
| 3 | ขอคำแนะนำนวดแก้ปวดหลัง (ออฟฟิศซินโดรม) ([MP4](image/ex2/ex2-case3-backpain.mp4)) | ![เคส 3 ปวดหลัง](image/ex2/ex2-case3-backpain.gif) |
| 4 | ถามโปรโมชั่น / ส่วนลดนักศึกษา ([MP4](image/ex2/ex2-case4-promo.mp4)) | ![เคส 4 โปรโมชั่น](image/ex2/ex2-case4-promo.gif) |
| 5 | จองคิวทีละขั้น → การ์ดจองสำเร็จ → `/bookings` มีแถวใหม่**จาก PostgreSQL จริง** ([MP4](image/ex2/ex2-case5-booking.mp4)) | ![เคส 5 จองคิว](image/ex2/ex2-case5-booking.gif) |
| 6 | ถามนอกเรื่อง (สูตรอาหาร) → ตอบสุภาพแล้ววกกลับเรื่องร้าน ([MP4](image/ex2/ex2-case6-offtopic.mp4)) | ![เคส 6 นอกเรื่อง](image/ex2/ex2-case6-offtopic.gif) |
| 7 | ลูกค้าพิมพ์ภาษาอังกฤษ ([MP4](image/ex2/ex2-case7-english.mp4)) | ![เคส 7 ภาษาอังกฤษ](image/ex2/ex2-case7-english.gif) |

*ภาพจริง (GIF จาก Playwright): หน้าแชท "สบายใจ นวดแผนไทย · เปิดทุกวัน 10:00–22:00" พร้อมปุ่มลัด ดูราคา · เวลาเปิดปิด · แนะนำนวดแก้ปวดหลัง · โปรโมชั่น · จองคิว*

### 4.4 · ปิดทุกอย่าง (ห้ามข้าม!)

💬 ใน `yolo1`:

```text
ใช้ skill vastai ลบเครื่อง ex2-ninfer-5090 แล้วสรุปค่าใช้จ่าย
```

🖥️ Git Bash ที่โฟลเดอร์ `frontend`:

```bash
docker compose --profile mock down
```

(ใส่ `-v` ต่อท้ายถ้าต้องการลบข้อมูลการจองทั้งหมด) แล้วเช็คหน้าเว็บ Instances ว่า**ว่าง**

---

## ความปลอดภัย (อ่านให้จบ)

- **ห้าม commit / ห้ามแคปหน้าจอ** API key, `.env`, `.env.vast` — ภาพทุกภาพใน LAB นี้เบลอข้อมูลสำคัญแล้ว
- `.env` และ `.env.vast` ถูก ignore ใน `.gitignore` แล้ว · อย่าเปิดใน JupyterLab (เกิดไฟล์ checkpoint ที่เป็นสำเนา)
- ⚠️ **`Devtool_SSH/devtoolSSH` (private key) ถูกแชร์ใน repo นี้เพื่อความสะดวกในห้องเรียน** → ใครมี repo ก็ ssh เข้าเครื่องที่เช่าด้วย key นี้ได้ระหว่างที่เครื่องยังเปิด → **ลบเครื่องทันทีหลังใช้**
- งานส่วนตัว ให้สร้าง key ของตัวเอง แล้วใส่ `.pub` ใหม่บนเว็บ (ขั้นที่ 2) และแก้ `VAST_SSH_KEY_FILE` ให้ชี้ไปที่ key ใหม่:

  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/id_vast
  ```

- API key หลุด → เว็บ Keys → แท็บ API Keys → กด 🗑️ ลบ key นั้น แล้วสร้างใหม่

## เช็คลิสต์

| ขั้น | ผลที่ควรได้ | ✓ |
|---|---|---|
| 2 | SSH Keys มีแถว `ssh-ed25519 … devtools-lab` | ☐ |
| 3 | API key `devtools-lab` (Billing Write ว่าง) คัดลอกแล้ว | ☐ |
| ส่วนที่ 2 | `.env` มี 3 บรรทัด VAST_ ไม่มี `"` ไม่มี comment ท้ายบรรทัด | ☐ |
| 4 | skill `OK` 6 บรรทัด · `/workspace` เห็น `.env` · `VAST_API_KEY OK` `VAST_SSH_KEY_FILE OK` | ☐ |
| 5 | `pip install 'vastai~=1.8'` เสร็จ | ☐ |
| 6 | ตารางความพร้อม ✅ | ☐ |
| 7–8 | `lab-4090` running บนเว็บ | ☐ |
| 9 | `nvidia-smi` เห็น RTX 4090 24564MiB | ☐ |
| 10 | ลบ `lab-4090` แล้ว + สรุปค่าใช้จ่าย · หน้า Instances ว่าง | ☐ |
| 4.1 | `backend/.env.vast` มี 3 บรรทัด LLM_ | ☐ |
| 4.2 | http://localhost:3300 ตอบภาษาไทย · `/bookings` มีแถว | ☐ |
| 4.3 | `npx playwright test` ผ่าน 7 เคส | ☐ |
| 4.4 | ลบ `ex2-ninfer-5090` แล้ว · `docker compose down` | ☐ |

## แก้ปัญหา

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `VAST_API_KEY MISSING` (ขั้นที่ 4) | ยังไม่ได้ใส่ค่าใน `.env` หรือสร้าง container ก่อนแก้ `.env` → แก้แล้ว**ทำขั้นที่ 4 ใหม่** |
| `Invalid user key` | ใน `.env` มี `"` ครอบ key หรือมี `# comment` ท้ายบรรทัด → แก้แล้ว**ทำขั้นที่ 4 ใหม่** (ค่าจาก `--env-file` ถูกอ่านตอนสร้าง container เท่านั้น) |
| `pip install` ค้างนาน | ปกติ ~5–12 นาที (PyPI ช้า) รอได้ ทำครั้งเดียวต่อ container ใหม่ |
| `ไม่มี offer <= $…/hr` | เพดานราคาต่ำไป → ตอบ skill ให้ยอมเพดานสูงขึ้น หรือเปลี่ยน GPU (เช่น RTX 3090) |
| ssh `Connection refused` หลังเช่า | เครื่องยังบูตไม่เสร็จ รอ 1–2 นาที หรือใช้คำสั่ง proxy |
| skill หา SSH key ไม่เจอ | เปิด Terminal ไม่ใช่ที่ `/workspace` → `cd /workspace` แล้วเปิด `yolo1` ใหม่ |
| แชทบอทขึ้น error | เช็ค `LLM_BASE_URL` (IP:port ของ 8080/tcp, ไม่มี `/v1`) และเครื่อง 5090 ยัง running → แก้ `.env` แล้ว `docker compose up -d --build web` |
| ลืมลบเครื่อง | เปิด https://cloud.vast.ai/instances/ → กด 🗑️ (destroy) ทุกเครื่องที่ไม่ใช้ · **stop ยังเสียค่า disk** |

## ข้อควรรู้

- skill จะ**ไม่ขึ้นเพดานราคาเอง** และ**ไม่ลบเครื่องเองโดยไม่ถาม** — ถ้าถาม ให้อ่านก่อนตอบ
- `pip install` ลงใน container (ไม่ใช่ volume) → ลบ container แล้วสร้างใหม่ต้องติดตั้งใหม่ แต่ล็อกอินและ skill ยังอยู่ใน volume `ai-accounts`
- แก้ `.env` แล้วต้องสร้าง container ใหม่ (ขั้นที่ 4) ค่าใหม่ถึงจะเข้า
- ราคา GPU บน Vast.ai เปลี่ยนตลอดเวลา ตัวเลขใน LAB นี้คือผลจริงวันที่ 14 ต.ค. 2026
- `stop` = หยุด GPU แต่ยังเก็บ disk (เสียเงินต่อ) · `destroy` = ลบทิ้งหมด หยุดจ่าย กู้ไม่ได้
