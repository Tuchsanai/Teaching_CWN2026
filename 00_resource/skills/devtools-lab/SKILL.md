---
name: devtools-lab
description: จำลองและตรวจสอบ LAB วิชา DevTools ใน Docker container แบบแยกและลบทิ้งหลังใช้งาน ใช้เมื่อต้องรันหนึ่งหรือหลายการทดลอง ทดสอบคำสั่งหรือบริการผ่าน SSH (password หรือ key devtoolSSH) หรือ JupyterLab หรือยืนยันว่า LAB ทำงานได้โดยไม่กระทบ environment หลัก
---

# DevTools Lab

รันแต่ละการทดลองใน container ชั่วคราวของตัวเอง แยกชื่อและ port ไม่ให้ชนกัน ตรวจสอบผลลัพธ์ที่โจทย์ต้องการ และลบทุก container ที่งานนี้สร้างทันทีเมื่อการทดลองจบ

**ไฟล์นี้อยู่ครบในตัวเอง** ข้อมูล image, port, credential และคำสั่งตรวจสอบทั้งหมดที่ skill นี้ต้องใช้อยู่ด้านล่างแล้ว ห้ามไปเปิดอ่าน README, คู่มือ setup, docker-compose หรือไฟล์อื่นในโปรเจกต์เพื่อหาค่าเหล่านี้ และห้ามเพิ่มการอ้างอิงไปยังไฟล์ภายนอกกลับเข้ามาในไฟล์นี้ — path ภายนอกเคยถูกย้ายจนอ้างไม่ได้มาแล้ว ให้ไฟล์นี้เป็นแหล่งข้อมูลเดียว

อ่านไฟล์อื่นได้เฉพาะไฟล์ของ LAB ที่ผู้ใช้สั่งให้ทดสอบโดยตรงเท่านั้น หากค่าในไฟล์นี้ไม่ตรงกับของจริงที่เจอตอนรัน ให้รายงานผู้ใช้และแก้ไฟล์นี้ ไม่ใช่ไปอ้างไฟล์อื่นแทน

## สเปกของ image ที่ใช้ทดลอง

| หัวข้อ | ค่า |
|--------|-----|
| Image (Docker Hub) | `tuchsanai/devtools:2569_1` — SSH ได้ **เฉพาะ password** (ไม่มีระบบ key `devtoolSSH`) |
| Image (build เอง) | build จาก `Dockerfile` ในโฟลเดอร์ reference ของวิชา (โฟลเดอร์ที่มี `Dockerfile`, `start.sh`, `jupyter_overrides.json`, `Devtool_SSH/`) — รองรับทั้ง password และ key ผู้เรียน tag เป็น `devtools:2569_1` |
| Base | Ubuntu 24.04, timezone `Asia/Bangkok`, locale UTF-8 |
| Docker | Docker-in-Docker (docker-ce, containerd, buildx, compose plugin) — ต้องรันด้วย `--privileged` |
| Runtime | Python 3 (`python` → `python3`), Node.js 22 LTS + npm/npx |
| JupyterLab | 4.x สตาร์ตอัตโนมัติตอน container ขึ้น kernel `python3` และ `bash` |
| Tooling | git (ล่าสุดจาก git-core PPA ทดสอบได้ 2.55), curl, wget, vim, nano, less, net-tools, ping, dnsutils, openssh-server |
| Workdir | `/workspace` |
| Port ใน container | `22` (SSH), `8888` (JupyterLab) |
| SSH login (password) | user `root` / password `passwd` — ใช้ได้ทั้งสอง image |
| SSH login (key) | เฉพาะ image ที่ build เอง: key ed25519 ชื่อ `devtoolSSH` / `devtoolSSH.pub` ในโฟลเดอร์ `/etc/devtools/ssh` (map มาจาก `Devtool_SSH/` บน host) — ดูหัวข้อ "ทดสอบ SSH ด้วย key" |
| JupyterLab login | ไม่มีรหัสผ่านและไม่ต้องใช้ token (ตั้งได้ด้วย `-e JUPYTER_PASSWORD=...`) — root_dir คือ `/` แสดง hidden file (`.env`, `.git`) ใน file browser, kernel `python3` และ `bash` |
| PID 1 | bash จาก `start.sh` ไม่ใช่ systemd — `systemctl` ใช้ไม่ได้ |

ข้อควรรู้เพิ่มเติมของ image นี้:

- container รันเป็น `root` ไม่มี user `student`
- `ss` อาจไม่มีติดมา ให้ตรวจ SSH จากข้างในด้วย bash `/dev/tcp/127.0.0.1/22` แทน
- `docker run` โดยไม่ใส่ `--hostname` จะได้ hostname เป็น container ID (เช่น `a8e69b9ae950`) ไม่ใช่ `devtools` — prompt `root@devtools` ในเอกสาร LAB จะตรงเฉพาะเมื่อรันผ่าน compose (ตั้ง `hostname: devtools`) หรือใส่ `--hostname devtools` อย่าตีว่า LAB ผิดเพราะ hostname ไม่ตรง
- รันด้วย `-dit` แล้ว `start.sh` จะ `exec bash` เป็น PID 1 (มี tty) ถ้าไม่มี tty จะ `tail -F /var/log/jupyter.log` แทน log อยู่ที่ `/var/log/dockerd.log` และ `/var/log/jupyter.log`
- Claude Code และ Codex **ไม่ได้ติดตั้งมาให้** ต้องติดตั้งเองเมื่อ LAB ต้องใช้ (ดูหัวข้อด้านล่าง)

รหัสผ่าน `passwd` ใช้ได้เฉพาะกับ image สำหรับ LAB นี้เท่านั้น ห้ามนำไปใช้กับ environment อื่นหรือถือว่าเป็นข้อมูลรับรองสำหรับ production และห้าม publish port ของ container ทดลองออก internet

## ห้ามยุ่งกับ container ของผู้เรียน

ผู้เรียนมี container ชื่อ **`devtools`** (ไม่มีขีดท้าย) เป็นพื้นที่ทำงานถาวรที่ VS Code attach อยู่ ตั้งไว้ด้วย `restart: unless-stopped`, `hostname: devtools` มี volume `./workspace:/workspace`, `./Devtool_SSH:/etc/devtools/ssh` และ named volume `devtools-dind:/var/lib/docker` ห้ามรัน compose ของผู้เรียนเพื่อทดลอง (ใช้ `container_name: devtools` และโหลด `.env` ส่วนตัว) ห้าม stop, `rm`, `docker compose down` หรือ `docker run --name devtools` ทับ เว้นแต่ผู้ใช้สั่งอย่างชัดเจนในข้อความนั้น ๆ

โดยค่าเริ่มต้น container `devtools` จอง **host port `2222` (SSH) และ `8888` (JupyterLab)** ไว้ ให้ถือว่าสองพอร์ตนี้ไม่ว่างเสมอ **แม้ตอนตรวจจะว่าง** (container อาจถูก stop ไว้ชั่วคราว) แต่ยังต้องตรวจของจริงก่อนทุกครั้งเพราะผู้ใช้เปลี่ยนค่าได้

ห้าม build ทับ tag `devtools:2569_1`, `tuchsanai/devtools:2569_1` หรือ `tuchsanai/devtools:latest` ของผู้ใช้ ถ้าต้อง build เพื่อทดลองให้ใช้ tag ของงานเอง เช่น `devtools-labtest:<hashid>` แล้ว `docker rmi` ทิ้งตอน cleanup

container ของ skill นี้ต้องขึ้นต้นด้วย `devtools-` เสมอ ตัวกรอง `--filter "name=^devtools-"` ที่ใช้ทั้งเอกสารนี้จึงไม่แตะชื่อ `devtools` แต่ห้ามเปลี่ยนไปใช้ pattern ที่กว้างกว่านั้น เช่น `name=devtools`

การลบ container ทำให้ไฟล์ใน writable layer หายทั้งหมด หากมีงานที่ต้องเก็บ ให้ `docker cp` ออกมาก่อนลบ

## กฎการแยกการทดลอง

- สร้างชื่อย่อของการทดลองเป็นตัวพิมพ์เล็กจาก LAB และวัตถุประสงค์ของงาน
- สร้าง hash ID สั้นสำหรับทุกครั้งที่รัน แล้วตั้งชื่อ container เป็น `devtools-<ชื่อการทดลอง>-<hashid>` เช่น `devtools-nginx-volume-a1b2c3` โดยห้ามสร้าง hash จากข้อมูลลับ
- ใช้ image `tuchsanai/devtools:2569_1` พร้อม `--privileged` เสมอ (จำเป็นสำหรับ Docker-in-Docker) ยกเว้น LAB ที่ต้องใช้ key login ให้ใช้ image ที่ build เองด้วย tag ของงาน และบันทึก image ID ที่ใช้จริงไว้ในรายงาน
- map host port ที่ไม่ซ้ำไปยัง port 22 ของ container เริ่มพิจารณาจาก `2223` และเลือก port ว่างที่มีค่าน้อยที่สุด (ข้าม `2222` ที่เป็นของ `devtools`) เว้นแต่ผู้ใช้กำหนด port มาแล้ว
- publish port อื่นเฉพาะเมื่อ LAB ต้องใช้จริง สำหรับ JupyterLab ให้ map ไปที่ port `8888` ของ container โดยเริ่มพิจารณา host port จาก `8889` แล้วเลือกเลขว่างถัดไป (ข้าม `8888` ที่เป็นของ `devtools`)
- หากผู้ใช้ระบุ port ที่ไม่ว่าง ให้แจ้งผู้ใช้ ห้ามเปลี่ยนไปใช้ port อื่นเงียบ ๆ
- ก่อนเริ่ม ให้ตรวจ container ที่ขึ้นต้นด้วย `devtools-` และ port ที่ถูกใช้อยู่ ห้ามใช้ชื่อหรือ port ที่เป็นของการทดลองอื่น รวมถึง port ที่ container `devtools` ของผู้เรียนจองไว้
- container ที่ขึ้นต้น `devtools-` อาจเป็นของ agent อื่นและใช้ image อื่น (เช่น `devtools-<lab>-<hash>-jenkins` จาก `jenkins/jenkins`) ให้นับรวมในโควตาแต่ห้ามแตะ
- ให้มี `devtools-` container ที่กำลังรันพร้อมกันได้รวมไม่เกิน 7 ตัว ตรวจจำนวนก่อนสร้างทุกครั้ง หากตัวใหม่จะทำให้เกินขีดจำกัด ให้รอการทดลองที่งานนี้เป็นเจ้าของจบและถูกลบ ห้ามลบ container ของ agent อื่นเพื่อแย่งโควตา
- กรณีทำงานหลายโปรเจกต์หรือหลาย agent ให้บันทึก mapping ระหว่าง agent เจ้าของ ชื่อ container และ host port อย่างชัดเจน แต่ละ agent ดูแลเฉพาะ container ของการทดลองที่ตนรับผิดชอบ

คำสั่งสำหรับตรวจสอบ:

```bash
docker ps --filter "name=^devtools-"
docker ps -a --format '{{.Names}}\t{{.Ports}}' --filter "name=^devtools-"
docker ps -a --format '{{.Names}}\t{{.Ports}}'   # ดูภาพรวมรวมถึง devtools ของผู้เรียน เพื่อเลี่ยง port ชน
```

ถ้า agent อยู่ใน container (มี `/.dockerenv`) port ที่ `ss`/`/dev/tcp/127.0.0.1` เห็นเป็นของ container agent เอง ไม่ใช่ host (เคยเจอ `8889` เป็น jupyter-lab ของ agent ทั้งที่ host ว่าง) ให้ตรวจ host port ผ่าน `docker ps` ร่วมกับ probe ที่ gateway:

```bash
G=$(ip route | awk '/default/ {print $3}')
for p in 2223 2224 8889 8890; do timeout 2 bash -c "(echo > /dev/tcp/$G/$p)" 2>/dev/null && echo "$p busy" || echo "$p free"; done
```

## การรันการทดลอง

หากพบ container เก่าที่มีชื่อตรงกันและตรวจสอบแล้วว่าปลอดภัยที่จะสร้างทับ ให้ลบเฉพาะชื่อนั้นก่อน:

```bash
docker rm -f devtools-<ชื่อการทดลอง>-<hashid> 2>/dev/null
```

เริ่ม server แยกสำหรับการทดลองด้วย port ที่จัดสรรไว้:

```bash
docker run -dit --name devtools-<ชื่อการทดลอง>-<hashid> --privileged \
  -p <ssh-host-port>:22 tuchsanai/devtools:2569_1
```

เพิ่ม `-p <jupyter-host-port>:8888` เมื่อ LAB ต้องใช้ JupyterLab:

```bash
docker run -dit --name devtools-<ชื่อการทดลอง>-<hashid> --privileged \
  -p <ssh-host-port>:22 -p <jupyter-host-port>:8888 tuchsanai/devtools:2569_1
```

ยืนยันว่า container กำลังทำงานและ port ที่ publish ตรงกับ mapping ก่อนเริ่มทำ LAB การตรวจก่อนสร้างไม่รับประกันว่า port จะยังว่างตอน start จริง

รอให้บริการพร้อมด้วย probe ที่มี deadline (เช่น 60 วินาที) แทนการ `sleep` ตายตัว:

```bash
docker exec <container> bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done'  # sshd พร้อม
docker exec <container> docker info                                                                    # dockerd ข้างในพร้อม
```

เชื่อมต่อผ่าน SSH เมื่อการทดลองต้องใช้ server session:

```bash
ssh root@localhost -p <ssh-host-port>     # password: passwd
```

ใช้ `docker exec` สำหรับคำสั่งทั่วไป และ `docker cp` สำหรับ fixture ที่จำเป็น

**bind mount (`-v src:dst`) แปล path ฝั่ง Docker host ไม่ใช่ฝั่ง agent** ถ้า agent อยู่ใน container path อย่าง scratchpad `/tmp/...` ไม่มีบน host และ `/root/workspace` ของ agent คือ path อื่นบน host ให้ดู mapping ก่อนด้วย `docker inspect $(hostname) --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'` แล้วใช้ Source ที่แปลงแล้ว (เช่น Docker Desktop บน Windows: `/run/desktop/mnt/host/c/Users/...`) หรือเลี่ยงไปใช้ `docker create` + `docker cp` + `docker start` รันคำสั่ง Docker ของ LAB **ภายใน container** ห้าม mount Docker socket ของ host หรือ directory งานจริงเข้า container ทดลอง

`--privileged` มีไว้ให้ Docker-in-Docker ทำงาน ไม่ใช่ sandbox ใช้กับ LAB ที่เชื่อถือได้เท่านั้น

ทำเฉพาะสิ่งที่ LAB ร้องขอภายใน container และตรวจสอบผลลัพธ์ที่สังเกตได้จริง เช่น สถานะ service, network response, mounted data, build output หรือ configuration state การที่ container ขึ้นได้ไม่เท่ากับ LAB ผ่าน

## ทดสอบ SSH ด้วย key (`devtoolSSH`)

ใช้เมื่อ LAB ให้ login ด้วย key ต้องใช้ image ที่ build จาก `Dockerfile` ของโฟลเดอร์ reference — image บน Docker Hub ปฏิเสธ key (`Permission denied (publickey,password)`) ทดสอบยืนยันแล้ว

```bash
docker build -t devtools-labtest:<hashid> <โฟลเดอร์ reference>
docker run -dit --name devtools-<ชื่อการทดลอง>-<hashid> --privileged -p <ssh-host-port>:22 \
  -v "<host-path>/Devtool_SSH:/etc/devtools/ssh:ro" devtools-labtest:<hashid>
docker logs devtools-<ชื่อการทดลอง>-<hashid> | grep "SSH key"
# [start.sh] SSH key login enabled: /etc/devtools/ssh/devtoolSSH.pub
```

พฤติกรรมของ `start.sh` ที่ตรวจแล้ว:

- มี `devtoolSSH.pub` ในโฟลเดอร์ → copy บรรทัดแรก (ตัด `\r`) ต่อท้าย `/root/.ssh/authorized_keys` (chmod 600, owner root) จึงใช้ได้แม้ bind mount จาก Windows เป็น 777 และ mount แบบ `:ro` ได้
- โฟลเดอร์ว่างและเขียนได้ → สร้างคู่ ed25519 ใหม่ (comment `devtools-lab`) ลงโฟลเดอร์นั้นและ log `generated new SSH key pair` — **ห้าม mount `Devtool_SSH/` จริงของผู้ใช้แบบเขียนได้ในการทดลอง** ให้ mount `:ro` หรือใช้โฟลเดอร์ชั่วคราวของงานเองเมื่อต้องทดสอบการสร้าง key
- ไม่มี `.pub` และเขียนไม่ได้ → log `SSH key login disabled` password ยังใช้ได้
- **authorized_keys สะสม ไม่ลบ key เก่า**: ลบ key แล้ว `docker restart` ได้คู่ใหม่ แต่ key เก่ายัง login ได้ใน container เดิม ต้อง `docker rm -f` แล้วรันใหม่ถึงจะเพิกถอน key เก่า

ฝั่ง client ต้อง `chmod 600` private key ก่อน (ถ้า 644 ssh จะขึ้น `UNPROTECTED PRIVATE KEY FILE` และไม่ใช้ key) ทดสอบด้วย copy ของ key ใน scratchpad ไม่ต้อง chmod ไฟล์ใน repo ผู้ใช้ และใช้ `BatchMode=yes` ยืนยันว่าเข้าได้โดยไม่ถามรหัสผ่าน:

```bash
O="-o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
ssh -i <key> $O -p <ssh-host-port> root@<host> "whoami && docker --version"
scp -i <key> $O -P <ssh-host-port> ./hello.txt root@<host>:/workspace/   # ssh ใช้ -p, scp ใช้ -P
```

ทดสอบ password แบบไม่ต้องพิมพ์เมื่อไม่มี `sshpass` (รหัส LAB `passwd` เท่านั้น):

```bash
printf '#!/bin/sh\necho passwd\n' > <scratchpad>/askpass && chmod +x <scratchpad>/askpass
SSH_ASKPASS=<scratchpad>/askpass SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid \
  ssh -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -p <ssh-host-port> root@<host> whoami </dev/null
```

`<host>` คือ `localhost` หรือ gateway เมื่อ agent อยู่ใน container

## ติดตั้งและตรวจ CLI

image ฐานไม่มี Claude Code และ Codex ติดมา ให้ติดตั้งเฉพาะเมื่อ LAB ต้องใช้ CLI เหล่านี้:

```bash
docker exec -it devtools-<ชื่อการทดลอง>-<hashid> bash -c \
  'curl -fsSL https://claude.ai/install.sh | bash && npm install -g @openai/codex'
```

ตรวจผล:

```bash
whoami            # ต้องได้ root
claude --version
codex --version
```

หากขึ้น `claude: command not found` แปลว่าเป็นปัญหา PATH ไม่ใช่การติดตั้งล้มเหลว ให้เพิ่มพาธติดตั้งใน shell ปัจจุบันก่อนตรวจซ้ำ:

```bash
export PATH="$HOME/.local/bin:$PATH"
claude --version
```

การเห็นเวอร์ชันยืนยันแค่ว่ามีเครื่องมือแล้ว **ยังไม่ใช่การเข้าสู่ระบบ** หาก LAB ต้องใช้บัญชีจริง ให้ทำตามหัวข้อการปกป้องข้อมูลรับรองด้านล่าง

## ใช้งานผ่าน JupyterLab

เมื่อ publish port Jupyter ไว้ เปิดที่ `http://localhost:<jupyter-host-port>/lab` แล้วใช้ **Launcher → Other → Terminal** ได้ shell เดียวกับที่เข้าผ่าน SSH หรือ `docker exec`

ตรวจแบบไม่ใช้ browser: `curl -s -o /dev/null -w '%{http_code}' http://<host>:<jupyter-host-port>/lab` ต้องได้ `200` และ `curl -s http://<host>:<jupyter-host-port>/api/contents/workspace` ต้องเห็นไฟล์ที่ขึ้นต้นด้วย `.` ด้วย (hidden file เปิดไว้) terminal มี copy/paste ด้วย `Ctrl+Shift+C/V`, `Ctrl+Insert`/`Shift+Insert` และ `Ctrl+V`

image นี้สตาร์ต `jupyter-lab` ให้อัตโนมัติตั้งแต่ container ขึ้น ไม่ต้องสั่งเอง และไม่ต้องใช้ token ตรวจได้ด้วย `docker exec <container> jupyter server list`

**ถ้า agent ทำงานอยู่ใน container เอง** `localhost` ของ agent ไม่ใช่ Docker host — `curl http://localhost:<jupyter-host-port>` จะได้ code `000` ทั้งที่บริการปกติดี ให้เปลี่ยนไปเรียกผ่าน gateway หรือ IP ของ container ทดลองแทน แล้วรายงาน URL แบบ `localhost` ให้ผู้ใช้ตามปกติ ห้ามแก้ปัญหานี้ด้วยการเพิ่ม `sleep` หรือเปิด bind `0.0.0.0`:

```bash
ip route | awk '/default/ {print $3}'                      # gateway ที่ใช้แทน localhost ของ host
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container>   # ยิงตรงที่ port 8888
```

Terminal ของ JupyterLab เจอปัญหา PATH เดียวกับข้างต้น ให้ `export PATH="$HOME/.local/bin:$PATH"` ก่อนเรียก `claude`

ตรวจว่าเป็นคนละ port กับ JupyterLab ของ container `devtools` ที่ผู้เรียนเปิดค้างอยู่ (ปกติ `8888`) ก่อนรายงาน URL

## การปกป้องตัวตนและข้อมูลรับรอง

- ห้ามใส่ email จริง ชื่อจริง access token, username จริง รหัสผ่าน API key หรือข้อมูลรับรองที่ใช้งานได้จริง ลงในเอกสาร LAB, ตัวอย่าง, template, screenshot, ไฟล์ที่สร้าง หรือรายงานผล
- ใช้ placeholder ที่เห็นชัด เช่น `<YOUR_EMAIL>`, `<YOUR_NAME>`, `<YOUR_USERNAME>`, `<YOUR_TOKEN>` และ `<YOUR_PASSWORD>` ในเนื้อหาที่ผู้เรียนจะเห็น
- ใช้ค่าจริงได้เฉพาะเมื่อจำเป็นต่อการทดลองจริงที่ได้รับอนุญาตแล้วเท่านั้น ให้เก็บค่าจริงไว้ใน runtime environment ห้าม echo และห้ามคัดลอกลงในคำสั่งหรือ output ที่จะถูกบันทึก
- ห้าม mount หรือ copy credential ของ Claude Code / Codex จากเครื่องหลักหรือจาก container `devtools` เข้า container ทดลอง ให้ login ใหม่ในการทดลองที่ได้รับอนุญาตเท่านั้น
- ห้ามโหลดไฟล์ `.env` ส่วนตัวของเครื่องหลักเข้า container ทดลอง แม้ container `devtools` ของผู้เรียนจะตั้งค่าให้โหลดไว้ก็ตาม
- หาก log เผยข้อมูลจริงโดยไม่ตั้งใจ ให้ปกปิดข้อมูลก่อนนำเสนอ หากไม่สามารถปกปิดอย่างปลอดภัย ให้สรุปเฉพาะผลการทดสอบแทนการคัดลอก log

## ต้อง cleanup ทุกครั้ง

บันทึกทุก container ที่งานสร้างพร้อม agent เจ้าของ และออกแบบ cleanup ให้ยังทำงานเมื่อคำสั่งล้มเหลว การตรวจสอบไม่ผ่าน SSH ถูกขัดจังหวะ หรือเริ่มหลาย container ได้เพียงบางส่วน

แต่ละ agent ต้องลบ container ของตัวเองทันทีเมื่อการทดลองจบ และยืนยันว่าลบแล้วก่อนส่งผลหรือส่งงานกลับ ห้ามทิ้ง cleanup ให้ coordinator หรือ agent อื่น

ลบ container ที่เป็นเจ้าของด้วยชื่อแบบเจาะจง:

```bash
docker rm -fv devtools-<ชื่อการทดลอง>-<hashid>
```

ใช้คำสั่งลบแบบกว้างด้านล่างเฉพาะเมื่อผู้ใช้สั่งให้ลบ `devtools-` container ทั้งหมดอย่างชัดเจน หรือยืนยันได้ว่า container ที่ตรงเงื่อนไขทั้งหมดเป็นของงานปัจจุบัน คำสั่งนี้ไม่แตะ container ชื่อ `devtools` ของผู้เรียน และห้ามแก้ pattern ให้ครอบคลุมชื่อนั้น ห้ามใช้ `docker system prune` หรือคำสั่งลบแบบกวาดทั้งเครื่อง:

```bash
docker rm -f $(docker ps -aq --filter "name=^devtools-") 2>/dev/null
```

ปิดงานด้วยการตรวจสอบว่าไม่มี container ของงานค้างอยู่:

```bash
docker ps -a --filter "name=^devtools-"
```

การลบ container ทดลองทิ้งข้อมูล Docker-in-Docker ที่อยู่ข้างในทั้งหมด ส่วน resource บน host ที่งานสร้างเพิ่ม เช่น named volume, network, image tag ของงาน (`docker rmi devtools-labtest:<hashid>`), โฟลเดอร์ชั่วคราวที่ใช้ bind mount และสำเนา private key ใน scratchpad ต้องตามลบแยก เพราะ `-v` ลบเฉพาะ anonymous volume ไม่ลบ named volume

ห้ามรายงานว่าการทดลองเสร็จหรือส่งต่องานจนกว่าจะตรวจผล LAB และยืนยัน cleanup ของ agent เจ้าของแล้ว รายงานชื่อการทดลอง port ที่ใช้ (SSH และ Jupyter ถ้ามี) image ID ผลการตรวจสอบ และสถานะ cleanup หาก cleanup ไม่สำเร็จ ให้ระบุชื่อ container ที่ยังค้างและลองลบแบบเจาะจงอย่างปลอดภัยต่อก่อนหยุด
