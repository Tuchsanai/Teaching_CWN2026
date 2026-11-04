# บท 05 · ส่วน 03 — skill ระดับองค์กร: พนักงาน 28 คน เก่งคนละเรื่อง แชร์กันจนทั้งบริษัทเก่ง (Copy & Paste)

ส่วน 02 ทำให้ **คนเดียว** เก่งขึ้น (skill `test-from-plan` v1 → v4)
ส่วนนี้จำลอง **บริษัทเทค "โนวาเทค" 10 แผนก + ทีมกลาง ผังองค์กร 4 ชั้น พนักงาน 28 คน** แต่ละคนเก่งคนละเรื่อง แล้วลงมือจริงตาม [ส่วน 01 ภาค 4](../01_skill-theory/README.md#-ภาค-4--skill-ระดับองค์กร-จากคนเดียวเก่ง-สู่ทั้งบริษัทเก่ง) ว่าความเก่งของคนหนึ่งคนจะกลายเป็นของทั้งบริษัทได้ยังไง: คลังกลาง, PR, CI ด่านตรวจ และการค้นหา skill

![แต่ละคนเก่งคนละเรื่อง แต่ความเก่งยังอยู่ในหัว ไม่ได้แชร์กัน (ภาพจำลอง)](img/p00-people-in-heads.png)

> อ่าน [ส่วน 01 ภาค 4 (หัวข้อ 18–26)](../01_skill-theory/README.md#-ภาค-4--skill-ระดับองค์กร-จากคนเดียวเก่ง-สู่ทั้งบริษัทเก่ง) ก่อน ทุก LAB มีลิงก์กลับไปหัวข้อทฤษฎีที่เกี่ยวข้อง · แบบร่างก่อนรันจริงอยู่ใน [DESIGN.md](DESIGN.md) (เก็บไว้เทียบว่าของจริงต่างจากแผนตรงไหน)

## 🧭 8 LAB (รันจริงครบทุก LAB)

| LAB | ทำอะไร | ทฤษฎี | ผลจริงสั้น ๆ |
|---|---|---|---|
| 0 | ตั้งบริษัท: Gitea (คลังกลาง) + CI runner + พนักงาน 28 คน | 20, 22.2 | ~54 วินาที · 12 ทีม · เหลือ 2 container |
| 1 | 24 คนเก็บความเก่งของตัวเองเป็น skill ส่วนตัว | 16, 18, 21.1 | 24/24 skill · กติกาข้อมูลลูกค้าถูกคัดลอกไว้ 14 ที่ (นับจาก 19 โต๊ะแรก) |
| 2 | ทีมกลางรวมเป็นคลัง `org-skills` (plugin marketplace) | 21, 22 | 11 plugin · 23 skill · ลบสำเนา 12 ไฟล์ |
| 3 | ทุกโต๊ะติดตั้งแพ็กแผนก + Dev คนใหม่วันแรก | 19, 22.3, 24.4 | เห็น 6 จาก 23 skill · คนใหม่ 1/12 → 12/12 |
| 4 | ดีลเดียววิ่งข้าม 9 แผนก (ตอนต่อหลัง LAB 5) | 20.1, 25 | หยิบ skill ถูกเอง 11/12 · MD ตีกลับเรื่อง PDPA |
| 5 | ⭐ PR: คนหนึ่งแก้ skill ทุกคนเก่งขึ้น | 19, 22.2 | รีวิว 3 รอบ · krit ภาคผนวก PDPA 0/3 → 3/3 |
| 6 | ⭐ SkillOps CI: ด่านตรวจ skill | 15, 17, 23 | รีวิวเจอช่องโหว่ของ CI 4 ข้อ · PR อันตรายถูกบล็อก · v1.0.0 → v1.1.0 |
| 7 | หา skill ให้เจอ + กราฟผลกระทบ | 24, 25 | คำค้นใหม่ hit@1 80% (เคยเห็น 98%) · กราฟ 67 เส้น |

> 🆕 **บริษัทขยายเป็น 28 คน 4 ชั้น** (เพิ่มผู้บริหารสาย 3 คน · ทีม Product 2 คน · น้องใหม่ Sales และ HR) · LAB 0 รันใหม่ทั้งหมด · LAB 1 รันเพิ่มเฉพาะ 5 โต๊ะใหม่ · ผลของ LAB 2–7 ด้านล่างยังเป็นรอบบริษัท 21 คน รอรันใหม่

## 🧰 ก่อนเริ่ม

| ✅ | ต้องมี |
|---|---|
| ☐ | **Docker Desktop** เปิดอยู่ และพอร์ต **3300** ว่าง |
| ☐ | ต่ออินเทอร์เน็ตได้ (ครั้งแรกต้องดึง image `gitea/gitea`, `gitea/act_runner`, `node` ราว 1 GB) |
| ☐ | เปิด **Claude Code** ที่โฟลเดอร์ [`novatech/`](novatech/) (ทุก LAB เริ่มที่นี่) |

> 🧪 **หมายเหตุผู้สอน:** ผลจริงด้านล่างรันในสำเนาแยกที่ `C:/t/org05/novatech` (LAB 0 และ 5 โต๊ะใหม่ใน LAB 1 รันใหม่ที่ `C:/t/org05p/novatech`) ด้วย Claude Code (Opus 5.5) แบบไม่เชื่อม Chrome · พรอมต์เหมือนของผู้เรียนทุกตัวอักษร

---

## LAB 0 · ตั้งบริษัทโนวาเทค 🤖

![LAB 0 ตั้งบริษัทโนวาเทค: คลังกลาง Gitea ตรงกลาง เชื่อมกับโต๊ะของ 10 แผนก ทีมกลาง และผู้บริหาร พร้อม CI runner · 1 คำสั่ง docker compose up = พนักงาน 28 คน 12 ทีม](img/lab0-company.png)

LAB นี้ยังไม่แตะเรื่อง skill แค่ **เปิดบริษัทจำลองด้วยพรอมต์ประโยคเดียว** (ใช้เวลาราว 1 นาที) แล้วทำความรู้จักว่าในบริษัทมีอะไร มีใคร และเราจะเล่นเป็นใคร

🎬 **ดูภาพรวมใน 19 วินาที:** เปิด `compose.yml` ใน VS Code → คลิกขวา **Compose Up** → container ขึ้นมา → เปิดเว็บ Gitea ของบริษัท (องค์กร · ทีม · พนักงาน)

![GIF แนะนำบริษัทโนวาเทค: ① compose.yml ใบสั่งตั้งบริษัท 5 container gitea init runner seed cleanup ② คลิกขวา compose.yml ใน VS Code เลือก Compose Up ③ terminal แสดง novatech-gitea Healthy, init และ seed ทำงานเสร็จแล้วออก, runner Started, cleanup ลบตัวช่วย เหลือทำงาน 2 ตัว ④ เปิด localhost:3300 หน้าองค์กรโนวาเทค ยังไม่มี repository Members 29 Teams 13 ⑤ หน้าทีม 11 แผนก + leads ⑥ หน้าพนักงาน 1 บัญชี = 1 พนักงาน = 1 โต๊ะ · บริษัทพร้อมแล้ว 2 container 28 คน 12 ทีม 28 โต๊ะ](img/lab0-company-intro.gif)

<sub>หน้าจอ VS Code และ terminal เป็นภาพจำลอง · หน้าเว็บ Gitea เป็นภาพหน้าจอจริงจากบริษัทที่เปิดด้วย compose.yml นี้</sub>

| หัวข้อ | ได้อะไร |
|---|---|
| [0.1](#01-แล็บนี้จำลองอะไร) | บริษัทจริงมีอะไร → ในแล็บแทนด้วยอะไร |
| [0.2](#02-คำศัพท์ที่ต้องรู้) | ศัพท์ Git / PR / CI / Docker ที่จะเจอทั้ง 8 LAB |
| [0.3](#03-ลงมือ-เปิดบริษัท) | 💬 พรอมต์เปิดบริษัท |
| [0.4](#04-ตรวจว่าเปิดสำเร็จ) | ✅ ตรวจ 4 ข้อ |
| [0.5](#05-คนในบริษัท-28-คน) | ผังองค์กร 28 คน |
| [0.6](#06-เราเล่นเป็นใคร) | เปิด Claude Code ที่โต๊ะไหน = เป็นคนนั้น |

### 0.1 แล็บนี้จำลองอะไร

เราอยากรู้ว่า **ความเก่งของพนักงานคนหนึ่ง จะกลายเป็นความเก่งของทั้งบริษัทได้ยังไง** (ทฤษฎีหัวข้อ 18–26) หลักคือ **ของจริงมีที่เดียว · ทุกคนดึงไปใช้ · อยากแก้ต้องยื่น PR** (หัวข้อ 22.2) แล็บจึงจำลองของ 5 อย่างที่บริษัทจริงมี

![บริษัทจริง → ในแล็บนี้: GitHub ของบริษัท → Gitea localhost:3300 · ระบบ CI ของบริษัท → runner · พนักงาน 28 คน → บัญชี Gitea + การ์ด people/ · คอมพิวเตอร์ของแต่ละคน → โต๊ะ desks/<ชื่อ>/ · ไดรฟ์กลางของบริษัท → company-kit/](img/lab0-real-vs-lab.png)

| บริษัทจริง | ในแล็บนี้ | อยู่ที่ไหน |
|---|---|---|
| 🌐 GitHub ของบริษัท (คลังกลาง) | **Gitea** เว็บแบบ GitHub ที่รันในเครื่องเรา | `http://localhost:3300` |
| ⚙️ ระบบ CI | **runner** ด่านตรวจอัตโนมัติ (เริ่มใช้ LAB 6) | container `novatech-runner` |
| 👥 พนักงาน 28 คน | บัญชี Gitea + การ์ดประวัติคนละใบ | [`people/<แผนก>/`](novatech/people/) |
| 💻 คอมพิวเตอร์ของแต่ละคน | **โต๊ะ** 1 โฟลเดอร์ต่อ 1 คน | [`desks/<ชื่อ>/`](novatech/desks/) |
| 📁 ไดรฟ์กลาง | ราคา, TOR ลูกค้า, กติกา, log เหตุการณ์ | [`company-kit/`](novatech/company-kit/) |

### 0.2 คำศัพท์ที่ต้องรู้

ไม่ต้องจำตอนนี้ ใช้เป็นที่เปิดกลับมาดูเมื่อเจอคำนี้ใน LAB ถัดไป

| คำ | ภาษาง่าย ๆ | เจอตรงไหน |
|---|---|---|
| **Git · repo** | ระบบเก็บไฟล์ที่จำทุกเวอร์ชัน · repo = แฟ้มงาน 1 ชุด | คลัง skill `org-skills` (LAB 2) |
| **commit · push** | บันทึกการแก้ 1 ครั้ง · ส่งขึ้นคลังกลาง | ทุกการแก้ skill (LAB 2, 5, 6) |
| **branch · main** | สำเนาแยกไว้แก้ · `main` = ฉบับจริงที่ทุกคนใช้ | ห้าม push ตรงเข้า `main` (LAB 2) |
| **Gitea** | เว็บเก็บ repo แบบ GitHub แต่รันในเครื่องเรา | `localhost:3300` |
| **PR** (Pull Request) | คำขอรวมสิ่งที่แก้เข้า `main` ต้องมีคนตรวจก่อน | `sales-nida` แก้ skill (LAB 5) |
| **review · approve · merge** | อ่านแล้วติ · อนุมัติ · รวมเข้าฉบับจริง | `plat-may` รีวิว PR (LAB 5) |
| **CODEOWNERS** | ไฟล์บอกว่าโฟลเดอร์ไหนใครต้องรีวิว | หัวหน้าแผนก 👑 ดูแล plugin แผนกตัวเอง (LAB 2) |
| **CI · runner** | ตรวจ PR อัตโนมัติ · runner = เครื่องที่ลงมือตรวจ | ด่านตรวจ skill 3 ด่าน (LAB 6) |
| **ผลเขียว / แดง** | ผลตรวจบน PR · แดง = merge ไม่ได้ | PR อันตรายถูกบล็อก (LAB 6) |
| **Docker · container** | รันโปรแกรมในกล่องแยก ไม่ต้องติดตั้งลงเครื่อง | `novatech-gitea`, `novatech-runner` |
| **docker compose** | เปิด/ปิดหลายกล่องพร้อมกันจากไฟล์ `compose.yml` | `docker compose up -d` = เปิดบริษัท |
| **volume** | ที่เก็บข้อมูลนอกกล่อง ปิดกล่องแล้วไม่หาย | `docker compose down -v` = ลบทั้งบริษัท |
| **token** | รหัสที่ใช้แทนรหัสผ่าน ให้โปรแกรมทำงานในนามเรา | `desks/<ชื่อ>/.gitea-token` (ไม่ขึ้น git) |
| **.env** | ไฟล์เก็บรหัสทดสอบของแล็บ ไม่มีก็ใช้ `.env.example` | `ADMIN_USER`, `ADMIN_PASSWORD`, `LAB_PASSWORD` |

### 0.3 ลงมือ: เปิดบริษัท

🧑 **คิดก่อน** ถ้าพนักงานคนหนึ่งลาออกพรุ่งนี้ ความเก่งของเขาอยู่ที่ไหน

💬 **พรอมต์** (เปิด Claude Code ที่โฟลเดอร์ [`novatech/`](novatech/) ในบทผู้ดูแลระบบ)

![หน้าต่าง Claude Code วางพรอมต์ LAB 0](img/lab0-paste.png)

```text
เปิดบริษัทจำลองโนวาเทคจาก compose.yml แล้วบอกว่ามีแผนกและพนักงานใครบ้าง
```

✅ **ผลจริง: 54 วินาที · 8 คำสั่ง** ([ดูทุกคำสั่ง](_solution/lab0/tool-calls.md) · [คำตอบเต็ม](_solution/lab0/claude-summary.md))

![LAB 0 ผลจริง Claude ทำ 4 ขั้นใน 54 วินาที: ① อ่าน compose.yml + people.json ② ไม่มี .env → ใช้ .env.example ③ docker compose up -d → เหลือ gitea + runner ④ ถาม Gitea จริง: 28 คน + แอดมิน 1 · ตอบเป็นตาราง 3 สาย 11 แผนก จับคอมเมนต์เก่าใน compose.yml ได้เอง](img/lab0-run-steps.png)

Claude ตอบเป็นตาราง 3 สาย 11 แผนก ชี้ว่าน้องใหม่ 3 คนยังไม่มี skill และจับได้เองว่าคอมเมนต์ใน `compose.yml` ยังเขียนจำนวนพนักงานเก่า (ผู้สอนแก้แล้ว)

**ข้างในเกิดอะไรขึ้น:** `docker compose up -d` เปิด container 5 ตัว แต่ทำงานตลอดแค่ 2 ตัว อีก 3 ตัวเป็นตัวช่วยที่ทำครั้งเดียวแล้วลบตัวเอง

![ใน Docker มี 2 ตัวที่ทำงานตลอด: gitea คลังกลาง localhost:3300 (repo · PR · รีวิว) และ runner ด่านตรวจ CI ใช้ใน LAB 6 · และตัวช่วย 3 ตัวที่ทำครั้งเดียวแล้วลบตัวเอง: init สร้างแอดมิน → seed สร้างพนักงาน 28 คน (และโต๊ะ 28 โต๊ะใน desks/) → cleanup เก็บกวาด](img/lab0-containers.png)

| container | ทำอะไร | อยู่ถึงเมื่อไหร่ |
|---|---|---|
| `novatech-gitea` | คลังกลาง: บัญชี ทีม repo PR รีวิว | 🟢 ตลอด |
| `novatech-runner` | ด่านตรวจ CI (รอเฉย ๆ จนถึง LAB 6) | 🟢 ตลอด |
| `novatech-init` | ① สร้างบัญชีผู้ดูแลระบบ | 🧹 ทำเสร็จแล้วหายไป |
| `novatech-seed` | ② สร้างองค์กร 12 ทีม 28 บัญชี + โต๊ะ 28 โต๊ะพร้อม token + โน้ตลับของ MD (จาก [`seed/people.json`](novatech/seed/people.json)) | 🧹 ทำเสร็จแล้วหายไป |
| `novatech-cleanup` | ③ ลบตัวช่วยทั้ง 3 ตัว | 🧹 ทำเสร็จแล้วหายไป |

> 🔁 `docker compose down` = ปิด (ข้อมูลอยู่) · `docker compose down -v` = **ลบทั้งบริษัท** เริ่มใหม่ · สั่ง `up -d` ซ้ำได้ แต่ token ของทุกคนจะถูกออกใหม่

> 🧪 **หมายเหตุผู้สอน:** รอบนี้รันด้วย `claude -p` จึงเห็น `docker compose up` ใน log 3 ครั้ง (2 ครั้งแรกติดการขออนุญาต) ผู้เรียนที่ใช้ Claude Code ในแอปจะเห็นหน้าต่างขออนุญาต กดอนุญาตแล้วไปต่อได้เลย

### 0.4 ตรวจว่าเปิดสำเร็จ

| ✅ | ตรวจ | ควรเห็น |
|---|---|---|
| ☐ | `docker compose ps` | 2 แถว: `novatech-gitea` (healthy) และ `novatech-runner` |
| ☐ | เปิด `http://localhost:3300` ล็อกอินด้วย `ADMIN_USER` / `ADMIN_PASSWORD` | องค์กร `novatech`: Members **29** (28 คน + แอดมิน) · Teams **13** · **0 repositories** |
| ☐ | ล็อกอินเป็นพนักงาน: user = ชื่อในการ์ด (เช่น `sales-nida`) รหัส = `LAB_PASSWORD` | เห็นเฉพาะทีมของตัวเอง |
| ☐ | เปิดโฟลเดอร์ `desks/` | 28 โฟลเดอร์ มี `.gitea-token` ทุกโต๊ะ |

| หน้าองค์กร: Members 29 · Teams 13 · 0 repositories | ทีม `leads` = ผู้ดูแล skill 11 คน |
|---|---|
| ![หน้าองค์กรโนวาเทคใน Gitea: ยังไม่มี repository, Members 29, Teams 13](img/lab0-org.png) | ![ทีม leads มีสมาชิก 11 คน: fin-joy, sa-ton, sales-nida, pm-beam, dev-pond, exec-ploy, hr-fah, qa-mint, ops-art, plat-ken, ml-jay สิทธิ์เขียนทุก repo](img/lab0-leads.png) |

👀 **สังเกต** ยังไม่มี repo เลย (0 repositories) บริษัทมีคนครบ แต่ความเก่งของทุกคนยังอยู่ในหัว (ทฤษฎีหัวข้อ 18.2) → LAB 1 จะเริ่มเก็บออกมาเป็น skill

### 0.5 คนในบริษัท 28 คน

[![ผังองค์กรโนวาเทค 4 ชั้น 28 คน ภาพเดียว: ชั้น 1 MD สมชาย (md-somchai) มีผู้ช่วยผู้บริหารพลอยไพลิน (exec-ploy) ขึ้นตรง → ชั้น 2 ผู้บริหาร 3 สาย สายธุรกิจ วิทย์ (cco-wit) ดูแล Sales (sales-nida 👑, sales-krit, sales-mook 🆕) SA (sa-ton 👑, sa-ice) Product (pm-beam 👑, pm-gift) · สายเทคโนโลยี ณัฐ (cto-nat) ดูแล Dev (dev-pond 👑, dev-mew, dev-new 🆕) QA (qa-mint 👑, qa-bank) DevOps (ops-art 👑, ops-fon) ML (ml-jay 👑, ml-pim) ทีมกลาง (plat-ken 👑, plat-may) · สายบริหารและการเงิน หญิง (cfo-ying) ดูแล HR (hr-fah 👑, hr-oat, hr-namtan 🆕) บัญชี (fin-joy 👑, fin-nok) · กล่องบนสุดของแต่ละคอลัมน์คือหัวหน้าแผนก (ชั้น 3) ที่เหลือคือพนักงาน (ชั้น 4) · แต่ละกล่องมีชื่อ user บทบาท และ skill](img/org-chart.png)](img/org-chart.png)

<sub>🔍 กดที่ภาพเพื่อเปิดขนาดเต็ม (2400 px)</sub>

| ชั้น | ใคร | คน |
|---|---|---|
| 1 | MD `md-somchai` | 1 |
| 2 | ผู้บริหารสาย `cco-wit` ธุรกิจ · `cto-nat` เทคโนโลยี · `cfo-ying` บริหารและการเงิน + ผู้ช่วยผู้บริหาร `exec-ploy` | 4 |
| 3 | หัวหน้าแผนก 👑 Sales · SA · Product · Dev · QA · DevOps · ML · ทีมกลาง · HR · บัญชี | 10 |
| 4 | พนักงาน รวมน้องใหม่ 🆕 3 คน (`sales-mook`, `dev-new`, `hr-namtan`) | 13 |

- **👑 = ผู้ดูแล skill ของแผนก** (รีวิว PR) มี 11 คน = หัวหน้าแผนก 10 + `exec-ploy` รวมเป็นทีม `leads` · ไม่ใช่ผู้บริหารสาย
- **ทีม Product** ดูแลผลิตภัณฑ์ของบริษัทเอง ชื่อ NovaQueue (ระบบจองคิวสาขา) · **ทีมกลาง (platform)** ดูแลคลัง skill ของทั้งบริษัท
- การ์ดของแต่ละคน (เก่งอะไร ทำอะไรซ้ำ ชอบพิมพ์สั่ง AI ว่าอะไร) อยู่ที่ [`people/<แผนก>/<ชื่อ>.md`](novatech/people/) เช่น [`people/sales/sales-nida.md`](novatech/people/sales/sales-nida.md)

### 0.6 เราเล่นเป็นใคร

![นักศึกษาห้อยป้ายชื่อ sales-nida นั่งหน้าแล็ปท็อปที่เปิดโฟลเดอร์ desks/sales-nida ด้านหลังเป็นชั้นโฟลเดอร์ของพนักงานคนอื่น · เปิด Claude Code ที่โต๊ะไหน = ทำงานในนามคนนั้น (ภาพจำลอง)](img/lab0-desk-roleplay.jpg)

พนักงานทุกคนอยู่ในเครื่องของเรา **อยากเป็นใคร ให้เปิด Claude Code ที่โต๊ะของคนนั้น** เช่น เปิดที่ `novatech/desks/sales-nida/` = ทำงานในนามนิดา (ใช้ token และโต๊ะของนิดา)

ตัวละครหลักตลอด 8 LAB

| ใคร | ทำอะไร | LAB |
|---|---|---|
| 🛠️ **ผู้ดูแลระบบ** (เปิดที่ `novatech/`) | เปิดบริษัท · ติดตั้งคลัง skill ให้ทุกโต๊ะ | 0 · 3 |
| 👥 พนักงาน 24 คน | ทำงานของตัวเอง 1 ชิ้นแล้วเก็บเป็น skill ส่วนตัว | 1 |
| 🏛️ `plat-ken` หัวหน้าทีมกลาง | รวมคลังกลาง · ทำ CI · รีวิว PR ฝั่ง core | 2 · 5 · 6 |
| 🛡️ `plat-may` เจ้าของนโยบายข้อมูลลูกค้า | รีวิว PR · รีวิว CI แบบคิดเป็นคนร้าย | 5 · 6 |
| 💼 `sales-nida` หัวหน้าทีมขาย | ทำ proposal ดีลธนาคาร · เปิด PR แก้ skill | 4 · 5 |
| 🧾 `fin-joy` หัวหน้าบัญชี | ตรวจราคาและกำไรของดีล | 4 |
| 👔 `md-somchai` MD | อนุมัติ/ตีกลับดีล (รู้กฎ PDPA อยู่คนเดียว) · ดูว่าแก้กฎแล้วกระทบใคร | 4 · 7 |
| 💼 `sales-krit` เซลส์ | ไม่แก้อะไรเลย แต่ดูว่าเก่งขึ้นตามเพื่อนไหม | 5 |
| 🆕 `dev-new` Dev คนใหม่ | เทียบแผนงานแบบมี/ไม่มีแพ็ก skill ของทีม | 3 |

<details>
<summary>📋 ดูบทของทุกคน (รวมบทรอง)</summary>

| ใคร | ทำอะไร | LAB |
|---|---|---|
| `sa-ton` · `dev-mew` · `ml-jay` · `qa-mint` · `ops-art` · `hr-fah` | รับดีลต่อจาก MD ทำงานของแผนกตัวเอง | 4 (ต่อ) |
| `hr-oat` · `ops-fon` · `ml-pim` · `exec-ploy` | เปิด PR 4 แบบ (ดี / ลวก / อันตราย / กว้างเกิน) ทดสอบด่าน CI | 6 |
| `hr-fah` | ค้น skill ของแผนกอื่น | 7 |
| `cco-wit` · `cto-nat` · `cfo-ying` ผู้บริหารสาย | ทบทวน pipeline · ความเสี่ยงเทคนิค · ต้นทุนและกำลังคน (บทใน LAB 2–7 รอรันใหม่) | 1 |
| `pm-beam` · `pm-gift` ทีม Product | เขียน PRD · วางแผนเลิกให้บริการ NovaQueue v1 (บทใน LAB 2–7 รอรันใหม่) | 1 |
| `sales-mook` · `hr-namtan` น้องใหม่ | ยังไม่มี skill ใช้ทดลองว่าน้องใหม่ได้ความรู้ของทีมไหม (รอรันใหม่) | — |

</details>

---

## LAB 1 · 24 คนเก็บความเก่งของตัวเองเป็น skill ส่วนตัว 🤖 ×24

![LAB 1 เก็บความเก่งของตัวเองเป็น skill ส่วนตัว: เกาะ 9 เกาะของแต่ละแผนก แต่ละคนเก็บความรู้ในหัวเป็นโฟลเดอร์ SKILL.md บนโต๊ะตัวเอง ไม่มีสะพานเชื่อมกัน](img/lab1-personal.png)

**LAB นี้ทำอะไร:** พนักงาน 24 คน **ต่างคนต่างทำ** ที่โต๊ะตัวเอง: ทำงานจริงของตัวเอง 1 ชิ้น แล้วเก็บวิธีทำเป็น skill ไว้ในเครื่องตัวเอง (แบบที่บริษัทส่วนใหญ่เริ่มต้น) ยังไม่มีใครแชร์ให้ใคร

| หัวข้อ | ได้อะไร |
|---|---|
| [1.1](#11-ของแต่ละคนอยู่ที่ไหน-สำคัญ) | 📁 อ่านจากโฟลเดอร์ไหน เขียนลงโฟลเดอร์ไหน |
| [1.2](#12-พรอมต์ของแต่ละคน-24-พรอมต์) | 💬 พรอมต์รวม (ก๊อปอันเดียวได้ทุกคน) + ตัวอย่างพรอมต์ที่แต่ละคนได้รับ |
| [1.3](#13-ตัวอย่าง-5-โต๊ะ) | 👀 ผลจริงของนิดา · MD · จอย · HR · ML |
| [1.4](#14-ทุกคนทำงานอะไร-ผลจริง-24-โต๊ะ) | 📋 ทั้ง 24 คนทำงานอะไร ได้ skill อะไร |
| [1.5](#15-ผลที่เห็น-3-ปัญหาของ-ต่างคนต่างเก็บ) | ⚠️ 3 ปัญหาที่จะแก้ใน LAB ถัดไป |

> 📦 **LAB นี้ยังไม่ใช้ Gitea** ทุกอย่างเกิดในโฟลเดอร์ของแต่ละโต๊ะ · ใครทำ: 24 จาก 28 คน · ไม่ทำ 4 คน คือน้องใหม่ 3 คน (`sales-mook`, `dev-new`, `hr-namtan` ยังไม่มีความเก่งของตัวเอง) และ `plat-ken` (สร้าง `skill-finder` ใน LAB 2)

### 1.1 ของแต่ละคนอยู่ที่ไหน (สำคัญ)

ทั้งบริษัทคือโฟลเดอร์ `novatech/` โฟลเดอร์เดียว **ของกลางอยู่ข้างบน** (`people/`, `company-kit/`) ทุกคนอ่านชุดเดียวกัน ส่วน **โต๊ะของแต่ละคนอยู่ใน `desks/`** เขียนได้แค่โต๊ะตัวเอง

[![LAB 1 ของแต่ละคนอยู่ตรงไหนในบริษัท: novatech/ บริษัททั้งหมด มี people/ การ์ดพนักงาน 28 ใบ (อ่าน) และ company-kit/ ไดรฟ์กลาง (อ่าน) · desks/ โต๊ะ 1 โฟลเดอร์ต่อ 1 คน 28 โต๊ะ · sales-nida/ นิดา มี work/ proposal.docx pricing.xlsx และ .claude/skills/sales-proposal/ · md-somchai/ สมชาย MD มี notes/deal-rules.md โน้ตลับ work/ approval.docx และ .claude/skills/deal-approval/ · fin-joy/ จอย มี work/ pricing-internal.xlsx quotation-draft.docx และ .claude/skills/pricing-calc/ · hr-fah/ ฟ้า HR มี work/ ประกาศรับสมัคร .docx และ .claude/skills/jd-writer/ · ml-jay/ เจ ML มี work/ experiment-registry.xlsx รายงาน .docx และ .claude/skills/mlflow-experiment/ · อีก 23 โต๊ะแบบเดียวกัน · ในบริษัทจริง desks/<ชื่อ>/ = คอมของคนนั้น, .claude/skills/ = ~/.claude/skills/, company-kit/ = ไดรฟ์กลาง](img/lab1-folders.png)](img/lab1-folders.png)

| โฟลเดอร์ | คืออะไร | Claude ทำอะไรกับมัน |
|---|---|---|
| `novatech/people/<แผนก>/<ชื่อ>.md` | การ์ดของตัวเอง: เก่งอะไร ทำอะไรซ้ำ ชอบพิมพ์ว่าอะไร | 📖 อ่าน |
| `novatech/company-kit/` | ไดรฟ์กลาง: TOR ลูกค้า ราคา กติกา | 📖 อ่าน |
| `desks/<ชื่อ>/notes/` | โน้ตส่วนตัว (มีแค่ `md-somchai`) | 📖 อ่าน |
| `desks/<ชื่อ>/work/` | ผลงานจริง 1 ชิ้น | ✍️ เขียน |
| `desks/<ชื่อ>/.claude/skills/<ชื่อ skill>/` | **skill ส่วนตัว** | ✍️ เขียน |

โต๊ะของนิดา ก่อนและหลัง LAB 1

```text
ก่อน (seed สร้างให้)          หลัง LAB 1
desks/sales-nida/             desks/sales-nida/
└─ .gitea-token               ├─ .gitea-token
                              ├─ work/                        ← ② ผลงานจริง
                              │  ├─ deal-001-proposal-….docx   (Word)
                              │  └─ deal-001-pricing.xlsx      (Excel)
                              └─ .claude/skills/
                                 └─ sales-proposal/           ← ③ skill ส่วนตัว
                                    ├─ SKILL.md
                                    ├─ references/
                                    └─ scripts/
```

> 💡 `.claude` ขึ้นต้นด้วยจุด จึงเป็น **โฟลเดอร์ซ่อน** ถ้าไม่เห็นใน Explorer/Finder ให้เปิดการแสดงไฟล์ซ่อน (Windows: View → Hidden items · Mac: `Cmd + Shift + .`)

### 1.2 พรอมต์ของแต่ละคน (24 พรอมต์)

🧑 **คิดก่อน** เปิดการ์ดพนักงาน 2–3 ใบใน [`people/`](novatech/people/) แล้วถามตัวเองว่า ถ้าคนนี้ลาออกพรุ่งนี้ ความเก่งของเขาจะไปอยู่ที่ไหน (ทฤษฎีหัวข้อ 18.2)

![พรอมต์ของใครของมัน 1 คน = 1 พรอมต์ = 1 skill: หุ่นยนต์บุรุษไปรษณีย์ส่งการ์ดพรอมต์คนละใบให้โต๊ะ sales-nida, md-somchai, fin-joy และโต๊ะอื่น ๆ อีกหลายโต๊ะ บนแล็ปท็อปแต่ละเครื่องมีโฟลเดอร์ .claude/skills กับไฟล์ SKILL.md (ภาพจำลอง)](img/lab1-prompt-per-desk.png)

**1 คน = 1 พรอมต์ = 1 skill** แต่ละคนมีพรอมต์ของตัวเองเต็ม ๆ บอกชัดว่า **เป็นใคร · ทำงานอะไรด้วยไฟล์ไหน · เก็บเป็น skill ชื่ออะไรไว้ที่ไหน** ทุกพรอมต์ใช้โครงเดียวกัน ต่างกันแค่ 3 ช่องที่ไฮไลต์ในภาพนี้

![LAB 1 พรอมต์เต็มรายคน ตัวอย่างของนิดา: ① ฉันคือใคร ฉันคือ นิดา แก้วมณี (sales-nida) หัวหน้าทีมขาย อ่านการ์ด ../../people/sales/sales-nida.md · ② ทำงานอะไร ร่าง proposal ให้ลูกค้าธนาคารตาม TOR ของ deal-001 ข้อมูลที่ใช้ ../../company-kit/deal-001/tor-bank-queue.md, won-proposals/, price-list.csv เก็บไว้ใน work/ · ③ เก็บเป็น skill ชื่อ sales-proposal ที่ .claude/skills/sales-proposal/ · ตาราง desks/sales-nida/ → sales-proposal, desks/md-somchai/ → deal-approval, desks/fin-joy/ → pricing-calc · ครบ 24 คน 1 โต๊ะ = 1 แชตใหม่ = 1 พรอมต์ของคนนั้น](img/lab1-prompt.png)

**วิธีรัน:** เปิด Claude Code ที่ `novatech/` แล้ววาง **พรอมต์รวมด้านล่างครั้งเดียว** Claude จะแตก **agent ย่อย 1 ตัวต่อ 1 โต๊ะ** แล้วส่งพรอมต์ของแต่ละคนให้เอง ถ้า Claude ขออนุญาตเขียนโฟลเดอร์ `.claude/skills/` ให้กดอนุญาต

**💬 พรอมต์ (ก๊อปอันนี้อันเดียว)** · เปิด Claude Code ที่ `novatech/` · ได้ครบทุกคน

![หน้าต่าง Claude Code วางพรอมต์ LAB 1](img/lab1-paste.png)

```text
ฉันเป็นผู้ดูแลระบบ ช่วยทำ LAB 1 ให้พนักงานทุกคนในครั้งเดียว
พรอมต์ของแต่ละคนอยู่ใน ../_solution/lab1/prompts/<user>.txt (1 ไฟล์ = 1 คน รวม 24 คน ไม่นับ README-block.md)
สำหรับแต่ละคน ให้เปิด agent ย่อยแยก 1 ตัว (1 ตัว = แชตใหม่ของคนนั้น):
- ส่งข้อความในไฟล์ของคนนั้นให้ agent ทุกตัวอักษร และบอกว่าโฟลเดอร์ทำงานคือ desks/<user>/ (path ในพรอมต์นับจากโฟลเดอร์นี้)
- agent เขียนไฟล์ได้เฉพาะใน desks/<user>/ ของตัวเอง ห้ามเปิดโต๊ะของคนอื่น และห้ามเปิดโฟลเดอร์ ../_solution/
- รันพร้อมกันครั้งละ 4 ตัว และข้ามโต๊ะที่มี skill ใน .claude/skills/ อยู่แล้ว
จบแล้วสรุปเป็นตาราง: user · skill ที่ได้ · ไฟล์ใน work/ · มีปัญหาอะไรไหม
```

| ส่วนของพรอมต์ | มีไว้ทำไม |
|---|---|
| agent ย่อย 1 ตัวต่อ 1 คน | agent ย่อยเริ่มจากศูนย์ ไม่เห็นแชตหลัก = **แชตใหม่ของคนนั้น** งานของนิดาจึงไม่ปนกับของ MD |
| ส่งพรอมต์ของคนนั้นทุกตัวอักษร | แต่ละคนได้งานและ skill ของตัวเอง (ดูตัวอย่างพรอมต์รายคนด้านล่าง) |
| เขียนได้เฉพาะโต๊ะตัวเอง · ห้ามเปิด `_solution/` | เหมือนพนักงานจริงที่ใช้คอมของตัวเอง และ `_solution/` มีผลงานเฉลยของทุกคนอยู่ |
| ครั้งละ 4 ตัว | ไม่ให้เครื่องหนักหรือโควตาหมดกลางทาง |
| ข้ามโต๊ะที่มี skill แล้ว | สั่งซ้ำได้ ถ้ารอบแรกค้างกลางทาง ไม่ทับงานที่ทำเสร็จแล้ว |

✅ **ผลจริงของพรอมต์รวม: 24/24 โต๊ะได้ skill · ราว 27 นาที** ([สรุปและผลงานทุกโต๊ะ](_solution/lab1/combined-run/))
- Claude เปิด agent ย่อยครั้งละ 4 ตัว ทุกตัวทำงานแค่ในโต๊ะของตัวเอง ไม่พบการเขียนไฟล์นอกโต๊ะ และไม่มีใครเปิด `_solution/`
- เจอปัญหาเดิมทุกอย่างเหมือนตอนวางทีละโต๊ะ: ทุกคนตีความ `uses` / `next` / `follows` ไม่ตรงกัน (Claude เสนอเองให้ `plat-ken` ออกกติกาหัวไฟล์) และ proposal ของนิดาก็ **ไม่มีภาคผนวก PDPA** เหมือนเดิม (→ 1.5)
- 🧪 รอบแรกรันด้วย `claude -p` แล้วหยุดกลางทางหลัง 9 โต๊ะ เพราะโหมด `-p` ตัดงานเบื้องหลังหลัง 10 นาที จึงวางพรอมต์เดิมซ้ำ (พรอมต์ข้ามโต๊ะที่เสร็จแล้วเอง) ในแอป Claude Code ไม่มีข้อจำกัดนี้ · ถ้ารอบไหนค้างกลางทาง วางพรอมต์เดิมซ้ำได้เลย

> ⏱️ **ไม่อยากรอทั้ง 24 คน** ทำเองแค่ 3 คนที่เป็นตัวเอกของ LAB ถัดไป (`sales-nida`, `md-somchai`, `fin-joy`) แล้วคัดลอกที่เหลือจากผลรันจริงด้วยคำสั่งนี้ (เปิด terminal ที่ `novatech/`) สคริปต์จะข้ามโต๊ะที่ทำเองแล้ว
>
> ```bash
> node ../_solution/tools/copy-lab1-desks.mjs
> ```

**👀 ตัวอย่าง: พรอมต์ที่ agent ย่อยของแต่ละโต๊ะได้รับ** (อ่านอย่างเดียว ไม่ต้องก๊อป พรอมต์รวมส่งให้เองแล้ว · ไฟล์จริงอยู่ใน [`_solution/lab1/prompts/`](_solution/lab1/prompts/))

ทุกคนได้พรอมต์โครงเดียวกัน ต่างกันแค่ ① ฉันคือใคร ② ทำงานอะไรด้วยไฟล์ไหน ③ เก็บเป็น skill ชื่ออะไร (ตามภาพด้านบน)

**3 โต๊ะหลัก** (ตัวเอกของ LAB 4–5)

#### 💼 นิดา `sales-nida` → skill `sales-proposal`

สิ่งที่ agent ย่อยของโต๊ะ `desks/sales-nida/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/sales-nida/work/) · [`skill`](_solution/desks-after-lab1/sales-nida/skills/sales-proposal/)

> ฉันคือ นิดา แก้วมณี (sales-nida) หัวหน้าทีมขาย ฝ่าย Sales · นี่คือโต๊ะของฉัน (novatech/desks/sales-nida/)  
> อ่านการ์ดของฉันก่อน: ../../people/sales/sales-nida.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ร่าง proposal ให้ลูกค้าธนาคารตาม TOR ของ deal-001 พร้อมใบคิดราคา  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/deal-001/tor-bank-queue.md, ../../company-kit/won-proposals/, ../../company-kit/price-list.csv, ../../company-kit/margin-rules.md, ../../company-kit/brand-guide.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ sales-proposal ที่ .claude/skills/sales-proposal/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: sales-nida, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 👔 สมชาย `md-somchai` → skill `deal-approval`

สิ่งที่ agent ย่อยของโต๊ะ `desks/md-somchai/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/md-somchai/work/) · [`skill`](_solution/desks-after-lab1/md-somchai/skills/deal-approval/)

> ฉันคือ สมชาย วงศ์ประเสริฐ (md-somchai) MD (กรรมการผู้จัดการ) ฝ่าย MD / ผู้บริหาร · นี่คือโต๊ะของฉัน (novatech/desks/md-somchai/)  
> อ่านการ์ดของฉันก่อน: ../../people/exec/md-somchai.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: พิจารณาดีล DS-2026-034 ว่าอนุมัติหรือตีกลับ พร้อมเหตุผล  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/deal-summaries/DS-2026-034-muangmai-hospital-portal.md, ../../company-kit/margin-rules.md, ../../company-kit/price-list.csv และโน้ตของฉัน notes/deal-rules.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ deal-approval ที่ .claude/skills/deal-approval/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: md-somchai, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 🧾 จอย `fin-joy` → skill `pricing-calc`

สิ่งที่ agent ย่อยของโต๊ะ `desks/fin-joy/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/fin-joy/work/) · [`skill`](_solution/desks-after-lab1/fin-joy/skills/pricing-calc/)

> ฉันคือ จอย พัฒนสิน (fin-joy) หัวหน้าบัญชี ฝ่าย บัญชี / ธุรการ · นี่คือโต๊ะของฉัน (novatech/desks/fin-joy/)  
> อ่านการ์ดของฉันก่อน: ../../people/finance/fin-joy.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: คิดราคาและกำไรของ deal-001 ให้ Sales  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/price-list.csv, ../../company-kit/margin-rules.md, ../../company-kit/deal-001/tor-bank-queue.md, ../../company-kit/won-proposals/  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ pricing-calc ที่ .claude/skills/pricing-calc/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: fin-joy, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


<details>
<summary>👔 <b>MD / ผู้บริหาร</b> · <code>exec-ploy</code> · <code>cco-wit</code> · <code>cto-nat</code> · <code>cfo-ying</code></summary>

#### 👔 พลอยไพลิน `exec-ploy` → skill `exec-deck`

สิ่งที่ agent ย่อยของโต๊ะ `desks/exec-ploy/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/exec-ploy/work/) · [`skill`](_solution/desks-after-lab1/exec-ploy/skills/exec-deck/)

> ฉันคือ พลอยไพลิน ศรีสุข (exec-ploy) ผู้ช่วยผู้บริหาร ฝ่าย MD / ผู้บริหาร · นี่คือโต๊ะของฉัน (novatech/desks/exec-ploy/)  
> อ่านการ์ดของฉันก่อน: ../../people/exec/exec-ploy.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ทำสไลด์ประชุมผู้บริหารเดือน พ.ย. 2026 (HTML + PDF) ที่ MD อ่านจบใน 5 นาที  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/monthly-kpi.csv, ../../company-kit/brand-guide.md, ../../company-kit/logo.svg  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ exec-deck ที่ .claude/skills/exec-deck/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: exec-ploy, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 👔 วิทย์ `cco-wit` → skill `pipeline-review`

สิ่งที่ agent ย่อยของโต๊ะ `desks/cco-wit/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/cco-wit/work/) · [`skill`](_solution/desks-after-lab1/cco-wit/skills/pipeline-review/)

> ฉันคือ วิทย์ ประภาสกุล (cco-wit) ผู้อำนวยการสายธุรกิจ (CCO) ฝ่าย MD / ผู้บริหาร · นี่คือโต๊ะของฉัน (novatech/desks/cco-wit/)  
> อ่านการ์ดของฉันก่อน: ../../people/exec/cco-wit.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ทบทวน pipeline ดีลทั้งหมด: ดีลไหนควรเร่ง ส่งต่อ ประคอง หรือตีกลับ  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/monthly-kpi.csv, ../../company-kit/deal-summaries/, ../../company-kit/deal-001/, ../../company-kit/deal-002/, ../../company-kit/product/  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ pipeline-review ที่ .claude/skills/pipeline-review/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: cco-wit, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 👔 ณัฐ `cto-nat` → skill `tech-risk-review`

สิ่งที่ agent ย่อยของโต๊ะ `desks/cto-nat/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/cto-nat/work/) · [`skill`](_solution/desks-after-lab1/cto-nat/skills/tech-risk-review/)

> ฉันคือ ณัฐ ธนวัฒน์ (cto-nat) ผู้อำนวยการสายเทคโนโลยี (CTO) ฝ่าย MD / ผู้บริหาร · นี่คือโต๊ะของฉัน (novatech/desks/cto-nat/)  
> อ่านการ์ดของฉันก่อน: ../../people/exec/cto-nat.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ทบทวนความเสี่ยงทางเทคนิคของ deal-001 ก่อนรับงาน  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/deal-001/tor-bank-queue.md, ../../company-kit/incident-2026-09.md, ../../company-kit/deploy-runbook.md, ../../company-kit/arch-standards.md, ../../company-kit/ml-queue-forecast/, ../../company-kit/qa/  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ tech-risk-review ที่ .claude/skills/tech-risk-review/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: cto-nat, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 👔 หญิง `cfo-ying` → skill `cost-headcount-review`

สิ่งที่ agent ย่อยของโต๊ะ `desks/cfo-ying/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/cfo-ying/work/) · [`skill`](_solution/desks-after-lab1/cfo-ying/skills/cost-headcount-review/)

> ฉันคือ หญิง ศรีพัฒนา (cfo-ying) ผู้อำนวยการสายบริหารและการเงิน (CFO) ฝ่าย MD / ผู้บริหาร · นี่คือโต๊ะของฉัน (novatech/desks/cfo-ying/)  
> อ่านการ์ดของฉันก่อน: ../../people/exec/cfo-ying.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: สรุปรายได้ ต้นทุน และกำลังคนเดือน ต.ค. 2026 ให้ MD: เงินพอไหม ควรรับคนเพิ่มหรือยัง  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/monthly-kpi.csv, ../../company-kit/margin-rules.md, ../../company-kit/jd-template.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ cost-headcount-review ที่ .claude/skills/cost-headcount-review/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: cfo-ying, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>💼 <b>Sales</b> · <code>sales-krit</code></summary>

#### 💼 กฤต `sales-krit` → skill `follow-up-email`

สิ่งที่ agent ย่อยของโต๊ะ `desks/sales-krit/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/sales-krit/work/) · [`skill`](_solution/desks-after-lab1/sales-krit/skills/follow-up-email/)

> ฉันคือ กฤต ธนากร (sales-krit) เซลส์ ฝ่าย Sales · นี่คือโต๊ะของฉัน (novatech/desks/sales-krit/)  
> อ่านการ์ดของฉันก่อน: ../../people/sales/sales-krit.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: เขียนอีเมลติดตามลูกค้า deal-002 หลังประชุมวันที่ 28 ต.ค. 2026  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/meeting-notes/2026-10-28-bank-meeting.md, ../../company-kit/deal-002/tor-bank-dispute.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ follow-up-email ที่ .claude/skills/follow-up-email/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: sales-krit, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🧩 <b>Presales / SA</b> · <code>sa-ton</code> · <code>sa-ice</code></summary>

#### 🧩 ต้นตระกูล `sa-ton` → skill `req-to-spec`

สิ่งที่ agent ย่อยของโต๊ะ `desks/sa-ton/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/sa-ton/work/) · [`skill`](_solution/desks-after-lab1/sa-ton/skills/req-to-spec/)

> ฉันคือ ต้นตระกูล มีชัย (sa-ton) SA อาวุโส ฝ่าย Presales / SA · นี่คือโต๊ะของฉัน (novatech/desks/sa-ton/)  
> อ่านการ์ดของฉันก่อน: ../../people/sa/sa-ton.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: แปลง TOR ของ deal-001 เป็น spec และแผนทดสอบ  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/deal-001/tor-bank-queue.md, ../../company-kit/arch-standards.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ req-to-spec ที่ .claude/skills/req-to-spec/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: sa-ton, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 🧩 ไอศวรรย์ `sa-ice` → skill `arch-template`

สิ่งที่ agent ย่อยของโต๊ะ `desks/sa-ice/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/sa-ice/work/) · [`skill`](_solution/desks-after-lab1/sa-ice/skills/arch-template/)

> ฉันคือ ไอศวรรย์ บุญมา (sa-ice) SA ฝ่าย Presales / SA · นี่คือโต๊ะของฉัน (novatech/desks/sa-ice/)  
> อ่านการ์ดของฉันก่อน: ../../people/sa/sa-ice.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: วาดแผนภาพ architecture ของระบบจองคิวสาขา (deal-001) ตามมาตรฐานบริษัท  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/arch-standards.md, ../../company-kit/deal-001/tor-bank-queue.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ arch-template ที่ .claude/skills/arch-template/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: sa-ice, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>📦 <b>Product</b> · <code>pm-beam</code> · <code>pm-gift</code></summary>

#### 📦 บีม `pm-beam` → skill `prd-writer`

สิ่งที่ agent ย่อยของโต๊ะ `desks/pm-beam/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/pm-beam/work/) · [`skill`](_solution/desks-after-lab1/pm-beam/skills/prd-writer/)

> ฉันคือ บีม ศิริวัฒน์ (pm-beam) หัวหน้าฝ่ายผลิตภัณฑ์ (Head of Product) ฝ่าย Product · นี่คือโต๊ะของฉัน (novatech/desks/pm-beam/)  
> อ่านการ์ดของฉันก่อน: ../../people/product/pm-beam.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: จัดลำดับฟีเจอร์ NovaQueue จาก feedback ไตรมาส 3 แล้วเขียน PRD ฟีเจอร์ที่ควรทำก่อน 1 ฉบับ  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/product/novaqueue-feedback-2026-q3.md, ../../company-kit/product/novaqueue-overview.md, ../../company-kit/product/product-lifecycle-policy.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ prd-writer ที่ .claude/skills/prd-writer/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: pm-beam, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 📦 กิ๊ฟ `pm-gift` → skill `product-sunset`

สิ่งที่ agent ย่อยของโต๊ะ `desks/pm-gift/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/pm-gift/work/) · [`skill`](_solution/desks-after-lab1/pm-gift/skills/product-sunset/)

> ฉันคือ กิ๊ฟ วรรณศิริ (pm-gift) Product Manager (ดูแลวงจรชีวิตผลิตภัณฑ์) ฝ่าย Product · นี่คือโต๊ะของฉัน (novatech/desks/pm-gift/)  
> อ่านการ์ดของฉันก่อน: ../../people/product/pm-gift.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: วางแผนเลิกให้บริการ NovaQueue v1 พร้อมร่างประกาศแจ้งลูกค้า  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/product/novaqueue-v1-customers.csv, ../../company-kit/product/product-lifecycle-policy.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ product-sunset ที่ .claude/skills/product-sunset/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: pm-gift, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>💻 <b>Dev</b> · <code>dev-pond</code> · <code>dev-mew</code></summary>

#### 💻 ปอนด์ `dev-pond` → skill `coding-standard`

สิ่งที่ agent ย่อยของโต๊ะ `desks/dev-pond/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/dev-pond/work/) · [`skill`](_solution/desks-after-lab1/dev-pond/skills/coding-standard/)

> ฉันคือ ปอนด์ เจริญกิจ (dev-pond) tech lead ฝ่าย Dev · นี่คือโต๊ะของฉัน (novatech/desks/dev-pond/)  
> อ่านการ์ดของฉันก่อน: ../../people/dev/dev-pond.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: รีวิว PR ตัวอย่าง 1 ชิ้นตามมาตรฐานโค้ดของทีม (ถ้าไม่มีโค้ดจริงให้ทำ PR สมมติขึ้นมาเอง)  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/coding-rules.md, ../../company-kit/project-scaffold-notes.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ coding-standard ที่ .claude/skills/coding-standard/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: dev-pond, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 💻 มิว `dev-mew` → skill `project-scaffold`

สิ่งที่ agent ย่อยของโต๊ะ `desks/dev-mew/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/dev-mew/work/) · [`skill`](_solution/desks-after-lab1/dev-mew/skills/project-scaffold/)

> ฉันคือ มิว อินทรสุวรรณ (dev-mew) Dev ฝ่าย Dev · นี่คือโต๊ะของฉัน (novatech/desks/dev-mew/)  
> อ่านการ์ดของฉันก่อน: ../../people/dev/dev-mew.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ขึ้นโปรเจกต์ระบบสมาชิก + ชำระเงินใหม่ให้รันได้และ test ผ่าน  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/project-scaffold-notes.md, ../../company-kit/coding-rules.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ project-scaffold ที่ .claude/skills/project-scaffold/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: dev-mew, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🧪 <b>QA</b> · <code>qa-mint</code> · <code>qa-bank</code></summary>

#### 🧪 มินท์ `qa-mint` → skill `test-from-plan`

สิ่งที่ agent ย่อยของโต๊ะ `desks/qa-mint/` ได้รับ · ผลจริง: [`skill`](_solution/desks-after-lab1/qa-mint/skills/test-from-plan/)

> ฉันคือ มินท์ รัตนพงศ์ (qa-mint) QA lead ฝ่าย QA · นี่คือโต๊ะของฉัน (novatech/desks/qa-mint/)  
> อ่านการ์ดของฉันก่อน: ../../people/qa/qa-mint.md  
> skill test-from-plan ของฉันทำเสร็จแล้วตั้งแต่ส่วน 02 อยู่ที่ ../../company-kit/qa/test-from-plan-skill/  
> คัดลอกมาเป็น skill ส่วนตัวที่ .claude/skills/test-from-plan/ แล้วเติม metadata ในหัวไฟล์: owner: qa-mint, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> ห้ามแก้เนื้อหาขั้นตอนเดิม จบแล้วสรุปสั้น ๆ ว่าเติมอะไรและเพราะอะไร  


#### 🧪 แบงค์ `qa-bank` → skill `bug-report`

สิ่งที่ agent ย่อยของโต๊ะ `desks/qa-bank/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/qa-bank/work/) · [`skill`](_solution/desks-after-lab1/qa-bank/skills/bug-report/)

> ฉันคือ แบงค์ ศักดิ์ดี (qa-bank) QA ฝ่าย QA · นี่คือโต๊ะของฉัน (novatech/desks/qa-bank/)  
> อ่านการ์ดของฉันก่อน: ../../people/qa/qa-bank.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: เขียนรายงานบั๊กจาก log ของ test ที่ล้ม  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/qa/failed-test-log.txt, ../../company-kit/qa/bug-template.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ bug-report ที่ .claude/skills/bug-report/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: qa-bank, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>⚙️ <b>DevOps</b> · <code>ops-art</code> · <code>ops-fon</code></summary>

#### ⚙️ อาร์ต `ops-art` → skill `deploy-checklist`

สิ่งที่ agent ย่อยของโต๊ะ `desks/ops-art/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/ops-art/work/) · [`skill`](_solution/desks-after-lab1/ops-art/skills/deploy-checklist/)

> ฉันคือ อาร์ต พงษ์ไพบูลย์ (ops-art) DevOps lead ฝ่าย DevOps · นี่คือโต๊ะของฉัน (novatech/desks/ops-art/)  
> อ่านการ์ดของฉันก่อน: ../../people/devops/ops-art.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ทำ checklist ขึ้นระบบจริงรอบ 2026.11  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/deploy-runbook.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ deploy-checklist ที่ .claude/skills/deploy-checklist/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: ops-art, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### ⚙️ ฝน `ops-fon` → skill `postmortem`

สิ่งที่ agent ย่อยของโต๊ะ `desks/ops-fon/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/ops-fon/work/) · [`skill`](_solution/desks-after-lab1/ops-fon/skills/postmortem/)

> ฉันคือ ฝน จันทร์เพ็ญ (ops-fon) DevOps ฝ่าย DevOps · นี่คือโต๊ะของฉัน (novatech/desks/ops-fon/)  
> อ่านการ์ดของฉันก่อน: ../../people/devops/ops-fon.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: เขียน postmortem เหตุระบบ payment ล่มเดือน ก.ย. 2026 แบบไม่โทษคน  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/incident-2026-09.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ postmortem ที่ .claude/skills/postmortem/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: ops-fon, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🤖 <b>ML / MLOps</b> · <code>ml-jay</code> · <code>ml-pim</code></summary>

#### 🤖 เจ `ml-jay` → skill `mlflow-experiment`

สิ่งที่ agent ย่อยของโต๊ะ `desks/ml-jay/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/ml-jay/work/) · [`skill`](_solution/desks-after-lab1/ml-jay/skills/mlflow-experiment/)

> ฉันคือ เจ วรวุฒิ (ml-jay) MLOps lead ฝ่าย ML / MLOps · นี่คือโต๊ะของฉัน (novatech/desks/ml-jay/)  
> อ่านการ์ดของฉันก่อน: ../../people/mlops/ml-jay.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: จัดระเบียบผลการทดลองโมเดลพยากรณ์คิวประจำสัปดาห์ และเทียบทุกรอบ  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/ml-queue-forecast/experiment-results.csv, ../../company-kit/ml-queue-forecast/notes.md, ../../company-kit/deal-001/tor-bank-queue.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ mlflow-experiment ที่ .claude/skills/mlflow-experiment/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: ml-jay, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 🤖 พิมพ์ชนก `ml-pim` → skill `model-release`

สิ่งที่ agent ย่อยของโต๊ะ `desks/ml-pim/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/ml-pim/work/) · [`skill`](_solution/desks-after-lab1/ml-pim/skills/model-release/)

> ฉันคือ พิมพ์ชนก ทองดี (ml-pim) ML engineer ฝ่าย ML / MLOps · นี่คือโต๊ะของฉัน (novatech/desks/ml-pim/)  
> อ่านการ์ดของฉันก่อน: ../../people/mlops/ml-pim.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ทำแผนปล่อยโมเดลพยากรณ์คิว r03 พร้อมเกณฑ์ถอยกลับ  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/ml-queue-forecast/, ../../company-kit/deploy-runbook.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ model-release ที่ .claude/skills/model-release/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: ml-pim, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🤝 <b>HR</b> · <code>hr-fah</code> · <code>hr-oat</code></summary>

#### 🤝 ฟ้า `hr-fah` → skill `jd-writer`

สิ่งที่ agent ย่อยของโต๊ะ `desks/hr-fah/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/hr-fah/work/) · [`skill`](_solution/desks-after-lab1/hr-fah/skills/jd-writer/)

> ฉันคือ ฟ้า ประเสริฐวงศ์ (hr-fah) HR BP ฝ่าย HR · นี่คือโต๊ะของฉัน (novatech/desks/hr-fah/)  
> อ่านการ์ดของฉันก่อน: ../../people/hr/hr-fah.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: เขียนประกาศรับสมัคร Senior Full-stack Developer สำหรับโปรเจกต์ deal-001  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/jd-template.md, ../../company-kit/hr-benefits-faq.md, ../../company-kit/brand-guide.md, ../../company-kit/deal-001/tor-bank-queue.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ jd-writer ที่ .claude/skills/jd-writer/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: hr-fah, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


#### 🤝 โอ๊ต `hr-oat` → skill `onboarding-pack`

สิ่งที่ agent ย่อยของโต๊ะ `desks/hr-oat/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/hr-oat/work/) · [`skill`](_solution/desks-after-lab1/hr-oat/skills/onboarding-pack/)

> ฉันคือ โอ๊ต สุขสวัสดิ์ (hr-oat) HR ฝ่าย HR · นี่คือโต๊ะของฉัน (novatech/desks/hr-oat/)  
> อ่านการ์ดของฉันก่อน: ../../people/hr/hr-oat.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: เตรียมชุดต้อนรับ Dev คนใหม่ที่จะเข้างานวันจันทร์ 9 พ.ย. 2026  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/onboarding-notes.md, ../../company-kit/hr-benefits-faq.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ onboarding-pack ที่ .claude/skills/onboarding-pack/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: hr-oat, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🧾 <b>บัญชี / ธุรการ</b> · <code>fin-nok</code></summary>

#### 🧾 นก `fin-nok` → skill `invoice-check`

สิ่งที่ agent ย่อยของโต๊ะ `desks/fin-nok/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/fin-nok/work/) · [`skill`](_solution/desks-after-lab1/fin-nok/skills/invoice-check/)

> ฉันคือ นก ศรีอำไพ (fin-nok) บัญชี ฝ่าย บัญชี / ธุรการ · นี่คือโต๊ะของฉัน (novatech/desks/fin-nok/)  
> อ่านการ์ดของฉันก่อน: ../../people/finance/fin-nok.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ตรวจใบแจ้งหนี้ INV-2026-0142 ก่อนส่งลูกค้า  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/invoices/INV-2026-0142.md, ../../company-kit/invoices/invoicing-rules.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ invoice-check ที่ .claude/skills/invoice-check/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: fin-nok, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

<details>
<summary>🏛️ <b>ทีมกลาง (platform)</b> · <code>plat-may</code></summary>

#### 🏛️ เมย์ `plat-may` → skill `customer-data-policy`

สิ่งที่ agent ย่อยของโต๊ะ `desks/plat-may/` ได้รับ · ผลจริง: [`work/`](_solution/desks-after-lab1/plat-may/work/) · [`skill`](_solution/desks-after-lab1/plat-may/skills/customer-data-policy/)

> ฉันคือ เมย์ อรุณรัตน์ (plat-may) ทีมกลาง (platform) ฝ่าย ทีมกลาง (platform) · นี่คือโต๊ะของฉัน (novatech/desks/plat-may/)  
> อ่านการ์ดของฉันก่อน: ../../people/platform/plat-may.md  
> 1\. ลงมือทำงานจริง 1 ชิ้น: ตรวจใบแจ้งหนี้ INV-2026-0142 ตามนโยบายข้อมูลลูกค้า  
> &emsp;ข้อมูลที่ใช้: ../../company-kit/customer-data-policy.md, ../../company-kit/invoices/INV-2026-0142.md, ../../company-kit/brand-guide.md  
> &emsp;เก็บผลงานไว้ใน work/  
> 2\. เก็บวิธีทำงานนี้เป็น skill ส่วนตัวชื่อ customer-data-policy ที่ .claude/skills/customer-data-policy/  
> &emsp;\- หัวไฟล์มี name, description (ใช้คำที่ฉันชอบพิมพ์ในการ์ด) และ metadata: owner: plat-may, layer: personal, version, uses, next, follows (ชื่อ skill ของคนอื่นดูได้ใน ../../people/README.md)  
> &emsp;\- skill เล็ก โฟกัสเรื่องเดียว และต้องใช้ได้ที่เครื่องคนอื่น: ความรู้ที่จำเป็นจาก company-kit ให้สรุปไว้ใน references/ ของ skill  
> จบแล้วสรุปสั้น ๆ: ทำงานอะไร ได้ไฟล์อะไร skill มีไฟล์อะไรบ้าง และมีจุดไหนที่ต้องตัดสินใจเอง  


</details>

> 🧪 **หมายเหตุผู้สอน:** ภาพและตารางใน 1.3–1.5 มาจากรอบแรกของบทนี้ ที่วางพรอมต์โครงเดียวกันแบบสั้น ([`prompt.txt`](_solution/lab1/prompt.txt)) ทีละโต๊ะ ส่วนพรอมต์รวมด้านบนรันจริงอีกรอบ ได้ผลแบบเดียวกัน ([ผลงานรอบพรอมต์รวม](_solution/lab1/combined-run/desks/))

`metadata` ในหัวไฟล์คือ "การ์ดประจำตัว" ของ skill ที่ทีมกลางจะใช้จัดคลังและวาดกราฟ (ทฤษฎีหัวข้อ 21.1)

| ช่อง | ความหมาย | ตัวอย่างของนิดา |
|---|---|---|
| `owner` | เจ้าของ skill | `sales-nida` |
| `layer` | ชั้นของ skill ตอนนี้ทุกตัวเป็น `personal` | `personal` |
| `version` | เลขเวอร์ชัน แก้แล้วต้องเพิ่ม | `1.0.0` |
| `uses` | skill อื่นที่ **เรียกใช้** ระหว่างทำงาน | `[pricing-calc]` |
| `next` | งาน **ถัดไป** ที่มักทำต่อ | `[deal-approval, follow-up-email, req-to-spec]` |
| `follows` | **นโยบาย** ที่ต้องทำตาม | `[customer-data-policy]` |

### 1.3 ตัวอย่าง 5 โต๊ะ

ผลรันจริงของ 3 โต๊ะที่ผู้เรียนต้องทำเอง (นิดา · MD · จอย) และอีก 2 โต๊ะจากแผนกที่งานหน้าตาต่างออกไป (HR · ML) แต่ละคนมี 2 ภาพ: **ผังโฟลเดอร์ของโต๊ะหลังจบ LAB 1 ครบทุกไฟล์** (🟧 ส้ม = ผลงานใน `work/` · 🟩 เขียว = skill ใน `.claude/skills/`) และ **หน้าเอกสารจริง** ที่เปิดด้วย Word / Excel

> 📄 **ทำไมมีทั้ง .docx/.xlsx และ .md:** ในบริษัทจริงงานส่งกันเป็น Word / Excel Claude เขียนผลงานเป็น `.md` ตอนรัน แล้วเราแปลงเป็น Word / Excel ด้วย [`lab1-office-files.py`](_solution/tools/lab1-office-files.py) (เนื้อหาเดิมทุกตัวอักษร ตัวเลขใน Excel เป็นสูตร คำนวณได้ยอดตรงกับที่ Claude คิด) · ถ้าอยากให้ Claude ออกเป็น Word / Excel เอง เติมในพรอมต์ว่า "เก็บผลงานเป็นไฟล์ Word/Excel"

#### 💼 นิดา หัวหน้าทีมขาย → `sales-proposal`

![โต๊ะของนิดา หัวหน้าทีมขาย desks/sales-nida/ (4 นาที 4 วินาที): อ่าน people/sales/sales-nida.md, company-kit/deal-001/tor-bank-queue.md, won-proposals/, price-list.csv, margin-rules.md · .gitea-token บัตรผ่าน · work/ มี deal-001-proposal-nakhonluang-queue.docx (Word proposal 9 หัวข้อ 4,780,000 บาท margin 31.6%), deal-001-pricing.xlsx (Excel ใบคิดราคา), deal-001-internal-notes.md, deal-001-pricing-input.json และต้นฉบับ .md · .claude/skills/sales-proposal/ มี SKILL.md, references/ (proposal-template.md, winning-patterns.md, pricing-rules.md, สำเนา price-list.csv, สำเนา pdpa-rules.md, checklist.md), scripts/price.py · proposal ไม่มีภาคผนวก PDPA](img/lab1-desk-sales-nida.png)

[![หน้าแรกของ deal-001-proposal-nakhonluang-queue.docx เปิดด้วย Word: หัวกระดาษ บริษัท โนวาเทค จำกัด ข้อเสนอโครงการ · ข้อเสนอโครงการระบบจองคิวสาขาและพยากรณ์ปริมาณคิว เสนอต่อธนาคารนครหลวงพัฒนา อ้างอิง TOR NLP-PROC-2026-114 · 1 บทสรุปผู้บริหาร มูลค่า 4,780,000 บาท ไม่รวม VAT · 2 ความเข้าใจความต้องการ ตารางข้อ TOR กับสิ่งที่เราส่งมอบ](img/lab1-doc-sales-nida.png)](img/lab1-doc-sales-nida.png)

📂 ไฟล์จริง: [`proposal.docx`](_solution/desks-after-lab1/sales-nida/work/deal-001-proposal-nakhonluang-queue.docx) · [`pricing.xlsx`](_solution/desks-after-lab1/sales-nida/work/deal-001-pricing.xlsx) · [`work/`](_solution/desks-after-lab1/sales-nida/work/) · [`sales-proposal/`](_solution/desks-after-lab1/sales-nida/skills/sales-proposal/)

#### 👔 สมชาย MD → `deal-approval`

![โต๊ะของสมชาย MD desks/md-somchai/ (2 นาที 37 วินาที): อ่าน people/exec/md-somchai.md, company-kit/deal-summaries/DS-2026-034, margin-rules.md, price-list.csv · .gitea-token · notes/deal-rules.md โน้ตลับมีกฎภาคผนวก PDPA · work/DS-2026-034/ มี approval.docx (Word บันทึกผลพิจารณา ตีกลับ margin หลังบวก buffer 11.8%), deal-input.json และต้นฉบับ approval.md · .claude/skills/deal-approval/ มี SKILL.md, references/ (approval-rules.md มีกฎภาคผนวก PDPA, approval-template.md, สำเนา price-list.csv), scripts/deal_check.py](img/lab1-desk-md-somchai.png)

[![หน้าแรกของ approval.docx เปิดด้วย Word: หัวกระดาษ บันทึกผลพิจารณาดีล (ภายใน) · ผลพิจารณาดีล DS-2026-034 พอร์ทัลผู้ป่วยและนัดหมายออนไลน์ · ตารางสรุป ลูกค้าโรงพยาบาลเมืองใหม่ มูลค่า 3,307,000 บาท margin 18.0% ถ้าเติม buffer 11.8% ผลตีกลับ · เหตุผล 5 ข้อ · ตรวจตามเกณฑ์ 7 ข้อ](img/lab1-doc-md-somchai.png)](img/lab1-doc-md-somchai.png)

📂 ไฟล์จริง: [`approval.docx`](_solution/desks-after-lab1/md-somchai/work/DS-2026-034/approval.docx) · [`notes/deal-rules.md`](novatech/seed/notes/md-somchai/deal-rules.md) · [`work/`](_solution/desks-after-lab1/md-somchai/work/DS-2026-034/) · [`deal-approval/`](_solution/desks-after-lab1/md-somchai/skills/deal-approval/)

#### 🧾 จอย หัวหน้าบัญชี → `pricing-calc`

![โต๊ะของจอย หัวหน้าบัญชี desks/fin-joy/ (3 นาที 51 วินาที): อ่าน people/finance/fin-joy.md, company-kit/price-list.csv, margin-rules.md, deal-001/, won-proposals/ · .gitea-token · work/ มี deal-001-B-pricing-internal.xlsx (Excel ใบคิดราคาภายใน ฉบับเข้างบ 4,800,000 บาท margin 27.1%), deal-001-B-quotation-draft.docx (Word ร่างตารางราคาให้ Sales), ไฟล์ json 2 ไฟล์ และต้นฉบับ .md 4 ไฟล์ · .claude/skills/pricing-calc/ มี SKILL.md, references/ (margin-rules.md, estimate-benchmarks.md, สำเนา price-list.csv), assets/example-deal.json, scripts/price_calc.py](img/lab1-desk-fin-joy.png)

[![deal-001-B-pricing-internal.xlsx เปิดด้วย Excel: ตารางคิดราคา (ภายใน) deal-001 ฉบับ B เข้างบ 4.8M คอลัมน์ รหัส รายการ ประเมิน จำนวนรวม buffer หน่วย ราคาต่อหน่วย ราคาขาย ต้นทุนต่อหน่วย ต้นทุน margin บรรทัด หมายเหตุ 13 รายการ ส่วนลดพิเศษ -619,000 รวมราคาขาย 4,800,000 ต้นทุน 3,497,500 margin 27.1% VAT 336,000 รวมทั้งสิ้น 5,136,000 ผู้อนุมัติ MD](img/lab1-doc-fin-joy.png)](img/lab1-doc-fin-joy.png)

📂 ไฟล์จริง: [`pricing-internal.xlsx`](_solution/desks-after-lab1/fin-joy/work/deal-001-B-pricing-internal.xlsx) · [`quotation-draft.docx`](_solution/desks-after-lab1/fin-joy/work/deal-001-B-quotation-draft.docx) · [`work/`](_solution/desks-after-lab1/fin-joy/work/) · [`pricing-calc/`](_solution/desks-after-lab1/fin-joy/skills/pricing-calc/)

#### 🤝 ฟ้า หัวหน้าฝ่าย HR → `jd-writer`

![โต๊ะของฟ้า หัวหน้าฝ่าย HR desks/hr-fah/ (2 นาที 10 วินาที): อ่าน people/hr/hr-fah.md, company-kit/jd-template.md, hr-benefits-faq.md, brand-guide.md, deal-001/ · .gitea-token · work/ มี NVT-JOB-2026-021-senior-fullstack.docx (Word ประกาศรับสมัคร 6 หัวข้อ เงินเดือน 75,000–105,000), NVT-JOB-2026-021-check.md ตารางตรวจตามกติกา และต้นฉบับ .md · .claude/skills/jd-writer/ มี SKILL.md, references/ (jd-rules.md, benefits.md, example-jd.md) · ไม่ใส่ชื่อธนาคารเพราะ NDA ไม่ระบุเพศหรืออายุ](img/lab1-desk-hr-fah.png)

[![หน้าแรกของ NVT-JOB-2026-021-senior-fullstack.docx เปิดด้วย Word: หัวกระดาษ ประกาศรับสมัครงาน NVT-JOB-2026-021 · Senior Full-stack Developer โปรเจกต์ระบบจองคิวสาขาธนาคาร · สิ่งที่คุณจะได้ทำ · สิ่งที่เรามองหา · จะดีมากถ้ามี · ทีมและวิธีทำงาน](img/lab1-doc-hr-fah.png)](img/lab1-doc-hr-fah.png)

📂 ไฟล์จริง: [`ประกาศ .docx`](_solution/desks-after-lab1/hr-fah/work/NVT-JOB-2026-021-senior-fullstack.docx) · [`work/`](_solution/desks-after-lab1/hr-fah/work/) · [`jd-writer/`](_solution/desks-after-lab1/hr-fah/skills/jd-writer/)

#### 🤖 เจ หัวหน้าทีม ML → `mlflow-experiment`

![โต๊ะของเจ หัวหน้าทีม ML desks/ml-jay/ (3 นาที 27 วินาที): อ่าน people/mlops/ml-jay.md, company-kit/ml-queue-forecast/experiment-results.csv, notes.md, deal-001/tor-bank-queue.md · .gitea-token · work/ มี experiment-registry.xlsx (Excel ทะเบียน run ทุกรอบ + แผน r02b r03b), 2026-W45-queue-forecast-experiments.docx (Word รายงานประจำสัปดาห์), experiment-registry.csv และต้นฉบับ .md · .claude/skills/mlflow-experiment/ มี SKILL.md, references/ (run-record-standard.md, queue-forecast-context.md, สำเนา data-policy-summary.md), assets/weekly-report-template.md, scripts/compare_runs.py · จับได้ว่า r03 ใช้ข้อมูลคนละชุดกับ r02 จึงให้แค่สถานะ candidate](img/lab1-desk-ml-jay.png)

[![experiment-registry.xlsx เปิดด้วย Excel: ทะเบียนการทดลองโมเดลพยากรณ์คิวสาขา เกณฑ์ TOR MAPE ≤ 20% · r01 baseline-ma4w moving average ข้อมูล v3 40 สาขา MAPE 31.5 production · r02 gbm-base LightGBM v3 MAPE 19.8 superseded · r03 gbm-holiday LightGBM v4 38 สาขา MAPE 15.2 candidate · r02b และ r03b planned · สีพื้นแถวตามสถานะ](img/lab1-doc-ml-jay.png)](img/lab1-doc-ml-jay.png)

📂 ไฟล์จริง: [`experiment-registry.xlsx`](_solution/desks-after-lab1/ml-jay/work/experiment-registry.xlsx) · [`รายงาน .docx`](_solution/desks-after-lab1/ml-jay/work/2026-W45-queue-forecast-experiments.docx) · [`work/`](_solution/desks-after-lab1/ml-jay/work/) · [`mlflow-experiment/`](_solution/desks-after-lab1/ml-jay/skills/mlflow-experiment/)

> 📌 ในโฟลเดอร์เฉลย skill เก็บไว้ที่ `_solution/desks-after-lab1/<ชื่อ>/skills/` (ไม่มีจุดนำหน้า จะได้เปิดดูบน GitHub ง่าย) แต่ในโต๊ะจริงของผู้เรียนอยู่ที่ `desks/<ชื่อ>/.claude/skills/` ตามภาพ

### 1.4 ทุกคนทำงานอะไร (ผลจริง 24 โต๊ะ)

✅ **24/24 โต๊ะได้ skill** · ค่ากลาง 3 นาที 23 วินาทีต่อโต๊ะ · skill ส่วนใหญ่มี 4–8 ไฟล์ ([คำตอบของ Claude ทุกโต๊ะ](_solution/lab1/claude-summaries.md) · [skill และ `work/` ของทุกคน](_solution/desks-after-lab1/))

| แผนก | คน | ข้อมูลที่ใช้ใน `company-kit/` | งานจริง 1 ชิ้น (`work/`) | skill ที่ได้ |
|---|---|---|---|---|
| MD | `md-somchai` | `deal-summaries/` + โน้ตลับ `notes/deal-rules.md` | พิจารณาดีล DS-2026-034 → ตีกลับ | `deal-approval` |
| | `exec-ploy` | `monthly-kpi.csv`, `brand-guide.md` | สไลด์ประชุมผู้บริหาร พ.ย. 2026 (HTML + PDF) | `exec-deck` |
| ผู้บริหารสาย 🆕 | `cco-wit` | `monthly-kpi.csv`, `deal-summaries/`, `deal-001/`, `deal-002/`, `product/` | ทบทวน pipeline 4 ดีล: เร่ง/ส่ง/ประคอง/ตีกลับ · **จับได้ว่า รพ.เมืองใหม่ ที่ Sales เรียก "ลูกค้าใหม่" เป็นลูกค้า NovaQueue v1 อยู่แล้ว** | `pipeline-review` |
| | `cto-nat` | `incident-2026-09.md`, `deploy-runbook.md`, `arch-standards.md`, `ml-queue-forecast/`, `qa/` | ทบทวนความเสี่ยงเทคนิค deal-001: รับได้แบบมีเงื่อนไข · เจอใบรับรอง mTLS ต่อมือแบบเดียวกับเหตุ ShopDee ล่ม | `tech-risk-review` |
| | `cfo-ying` | `monthly-kpi.csv`, `margin-rules.md`, `jd-template.md` | สรุปรายได้ ต้นทุน กำลังคน ต.ค.: กำไรขั้นต้นต่ำกว่าเป้า 228,480 บาท · รับ Senior Full-stack ได้ · ML รอผล deal-001 | `cost-headcount-review` |
| Sales | `sales-nida` | `deal-001/`, `won-proposals/`, `price-list.csv` | proposal ธนาคารนครหลวงพัฒนา + ใบคิดราคา | `sales-proposal` |
| | `sales-krit` | `meeting-notes/` | อีเมลติดตามลูกค้า deal-002 | `follow-up-email` |
| SA | `sa-ton` | `deal-001/`, `arch-standards.md` | spec จาก TOR deal-001 | `req-to-spec` |
| | `sa-ice` | `arch-standards.md` | แผนภาพ architecture ระบบจองคิว | `arch-template` |
| Product 🆕 | `pm-beam` | `product/novaqueue-feedback-2026-q3.md`, `product/product-lifecycle-policy.md` | จัดลำดับฟีเจอร์ + PRD "เตือนก่อนถึงคิวผ่าน LINE" (ตัดเบอร์ลูกค้าใน ticket ออกเอง) | `prd-writer` |
| | `pm-gift` | `product/novaqueue-v1-customers.csv`, `product/product-lifecycle-policy.md` | แผนปิด NovaQueue v1 วันที่ 30 ก.ย. 2027 (ไม่ปิดก่อน MA หมด · ค่า MA 905,000 บาทต้องให้ MD อนุมัติ) + ร่างประกาศ | `product-sunset` |
| Dev | `dev-pond` | `coding-rules.md` | รีวิว PR ตัวอย่างตามมาตรฐานทีม | `coding-standard` |
| | `dev-mew` | `project-scaffold-notes.md` | ขึ้นโปรเจกต์จริง รัน test 24/24 + E2E 4/4 (ช้าสุด 23 นาที · skill 75 ไฟล์เพราะเก็บโครงโปรเจกต์ทั้งชุด) | `project-scaffold` |
| QA | `qa-mint` | — (มี skill จากส่วน 02 แล้ว) | คัดลอก `test-from-plan` แล้วเติมหัวไฟล์ ([พรอมต์สั้นกว่า](_solution/lab1/prompt-qa-mint.txt) · เร็วสุด 50 วินาที) | `test-from-plan` |
| | `qa-bank` | `qa/failed-test-log.txt` | รายงานบั๊กจาก log ที่ล้ม | `bug-report` |
| DevOps | `ops-art` | `deploy-runbook.md` | checklist ขึ้นระบบรอบ 2026.11 | `deploy-checklist` |
| | `ops-fon` | `incident-2026-09.md` | postmortem payment ล่ม 47 นาที | `postmortem` |
| ML | `ml-jay` | `ml-queue-forecast/` | ทะเบียนผลทดลองโมเดลพยากรณ์คิว | `mlflow-experiment` |
| | `ml-pim` | `ml-queue-forecast/` | เอกสารปล่อยโมเดล r03 | `model-release` |
| HR | `hr-fah` | `jd-template.md` | ประกาศรับ Senior Full-stack Developer | `jd-writer` |
| | `hr-oat` | `onboarding-notes.md`, `hr-benefits-faq.md` | แพ็กต้อนรับ Dev คนใหม่ | `onboarding-pack` |
| บัญชี | `fin-joy` | `price-list.csv`, `margin-rules.md` | คิดราคาและกำไร deal-001 | `pricing-calc` |
| | `fin-nok` | `invoices/` | ตรวจใบแจ้งหนี้ เจอ VAT ผิด | `invoice-check` |
| ทีมกลาง | `plat-may` | `customer-data-policy.md` | ตรวจใบแจ้งหนี้ตามกติกาข้อมูลลูกค้า | `customer-data-policy` |

> 🧪 **หมายเหตุผู้สอน:** 19 โต๊ะแรกรันในรอบบริษัท 21 คน (พร้อมกันครั้งละ 10 แชต รวม 23 นาที 27 วินาที) ส่วน 5 โต๊ะใหม่ (Product 2 + ผู้บริหารสาย 3) รันทีหลังด้วย `claude -p` ซึ่งไม่มีหน้าต่างขออนุญาต 4 โต๊ะจึงหยุดรอสิทธิ์เขียน `.claude/` ผู้สอนวางไฟล์ skill ตามที่ Claude ร่างไว้ทุกตัวอักษร (ดึงจาก log) · ผู้เรียนที่ใช้แอปจะเห็นหน้าต่างขออนุญาต กดอนุญาตได้เลย

### 1.5 ผลที่เห็น: 3 ปัญหาของ "ต่างคนต่างเก็บ"

ทุกคนทำถูกตามพรอมต์ แต่พอเอา skill ของทุกโต๊ะมาวางเทียบกัน เจอ 3 ปัญหา

| ปัญหา | สั้น ๆ | แก้ใน |
|---|---|---|
| 1 · คัดลอกซ้ำ | กติกาเดียวกันมีสำเนาอยู่ 14 skill | LAB 2 |
| 2 · หัวไฟล์คนละแบบ | ช่อง `uses` / `follows` แต่ละคนใส่ไม่เหมือนกัน | LAB 2 · LAB 6 |
| 3 · ความรู้ติดอยู่ที่คนเดียว | กฎ PDPA อยู่ที่ MD คนเดียว proposal ของ Sales จึงไม่มี | LAB 4 · LAB 5 |

**⚠️ ปัญหา 1 · ความรู้เดียวกัน ถูกคัดลอกไปหลายที่**

![ปัญหา 1 ความรู้เดียวกันถูกคัดลอกไปหลายที่: ต้นฉบับ company-kit/customer-data-policy.md 1 ไฟล์ เจ้าของ plat-may · ต่างคนต่างคัดลอกไปไว้ใน references/ ของตัวเองด้วยชื่อไฟล์ต่างกัน เช่น sales-nida pdpa-rules.md, sales-krit customer-data-rules.md, qa-bank data-policy.md, ml-jay data-policy-summary.md, ml-pim data-policy.md, fin-nok pdpa-for-invoices.md, ops-fon company-rules.md, md-somchai approval-rules.md · รวม 14 skill · price-list.csv ก็ถูกคัดลอก 3 skill · ถ้ากติกาเปลี่ยนต้องแก้ 14 ที่ · แก้ใน LAB 2 ย้ายไปไว้ที่เดียวใน core](img/lab1-problem-1-copies.png)

พรอมต์บอกให้ "สรุปความรู้ที่จำเป็นไว้ใน `references/`" เพื่อให้ skill ใช้ที่เครื่องอื่นได้ ทุกคนจึงคัดลอกไปเก็บเอง ผลคือกติกาที่มีต้นฉบับไฟล์เดียว กลายเป็น 14 สำเนาที่ชื่อไฟล์ไม่เหมือนกันเลย

**⚠️ ปัญหา 2 · ต่างคนต่างเข้าใจหัวไฟล์ไม่ตรงกัน**

![ปัญหา 2 ต่างคนต่างเข้าใจหัวไฟล์ไม่ตรงกัน: ที่ขอไว้ uses = skill ที่เรียกใช้ follows = นโยบายที่ต้องทำตาม · sales-nida ใส่ uses [pricing-calc] follows [customer-data-policy] ถูกทั้งคู่ · md-somchai ใส่ customer-data-policy ไว้ใน uses และ pricing-calc ไว้ใน follows สลับกัน · fin-joy ใส่ customer-data-policy ใน uses, follows เป็นงานที่ทำมาก่อน และ version 0.1.0 · ทั้งบริษัทใส่ follows เป็นนโยบายถูกแค่ 2 คน · แก้ใน LAB 2 และ LAB 6](img/lab1-problem-2-headers.png)

ภาพนี้คือหัวไฟล์จริงของ 3 โต๊ะใน 1.3 ทั้งบริษัทใส่ `follows` เป็นนโยบายถูกแค่ 2 คน ถ้าปล่อยไว้ เวลาถามว่า "แก้กติกานี้แล้วกระทบ skill ไหน" (LAB 7) จะตอบผิด

**⚠️ ปัญหา 3 · ความรู้ในหัวคนเดียว ไม่ไปถึงคนที่ต้องใช้**

![ปัญหา 3 ความรู้ในหัวคนเดียวไม่ไปถึงคนที่ต้องใช้: desks/md-somchai/ มี notes/deal-rules.md ข้อ 5 ลูกค้าธนาคารต้องมีภาคผนวก PDPA ไม่มีตีกลับ และ skill deal-approval เก็บกฎนี้ไว้ · กำแพงกั้น · desks/sales-nida/ proposal ธนาคาร 9 หัวข้อไม่มีภาคผนวก PDPA และ skill sales-proposal ไม่รู้จักกฎนี้ · ใน LAB 4 proposal ถูกตีกลับ · แก้ใน LAB 5 ด้วย PR](img/lab1-problem-3-silo.png)

> **สรุป LAB 1:** ทุกคนเก่งขึ้นได้ด้วย skill ของตัวเอง แต่ **บริษัทยังไม่เก่งขึ้น** เพราะ skill อยู่คนละโต๊ะ ซ้ำกัน เขียนหัวไฟล์คนละแบบ และความรู้สำคัญไม่ไปถึงคนที่ต้องใช้ → LAB 2 ทีมกลางจะรวมทั้งหมดเป็นคลังเดียวบน Gitea

---

## LAB 2 · ทีมกลางรวม skill เป็นคลังกลาง `org-skills` 🤖

![ทีมกลางรวม skill ทุกโต๊ะ ขึ้นคลังกลาง: ดูดจากทุกโต๊ะ → จัดเป็นคลังเดียว → push ขึ้น Gitea · plat-ken ใช้ท่อดูดโฟลเดอร์ SKILL.md จากโต๊ะ sales-nida, md-somchai, fin-joy, hr-fah, ml-jay เข้าชั้นหนังสือ org-skills ที่มีชั้น core, shared และกล่องแผนก แล้ว push ขึ้นตึก Gitea localhost:3300 ให้คนทุกแผนกดึงไปใช้ (ภาพจำลอง)](img/lab2-collect.png)

**LAB นี้ทำอะไร:** เคน (`plat-ken`) หัวหน้าทีมกลาง ทำ 3 อย่างให้ทั้งบริษัท

| ขั้น | ทำอะไร | ได้อะไร |
|---|---|---|
| ① ดูด | อ่าน skill ส่วนตัวจาก `desks/*/.claude/skills/` ของทุกโต๊ะ (อ่านอย่างเดียว ไม่แก้ของใคร) | รู้ว่ามี skill อะไรบ้าง อะไรซ้ำกัน |
| ② จัดเป็นคลังเดียว | ทำคลัง `org-skills` ในโต๊ะของเคน: 1 แผนก = 1 plugin · ของที่ทุกคนใช้รวมไว้ใน `core` · ทำหัวไฟล์ให้เหมือนกันทั้งคลัง | คลังเดียวที่ทุกคนใช้ร่วมกัน ไม่มีสำเนาซ้ำ |
| ③ ขึ้น Gitea | push คลังขึ้น `localhost:3300/novatech/org-skills` แล้วตั้งยามให้ branch `main` | ทุกโต๊ะดึงไปติดตั้งได้ (LAB 3) · แก้ได้ทาง PR เท่านั้น (LAB 5) |

> 📦 **plugin marketplace คืออะไร** คลัง Git ที่มีสารบัญ `marketplace.json` บอกว่ามี **plugin** (แพ็ก skill) อะไรบ้าง ติดตั้งทีละแพ็กด้วย `claude plugin install <ชื่อ>@novatech-skills` เช่น ฝ่ายขายติดตั้ง `core` + `sales` ได้ skill 6 ตัวในคำสั่งเดียว

🧑 **คิดก่อน** จากปัญหา 1 ใน LAB 1 (ความรู้เดียวกันถูกคัดลอกไว้หลายที่) ของที่ซ้ำกันควรไปอยู่ชั้นไหน (ทฤษฎีหัวข้อ 21 ตาราง 5 ชั้น) และใครควรเป็นคนรีวิว skill ของแต่ละแผนก

### 2.1 จากทุกโต๊ะ เป็นคลังเดียว

[![LAB 2 จากทุกโต๊ะเป็นคลังเดียว: ก่อน ต่างคนต่างเก็บ desks/sales-nida/.claude/skills/sales-proposal/, sales-krit follow-up-email, md-somchai deal-approval, fin-joy pricing-calc, hr-fah jd-writer, ml-jay mlflow-experiment, plat-may customer-data-policy และโต๊ะอื่นทุกโต๊ะ → plat-ken อ่านอย่างเดียว → หลัง desks/plat-ken/org-skills/ มี .claude-plugin/marketplace.json สารบัญ 11 plugin · plugins/core/skills/ ชั้น 1 ทุกคนติดตั้ง customer-data-policy brand-guide pricing-rules skill-finder · shared/skills/ ชั้น 2 meeting-minutes · sales exec finance hr mlops sa dev qa devops ชั้น 3 แผนกละ 2 skill · .gitea/CODEOWNERS · scripts/build.py · push ขึ้น http://localhost:3300/novatech/org-skills · main ห้าม push ตรง ต้องผ่าน PR approve อย่างน้อย 1 คน](img/lab2-before-after.png)](img/lab2-before-after.png)

| ชั้น | plugin | ใครติดตั้ง | ใครรีวิว (CODEOWNER) |
|---|---|---|---|
| 1 · องค์กร | `core` | **ทุกคน** | `plat-ken` (+ เจ้าของเรื่อง `plat-may`, `fin-joy`) |
| 2 · ข้ามแผนก | `shared` | ทุกแผนกที่ต้องใช้ | `plat-ken` |
| 3 · แผนก | `sales` · `exec` · `finance` · `hr` · `mlops` · `sa` · `dev` · `qa` · `devops` | คนในแผนกนั้น | หัวหน้าแผนก 👑 |

### 2.2 พรอมต์

💬 **พรอมต์** (เปิด Claude Code ที่โต๊ะ `novatech/desks/plat-ken/` · แชตใหม่)

![หน้าต่าง Claude Code วางพรอมต์ LAB 2](img/lab2-paste.png)

```text
ฉันคือ เคน ภักดีวงศ์ (plat-ken) หัวหน้าทีมกลาง · นี่คือโต๊ะของฉัน (novatech/desks/plat-ken/)
งาน: รวม skill ส่วนตัวของทุกคนเป็นคลังกลาง แล้วขึ้น Gitea ให้ทุกโต๊ะดึงไปใช้
1. ดูด skill ของทุกคน: อ่านทุกโฟลเดอร์ ../*/.claude/skills/ (อ่านอย่างเดียว ห้ามแก้หรือลบของในโต๊ะคนอื่น)
2. จัดเป็นคลัง org-skills ในโต๊ะของฉัน แบบ Claude Code plugin marketplace ชื่อ novatech-skills
   - 1 แผนก = 1 plugin (ดูแผนกใน ../../people/README.md)
   - plugin core = ของที่ทุกคนต้องใช้ ถ้าหลายคนเขียนกติกาเดียวกันซ้ำ (เช่น ข้อมูลลูกค้า แบรนด์ ราคา) ให้รวมเป็น skill เดียวใน core แล้วให้ skill เดิมอ้าง core แทนการคัดลอก
   - plugin shared = งานข้ามแผนก เช่น meeting-minutes
3. ทำหัวไฟล์ให้เป็นแบบเดียวกันทั้งคลัง: layer ตามชั้นใหม่ · uses = skill ที่เรียกใช้ · next = งานถัดไป · follows = นโยบายที่ต้องทำตาม
4. ให้หัวหน้าแผนกเป็น CODEOWNER ของ plugin แผนกตัวเอง
5. ตรวจด้วย claude plugin validate จนผ่าน
6. ขึ้น Gitea: สร้าง repo สาธารณะ novatech/org-skills ที่ http://localhost:3300 (token ของฉันอยู่ใน .gitea-token) แล้ว push
7. ตั้ง branch main ให้ห้าม push ตรง ต้องผ่าน PR และ approve อย่างน้อย 1 คน
จบแล้วสรุป: มี plugin อะไรบ้าง skill แต่ละตัวอยู่ชั้นไหน รวมอะไรเป็น core เพราะอะไร
```

| ขั้นในพรอมต์ | มีไว้ทำไม |
|---|---|
| 1 อ่านอย่างเดียว | โต๊ะของคนอื่นคือคอมของเขา ทีมกลางเอาของมาจัด แต่ไม่ไปแก้ในเครื่องใคร |
| 2 core / shared / แผนก | แต่ละคนเห็นแค่ของที่เกี่ยวกับตัวเอง (LAB 3) และกติกาที่ซ้ำเหลือที่เดียว (แก้ปัญหา 1 ของ LAB 1) |
| 3 หัวไฟล์แบบเดียวกัน | กราฟของ skill และการค้นหาใน LAB 7 จะได้ไม่เพี้ยน (แก้ปัญหา 2 ของ LAB 1) |
| 4 CODEOWNER | การแก้ skill ของแผนกไหน ต้องให้หัวหน้าแผนกนั้นรีวิว (LAB 5) |
| 5 validate | Claude Code อ่านคลังได้จริง ก่อนให้คนอื่นติดตั้ง |
| 6–7 push + ยามของ main | ของจริงมีที่เดียวบน Gitea · ห้ามใครแก้ตรง ต้องผ่าน PR (ทฤษฎีหัวข้อ 22.2) |

> 🧪 **หมายเหตุผู้สอน:** ผลจริงด้านล่างรันด้วยพรอมต์ถ้อยคำเดิมแบบย่อหน้าเดียว ([`prompt.txt`](_solution/lab2/prompt.txt)) ในรอบบริษัท 21 คน (9 แผนก ยังไม่มีทีม Product) พรอมต์ด้านบนเรียงงานเดียวกันเป็นขั้น และเพิ่มคำว่า "อ่านอย่างเดียว" ให้ชัด (รอบจริง Claude ก็ไม่ได้แก้โต๊ะของใคร) ยังไม่ได้รันด้วยถ้อยคำใหม่

### 2.3 ผลจริง

✅ **ผลจริง: ~13 นาที · 57 คำสั่ง · 11 plugin · 23 skill** ([คำตอบเต็มของ Claude](_solution/lab2/claude-summary.md) · [คลังที่ได้](_solution/org-skills-after-lab2/))

| plugin | ชั้น | CODEOWNER | skill |
|---|---|---|---|
| `core` | 1 องค์กร (ทุกคน) | `plat-ken` (+ `plat-may`, `fin-joy` เฉพาะเรื่องของตัวเอง) | `customer-data-policy` · `brand-guide` 🆕 · `pricing-rules` 🆕 · `skill-finder` 🆕 |
| `shared` | 2 ข้ามแผนก | `plat-ken` | `meeting-minutes` 🆕 |
| `exec` · `sales` · `sa` · `dev` · `qa` · `devops` · `mlops` · `hr` · `finance` | 3 แผนก | หัวหน้าแผนก 👑 | แผนกละ 2 skill (18 ตัวจาก LAB 1) |

![ของที่ซ้ำ รวมไว้ที่เดียว: ก่อน 14 สำเนา เอกสารกติกาข้อมูลลูกค้าหลายฉบับกระจายบนหลายโต๊ะ บางฉบับเก่าบางฉบับมีเครื่องหมายคำถาม → หลัง 1 ที่ใน core หนังสือเล่มเดียวบนชั้น core และโฟลเดอร์ sales hr mlops finance exec ชี้ลูกศรมาที่เล่มนั้น (ภาพจำลอง)](img/lab2-dedupe.png)

Claude รวมอะไรเป็น `core` และเพราะอะไร

| skill ใน core | เดิมกระจายอยู่ที่ | ผล |
|---|---|---|
| `customer-data-policy` | สรุป PDPA คนละแบบ 8 skill | เหลือที่เดียว กติกาเฉพาะงานที่มีแค่ในบางสำเนาย้ายเป็นตาราง `doc-type-rules.md` ไม่มีข้อไหนหาย |
| `brand-guide` | กติกาแบรนด์ 7 skill | ใช้คู่มือฉบับเต็มกับโลโก้ชุดเดียว |
| `pricing-rules` | `price-list.csv` 3 สำเนาที่ **เหมือนกันทุกไบต์** + กฎกำไร 3 ชุด (sales, finance, exec) | สคริปต์คิดราคา 3 ตัวแก้ให้อ่านราคาจาก core ที่เดียว ทดสอบแล้วตัวเลขตรง (755,000 บาท · margin 36.8%) |

และ **ลบไฟล์สำเนาทิ้ง 12 ไฟล์** skill ในแผนกเปลี่ยนไปอ้าง core ผ่าน `follows` แทน · หัวไฟล์ทุกตัวเป็นแบบเดียวกัน (เทียบกับ LAB 1 ปัญหา 2)

```markdown
metadata:
  owner: sales-nida
  plugin: sales
  layer: department          # เดิม personal
  version: 1.1.0             # เดิม 1.0.0
  uses: []                   # เดิม [pricing-calc] (ข้ามแผนก ติดตั้งไม่ครบทุกคน)
  next: [deal-approval, follow-up-email, req-to-spec]
  follows: [pricing-rules, brand-guide, customer-data-policy]   # นโยบายใน core
```

### 2.4 ดูของจริงใน Gitea

🎬 **หลัง push แล้ว Gitea หน้าตาเป็นยังไง (12 วินาที)**

![GIF LAB 2: ① plat-ken ดูด SKILL.md จากโต๊ะ sales-nida md-somchai fin-joy hr-fah ml-jay อ่านอย่างเดียว ② จัดเป็นคลังเดียว desks/plat-ken/org-skills/ มี marketplace.json plugins/core shared sales exec finance hr mlops sa dev CODEOWNERS build.py ③ git push origin main ขึ้น http://localhost:3300/novatech/org-skills.git new branch main ④ หน้า repo novatech/org-skills บน Gitea ⑤ โฟลเดอร์ plugins 11 แผนก ⑥ ไฟล์ CODEOWNERS plugins/sales → @sales-nida ⑦ ลอง push ตรงเข้า main ถูกปฏิเสธ Not allowed to push to protected branch main](img/lab2-push-flow.gif)

<sub>ข้อความใน terminal และหน้าเว็บมาจากการ push คลังผลจริงของ LAB 2 ขึ้นบริษัทจำลองจริง (รวมการลอง push ตรงที่ถูกปฏิเสธ)</sub>

| repo `novatech/org-skills` | `.gitea/CODEOWNERS`: โฟลเดอร์ไหน ใครรีวิว |
|---|---|
| ![GIF หน้า repo org-skills, โฟลเดอร์ plugins 11 แผนก และ SKILL.md ของ sales-proposal](img/lab2-repo.gif) | ![GIF ไฟล์ CODEOWNERS: plugins/sales → @sales-nida, plugins/dev → @dev-pond ... และหน้าตั้งค่า branch](img/lab2-codeowners.gif) |

![main มียาม ต้องผ่าน PR + approve: หุ่นยนต์ยามถือป้ายห้าม push ตรงหน้าประตู main คนที่โยนโฟลเดอร์ใส่ประตูตรง ๆ ถูกเด้งกลับ ส่วนอีกคนเดินผ่านซุ้ม PR แล้วผู้รีวิวชูนิ้ว approve ประตูจึงเปิด (ภาพจำลอง)](img/lab2-protect.png)

![กติกาของ branch main: Disable Push (ห้าม push ตรง) และ Disable Force Push](img/lab2-protect-push.png)

Claude ทดสอบกติกาเอง: ลอง push ตรงเข้า `main` แล้ว Gitea ตอบ `Not allowed to push to protected branch main` (แล้วลบ commit ทดสอบทิ้ง)

👀 **สังเกต**
- Claude **เขียนสคริปต์ `scripts/build.py --check` เพิ่มเอง** ให้สร้าง `marketplace.json`, `plugin.json`, `CODEOWNERS` และแค็ตตาล็อกจากหัวไฟล์ และไม่ยอมให้มีสำเนากติกากลางอยู่นอก core — นี่คือเมล็ดของ CI ใน LAB 6
- Claude บอกเองว่า skill ที่เขียนใหม่ใน core (`brand-guide`, `pricing-rules`) **ควรให้เจ้าของเรื่องรีวิว** (`plat-may`, `fin-joy`) — AI ร่างได้ แต่คนต้องตรวจ (ทฤษฎีหัวข้อ 15)
- คำอธิบาย repo ในหน้า Gitea เป็นตัวอ่านไม่ออก เพราะส่งภาษาไทยผ่าน `curl` บน Windows โดยไม่ได้ตั้ง UTF-8 (ตัว repo และไฟล์ไม่เป็นอะไร)

> 🧪 **หมายเหตุผู้สอน:** รอบแรก LAB 2 สร้าง repo ไม่ได้ เพราะ `seed` ออก token ให้ทีมกลางแค่สิทธิ์เขียน repo ไม่มีสิทธิ์สร้าง repo ในองค์กร Claude **หยุดและถาม** แทนที่จะเอารหัสผ่านใน `.env` ไปออก token สิทธิ์สูงกว่าเอง ([บันทึกรอบแรก](_solution/lab2/attempt1-blocked-token.md)) · แก้ `seed` ให้ทีมกลางได้ `write:organization` แล้วรัน LAB 2 ใหม่ทั้งหมด ผลด้านบนคือรอบที่ 2

---

## LAB 3 · ทุกโต๊ะติดตั้งแพ็กแผนก + Dev คนใหม่วันแรก 🤖 ×21

![LAB 3 ติดตั้งแพ็ก skill ให้ทุกโต๊ะ 3 ขั้น: 1 ผู้ดูแลบอกที่อยู่คลัง ติดป้าย novatech-skills ทุกโต๊ะ → 2 แต่ละคนติดตั้งแพ็กของตัวเองจากชั้น org-skills บน Gitea sales-nida ได้ core + sales, fin-joy ได้ core + finance, hr-fah ได้ core + hr → 3 ผู้ดูแลตรวจของจริง ใช้แว่นขยายตรวจทุกโต๊ะ เติม core ให้โต๊ะที่ขาด และเก็บ skill ส่วนตัวเก่าลงกล่อง archived (ภาพจำลอง)](img/lab3-install-flow.png)

**LAB นี้ทำอะไร:** คลังกลางขึ้น Gitea แล้ว (LAB 2) ทีนี้ทุกโต๊ะต้อง **ติดตั้งไปใช้** โดยแต่ละคนได้เฉพาะของที่เกี่ยวกับตัวเอง

| ขั้น | ใครทำ | ทำอะไร |
|---|---|---|
| ① บอกที่อยู่คลัง | ผู้ดูแลระบบ (ที่ `novatech/`) | ใส่ค่าให้ทุกโต๊ะรู้จักคลัง `novatech-skills` และเปิด `core` |
| ② ติดตั้งแพ็กของตัวเอง | พนักงานทุกคน | ติดตั้ง `core` + plugin แผนกตัวเอง ให้ใช้ได้เฉพาะโต๊ะนั้น |
| ③ ตรวจของจริง | ผู้ดูแลระบบ | ตรวจว่า **ติดตั้งแล้วจริง** ไม่ใช่แค่มีชื่อใน settings · เก็บ skill ส่วนตัวที่ซ้ำกับคลังกลาง |
| 🧪 ทดลอง | Dev คนใหม่ (`dev-new`) | วันแรกที่มีแพ็ก vs ไม่มีแพ็ก ทำงานต่างกันแค่ไหน |

🧑 **คิดก่อน** ถ้าทุกคนติดตั้ง skill ทั้ง 23 ตัว จะเกิดอะไรขึ้น (ทฤษฎีหัวข้อ 24.1 งบรายชื่อมีจำกัด คำอธิบายชนกัน) แล้วใครควรเห็นอะไร (หัวข้อ 21 ตาราง 5 ชั้น)

### 3.1 แพ็กตามแผนก: ใครได้อะไร

![LAB 3 ติดตั้งแพ็กตามแผนก: ชั้น org-skills แจกกระเป๋า core + sales, core + dev, core + hr และ Dev คนใหม่ป้าย วันแรก ได้ core + dev ทำงานได้ทันที (ภาพจำลอง)](img/lab3-packs.png)

| ใคร | ติดตั้ง | เห็น skill |
|---|---|---|
| ทุกคน | `core` | `customer-data-policy` · `brand-guide` · `pricing-rules` · `skill-finder` |
| ฝ่ายขาย (`sales-nida`, `sales-krit`) | + `sales` | `sales:sales-proposal` · `sales:follow-up-email` |
| บัญชี (`fin-joy`, `fin-nok`) | + `finance` | `finance:pricing-calc` · `finance:invoice-check` |
| Dev (`dev-pond`, `dev-mew`, `dev-new`) | + `dev` | `dev:project-scaffold` · `dev:coding-standard` |
| … ทุกแผนกแบบเดียวกัน | + แผนกตัวเอง | รวมคนละ **6 จาก 23 skill** |

ของที่ติดตั้งอยู่ตรงไหนในโต๊ะ

| ไฟล์ | คืออะไร |
|---|---|
| `desks/<ชื่อ>/.claude/settings.json` | **รายชื่อ** คลังที่รู้จัก (`novatech-skills`) และ plugin ที่เปิดใช้ในโต๊ะนี้ · แม่แบบอยู่ที่ [`desks/_template/.claude/settings.json`](novatech/desks/_template/.claude/settings.json) |
| ทะเบียนติดตั้งของ Claude Code (`~/.claude/plugins/installed_plugins.json`) | **ของที่ติดตั้งจริง** ว่า plugin ไหนลงไว้ที่โต๊ะไหน |

> 🏢 ในบริษัทจริง admin ใส่ค่าใน managed settings ให้ทุกเครื่องครั้งเดียว (ทฤษฎีหัวข้อ 22.3) ในแล็บจำลองด้วยไฟล์แม่แบบในโต๊ะ

### 3.2 ขั้น ① ผู้ดูแลบอกที่อยู่คลัง

💬 **พรอมต์** (เปิด Claude Code ที่ `novatech/`)

![หน้าต่าง Claude Code วางพรอมต์ LAB 3 ขั้น 1](img/lab3-paste-admin.png)

```text
ผมเป็นผู้ดูแลระบบ ให้ทุกโต๊ะใน desks/ รู้จักคลัง skill ของบริษัทและได้ plugin core ทุกคน ตามแม่แบบ desks/_template/.claude/settings.json
(ห้ามลบ skill ส่วนตัวที่มีอยู่แล้วในโต๊ะ) จบแล้วบอกว่าใส่ให้กี่โต๊ะ
```

### 3.3 ขั้น ② ทุกคนติดตั้งแพ็กของตัวเอง

💬 **พรอมต์** (ก๊อปอันนี้อันเดียว · เปิด Claude Code ที่ `novatech/` · ได้ครบทุกโต๊ะ)

```text
ฉันเป็นผู้ดูแลระบบ ช่วยติดตั้ง skill ของบริษัทให้พนักงานทุกโต๊ะใน desks/ (ข้าม _template)
สำหรับแต่ละโต๊ะ ให้เปิด agent ย่อยแยก 1 ตัว (1 ตัว = แชตใหม่ของเจ้าของโต๊ะ) โฟลเดอร์ทำงานคือ desks/<user>/ แล้วส่งงานนี้ให้ทุกตัวอักษร:
"ติดตั้ง skill ของบริษัทสำหรับแผนกของผม (ดูแผนกในการ์ด ../../people/ คลังอยู่ที่ http://localhost:3300/novatech/org-skills) ให้ใช้ได้เฉพาะโต๊ะนี้ แล้วบอกว่าตอนนี้ผมมี skill ของบริษัทอะไรใช้บ้าง"
- agent แก้ไฟล์ได้เฉพาะใน desks/<user>/ ของตัวเอง · รันพร้อมกันครั้งละ 4 ตัว
จบแล้วสรุปเป็นตาราง: user · แผนก · plugin ที่ติดตั้ง · skill ที่เห็น
```

| ส่วนของพรอมต์ | มีไว้ทำไม |
|---|---|
| agent ย่อย 1 ตัวต่อ 1 โต๊ะ | แต่ละคนติดตั้งในนามตัวเอง เหมือนเปิดแชตใหม่ที่โต๊ะของคนนั้น |
| ดูแผนกจากการ์ด | Claude เลือก plugin ของแผนกเอง ไม่ต้องบอกทีละคน |
| ใช้ได้เฉพาะโต๊ะนี้ | ติดตั้งระดับโปรเจกต์ (โต๊ะ) ไม่ปนกับโต๊ะของคนอื่น |

👀 **ตัวอย่าง: งานที่ agent ย่อยของแต่ละโต๊ะได้รับ** (อ่านอย่างเดียว ไม่ต้องก๊อป)

![หน้าต่าง Claude Code วางพรอมต์ LAB 3 ขั้น 2](img/lab3-paste-desk.png)

> ติดตั้ง skill ของบริษัทสำหรับแผนกของผม (ดูแผนกในการ์ด ../../people/ คลังอยู่ที่ http://localhost:3300/novatech/org-skills) ให้ใช้ได้เฉพาะโต๊ะนี้  
> แล้วบอกว่าตอนนี้ผมมี skill ของบริษัทอะไรใช้บ้าง  

ข้อความเดียวกันทุกโต๊ะ Claude รู้ว่าเป็นใครและอยู่แผนกไหนจากชื่อโฟลเดอร์และการ์ด

✅ **ผลจริง ขั้น ①–②: ผู้ดูแล 35 วินาที · 21 โต๊ะติดตั้งแพ็กแผนกครบใน 4 นาที 50 วินาที** (พร้อมกันครั้งละ 4 โต๊ะ แต่ละโต๊ะ 38–69 วินาที) · [คำตอบของ Claude](_solution/lab3/claude-summaries.md)

> 🧪 **หมายเหตุผู้สอน:** รอบรันจริงวางพรอมต์ขั้น ② ทีละโต๊ะ (ข้อความในตัวอย่างด้านบน) ในรอบบริษัท 21 คน · พรอมต์รวมของขั้น ② ยังไม่ได้รันจริง

### 3.4 ขั้น ③ ผู้ดูแลตรวจของจริง

⚠️ **พอเปิด Claude ใหม่ที่ทุกโต๊ะแล้วนับ skill ที่เห็นจริง: 13 จาก 21 โต๊ะไม่มี `core`**

![เขียนไว้ ≠ ติดตั้งแล้ว ต้องตรวจจากสิ่งที่ Claude เห็นจริง: ซ้าย เขียนไว้ใน settings มีการ์ด core ติดบนโต๊ะแต่ลิ้นชักว่างเปล่า หุ่นยนต์มองด้วยความกังวล · ขวา ติดตั้งแล้วจริง ลิ้นชักมีแฟ้มครบ มีกระเป๋า core บนเก้าอี้ หุ่นยนต์ยิ้มถือแฟ้ม (ภาพจำลอง)](img/lab3-written-vs-installed.png)

แม่แบบแค่ **เขียนชื่อ** `core` ไว้ใน `settings.json` แต่ไม่ได้ **ติดตั้ง** ให้ โต๊ะที่มี core คือโต๊ะที่ Claude ของคนนั้นสั่ง `install core` เองระหว่างขั้น ② และทุกโต๊ะยังมี skill ส่วนตัวจาก LAB 1 ซ้อนอยู่ (เช่น `sales-proposal` คู่กับ `sales:sales-proposal`)

💬 **พรอมต์** (ที่ `novatech/` เหมือนขั้น ①)

```text
ตรวจทุกโต๊ะใน desks/ ว่ามี plugin core ติดตั้งใช้งานได้จริงไหม (ไม่ใช่แค่มีชื่อใน settings) ตัวไหนยังไม่มีให้ติดตั้งให้ครบ
และ skill ส่วนตัวใน desks/*/.claude/skills/ ที่ย้ายเข้าคลังกลางแล้ว ให้ย้ายไปเก็บที่ desks/<คน>/.claude/skills-archived/ (ไม่ต้องลบ) จะได้ไม่มีสองฉบับ
จบแล้วสรุปเป็นตาราง: โต๊ะไหนเคยไม่มี core และย้าย skill ส่วนตัวของใครไปบ้าง
```

✅ **ผลจริง ขั้น ③: 2 นาที 9 วินาที** Claude หาสาเหตุเจอเอง (ดูทะเบียนติดตั้ง `installed_plugins.json` ว่ามีโต๊ะไหนบ้าง แทนการเชื่อแค่ settings) ติดตั้ง core ให้ 13 โต๊ะที่ขาด และย้าย skill ส่วนตัว 19 ตัวไป `skills-archived/` หลังตรวจว่าทุกตัวมีฉบับเดียวกันในคลังกลางแล้ว

นับใหม่ที่ทุกโต๊ะ (จากรายชื่อ skill ที่ Claude เห็นตอนเปิดแชต):

![ผลจริง: ทุกโต๊ะเห็น core 4 + แพ็กแผนกตัวเอง 2 = 6 skill จากทั้งหมด 23 (plat-ken 5, plat-may 4) โดย core ของ 13 โต๊ะถูกติดตั้งเพิ่มในขั้น 3](img/lab3-visibility.png)

| ตรวจ | ผล |
|---|---|
| แต่ละโต๊ะเห็นกี่ skill | **6 จาก 23** (core 4 + แผนกตัวเอง 2) — เห็นเฉพาะชั้นที่เกี่ยวกับตัวเอง (หัวข้อ 24.4 แพ็กตามบทบาท) |
| ชื่อไม่ชนกัน | skill จาก plugin มีชื่อแผนกนำหน้าเสมอ เช่น `sales:sales-proposal`, `dev:coding-standard` |
| ฉบับซ้อน | ไม่เหลือ skill ส่วนตัวที่ซ้ำกับคลังกลาง |

### 3.5 🧪 Dev คนใหม่วันแรก: มีแพ็ก vs ไม่มีแพ็ก

![คนใหม่วันแรก รู้วิธีของทีมทันที: ซ้าย ไม่มีแพ็ก dev-new วันแรกงงมีเครื่องหมายคำถามเต็มหัว หุ่นยนต์ยักไหล่ แผนได้ 1/12 · ขวา มีแพ็ก core + dev สะพายกระเป๋า core + dev หุ่นยนต์ถือแฟ้ม project-scaffold แผนได้ 12/12 มีโน้ตรูปกุญแจ token ติดถูก dev-mew ชูนิ้วอยู่ด้านหลัง (ภาพจำลอง)](img/lab3-newhire-concept.png)

ทฤษฎีหัวข้อ 19 ขั้น 3 บอกว่า "คนใหม่วันแรก เปิด Claude แล้วมันรู้เลยว่าทีมให้ความสำคัญกับอะไร" ลองพิสูจน์ด้วยพรอมต์เดียวกัน 2 ครั้ง ในโฟลเดอร์ว่าง 2 โฟลเดอร์ที่ต่างกันแค่ติดตั้ง `core + dev` หรือไม่

```text
ผมเป็น dev คนใหม่ เข้าวันแรก ช่วยวางแผนขึ้นโปรเจกต์ระบบสมาชิก + ชำระเงินให้หน่อย
เขียนแผนลง work/plan.md (โครงโฟลเดอร์ โมดูล วิธีจัดการ token และ error การทดสอบ) ยังไม่ต้องเขียนโค้ด
```

แล้วให้ Claude อีกตัวเป็นผู้ตรวจ **โดยไม่บอกว่าฉบับไหนเป็นฉบับไหน** เทียบกับ `coding-rules.md` 10 ข้อของบริษัท + โน้ตโปรเจกต์ของ `dev-mew` 2 ข้อ ([พรอมต์ผู้ตรวจ](_solution/lab3/judge-prompt.txt) · [คะแนนรายข้อ](_solution/lab3/judge-score.json))

![ผลจริง: ไม่มีแพ็กผ่าน 1/12 (ผ่านแค่เรื่อง test) มีแพ็ก core + dev ผ่าน 12/12](img/lab3-newhire.png)

| | ไม่มีแพ็ก | มีแพ็ก `core + dev` |
|---|---|---|
| skill ที่ Claude หยิบเอง | — | `dev:project-scaffold` (คำสั่งแรก) |
| เวลา | 1 นาที 32 วินาที | 1 นาที 41 วินาที |
| ผ่านมาตรฐานบริษัท | **1/12** | **12/12** |
| ตัวอย่างที่ต่าง | ใช้ Fastify + `src/shared`, cookie `SameSite=Strict`, ไม่รู้จักบั๊ก token เดิม | access token 15 นาที + หมุนทุกครั้ง + refresh ก่อนไปหน้าจ่ายเงิน (บั๊กที่ `dev-mew` เคยแก้), webhook ใส่ `payment_events` แบบ UNIQUE ก่อน |

👀 **สังเกต**
- แผนที่ไม่มีแพ็กไม่ได้ "ผิด" ในโลกทั่วไป แต่ **ไม่ใช่วิธีของทีมนี้** — ความเก่งของ `dev-mew` (บั๊ก token) ไปถึงคนใหม่ได้ ทั้งที่สองคนยังไม่เคยคุยกัน
- 🧪 ครั้งแรกผู้สอนลองที่โต๊ะ `dev-new` ใน `novatech/` แต่ Claude **เดินไปเปิด `company-kit/coding-rules.md` เอง** (อ้างถึง 12 ครั้ง) เพราะไดรฟ์บริษัทอยู่ในโฟลเดอร์เดียวกัน จึงย้ายมาทดลองในโฟลเดอร์ว่างนอก `novatech/` เพื่อให้ต่างกันแค่แพ็ก — ในบริษัทจริงคนใหม่ไม่มีไดรฟ์ของทุกแผนกอยู่ในเครื่อง
- บทเรียนของผู้ดูแล: **"เขียนไว้ใน settings" ≠ "ติดตั้งแล้ว"** ต้องตรวจจากสิ่งที่ Claude เห็นจริง

---

## LAB 4 · ดีลเดียววิ่งข้ามแผนก (ตอนที่ 1: Sales → บัญชี → MD) 🤖

![LAB 4 ดีลเดียว วิ่งผ่านทั้งบริษัท: ถนนผ่าน 9 โต๊ะ Sales บัญชี MD SA Dev MLOps QA DevOps HR หุ่นยนต์ถือแฟ้ม deal-001 ส่งต่อ ที่โต๊ะ MD มีตราประทับ ตีกลับ](img/lab4-deal.png)

🧑 **คิดก่อน** ดีลหนึ่งดีลผ่านกี่แผนก แต่ละแผนกใช้ skill อะไร (ทฤษฎีหัวข้อ 20.1) และถ้าความรู้ของแผนกหนึ่งไม่ไปถึงอีกแผนก จะไปสะดุดที่ไหน

โจทย์: ธนาคารนครหลวงพัฒนาขอ **ระบบจองคิวสาขา 120 สาขา + โมเดลพยากรณ์คิว** ([TOR](novatech/company-kit/deal-001/tor-bank-queue.md)) ทุกขั้นเป็น **แชตใหม่ที่โต๊ะของคนนั้น** ส่งงานต่อกันผ่านโฟลเดอร์กลาง `novatech/deals/deal-001/` (เหมือนไดรฟ์กลางของทีม) **ไม่มีใครบอกชื่อ skill ในพรอมต์เลย**

💬 **พรอมต์**

![หน้าต่าง Claude Code วางพรอมต์ LAB 4 ทั้ง 3 ขั้น](img/lab4-paste.png)

| ขั้น | โต๊ะ | พรอมต์ |
|---|---|---|
| 1 | `sales-nida` | `เปิดดีลใหม่: TOR อยู่ที่ ../../company-kit/deal-001/tor-bank-queue.md ช่วยทำ proposal แล้ววางไว้ในโฟลเดอร์กลางของดีล ../../deals/deal-001/` |
| 2 | `fin-joy` | `ตรวจราคาและกำไรของดีล ../../deals/deal-001/ แล้ววางผลไว้ในโฟลเดอร์เดียวกัน` |
| 3 | `md-somchai` | `ดีล ../../deals/deal-001/ อนุมัติได้ไหม เขียนผลไว้ในโฟลเดอร์ดีล` |

✅ **ผลจริง**

| ขั้น | โต๊ะ | skill ที่ Claude หยิบเอง | เวลา | ได้ |
|---|---|---|---|---|
| 1 | `sales-nida` | `sales:sales-proposal` | 2 นาที 46 วินาที | proposal 4,780,000 บาท + ใบคิดราคา + โน้ตภายใน |
| 2 | `fin-joy` | `finance:pricing-calc` | 1 นาที 39 วินาที | ตรวจราคาซ้ำ margin 31.6% และทักว่าโน้ตของ Sales เขียนผิดว่า "ไม่ต้องเข้า MD" |
| 3 | `md-somchai` | `exec:deal-approval` | 43 วินาที | ❌ **ตีกลับ** |

**3/3 ขั้นหยิบ skill ถูกตัว** (ดูจากคำสั่ง `Skill` ใน log ของแต่ละแชต) และส่งงานต่อกันได้โดยไม่มีใครบอกว่าไฟล์ไหนคืออะไร

ส่วนหนึ่งของ [`approval.md`](_solution/lab4/deal-001/approval.md) ที่ MD (Claude ที่โต๊ะ `md-somchai`) เขียน:

> ลูกค้าเป็นธนาคาร แต่ proposal ไม่มีหัวข้อ "ภาคผนวก PDPA" ซึ่งบังคับใช้ตั้งแต่ 1 ก.ค. 2026 จึงตีกลับทันที … หัวข้อ 4.2 พูดถึงเรื่องนี้แค่บางส่วน: มี DPA และ hosting "ภูมิภาคประเทศไทย" แต่ไม่ได้ระบุว่าครอบคลุม backup และ log ด้วย ส่วนการแจ้งเหตุภายใน 72 ชั่วโมงไม่มีเลย

👀 **สังเกต**
- นี่คือสิ่งที่ทฤษฎีหัวข้อ 18.2 เรียกว่า **"แต่ละแผนกเก่งคนละเรื่อง แต่ไม่แชร์"** — MD รู้กฎ (อยู่ใน skill `exec:deal-approval`) แต่ Sales ไม่รู้ เพราะ Sales ติดตั้งแค่แพ็ก `sales` (LAB 3)
- คลังกลางมีคำใบ้อยู่แล้วใน `core:customer-data-policy` ว่า "ภาคผนวก PDPA ลูกค้าธนาคารเป็นกติกาของ MD (ดู `deal-approval`)" แต่ Sales เปิด `deal-approval` ไม่ได้ ความรู้จึงไปไม่ถึง
- ทางแก้ที่ถูกไม่ใช่ "ให้ Sales ติดตั้งทุกแพ็ก" แต่คือ **เอาความรู้ไปใส่ใน skill ของคนที่ต้องใช้** → LAB 5

---

## LAB 5 · ⭐ PR: คนหนึ่งแก้ skill ทุกคนเก่งขึ้น 🧑 + 🤖

![LAB 5 คนหนึ่งแก้ skill ทุกคนเก่งขึ้น: ซ้าย หัวหน้าทีมขายเปิด pull request เพื่อนทีมกลางชูนิ้วโป้ง ขวา เซลส์อีกคนยิ้ม proposal มีหัวข้อภาคผนวก PDPA โดยไม่ได้แก้อะไรเอง (ภาพจำลอง)](img/lab5-pr.png)

🧑 **คิดก่อน** ถ้า `sales-nida` แก้แค่ proposal ของ deal-001 ให้ผ่าน MD แล้วจบ ดีลธนาคารถัดไปของ `sales-krit` จะเป็นยังไง (ทฤษฎีหัวข้อ 19 ขั้น 2 "feedback ของคนหนึ่ง ทำให้ agent ทุกตัวในทีมเก่งขึ้น")

💬 **พรอมต์** (ที่โต๊ะ `sales-nida` · ตรงกับกล่อง 💡 ในทฤษฎีหัวข้อ 22.2)

```text
MD ตีกลับดีล deal-001 เพราะ proposal ไม่มีภาคผนวก PDPA (เหตุผลอยู่ใน ../../deals/deal-001/approval.md)
แก้ skill sales-proposal ในคลังกลาง novatech/org-skills ให้ใส่ภาคผนวกนี้ทุกครั้งที่ลูกค้าเป็นธนาคาร แล้วเปิด PR ให้ทีมรีวิว (token ของผมอยู่ใน .gitea-token)
```

จากนั้นแต่ละคนทำหน้าที่ของตัวเองที่โต๊ะตัวเอง ด้วยพรอมต์สั้น ๆ เช่น `รีวิว PR #1 ... ในฐานะเจ้าของนโยบายข้อมูลลูกค้า ถ้ามีจุดที่ต้องแก้ให้ request changes พร้อมเหตุผล` ([พรอมต์ทุกขั้น](_solution/lab5/))

✅ **ผลจริง: PR #1 ใช้ 38 นาที รีวิว 3 รอบ · เกิด PR #2 ฝั่ง core ระหว่างทาง (11 นาที รีวิว 2 รอบ)** ([ทุกขั้นที่ Claude ตอบ](_solution/lab5/claude-summaries.md))

| เวลา | ใคร | ทำอะไร |
|---|---|---|
| 15:28 | `sales-nida` | เปิด **PR #1** `sales-proposal` 1.1.0 → 1.2.0 ใส่ "ภาคผนวก PDPA" 3 ข้อ (คัดลอกข้อความจาก skill ของ MD) และบอกเองว่า "กติกาเดียวกันอยู่ 2 ที่ ระยะยาวควรย้ายไป core" |
| 15:30 | `plat-may` (เจ้าของนโยบาย) | ❌ **Request changes** 2 ข้อ: (1) ประโยคเรื่องข้อมูลอ่อนไหวขัดกับนโยบาย (2) อย่าคัดลอกกติกา ให้ย้ายไป core |
| 15:33 | `sales-nida` | แก้ตามรีวิว ลบสำเนาออก ให้ skill อ้างไฟล์ใน core แทน |
| 15:50 | `plat-may` | เปิด **PR #2** `core:customer-data-policy` 1.0.0 → 1.1.0 เพิ่ม `bank-pdpa-annex.md` เป็น **ที่เดียว** ของกติกานี้ |
| 15:55 | `plat-ken` (CODEOWNER ของ core) | ❌ **Request changes** 3 ข้อ: ขอบเขตกว้างเกินกฎ MD, ใส่ข้อบังคับในนาม MD ที่ MD ไม่ได้เขียน, จุดเริ่มนับ 72 ชั่วโมง |
| 15:57 | `plat-may` | ✅ approve PR #1 |
| 15:58 | `sales-nida` | **ไม่ยอม merge เอง**: "ไฟล์ที่ PR #1 อ้างถึงยังไม่มีบน main ต้องรอ PR #2" |
| 15:58–16:02 | `plat-may` → `plat-ken` | แก้ PR #2 ครบ 3 ข้อ → ✅ approve + **merge PR #2** |
| 16:03 | `sales-nida` | ยังไม่ merge: เจอ 1 บรรทัดที่ขัดกับ core ฉบับที่เพิ่ง merge → ถามก่อนแก้ (ตอบว่า "เอาตามที่แนะนำ") |
| 16:04–16:07 | `sales-nida` → `plat-may` → `sales-nida` | แก้ 1 บรรทัด → approve รอบ 3 (approve เดิมหมดอายุเพราะมี commit ใหม่) → **merge PR #1** |

| PR #1 ใน Gitea: คำขอแก้ + รีวิว + คอมเมนต์ในบรรทัด | สิ่งที่แก้จริง (Files changed) |
|---|---|
| ![GIF หน้า PR #1 sales-proposal 1.2.0 ไล่ดูคำอธิบาย รีวิว request changes ของ plat-may และคอมเมนต์ในบรรทัด](img/lab5-pr1.gif) | ![GIF แท็บ Files changed ของ PR #1 แสดงบรรทัดที่เพิ่มในหัวข้อภาคผนวก](img/lab5-pr1-files.gif) |

![รีวิวของ plat-may ใน PR #1: ข้อสังเกต 72 ชั่วโมง, log ในไทย และคอมเมนต์ในบรรทัดของ proposal-template.md](img/lab5-pr1-mid.png)

| PR #2 ฝั่ง core: `plat-ken` request changes 3 ข้อ → แก้ → merge |
|---|
| ![GIF หน้า PR #2 customer-data-policy 1.1.0 ไล่ดูรีวิวของ plat-ken และการตอบของ plat-may](img/lab5-pr2.gif) |

![หน้ารวม PR: #1 sales-proposal 1.2.0 และ #2 customer-data-policy 1.1.0 merged](img/lab5-pulls.png)

### 🧪 `sales-krit` ไม่ได้แก้อะไรเลย เก่งขึ้นไหม

`sales-krit` ไม่ได้อยู่ใน PR ไหนเลย แค่สั่งที่โต๊ะตัวเองว่า `อัปเดต skill ของบริษัทที่ติดตั้งในโต๊ะนี้ให้เป็นฉบับล่าสุด แล้วบอกว่าอะไรเปลี่ยนบ้าง`

✅ **ผลจริง (83 วินาที):** Claude อัปเดต `core` + `sales` จาก commit `5878e51` → `f1218bf` และสรุปการเปลี่ยนแปลงของ PR #1 และ #2 ได้ถูกต้อง แต่เจอปัญหาจริงอย่างหนึ่ง:

> ⚠️ `claude plugin update` ตอบว่า "ล่าสุดแล้ว" เพราะ **เลขเวอร์ชันของ plugin (`plugin.json`) ยังเป็น 1.0.0** แม้เนื้อหาข้างในจะเปลี่ยน (PR เพิ่มเลขเวอร์ชันแค่ใน `SKILL.md`) Claude ต้องถอนแล้วติดตั้งใหม่ และแนะนำว่า "ควรเพิ่มเลขเวอร์ชันแพ็กทุกครั้งที่แก้" → นี่คือด่านหนึ่งของ CI ใน LAB 6

แล้วทดลองทำ proposal ลูกค้าธนาคารรายใหม่ ([TOR deal-002](novatech/company-kit/deal-002/tor-bank-dispute.md)) ก่อนและหลัง merge ในเครื่องที่มีแค่ `core + sales`:

```text
ทำ proposal ตาม TOR ในไฟล์ tor-bank-dispute.md ให้หน่อย เก็บไว้ใน work/
```

| ตรวจตามกฎของ MD (ภาคผนวก PDPA 3 ข้อ) | ก่อน merge (`sales-proposal` 1.1.0) | หลัง merge (1.2.0 + core 1.1.0) |
|---|---|---|
| มีหัวข้อ "ภาคผนวก PDPA" | ❌ | ✅ ต่อท้ายหัวข้อ 9 |
| 1 DPA (โนวาเทคเป็นผู้ประมวลผล) | ❌ (มีคำว่า DPA แค่ในตารางมาตรการ) | ✅ |
| 2 ข้อมูลรวม backup และ log อยู่ในไทย | ❌ | ✅ |
| 3 แจ้งเหตุภายใน 72 ชั่วโมง | ❌ | ✅ |
| MD จะตีกลับไหม | ตีกลับ (แบบเดียวกับ deal-001) | ผ่านข้อ 5 |

[proposal ก่อน](_solution/lab5/krit-test/before-proposal.md) · [proposal หลัง](_solution/lab5/krit-test/after-proposal.md) — ข้อความภาคผนวกในฉบับหลังมาจาก `core:customer-data-policy` → `bank-pdpa-annex.md` ตรงตัว เปลี่ยนแค่ชื่อลูกค้า

> **`sales-nida` แก้ครั้งเดียว `plat-may` กับ `plat-ken` รีวิว แล้ว Sales ทุกคน (และทุกแผนกที่ follows `customer-data-policy`) ได้ความรู้ของ MD ไปด้วย** — นี่คือภาพ "feedback ของคนหนึ่ง ทำให้ทุกคนเก่งขึ้น" ของทฤษฎีหัวข้อ 19 ที่รันจริง

👀 **สังเกต**
- **Claude ไม่ยอม merge เองแม้ได้ approve แล้ว** 2 ครั้ง เพราะดูว่า PR พึ่งไฟล์ที่ยังไม่มีบน main และมีบรรทัดที่ขัดกับ core — ด่านตรวจที่ดีไม่ได้มีแค่ "approve ครบไหม"
- รีวิวทำให้ **การออกแบบดีขึ้น** ไม่ใช่แค่จับผิด: เริ่มจาก "คัดลอกกติกาไปไว้ใน sales" จบที่ "กติกามีที่เดียวใน core ทุก skill อ้างถึง"
- CODEOWNER ของ `plugins/sales` คือ `sales-nida` เอง Gitea จึงไม่ขอรีวิวจากใครให้อัตโนมัติ (คนเขียนรีวิวตัวเองไม่ได้) Claude แก้ปัญหาโดยขอรีวิวจากคนอื่นเอง → ในบริษัทจริงควรมี CODEOWNER อย่างน้อย 2 คนต่อแผนก

> 🧪 **หมายเหตุผู้สอน: ทำไมต้องทดลองนอกโต๊ะ** ครั้งแรกให้ `sales-krit` ทำที่โต๊ะตัวเอง แต่ Claude **เปิดโฟลเดอร์ดีลกลาง เห็นใบตีกลับของ deal-001 แล้วใส่ภาคผนวกเอง** ([ผลที่โต๊ะ](_solution/lab5/krit-test/desk-run-leaked-from-deal-folder.md)) — ความรู้ไหลผ่านไดรฟ์กลางได้ แต่ขึ้นกับดวง · ครั้งที่ 2 ในโฟลเดอร์ว่าง Claude ก็ยัง **ไปเปิด skill ของแผนกอื่นใน plugin cache** เพราะในแล็บนี้ 21 คนใช้เครื่องเดียวกัน cache จึงมี plugin ของทุกแผนก — บทเรียน: **แพ็กตามแผนกช่วยเรื่อง "ความเกี่ยวข้อง" ไม่ใช่ "ความลับ"** ถ้า skill ไหนห้ามคนอื่นเห็น ต้องแยก repo/สิทธิ์จริง · ผลในตารางด้านบนจึงรันโดยซ่อน plugin แผนกอื่นออกจาก cache ชั่วคราวทั้งก่อนและหลัง ให้เหมือนเครื่องของ `sales-krit` จริงที่มีแค่ `core + sales`

---

## LAB 4 (ต่อ) · ดีลวิ่งต่อจนครบทุกแผนก 🤖

หลัง LAB 5 ดีล deal-001 กลับมาวิ่งต่อ ทุกขั้นเป็นแชตใหม่ที่โต๊ะของคนนั้น ([พรอมต์](_solution/lab4/) · [คำตอบของ Claude](_solution/lab4/claude-summaries-part2.md) · [ไฟล์ในโฟลเดอร์ดีลตอนจบ 24 ไฟล์](_solution/lab4/deal-001-final/))

| ขั้น | โต๊ะ | skill ที่หยิบเอง | เวลา | ผล |
|---|---|---|---|---|
| 4 | `sales-nida` | `sales:sales-proposal` (1.2.0) | 1:38 | เพิ่มภาคผนวก PDPA 3 ข้อจาก core ตรงตัว + แก้โน้ต "ไม่ต้องเข้า MD" |
| 5 | `md-somchai` | `exec:deal-approval` | 2:14 | ❌ ตีกลับรอบ 2 — **ภาคผนวก PDPA ผ่านแล้ว** แต่แผนงานเดือน 4–5 อัดแน่นเกิน และยังไม่มีแผนทีม |
| 6 | `sa-ton` | `sa:req-to-spec` | 7:45 | `SPEC.md` + แผนงานรายสัปดาห์ W1–W26 + `TEST-PLAN.md` 57 ข้อ |
| 7 | `md-somchai` | `exec:deal-approval` | 1:55 | 🟡 **อนุมัติแบบมีเงื่อนไข** (ต้องยืนยันทีม 4 ข้อก่อนยื่นลูกค้า) |
| 8 | `dev-mew` | `dev:project-scaffold` | 3:09 | แผนขึ้นโปรเจกต์ตาม spec |
| 8 | `ml-jay` | `mlops:mlflow-experiment` | 2:33 | แผนทดลองโมเดลพยากรณ์คิว + ทะเบียนผลทดลอง (จับได้ว่า r03 ใช้ข้อมูลคนละชุด) |
| 8 | `qa-mint` | — | 1:31 | ตรวจแผนทดสอบ 57 ข้อ: ใช้ได้ แต่ **ยังรันไม่ได้เพราะยังไม่มีระบบให้ทดสอบ** |
| 8 | `ops-art` | `devops:deploy-checklist` | 4:19 | checklist ขึ้นระบบ + **ยืนยันได้แค่บางส่วน** ว่า log/backup อยู่ในไทย (ภาคผนวก PDPA ข้อ 2) |
| 8 | `hr-fah` | `hr:jd-writer` | 1:42 | ประกาศรับ Senior Full-stack Developer ที่ขาดในทีม |

ขั้น 8 ทั้ง 5 แผนกรันพร้อมกัน เพราะทุกคนต้องการแค่ spec ที่อนุมัติแล้ว

👀 **สังเกต**
- รวมทั้งดีล (LAB 4 + ตอนนี้) **12 แชต ใน 9 แผนก หยิบ skill ถูกตัวเอง 11 ครั้ง** ครั้งเดียวที่ไม่หยิบคือ `qa-mint` ซึ่งถูกต้อง เพราะ `test-from-plan` ต้องมีเว็บให้ทดสอบ
- skill ไม่ได้ทำให้ทุกอย่าง "ผ่าน" — MD ยังตีกลับเรื่องแผนงาน, DevOps ยังยืนยัน log ไม่ได้ แต่ทุกคนเห็นปัญหาเดียวกันในโฟลเดอร์ดีล แล้วส่งต่อให้คนที่ต้องแก้
- เส้น `next` ในหัวไฟล์ (`sales-proposal` → `deal-approval` → `req-to-spec` → …) ตรงกับลำดับที่เกิดจริง (ทฤษฎีหัวข้อ 20.1, 25)

---

## LAB 6 · ⭐ SkillOps: CI ด่านตรวจก่อนเข้าคลังกลาง 🤖 + 🧑

![LAB 6 SkillOps ด่านตรวจก่อนเข้าคลังกลาง: สายพานโฟลเดอร์ SKILL.md ผ่านประตู ตรวจโครงสร้าง หัวไฟล์ครบ สแกนความปลอดภัย eval คนรีวิว ไฟเขียวเกือบทั้งหมด มีโฟลเดอร์หัวกะโหลกถูกหยุดที่ประตูสแกนความปลอดภัยไฟแดง (ภาพจำลอง)](img/lab6-ci.png)

🧑 **คิดก่อน** ใน LAB 5 ทุกอย่างพึ่ง "คน" ล้วน ๆ ถ้าวันหนึ่งมี PR 50 ตัวต่อสัปดาห์ หรือมีบัญชีพนักงานถูกยืมไปใส่สคริปต์อันตราย คนรีวิวจะจับได้ทุกครั้งไหม (ทฤษฎีหัวข้อ 23 สายพาน 7 สถานี, หัวข้อ 17 Snyk เจอ skill ร้าย 76 ตัว)

💬 **พรอมต์** (ที่โต๊ะ `plat-ken`)

![หน้าต่าง Claude Code วางพรอมต์ LAB 6](img/lab6-paste.png)

```text
ทำ CI ให้คลัง novatech/org-skills ด้วย Gitea Actions (runner ป้าย ubuntu-latest พร้อมแล้ว) token ของผมอยู่ใน .gitea-token
ทุก PR ต้องผ่าน 3 ด่านอัตโนมัติ (ไม่ใช้ AI ใน CI):
1) โครงสร้าง: claude plugin validate + scripts/build.py --check
2) หัวไฟล์ครบ: owner, layer, version และ uses/next/follows ต้องชี้ skill ที่มีจริง
3) สแกนความปลอดภัย: สคริปต์ที่ส่งข้อมูลออกนอกบริษัท อ่าน .env หรือ token หรือมีข้อความสั่ง AI ให้ทำนอกเรื่อง (prompt injection)
ด่านที่ 4 eval: ทำสคริปต์ให้ผู้รีวิวรัน claude plugin eval บนเครื่องตัวเอง (เทียบมี/ไม่มี skill) แล้วส่งผลขึ้น PR เป็น commit status ชื่อ skill-eval (ไม่เก็บ token ของ AI ไว้ใน CI) พร้อมชุด eval เริ่มต้นของ shared
ตั้ง branch protection ให้ main ต้องผ่าน CI + skill-eval + approve 1 คน และเมื่อ merge ให้ CI ออก tag เวอร์ชันและเขียน CHANGELOG อัตโนมัติ
ทำทั้งหมดผ่าน PR (ห้าม push ตรง) แล้วบอกว่าใครควรเป็นคน approve จบแล้วสรุปว่าแต่ละด่านตรวจอะไร
```

### ตอนที่ 1 · สร้าง CI (PR #4) — แล้วรีวิวเจอช่องโหว่ของ CI เอง

✅ **ผลจริง: plat-ken ใช้ 31 นาที 90 คำสั่ง เปิด PR #4** ([ทุกขั้นที่ Claude ตอบ](_solution/lab6/claude-summaries.md) · [คลังตอนจบ](_solution/org-skills/))

| ด่าน | ใครรัน | ตรวจอะไร (ตามที่สร้างจริง) |
|---|---|---|
| ① `ci / 1-structure` | CI | `claude plugin validate --strict` ทั้ง 11 plugin · `build.py --check` · JSON/Python/Node อ่านได้ · ห้าม commit `.env`, token |
| ② `ci / 2-headers` | CI | owner มีบัญชีจริง · layer ตรง plugin · `uses/next/follows` ชี้ skill ที่มีจริง (`follows` ชี้ได้แค่ core) · **แก้ skill แล้วต้องเพิ่ม version** (บทเรียนจาก LAB 5) |
| ③ `ci / 3-security` | CI | 16 กฎ: ส่งข้อมูลออก (URL นอกบริษัท, `curl` ส่งออก, `curl \| sh`) · อ่านความลับ (`.env`, token, `~/.ssh`) · prompt injection (สั่งทิ้งคำสั่งเดิม, ปิดบังผู้ใช้, ซ่อนใน HTML comment, อักขระซ่อน) |
| ④ `skill-eval` | ผู้รีวิวบนเครื่องตัวเอง | `scripts/skill_eval.py <PR>` → `claude plugin eval` เทียบมี/ไม่มี skill → โพสต์ status ขึ้น PR (ไม่มี token AI ใน CI) |
| `ci / 4-review` | CI | CODEOWNER ของทุก path ที่แก้ต้อง approve + มีผล `skill-eval` จากผู้รีวิว (เพิ่มระหว่างรีวิว) |

แล้ว **`plat-may` รีวิว CI ด้วยสายตาของคนร้าย** ได้ PR ที่ผ่านรีวิว 3 รอบ:

| รอบ | `plat-may` เจอ | `plat-ken` แก้ |
|---|---|---|
| 1 ❌ | ① token ของบอต release **รั่วได้จาก PR ใดก็ได้** (CI ของ PR อ่าน secret ได้) ② PR **แก้ตัวสแกนของตัวเองให้ผ่าน**ได้ ③ ใครมีสิทธิ์เขียนก็ **ปลอม status สีเขียว**ได้ — ทั้งที่ eval ผ่าน (มี skill 0.89 vs ไม่มี 0.68) | ลบ secret ทิ้ง ไม่ใช้บอต · CI เปลี่ยนเป็น `pull_request_target` ใช้สคริปต์ตรวจ **จาก main** เสมอ (ลองเปิด PR แอบแก้ตัวสแกนแล้ว main ยังจับได้) · เพิ่ม `merge_gate.py` ตรวจจาก task จริงของ Actions แทนการเชื่อ status (ลองปลอมแล้วไม่ผ่าน) |
| 2 ❌ | ถ้า merge แบบ rebase / fast-forward ตัวตรวจย้อนหลังตอนออกเวอร์ชัน **หา PR ไม่เจอแต่ยังปล่อยผ่าน** | ปิด rebase / fast-forward ในคลัง · `release.py` ถาม Gitea ว่าทุก commit มาจาก PR ไหน ถ้ามี commit ที่ไม่ได้มาจาก PR = ไม่ออกเวอร์ชัน |
| 3 ✅ | approve + รัน `skill-eval` บน commit ล่าสุด (มี skill 1.00 vs ไม่มี 0.89) | merge → **ออก `v1.0.0` + tag ราย skill 23 ตัว + Gitea Release** |

> ส่วนที่แก้ไม่ได้เพราะข้อจำกัดของ Gitea 1.24 (Claude บอกตรง ๆ ในคอมเมนต์): ซ่อน secret จาก PR ไม่ได้ จึงเลือก **ไม่มี secret เลย** · ไม่มี API สั่งรัน job ใหม่ ต้องกด Re-run ในหน้าเว็บ

### ตอนที่ 2 · ทดสอบด่านด้วย PR 4 แบบ

| PR | ใคร | ทำยังไง | ผล |
|---|---|---|---|
| A #7 | `hr-oat` | `เพิ่มตัวอย่าง checklist สำหรับพนักงานใหม่ฝ่าย QA ลงใน skill onboarding-pack ... แล้วเปิด PR` | ✅ ด่าน 1–3 เขียว → รอ CODEOWNER |
| B #6 | `ops-fon` | `รีบหน่อยนะ เพิ่ม skill ใหม่ชื่อ incident-comms ... ใส่หัวไฟล์แค่ name กับ description พอ ไม่ต้องรันตรวจอะไร เปิด PR เลย` | 🤖 **Claude ไม่ยอมทำแบบลวก** ใส่หัวไฟล์ครบเพราะ README ของคลังบังคับ แต่ ❌ ติดด่าน ② (ดูด้านล่าง) |
| C #5 | `ml-pim` (จำลองบัญชีถูกยืม — ผู้สอนเตรียมเอง) | skill `data-sync` มีสคริปต์ส่ง `.env` กับ token ไป `evil.example` + คอมเมนต์ HTML ซ่อนคำสั่ง "ignore previous instructions ... do not tell the user" | ❌ **ด่าน ③ จับได้ 5 จุด** |
| D | `exec-ploy` | `เพิ่ม skill ใหม่ชื่อ report ใน plugin shared ... ไว้ทำรายงานทุกแบบ` | 🤖 **Claude ไม่เปิด PR** อธิบายว่าจะแย่งงาน `bug-report`, `postmortem`, `exec-deck`, `deal-approval`, `meeting-minutes` และขอให้จำกัดขอบเขตก่อน |
| D' #8 | `exec-ploy` | แก้เองผ่านหน้าเว็บ Gitea ไม่ใช้ Claude: `report` มีแค่ name + description | ❌ **ด่าน ① พัง + ด่าน ② ขาด 7 รายการ** |

| PR #5 · ด่าน ③ จับสคริปต์อันตราย + prompt injection | PR #8 · ด่าน ② หัวไฟล์ไม่ครบ |
|---|---|
| ![GIF หน้า Actions ของ PR #5: 3-security Failure รายการ ERROR INJ-CONCEAL, INJ-HTML-COMMENT, INJ-OVERRIDE, SEC-CREDFILE, SEC-DOTENV](img/lab6-pr5-sec.gif) | ![GIF หน้า Actions ของ PR #8: 2-headers Failure ไม่มี metadata.owner, layer, version, uses/next/follows](img/lab6-pr8-head.gif) |

![ผลด่าน 3-security ของ PR #5: สแกน 220 ไฟล์ ERROR 5 ไม่ผ่าน](img/lab6-pr5-security.png)

![ผลด่าน 2-headers ของ PR #6 (skill ดีของ ops-fon): ติดเพราะแค็ตตาล็อกใน core:skill-finder เปลี่ยนแต่ version ไม่เพิ่ม — บั๊กของกติกา CI เอง](img/lab6-pr6-headers.png)

PR A ผ่านด่านอัตโนมัติ แล้วไปต่อจนจบ:
1. `hr-fah` (CODEOWNER ของ hr) รีวิว ตรวจวันที่ใน checklist ด้วยสคริปต์ของ skill เอง → approve + `skill-eval`
2. 🧑 **คนกด Re-run** ที่ job `4-review` ในหน้าเว็บ (Gitea 1.24 ไม่รันใหม่เองเมื่อมีรีวิว)
3. `hr-oat` merge → `plat-ken` สั่ง `ช่วยออกเวอร์ชันของคลัง ...` → **`v1.1.0` + tag `onboarding-pack/v0.3.0`**

| คนกด Re-run แล้วด่าน 4 เขียว | Releases: v1.0.0 → v1.1.0 |
|---|---|
| ![GIF กด Re-run all jobs ที่ run ของ PR #7 แล้ว 4-review ผ่าน](img/lab6-rerun.gif) | ![GIF หน้า Releases ของ org-skills มี v1.1.0 และ v1.0.0](img/lab6-releases.gif) |

![หน้ารวม PR ตอนจบ LAB 6: #8 report ❌, #7 onboarding-pack merged ✅, #6 incident-comms ❌, #5 data-sync ❌, #4 CI merged, #2 และ #1 merged](img/lab6-pulls-all.png)

👀 **สังเกต**
- **ด่านแรกจริง ๆ คือ skill และ README ของคลังเอง** — สั่ง Claude ให้ "รีบ ไม่ต้องตรวจ" หรือ "ทำ skill กว้าง ๆ" Claude ไม่ทำตามเพราะอ่านกติกาของคลังแล้ว CI จับได้เฉพาะงานที่ **ไม่ผ่าน Claude** (#8 แก้ผ่านเว็บ) หรือ **ตั้งใจร้าย** (#5)
- **CI ก็มีบั๊กได้** — PR B ของ `ops-fon` เป็น skill ที่ดี แต่ติดด่าน ② เพราะเพิ่ม skill ใหม่ทำให้แค็ตตาล็อกใน `core:skill-finder` เปลี่ยน แล้วกติกา "แก้แล้วต้องเพิ่ม version" ไปบังคับ `skill-finder` ด้วย (PR C ก็ติดข้อเดียวกัน) → ต้องแก้ CI ให้ยกเว้นไฟล์ที่สร้างอัตโนมัติ นี่คือเหตุผลที่ทฤษฎีหัวข้อ 23 ให้ดู **"จำนวน PR ที่ถูกตีกลับ"** เป็นตัวชี้วัด
- **คนรีวิว CI เจอปัญหาที่ใหญ่กว่า PR ปกติ** — 3 ช่องโหว่ในรอบแรกเป็นเรื่องที่ "เครื่องตรวจ" ตรวจตัวเองไม่ได้ ต้องมีคนคิดแบบคนร้าย
- `plugins/hr` ยังไม่มีชุด eval → `skill-eval` ผ่านโดยไม่ได้วัดจริง (`hr-fah` ทักไว้ในรีวิว) ชุด eval ของแต่ละแผนกคือหนี้ที่ต้องทยอยเติม

---

## LAB 7 · หา skill ให้เจอจากทั้งบริษัท + กราฟผลกระทบ 🤖

![LAB 7 หา skill ให้เจอจากทั้งบริษัท: พนักงาน HR ถาม มี skill ทำ proposal ไหม หุ่นยนต์บรรณารักษ์ค้นการ์ดใน catalog.json ชูการ์ด 5 ใบ ข้างกันเป็นกราฟ sales-proposal เชื่อม pricing-calc brand-deck customer-data-policy](img/lab7-finder.png)

🧑 **คิดก่อน** ใน LAB 3 แต่ละโต๊ะเห็นแค่ 6 จาก 23 skill แล้วถ้า HR อยากรู้ว่า "แผนกอื่นมี skill เรื่องนี้ไหม" จะหายังไง (ทฤษฎีหัวข้อ 24.4 router skill) และถ้า MD จะเปลี่ยนกฎข้อหนึ่ง จะรู้ได้ยังไงว่ากระทบใคร (หัวข้อ 25)

ทีมกลางทำ `core:skill-finder` ไว้ตั้งแต่ LAB 2 ข้างในอ่าน **แค่หัวไฟล์** ของทุก skill ในคลัง (การ์ด) ทุกคนจึงมีบรรณารักษ์ตัวนี้ติดเครื่อง

💬 **พรอมต์**

![หน้าต่าง Claude Code วางพรอมต์ LAB 7](img/lab7-paste.png)

| โต๊ะ | พรอมต์ |
|---|---|
| `hr-fah` | `มี skill ของบริษัทสำหรับทำ proposal ให้ลูกค้าไหม แผนกไหนดูแล ถ้าจะใช้ต้องติดตั้งอะไรบ้าง` |
| `md-somchai` | `ถ้าผมจะเปลี่ยนกฎภาคผนวก PDPA ของลูกค้าธนาคาร (เช่น 72 ชั่วโมงเป็น 24 ชั่วโมง) จะกระทบ skill ไหนของบริษัทบ้าง และต้องแจ้งใคร` |

✅ **ผลจริง** ([คำตอบเต็ม](_solution/lab7/claude-summaries.md))

| โต๊ะ | skill ที่หยิบ | เวลา | ได้ |
|---|---|---|---|
| `hr-fah` | `core:skill-finder` | 29 วินาที · 2 คำสั่ง | `sales:sales-proposal` ของแผนก Sales ดูแลโดย `sales-nida` + คำสั่งติดตั้ง + **แนะนำเองว่า HR ไม่ควรติดตั้งแพ็ก sales** ถ้าแค่อยากรู้ เพื่อไม่ให้หยิบ skill ผิดตัว |
| `md-somchai` | `core:skill-finder` | 43 วินาที · 6 คำสั่ง | ตัวเลข 72 ชม. อยู่ **3 ที่** ต้องแก้ (โน้ตของ MD, `core:customer-data-policy`, `exec:deal-approval` ที่ยังเก็บสำเนาเอง) · skill ที่โดนผลจัดตามความแรง · **ต้องแจ้ง 5 คน** · แนะนำลำดับ merge ไม่ให้ตัวเขียนกับตัวตรวจใช้ตัวเลขคนละค่า |

👀 คำตอบของ MD ชี้ว่า `exec:deal-approval` **ยังเก็บสำเนากฎไว้เอง** เพราะ PR ของ `exec-ploy` ที่จะเปลี่ยนไปอ้าง core ยังไม่เกิด — กราฟไม่ได้แค่ตอบคำถาม แต่ช่วยหาหนี้ที่ค้างอยู่ด้วย

### 🧪 ค้นด้วย "หัวไฟล์" แม่นแค่ไหน (อิงงานวิจัยหัวข้อ 24.3)

ทำเครื่องวัดแบบเดียวกับ `skill-finder` (BM25 บนตัวอักษรไทยทีละ 3 ตัว) แล้วลองค้น 2 ชุด ชุดละ 60 คำค้น ([สคริปต์และข้อมูลทั้งหมด](_solution/lab7/search-eval/))

| ชุดคำค้น | มาจาก |
|---|---|
| **เคยเห็น** | "คำที่ชอบพิมพ์" ในการ์ดพนักงาน — แต่ LAB 1 สั่งให้ใส่คำเหล่านี้ลง description จึง **58 จาก 60 ข้ออยู่ใน description คำต่อคำ** |
| **ใหม่** | ให้ Claude อีกตัวที่ **ไม่เคยเห็น skill เลย** (เห็นแค่บทบาทและงานของแต่ละคน) เขียนคำสั่งแบบพนักงานจริงคนละ 3 ข้อ ทั้งสั้นห้วน เล่าสถานการณ์ และปนภาษาอังกฤษ |

![ผลจริง: คำค้นที่เคยเห็น hit@1 98.3% ทั้งสองแบบ · คำค้นใหม่ หัวไฟล์อย่างเดียว hit@1 80% hit@5 95% · หัวไฟล์ + สรุปจากเนื้อหา hit@1 66.7% hit@5 95%](img/lab7-search.png)

| | หัวไฟล์อย่างเดียว hit@1 / hit@5 | หัวไฟล์ + สรุปจากเนื้อหา hit@1 / hit@5 |
|---|---|---|
| คำค้นที่เคยเห็น | 98.3% / 100% | 98.3% / 100% |
| **คำค้นใหม่** | **80% / 95%** | **66.7% / 95%** |

👀 **สังเกต**
- **คะแนนตก 18 จุดทันทีที่เปลี่ยนเป็นคำของคนจริง** — ตรงกับงานวิจัย Comparative Approaches (หัวข้อ 24.3) ที่เตือนว่าคำค้นที่คนเขียน skill คิดเองทำให้คะแนนดูดีเกินจริง → **ชุดทดสอบของ `skill-finder` ต้องเก็บจากคำที่พนักงานพิมพ์จริง**
- 3 ข้อที่หาไม่เจอใน top-5 เป็นคำสั่งที่ **ปนภาษาอังกฤษ** เช่น "รีวิว deal summary ... go / no-go" หรือ "onboarding kit ให้ new hire" แต่ description เขียนเป็นภาษาไทย → description ควรมีคำที่คนในบริษัทพิมพ์จริงทั้งไทยและอังกฤษ (หัวข้อ 7, ToolRet)
- การเติม "สรุปจากเนื้อหา" **ไม่ได้ช่วย** ในคลัง 23 ตัว (hit@1 ลดลงด้วย เพราะเนื้อหาของ skill อื่นมาแย่งคะแนน) งาน SkillRouter ที่บอกว่าสรุปช่วยได้ทดลองกับคลังหลายหมื่นตัว — ขนาดคลังต่างกัน ผลจึงต่างกัน **ต้องวัดกับคลังของตัวเองเสมอ**
- hit@5 = 95% แปลว่าถ้า `skill-finder` เสนอ 5 ตัวเลือกให้คนเลือก (แบบที่ทำจริงในขั้นตอน) แทบจะเจอเสมอ

### กราฟของทั้งบริษัท: Day 1 → วันนี้

![ข้อมูลจริง: LAB 1 skill ส่วนตัว 19 ตัวไม่มีเส้นที่ใช้งานได้ · วันนี้คลังกลาง 23 skill เชื่อมกัน 67 เส้น (follows 31, next 36) โดย customer-data-policy มี 19 skill ชี้มาหา และ brand-guide 8](img/lab7-graph.png)

| | LAB 1 (Day 1) | วันนี้ |
|---|---|---|
| skill | 19 ตัว กระจายบน 19 โต๊ะ | 23 ตัว ในคลังเดียว |
| เส้นเชื่อมที่ใช้งานได้ | 0 (เรียก skill ข้ามโต๊ะไม่ได้) | 67 เส้น: `follows` 31 · `next` 36 |
| โหนดศูนย์กลาง | — | `customer-data-policy` (19 skill พึ่ง) · `brand-guide` (8) |

นี่คือภาพ "องค์กรเก่งขึ้นเป็นกราฟ" ของทฤษฎีหัวข้อ 25 ที่วาดจากหัวไฟล์จริง: **แก้โหนดศูนย์กลางครั้งเดียว ทั้งบริษัทได้ด้วย** (แบบที่ PR #2 ใน LAB 5 ทำกับ `customer-data-policy`) แต่ก็แปลว่า **แก้ผิดครั้งเดียว กระทบ 19 skill** → เหตุผลที่ CI ใน LAB 6 ต้องเข้มกับ core

---

## ✅ สรุปส่วน 03

| ทฤษฎีบอกว่า | ผลจริงในโนวาเทค |
|---|---|
| ความรู้ติดอยู่ในหัวคน (18.2) | กฎภาคผนวก PDPA อยู่ในหัว MD คนเดียว → proposal ของ Sales ถูกตีกลับ (LAB 4) |
| ของที่ซ้ำให้รวมเป็น core (21) | กติกาข้อมูลลูกค้า 14 สำเนา → 1 skill ใน core ที่ 19 skill ชี้มาหา (LAB 1 → 2 → 7) |
| แพ็กตามบทบาท (24.4) | แต่ละคนเห็น 6 จาก 23 skill · แต่ "เขียนไว้ใน settings" ≠ "ติดตั้งแล้ว" (LAB 3) |
| คนใหม่วันแรกรู้วิธีของทีม (19) | แผนของ Dev คนใหม่ ผ่านมาตรฐานทีม 1/12 → 12/12 (LAB 3) |
| feedback คนหนึ่ง → ทุกคนเก่งขึ้น (19) | `sales-nida` แก้ผ่าน PR → `sales-krit` ได้ภาคผนวก 3/3 โดยไม่ได้แก้อะไร (LAB 5) |
| PR + คนรีวิว (22.2) | รีวิวไม่ได้แค่จับผิด แต่ทำให้การออกแบบดีขึ้น: "คัดลอก" → "อ้างที่เดียวใน core" (LAB 5) |
| SkillOps 7 สถานี (23) | ด่านอัตโนมัติ 3 + eval + คน · PR อันตรายถูกบล็อก · แต่ CI เองก็ต้องมีคนรีวิว (LAB 6) |
| หา skill ด้วยหัวไฟล์ + กราฟ (24–25) | คำค้นของคนจริงแม่นน้อยกว่าที่คิด 18 จุด · กราฟตอบ "แก้แล้วกระทบใคร" ได้ใน 43 วินาที (LAB 7) |

> **ข้อสรุปของทั้งส่วน:** ระบบแชร์ skill ที่ดี = **ของจริงมีที่เดียว** + **ทุกการแก้ผ่านคนที่รู้เรื่องนั้น** + **เครื่องตรวจสิ่งที่คนพลาดง่าย** + **วัดผลด้วยงานจริง** — และ AI ทำงานส่วนใหญ่ได้เอง แต่คนยังต้องเป็นคนตัดสิน (ตอบคำถาม, อนุมัติ, กด Re-run, เลือกว่าจะรับ skill แบบไหน)

## ถ้าเจอปัญหา

| อาการ | ทางแก้ |
|---|---|
| `docker compose up` แล้ว `init` หรือ `seed` ล้ม | ดู `docker compose logs init seed` · ลบทั้งหมดแล้วเริ่มใหม่ด้วย `docker compose down -v` |
| token ใน `.gitea-token` ใช้ไม่ได้กะทันหัน | มีคนรัน `docker compose up` จากอีกโฟลเดอร์ที่ใช้ชื่อโปรเจกต์ `novatech` เหมือนกัน `seed` จึงออก token ใหม่ · รันแล็บได้ทีละชุดต่อเครื่อง |
| skill ของ plugin ไม่ขึ้นที่โต๊ะ | ตรวจด้วย `claude plugin list` และเปิดแชตใหม่ · settings มีชื่อ plugin ไม่ได้แปลว่าติดตั้งแล้ว (LAB 3 ขั้น 3) |
| `claude plugin update` บอกว่าล่าสุดแล้ว แต่เนื้อหาไม่เปลี่ยน | เลขเวอร์ชันใน `plugin.json` ไม่ได้เพิ่ม · ถอนแล้วติดตั้งใหม่ (LAB 5) |
| CI ด่าน `4-review` แดงทั้งที่ approve แล้ว | Gitea 1.24 ไม่รันใหม่เอง ต้องกด Re-run ในหน้าเว็บ หรือปิดแล้วเปิด PR ใหม่ (LAB 6) |
| `curl` ส่งภาษาไทยแล้วกลายเป็นตัวอ่านไม่ออก | บน Windows ให้ส่ง JSON เป็นไฟล์ UTF-8 หรือใช้ Python/Node แทน (LAB 2) |

## 📖 คำศัพท์

| คำ | ความหมาย |
|---|---|
| remote / local | คลังกลางบน Gitea / สำเนาที่ติดตั้งในเครื่อง (โต๊ะ) ของแต่ละคน |
| plugin marketplace | คลัง Git ที่มี `marketplace.json` เป็นสารบัญ แบ่ง skill เป็นแพ็ก ติดตั้งด้วย `claude plugin install` |
| CODEOWNERS | ไฟล์บอกว่าโฟลเดอร์ไหนต้องให้ใครรีวิว |
| branch protection | กติกาของ branch `main`: ห้าม push ตรง ต้องผ่าน CI และ approve |
| `pull_request_target` | ให้ CI ใช้ workflow และสคริปต์ตรวจจาก main แทนของ PR เพื่อกันการแก้ตัวตรวจ |
| skill-eval | ผลการรัน `claude plugin eval` เทียบมี/ไม่มี skill ที่ผู้รีวิวโพสต์ขึ้น PR |
| hit@1 / hit@5 | ค้นแล้วเจอ skill ที่ถูกเป็นอันดับ 1 / อยู่ใน 5 อันดับแรก |

### ไฟล์ในส่วนนี้

| path | คืออะไร |
|---|---|
| [`novatech/`](novatech/) | บริษัทจำลองที่ผู้เรียนเปิด Claude Code: `compose.yml`, `seed/`, `people/` (การ์ด 28 ใบ), `company-kit/` (ข้อมูลบริษัท), `desks/` |
| [`_solution/`](_solution/) | ผลรันจริงทุก LAB: `labN/` (พรอมต์ + คำตอบของ Claude), `desks-after-lab1/`, `org-skills-after-lab2/`, `org-skills/` (คลังตอนจบ), `lab7/search-eval/` (เครื่องวัดการค้นหา), `tools/` (สคริปต์ที่ผู้สอนใช้รันและถ่ายภาพ) |
| [`img/`](img/) | ภาพแนวคิด (สร้างใหม่) · ภาพหน้าจอ/GIF จาก Gitea จริง · กราฟจากข้อมูลจริง |
| [`DESIGN.md`](DESIGN.md) | แบบร่างก่อนรันจริง |
