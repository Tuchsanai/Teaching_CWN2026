---
name: k8s-lab
description: จำลองและตรวจสอบ LAB Kubernetes (kind ใน Docker-in-Docker) ใน container ชั่วคราว k8s-lab-<ชื่อการทดลอง>-<hashid> จาก image tuchsanai/devtools-kind:2569_1 รันหลายการทดลองพร้อมกันได้โดยแยกชื่อ/port อัตโนมัติด้วยสคริปต์ที่ฝังในไฟล์ (single-file, stand-alone) ตรวจผลแบบ PASS/FAIL และลบทิ้งหลังใช้งาน ใช้เมื่อต้องทดลองคำสั่ง kubectl/kind/helm/k9s สร้างคลัสเตอร์ด้วย k8s-up ทดสอบ manifest, NodePort 30080-30082, kind load docker-image, ทดสอบ SSH (password หรือ key devtoolSSH) หรือ JupyterLab ของ k8s-lab, หรือ build/push image devtools-kind โดยไม่กระทบ container k8s-lab ของผู้เรียน
---

# K8s Lab

รันแต่ละการทดลอง Kubernetes ใน container ชั่วคราวของตัวเอง ภายในมี dockerd (Docker-in-Docker) ที่ kind ใช้สร้าง node เป็น container แยกชื่อและ port ไม่ให้ชนกัน ตรวจผลที่ LAB ต้องการ แล้วลบทุก container ที่งานนี้สร้างทันทีเมื่อจบ

**ไฟล์นี้มีข้อมูลครบในตัว** ค่า image, port, credential ของ LAB, พฤติกรรมของสคริปต์ และคำสั่งตรวจสอบที่ต้องใช้อยู่ด้านล่างและในสคริปต์ที่ฝังท้ายไฟล์แล้ว ทั้งหมดได้จากการทดลองจริงเมื่อ 4–5 ต.ค. 2569 ไม่ต้องไปเปิด README หรือ Dockerfile เพื่อหาค่าเหล่านี้ และห้ามเพิ่ม path ไฟล์ภายนอก (เช่น path ของ `.env`, README, Dockerfile หรือโฟลเดอร์ของเครื่องใดเครื่องหนึ่ง) เข้ามาใน skill นี้หรือในสคริปต์ ถ้าค่าจริงตอนรันไม่ตรงกับที่เขียนไว้ ให้รายงานผู้ใช้และแก้ไฟล์นี้ อ่านไฟล์อื่นได้เฉพาะไฟล์ LAB ที่ผู้ใช้สั่งให้ทดสอบโดยตรง

## สเปกของ image

| หัวข้อ | ค่า |
|--------|-----|
| Image หลัก (Docker Hub) | **`tuchsanai/devtools-kind:2569_1`** ใช้ตัวนี้เป็นค่าเริ่มต้นเสมอ (push 4 ต.ค. 2569 จาก `devtools-kind:2569_1`, image ID `8108a1bc7901`, digest `sha256:75a9ae45…c472c`) |
| Image ที่ build เองในเครื่อง | `devtools-kind:2569_1` เป็น tag ของผู้ใช้ ใช้ได้เมื่อยังไม่ได้ pull image จาก Hub แต่ห้าม build ทับ |
| Base | Ubuntu 24.04, `Asia/Bangkok`, UTF-8, Python 3, Node.js 22, git, JupyterLab 4 (kernel `python3` และ `bash`) |
| Docker | Docker-in-Docker (docker-ce, buildx, compose) ต้องรันด้วย `--privileged`, `VOLUME /var/lib/docker` |
| Kubernetes tools | kubectl `v1.37.1` (Kustomize v5.8.1), kind `0.33.0`, helm `v4.3.0`, k9s `v0.51.0`, bash-completion และ `alias k=kubectl` ใน `/etc/bash.bashrc` (ใช้ได้ใน shell แบบ interactive เท่านั้น ส่วน `docker exec ... bash -c` ไม่เห็น alias) |
| Node ของ kind | `kindest/node` default ของ kind 0.33 → Kubernetes `v1.37.0`, Debian 13, containerd 2.3 |
| Port ใน container | `22` SSH, `8888` JupyterLab, `30080–30082` NodePort ของ kind (ผ่าน `extraPortMappings` บน control-plane) |
| SSH login | `root` / `passwd` และ key ed25519 `devtoolSSH` ทำงานบน image นี้ทั้งคู่ (ต่างจาก `tuchsanai/devtools` ที่ใช้ได้แค่ password) |
| JupyterLab | ไม่มี token และไม่มีรหัสผ่าน (ตั้งได้ด้วย `-e JUPYTER_PASSWORD=...`), `root_dir=/`, แสดง hidden file |
| Workdir | `/workspace` โดย `start.sh` copy `/opt/k8s-lab/examples` ไปที่ `/workspace/examples` ครั้งแรก |
| PID 1 | bash จาก `start.sh` ไม่ใช่ systemd จึงใช้ `systemctl` ไม่ได้ log อยู่ที่ `/var/log/{dockerd,jupyter,k8s-up}.log` |
| image ไม่มี key ฝังมา | `/etc/devtools/ssh` ว่าง และไม่มี `/root/.ssh/authorized_keys` (`.dockerignore` ตัด `Devtool_SSH` ออก) |

### สคริปต์ในตัว image

- **`k8s-up`** รอ dockerd พร้อมไม่เกิน 90 วินาที แล้วสร้าง kind cluster ชื่อ `lab` (context `kind-lab`) เป็น 1 control-plane + 2 worker จาก `/etc/devtools/kind/kind-lab.yaml` จากนั้นรอทุก node `Ready` ไม่เกิน 180 วินาที ถ้ามี cluster อยู่แล้วจะข้ามการสร้าง override ได้ด้วย `KIND_CLUSTER_NAME`, `KIND_CONFIG` และ `KIND_NODE_IMAGE` **ทดลองจริงใช้เวลาประมาณ 51 วินาที** เมื่อมี node image ใน cache แล้ว รอบแรกต้องเผื่อเวลา pull image ราว 1 GB
- **`k8s-down`** รัน `kind delete cluster --name ${KIND_CLUSTER_NAME:-lab}`
- **`-e KIND_AUTO_CREATE=1`** ตอน `docker run` จะรัน `k8s-up` แบบ background ตอน start และเขียน log ไว้ที่ `/var/log/k8s-up.log` ค่าเริ่มต้นคือ `0` ซึ่งไม่สร้างให้
- `start.sh` ตั้ง cgroup v2 nesting ให้ก่อนเริ่ม dockerd ใน log ต้องเห็น `cgroup v2 controllers: cpuset cpu io memory hugetlb pids rdma` ถ้า `memory` หรือ `io` ขาดไป kind node จะล้มด้วยข้อความ `Structure needs cleaning`
- `start.sh` ลบ pid file ค้างของ dockerd ให้ จึง `docker restart` ได้ **cluster รอด restart** (ทดสอบแล้ว node กลับมา `Ready` ภายในไม่กี่วินาที) แต่ Pod ที่ใช้ `restartPolicy: Never` เช่น `hello` จะค้างสถานะ `Unknown`

### ไฟล์ตัวอย่างใน `/workspace/examples` (ทดสอบผ่านแล้ว)

| ไฟล์ | สิ่งที่ทำ | ผลที่ต้องเห็น |
|------|----------|---------------|
| `hello-pod.yaml` | Pod `hello` (busybox:1.36, `restartPolicy: Never`) | `kubectl logs hello` แสดง `Hello from Kubernetes pod hello` |
| `web-deployment.yaml` | Deployment `web` nginx:alpine 3 replicas + Service NodePort `30080` | `curl localhost:30080` แสดง `<title>Welcome to nginx!</title>` |
| `myapp/` (`Dockerfile`, `index.html`, `myapp.yaml`) | build `myapp:1.0` → `kind load docker-image myapp:1.0 --name lab` → Deployment 2 replicas + NodePort `30081` (`imagePullPolicy: IfNotPresent`) | `curl localhost:30081` แสดง `<h1>Hello from myapp:1.0</h1>` |

ถ้าไม่ `kind load` ก่อน Pod ของ myapp จะติด `ErrImagePull` เพราะ node ของ kind มองไม่เห็น image ใน dockerd ของ container

## ห้ามยุ่งกับ container ของผู้เรียน

ผู้เรียนมี container ชื่อ **`k8s-lab`** (ไม่มีขีดต่อท้าย, hostname `k8s-lab`) ที่รันด้วย `-p 2223:22 -p 8889:8888 -p 30080-30082:30080-30082` และ mount `Devtool_SSH` ไว้ และอาจมี container **`devtools`** ของวิชา DevTools ที่จอง `2222` กับ `8888` ด้วย ห้าม stop, rm, restart, exec คำสั่งที่เปลี่ยนสถานะ (`k8s-up`/`k8s-down`/`kubectl apply`) หรือ `docker run --name k8s-lab` ทับ เว้นแต่ผู้ใช้สั่งชัดเจนในข้อความนั้น

ให้ถือว่า host port **`2222`, `2223`, `8888`, `8889` และ `30080–30082` ไม่ว่างเสมอ** แม้ตอนตรวจจะว่าง เพราะ container อาจถูก stop ไว้ชั่วคราว (สคริปต์ใส่ไว้ใน `RESERVED` แล้ว)

ห้าม build ทับ tag `devtools-kind:2569_1`, `tuchsanai/devtools-kind:2569_1` หรือ tag อื่นของผู้ใช้ ถ้าต้อง build เพื่อทดสอบให้ใช้ tag ของงานเอง เช่น `k8s-lab-test:<hashid>` แล้ว `docker rmi` ตอน cleanup

ชื่อ container ของ skill นี้ต้องขึ้นต้นด้วย **`k8s-lab-`** (มีขีด) ตัวกรอง `--filter "name=^k8s-lab-"` จึงไม่จับ `k8s-lab` ของผู้เรียน ห้ามเปลี่ยนเป็น pattern ที่กว้างกว่า เช่น `name=k8s-lab` สคริปต์ปฏิเสธ `down`/`check` กับชื่อที่ไม่ขึ้นต้นด้วย `k8s-lab-` อยู่แล้ว

kind ภายใน container ทดลองสร้าง node (`lab-control-plane`, `lab-worker`, `lab-worker2`) ไว้ใน dockerd **ของ container นั้นเอง** จึงไม่ชนกับคลัสเตอร์ `lab` ของผู้เรียนหรือของการทดลองอื่น แม้จะใช้ชื่อเดียวกัน และ `hostPort: 30080` ใน kind-lab.yaml หมายถึง port ของ container ทดลอง ไม่ใช่ของ host

## สคริปต์ช่วย `k8s-lab.sh` (ฝังอยู่ท้ายไฟล์นี้)

skill นี้เป็น **ไฟล์เดียว stand-alone**: copy แค่ `SKILL.md` ไปเครื่องอื่นแล้วใช้ได้ทันที สคริปต์ฝังอยู่ในหัวข้อ "ภาคผนวก: k8s-lab.sh" ท้ายไฟล์ ต้องการแค่ `bash`, docker CLI และ coreutils (`curl`, `ssh`, `flock` ใช้เมื่อมี) ไม่อ่าน config หรือ path ใดภายนอก

แตกสคริปต์ออกมาก่อนใช้ (ทำครั้งเดียวต่อ session; `<SKILL.md>` คือ path ของไฟล์นี้ที่โหลดอยู่ `<tmp>` คือ scratchpad ของ agent หรือ `${TMPDIR:-/tmp}`):

```bash
awk '/^```bash k8s-lab\.sh$/{f=1;next} f&&/^```$/{exit} f' <SKILL.md> > <tmp>/k8s-lab.sh && chmod +x <tmp>/k8s-lab.sh
```

```bash
L=<tmp>/k8s-lab.sh
$L run <ชื่อการทดลอง> --ssh --jupyter --nodeport   # up → wait → k8s-up → check all → ลบทิ้งเสมอ (แม้ล้มหรือโดน SIGTERM)
```

| คำสั่ง | ทำอะไร |
|--------|--------|
| `up <exp> [--ssh] [--jupyter] [--nodeport] [--auto-create] [--wait-slot] [--ssh-port N] [--jupyter-port N] [--nodeport-base N] [-- <docker run args>]` | สร้าง `k8s-lab-<exp>-<hashid>` พิมพ์ชื่อออก stdout publish เฉพาะ port ที่ขอ |
| `wait <C> [secs]` | รอ sshd + dockerd ข้างใน (default 90s) |
| `cluster <C> [secs]` | `k8s-up` แล้วยืนยัน 3 node `Ready` (default 400s) |
| `check <C> [tools cluster examples host ssh jupyter \| all]` | ตรวจผลตามหัวข้อ "ผลที่ต้องเห็น" พิมพ์ `PASS`/`FAIL`/`SKIP` ต่อบรรทัด exit ≠ 0 ถ้ามี FAIL |
| `expect <C> <regex> [secs] -- <cmd>` | รันคำสั่งใน container ซ้ำจนผลตรง regex ภายใน deadline ใช้ตรวจผลที่โจทย์ LAB ต้องการ |
| `expect-host <C> <container-port> <regex> [secs] [path]` | `curl` จาก host ผ่าน port ที่ map ไว้ซ้ำจนผลตรง regex |
| `cp <C> <local-path> [dest]` | `docker cp` ไฟล์ LAB เข้า container (default `/workspace/lab/`) |
| `info <C>` / `ls` | ดู owner, hashid, image ID, port / ดู `k8s-lab-*` ทุกตัวของทุก agent |
| `down <C>...` | `docker rm -fv` แล้วยืนยันว่าหายจริง |

ตัวแปร env: `K8S_LAB_IMAGE` (default `tuchsanai/devtools-kind:2569_1`), `K8S_LAB_MAX` (default `5`), `K8S_LAB_OWNER` (default hostname ของ agent), `K8S_LAB_HOST` (override host ที่ใช้ probe port), `K8S_LAB_LOCK` (default `${TMPDIR:-/tmp}/k8s-lab.ports.lock`)

## กฎการแยกการทดลอง (สคริปต์บังคับให้แล้ว)

- **ชื่อ**: `k8s-lab-<ชื่อการทดลอง>-<hashid>` เช่น `k8s-lab-nodeport-a1b2c3` ชื่อการทดลองถูกแปลงเป็นตัวพิมพ์เล็ก `[a-z0-9-]` ยาวไม่เกิน 40 ตัว (`"Custom LAB!"` → `custom-lab`)
- **hashid**: 6 hex สุ่มใหม่ทุกครั้งที่รันจาก `/dev/urandom` (`od -An -N3 -tx1 /dev/urandom`) **ห้ามสร้าง hash จากข้อมูลลับ** เช่น token, password, key, `.env` หรือ email ถ้าชื่อซ้ำจะสุ่มใหม่
- **label** ทุกตัวมี `k8s-lab.owner`, `k8s-lab.hashid`, `k8s-lab.experiment`, `k8s-lab.created` ใช้ระบุเจ้าของเมื่อหลาย agent ทำงานพร้อมกัน แต่ละ agent ดูแลและลบเฉพาะ container ของตัวเอง ตั้ง `K8S_LAB_OWNER=<ชื่อ agent>` เมื่อหลาย agent อยู่ในเครื่องเดียวกัน
- **port**: เลือก host port ว่างที่น้อยที่สุด โดยถือว่า port ที่ container ใด ๆ (รวมตัวที่ stop) จองไว้, port ใน `RESERVED` และ port ที่ probe แล้วมีคนฟังอยู่ ไม่ว่าง:
  - SSH → `22`: เริ่มที่ `2224`
  - JupyterLab → `8888`: เริ่มที่ `8890`
  - NodePort → `30080-30082`: บล็อกละ 3 port ต่อเนื่อง เริ่ม `30090-30092` แล้วขยับทีละ 10 (`30100-30102`, …)
  - publish เฉพาะที่ขอ (`--ssh`, `--jupyter`, `--nodeport`) ถ้าไม่ขอเลยจะไม่มี port บน host
- **กันชนกันตอนสร้างพร้อมกัน**: ใช้ `flock` บน lock file ระหว่างนับโควตา เลือก port จนถึง `docker run` และถ้ายังชน (`port is already allocated` จาก agent ที่ไม่ได้แชร์ `/tmp`) จะลบตัวที่สร้างไม่สำเร็จแล้วสุ่มชื่อและเลือก port ใหม่ สูงสุด 5 ครั้ง
- **port ที่ผู้ใช้กำหนด** (`--ssh-port`, `--jupyter-port`, `--nodeport-base`) ถ้าไม่ว่างสคริปต์จะ error ทันที ห้ามเปลี่ยนไปใช้ port อื่นเอง ให้แจ้งผู้ใช้
- **โควตา**: รัน `k8s-lab-*` พร้อมกันได้ไม่เกิน `K8S_LAB_MAX=5` (นับรวมของ agent อื่น แต่ไม่แตะ) เพราะแต่ละตัวมี kind 3 node ใช้แรมหลาย GB เกินแล้ว `up` จะ error หรือรอด้วย `--wait-slot` (สูงสุด 30 นาที)
- ใช้ `--hostname k8s-lab` ให้ prompt ตรงกับเอกสาร (`root@k8s-lab`) และ `--privileged` เสมอ

ถ้า agent อยู่ใน container (มี `/.dockerenv`) `localhost` ไม่ใช่ Docker host สคริปต์จะ probe ผ่าน default gateway ให้เอง ส่วนรายงานกับผู้ใช้ให้ใช้ URL แบบ `localhost:<port>`

## การรันการทดลอง

**ทดสอบ image/ตัวอย่างมาตรฐาน** ใช้คำสั่งเดียว:

```bash
$L run smoke --ssh --jupyter --nodeport
```

**ทดสอบ LAB ของโจทย์** (หลาย Bash call แยกกัน ต้อง `down` เองตอนจบเสมอ แม้ขั้นก่อนหน้าล้ม):

```bash
C=$($L up <ชื่อการทดลอง> --nodeport)          # จด $C ไว้ทุกครั้ง
$L wait $C && $L cluster $C
$L cp $C ./lab-files/                          # ไฟล์ของโจทย์ → /workspace/lab/
docker exec $C bash -lc 'cd /workspace/lab/lab-files && kubectl apply -f .'
$L expect $C '3/3' 180 -- 'kubectl get deploy web --no-headers'        # ผลที่โจทย์ต้องการ
$L expect-host $C 30080 '<title>Welcome to nginx!</title>' 90          # ผ่าน NodePort จาก host
$L down $C
```

**หลายการทดลองพร้อมกัน** รันแบบ background ได้เลย ชื่อและ port จะไม่ชนกัน (ทดสอบจริงแล้ว 5 ตัวพร้อมกันขณะที่ agent อื่นถือ `30090` อยู่ ได้ NodePort `30100/30110/30120/30130/30140`, SSH `2224/2225`, Jupyter `8890` ทุกตัวผ่านทุกข้อ ใช้แรมรวมราว 6 GB):

```bash
$L run exp-a --nodeport > a.log 2>&1 &
$L run exp-b --ssh --nodeport > b.log 2>&1 &
wait; grep -E '^(PASS|FAIL|SKIP|==)' a.log b.log; $L ls
```

ถ้าจะทำด้วยมือโดยไม่ใช้สคริปต์ ให้ทำตามกฎข้างบนครบทุกข้อ แล้วใช้คำสั่งเทียบเท่า:

```bash
docker run -dit --name $C --hostname k8s-lab --privileged --label k8s-lab.owner=<agent> \
  -p <ssh>:22 -p <np0>-<np2>:30080-30082 tuchsanai/devtools-kind:2569_1
timeout 60 docker exec $C bash -c 'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done; until docker info >/dev/null 2>&1; do sleep 1; done'
timeout 400 docker exec $C k8s-up
```

`check examples` ทำเท่ากับ: apply `hello-pod.yaml` + `web-deployment.yaml` → `kubectl logs hello` → `curl localhost:30080` → `docker build myapp` + `kind load docker-image myapp:1.0 --name lab` + apply `myapp/myapp.yaml` → `curl localhost:30081`

kubectl ใน container ใช้ context `kind-lab` ให้อัตโนมัติ ส่วน `k9s` เป็น TUI ต้องมี tty จึงทดสอบด้วยแค่ `k9s version` หรือใช้ `docker exec -it` เมื่อผู้ใช้สั่ง `expect` ใช้ `bash -lc` จึงไม่เห็น alias `k` ให้เขียน `kubectl` เต็ม

ใช้ `docker cp` (หรือ `$L cp`) สำหรับ manifest หรือ fixture ของ LAB ห้าม bind mount path ของ agent เพราะเมื่อ agent อยู่ใน container path จะถูกแปลเป็น path ฝั่ง Docker host ซึ่งไม่ใช่ไฟล์เดียวกัน ห้าม mount Docker socket ของ host หรือโฟลเดอร์งานจริงเข้า container ทดลอง และ `--privileged` ไม่ใช่ sandbox ให้ใช้กับ LAB ที่เชื่อถือได้เท่านั้น

container ขึ้นได้ยังไม่ถือว่า LAB ผ่าน ต้องดูผลที่สังเกตได้จริง เช่น node `Ready`, Pod `Running`, ผล `curl` ผ่าน NodePort หรือผล `kubectl logs` ให้รายงานบรรทัด `PASS`/`FAIL` จริง

## SSH (password และ key `devtoolSSH`)

`$L check $C ssh` ทดสอบทั้ง password และ key ให้ (ไฟล์ askpass/key ชั่วคราวอยู่ใน `mktemp -d` และถูกลบเมื่อจบ) ต้อง `up` ด้วย `--ssh` ก่อน

password (`passwd` ใช้ได้กับ LAB นี้เท่านั้น ห้ามนำไปใช้ที่อื่น) ทดสอบด้วยมือแบบไม่ต้องพิมพ์ได้ด้วย askpass ใน scratchpad:

```bash
printf '#!/bin/sh\necho passwd\n' > <scratchpad>/askpass && chmod +x <scratchpad>/askpass
SSH_ASKPASS=<scratchpad>/askpass SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid \
  ssh -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <ssh> root@<host> 'hostname; kubectl get nodes' </dev/null
```

พฤติกรรมของ key ใน `start.sh` (โฟลเดอร์ `/etc/devtools/ssh`):

- ถ้ามี `devtoolSSH.pub` จะเพิ่มบรรทัดแรกเข้า `/root/.ssh/authorized_keys` ให้ สามารถ mount `:ro` ได้ และใช้ได้แม้ไฟล์จาก Windows มี permission 777
- ถ้าโฟลเดอร์ว่างและเขียนได้ (กรณีรันโดยไม่ mount) จะสร้าง key pair ใหม่และ log `generated new SSH key pair` ทดสอบ key login ได้ด้วยการ copy private key ที่สร้างขึ้นออกมา:
  ```bash
  docker cp $C:/etc/devtools/ssh/devtoolSSH <scratchpad>/key && chmod 600 <scratchpad>/key
  ssh -i <scratchpad>/key -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p <ssh> root@<host> 'kubectl config current-context'
  ```
- ห้าม mount `Devtool_SSH/` จริงของผู้ใช้แบบเขียนได้ ถ้าจะทดสอบ key ของผู้ใช้ให้ใช้ `docker create` → `docker cp devtoolSSH.pub $C:/etc/devtools/ssh/` → `docker start`
- authorized_keys จะสะสม key ไปเรื่อย ๆ การ restart ไม่ได้เพิกถอน key เก่า ถ้าต้องการเพิกถอนต้อง `docker rm -f` แล้วสร้าง container ใหม่

## JupyterLab

`up` ด้วย `--jupyter` แล้วใช้ `$L check $C jupyter` เปิดได้ที่ `http://localhost:<jupyter>/lab` แล้วเลือก Launcher → Terminal จะได้ shell เดียวกับ SSH ตรวจแบบไม่ใช้ browser ด้วย `curl -s -o /dev/null -w '%{http_code}' http://<host>:<jupyter>/lab` ต้องได้ `200` หรือใช้ `docker exec $C jupyter server list`

## Build และ push image (เฉพาะเมื่อผู้ใช้สั่ง)

การ push ขึ้น Docker Hub เป็นการเผยแพร่ออกภายนอก ทำเฉพาะเมื่อผู้ใช้สั่งในข้อความนั้น ก่อน push ให้ตรวจว่าไม่มี key ฝังอยู่ใน image:

```bash
docker run --rm --entrypoint bash <image> -c 'ls -A /etc/devtools/ssh; ls -A /root/.ssh'   # ต้องว่าง
```

credential ของ Docker Hub ต้องอยู่ในตัวแปร `DOCKER_USER` และ `DOCKER_TOKEN` ของ shell agent อยู่แล้ว skill นี้ไม่กำหนด path ของไฟล์ credential ถ้ายังไม่มี ให้ถามผู้ใช้ว่าจะ load จากที่ไหน ห้ามเดาค้นหาไฟล์ `.env` เอง ห้าม echo ค่า และให้ใช้ `DOCKER_CONFIG` ชั่วคราว เพราะบางเครื่อง (เช่น Docker Desktop ที่ใช้ credential helper `desktop`) บันทึก credential ไม่ได้ (`error storing credentials - err: exit status 255`):

```bash
export DOCKER_CONFIG=$(mktemp -d); echo '{}' > $DOCKER_CONFIG/config.json
printf '%s' "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
docker tag devtools-kind:2569_1 tuchsanai/devtools-kind:2569_1 && docker push tuchsanai/devtools-kind:2569_1
docker logout; rm -rf $DOCKER_CONFIG; unset DOCKER_CONFIG
```

ถ้า build ใหม่จาก Dockerfile ของ LAB ให้ใช้ tag ของงาน (`k8s-lab-test:<hashid>`) เว้นแต่ผู้ใช้สั่งให้ build เป็น tag จริง

## การปกป้องข้อมูลรับรอง

- **ห้ามส่งไฟล์ credential (`.env` ฯลฯ) หรือตัวแปร token เข้า container ทดลอง** ไม่ว่าจะด้วย `--env-file`, `-e`, `-- <docker run args>` ของสคริปต์ หรือ `docker cp` ใช้ credential ใน shell ของ agent เฉพาะเพื่อ `docker login` ตามหัวข้อด้านบนเท่านั้น
- ห้ามใช้ข้อมูลลับเป็นส่วนหนึ่งของชื่อ container, hashid, label หรือชื่อการทดลอง
- ห้ามใส่ email, ชื่อจริง, token หรือรหัสผ่านจริงลงในเอกสาร LAB ตัวอย่าง ไฟล์ที่สร้าง หรือรายงาน ให้ใช้ placeholder เช่น `<YOUR_TOKEN>` แทน
- ถ้า log แสดงข้อมูลจริงโดยไม่ตั้งใจ ให้ปกปิดก่อนนำเสนอ หรือสรุปเฉพาะผลแทนการคัดลอก log

## ต้อง cleanup ทุกครั้ง

ลบ container ที่ตัวเองสร้างทันทีเมื่อจบงาน แม้คำสั่งก่อนหน้าจะล้มเหลวหรือถูกขัดจังหวะ และต้องยืนยันว่าลบแล้วก่อนรายงานผล การลบ container จะลบ kind cluster และข้อมูล DinD ข้างในไปด้วย เพราะใช้ `-v` ลบ anonymous volume ของ `/var/lib/docker`:

```bash
$L down k8s-lab-<ชื่อการทดลอง>-<hashid>       # = docker rm -fv + ตรวจว่าหายจริง (log "removed" หรือ "STILL PRESENT")
$L ls                                          # ต้องไม่เหลือ container ของงานนี้ (ดูคอลัมน์ owner)
```

`$L run` ลบให้เองผ่าน trap แม้ check ล้มหรือโดน SIGTERM/Ctrl-C (ทดสอบแล้ว) แต่ถ้าใช้ `up` แยก ต้อง `down` เองเสมอ

ใช้คำสั่งลบแบบกว้าง `docker rm -fv $(docker ps -aq --filter "name=^k8s-lab-")` เฉพาะเมื่อผู้ใช้สั่ง หรือยืนยันแล้วว่าทุกตัวที่ตรงเงื่อนไขเป็นของงานนี้ ห้ามใช้ `docker system prune` และห้ามแตะ `k8s-lab` หรือ `devtools` ของผู้เรียน

ต้องลบแยกเองด้วย ได้แก่ image tag ของงาน (`k8s-lab-test:<hashid>`), สำเนา key และ askpass ที่สร้างเองด้วยมือ และ `DOCKER_CONFIG` ชั่วคราว

รายงานให้ครบ: ชื่อ container (`k8s-lab-<exp>-<hashid>`), owner, port ที่ใช้ (SSH, NodePort และ Jupyter ถ้ามี), image ID, ผลตรวจแต่ละข้อ และสถานะ cleanup ถ้า cleanup ไม่สำเร็จให้ระบุชื่อ container ที่ยังค้างอยู่

## ภาคผนวก: k8s-lab.sh

ห้ามแก้แค่ในไฟล์ที่แตกออกไป ถ้าต้องแก้สคริปต์ให้แก้ในบล็อกนี้แล้วทดสอบใหม่ บล็อกต้องขึ้นต้นด้วย ```` ```bash k8s-lab.sh ```` เพื่อให้คำสั่ง `awk` ข้างบนหาเจอ

```bash k8s-lab.sh
#!/usr/bin/env bash
# k8s-lab.sh — run Kubernetes LAB experiments in throwaway, isolated containers.
# Self-contained: needs only bash, docker CLI and coreutils (curl/ssh/flock optional).
# Every container is named k8s-lab-<experiment>-<hashid> and labelled so that
# concurrent agents never touch each other's containers or ports.
set -uo pipefail

IMAGE=${K8S_LAB_IMAGE:-tuchsanai/devtools-kind:2569_1}
MAX=${K8S_LAB_MAX:-5}
OWNER=${K8S_LAB_OWNER:-$(hostname)}
LOCK=${K8S_LAB_LOCK:-${TMPDIR:-/tmp}/k8s-lab.ports.lock}
# Host ports that belong to the student's own k8s-lab/devtools containers.
RESERVED="2222 2223 8888 8889 30080 30081 30082"
PREFIX=k8s-lab-

die()  { echo "ERROR: $*" >&2; exit 1; }
log()  { echo "[k8s-lab] $*" >&2; }
pass() { echo "PASS  $*"; }
fail() { echo "FAIL  $*"; FAILED=$((FAILED+1)); }
FAILED=0

usage() {
  cat <<'EOF'
usage: k8s-lab.sh <command> [args]

  up <experiment> [--ssh] [--jupyter] [--nodeport] [--auto-create] [--wait-slot]
                  [--ssh-port N] [--jupyter-port N] [--nodeport-base N] [-- extra docker run args]
        create k8s-lab-<experiment>-<hashid>, print its name on stdout
  wait <C> [secs]          wait for sshd + inner dockerd (default 90s)
  cluster <C> [secs]       run k8s-up and wait for 3 nodes Ready (default 400s)
  check <C> [what...]      what = tools cluster examples host ssh jupyter all (default all)
  expect <C> <regex> [secs] -- <cmd...>
                           retry <cmd> inside C until output matches regex
  expect-host <C> <container-port> <regex> [secs] [path]
                           curl the mapped host port until body matches regex
  cp <C> <local-path> [dest]   copy LAB files into C (default dest /workspace/lab/)
  info <C>                 name, owner, hashid, image ID, host ports
  ls                       list all k8s-lab-* containers (all owners)
  down <C>...              remove container(s) + DinD volume, verify gone
  run <experiment> [up opts]   up -> wait -> cluster -> check all -> down (always)

env: K8S_LAB_IMAGE K8S_LAB_MAX(5) K8S_LAB_OWNER(hostname) K8S_LAB_HOST K8S_LAB_LOCK
EOF
}

# ---------- helpers ----------
hashid() { # random, never derived from any secret
  od -An -N3 -tx1 /dev/urandom | tr -d ' \n'
}

sanitize() { # docker-safe experiment slug
  local s
  s=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-' | tr -s '-' | sed 's/^-*//; s/-*$//')
  s=${s:0:40}
  [ -n "$s" ] || die "invalid experiment name: '$1'"
  printf '%s' "$s"
}

probe_host() { # where published host ports are reachable from here
  if [ -n "${K8S_LAB_HOST:-}" ]; then echo "$K8S_LAB_HOST"
  elif [ -f /.dockerenv ]; then ip route 2>/dev/null | awk '/^default/ {print $3; exit}'
  else echo 127.0.0.1; fi
}
HOST=$(probe_host); HOST=${HOST:-127.0.0.1}

used_ports() { # all host ports bound by any container (running or stopped) + reserved
  echo $RESERVED | tr ' ' '\n'
  local ids; ids=$(docker ps -aq)
  [ -n "$ids" ] && docker inspect --format \
    '{{range $p,$b := .HostConfig.PortBindings}}{{range $b}}{{.HostPort}}{{"\n"}}{{end}}{{end}}' $ids 2>/dev/null
  # ranges like "30080-30082" may appear when bound as ranges
  true
}

expand_used() {
  used_ports | while read -r p; do
    [ -z "$p" ] && continue
    if [[ $p == *-* ]]; then seq "${p%-*}" "${p#*-}"; else echo "$p"; fi
  done | sort -un
}

port_open() { timeout 2 bash -c "echo > /dev/tcp/$HOST/$1" 2>/dev/null; }

port_free() { # $1 port, $2 = newline list of used ports
  grep -qx "$1" <<<"$2" && return 1
  port_open "$1" && return 1
  return 0
}

pick_port() { # $1 start, $2 used list
  local p=$1
  while ! port_free "$p" "$2"; do p=$((p+1)); [ $p -gt 65000 ] && die "no free port from $1"; done
  echo "$p"
}

pick_np_base() { # 3 consecutive ports, start 30090, step 10
  local b=$1 used=$2
  while :; do
    if port_free "$b" "$used" && port_free $((b+1)) "$used" && port_free $((b+2)) "$used"; then echo "$b"; return; fi
    b=$((b+10)); [ $b -gt 32760 ] && die "no free NodePort block"
  done
}

running_count() { docker ps -q --filter "name=^${PREFIX}" | wc -l; }

hostport() { # $1 C, $2 container port -> host port (empty if not published)
  docker port "$1" "$2/tcp" 2>/dev/null | head -1 | awk -F: '{print $NF}'
}

need_c() {
  [ -n "${1:-}" ] || die "container name required"
  [[ $1 == ${PREFIX}* ]] || die "refusing: '$1' is not a ${PREFIX}* container"
  docker inspect "$1" >/dev/null 2>&1 || die "no such container: $1"
}

# ---------- commands ----------
cmd_up() {
  local exp="" ssh=0 jup=0 np=0 auto=0 waitslot=0 sshp="" jupp="" npb="" extra=()
  while [ $# -gt 0 ]; do
    case $1 in
      --ssh) ssh=1;; --jupyter) jup=1;; --nodeport) np=1;; --auto-create) auto=1;;
      --wait-slot) waitslot=1;;
      --ssh-port) sshp=$2; ssh=1; shift;; --jupyter-port) jupp=$2; jup=1; shift;;
      --nodeport-base) npb=$2; np=1; shift;;
      --) shift; extra=("$@"); break;;
      -*) die "unknown option $1";;
      *) [ -z "$exp" ] && exp=$1 || die "unexpected arg $1";;
    esac; shift
  done
  [ -n "$exp" ] || die "usage: up <experiment> [opts]"
  exp=$(sanitize "$exp")

  docker image inspect "$IMAGE" >/dev/null 2>&1 || { log "pulling $IMAGE"; docker pull -q "$IMAGE" >&2 || die "pull failed"; }

  # concurrency quota (counts every agent's k8s-lab-* containers, touches none);
  # checked under the lock so simultaneous `up` calls cannot overshoot MAX
  local t0=$SECONDS attempt name hid args used s j b out
  { exec 9>"$LOCK"; } 2>/dev/null
  while :; do
    command -v flock >/dev/null && flock -w 120 9 2>/dev/null
    [ "$(running_count)" -lt "$MAX" ] && break
    flock -u 9 2>/dev/null
    [ $waitslot = 1 ] || die "quota reached: $(running_count)/$MAX k8s-lab-* containers running (use --wait-slot or K8S_LAB_MAX)"
    [ $((SECONDS-t0)) -gt 1800 ] && die "waited 30 min for a free slot"
    log "quota $MAX reached, waiting for a slot..."; sleep 10
  done
  for attempt in 1 2 3 4 5; do
    hid=$(hashid); name="${PREFIX}${exp}-${hid}"
    docker inspect "$name" >/dev/null 2>&1 && continue
    used=$(expand_used)
    args=(-dit --name "$name" --hostname k8s-lab --privileged
          --label k8s-lab.owner="$OWNER" --label k8s-lab.hashid="$hid"
          --label k8s-lab.experiment="$exp" --label k8s-lab.created="$(date -u +%FT%TZ)")
    if [ $ssh = 1 ]; then
      if [ -n "$sshp" ]; then port_free "$sshp" "$used" || die "requested SSH port $sshp is busy"; s=$sshp
      else s=$(pick_port 2224 "$used"); fi
      args+=(-p "$s:22"); used+=$'\n'$s
    fi
    if [ $jup = 1 ]; then
      if [ -n "$jupp" ]; then port_free "$jupp" "$used" || die "requested Jupyter port $jupp is busy"; j=$jupp
      else j=$(pick_port 8890 "$used"); fi
      args+=(-p "$j:8888"); used+=$'\n'$j
    fi
    if [ $np = 1 ]; then
      if [ -n "$npb" ]; then
        for k in 0 1 2; do port_free $((npb+k)) "$used" || die "requested NodePort port $((npb+k)) is busy"; done; b=$npb
      else b=$(pick_np_base 30090 "$used"); fi
      args+=(-p "$b-$((b+2)):30080-30082")
    fi
    [ $auto = 1 ] && args+=(-e KIND_AUTO_CREATE=1)
    if out=$(docker run "${args[@]}" "${extra[@]}" "$IMAGE" 2>&1); then
      flock -u 9 2>/dev/null; exec 9>&-
      log "created $name (owner=$OWNER image=$(docker inspect -f '{{.Image}}' "$name" | cut -c8-19))"
      echo "$name"; return 0
    fi
    docker rm -fv "$name" >/dev/null 2>&1
    if grep -qiE 'already allocated|address already in use|bind' <<<"$out" && [ -z "$sshp$jupp$npb" ]; then
      log "port race on attempt $attempt, retrying"; continue
    fi
    flock -u 9 2>/dev/null; exec 9>&-
    die "docker run failed: $out"
  done
  die "could not create container after 5 attempts"
}

cmd_wait() {
  need_c "$1"; local secs=${2:-90}
  timeout "$secs" docker exec "$1" bash -c \
    'until (echo > /dev/tcp/127.0.0.1/22) 2>/dev/null; do sleep 1; done; until docker info >/dev/null 2>&1; do sleep 1; done' \
    || die "$1 not ready after ${secs}s"
  log "$1 ready (sshd + dockerd)"
}

cmd_cluster() {
  need_c "$1"; local secs=${2:-400}
  timeout "$secs" docker exec "$1" k8s-up >&2 || die "k8s-up failed/timeout in $1"
  local n; n=$(docker exec "$1" kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready"' | wc -l)
  [ "$n" -eq 3 ] || die "expected 3 Ready nodes, got $n"
  log "$1 cluster lab: 3 nodes Ready"
}

# retry a command inside C until regex matches
cmd_expect() {
  local c=$1 re=$2 secs=60; shift 2
  [ "${1:-}" != "--" ] && { secs=$1; shift; }
  [ "${1:-}" = "--" ] && shift
  need_c "$c"; local out="" t0=$SECONDS
  while :; do
    out=$(docker exec "$c" bash -lc "$*" 2>&1)
    if grep -qE "$re" <<<"$out"; then pass "$* =~ /$re/ -> $(grep -oE "$re" <<<"$out" | head -1)"; return 0; fi
    [ $((SECONDS-t0)) -ge "$secs" ] && { fail "$* !~ /$re/ (last: $(tail -c 200 <<<"$out" | tr '\n' ' '))"; return 1; }
    sleep 2
  done
}

cmd_expect_host() {
  local c=$1 cport=$2 re=$3 secs=${4:-60} path=${5:-/}
  need_c "$c"; local hp; hp=$(hostport "$c" "$cport")
  [ -n "$hp" ] || { fail "port $cport not published on $c"; return 1; }
  local out="" t0=$SECONDS
  while :; do
    out=$(curl -s --max-time 5 "http://$HOST:$hp$path")
    if grep -qE "$re" <<<"$out"; then pass "host :$hp -> $cport =~ /$re/ (localhost:$hp$path)"; return 0; fi
    [ $((SECONDS-t0)) -ge "$secs" ] && { fail "host :$hp$path !~ /$re/"; return 1; }
    sleep 2
  done
}

chk_tools() {
  local c=$1 v
  v=$(docker exec "$c" kubectl version --client 2>&1 | tr '\n' ' '); [[ $v == *v1.* ]] && pass "kubectl: $v" || fail "kubectl: $v"
  v=$(docker exec "$c" kind --version 2>&1); [[ $v == kind* ]] && pass "$v" || fail "kind: $v"
  v=$(docker exec "$c" helm version --short 2>&1); [[ $v == v* ]] && pass "helm $v" || fail "helm: $v"
  v=$(docker exec "$c" k9s version --short 2>&1 | tr -s ' \n' ' '); [[ $v == *Version* ]] && pass "k9s $v" || fail "k9s: $v"
  v=$(docker logs "$c" 2>&1 | grep -o 'cgroup v2 controllers:.*' | head -1)
  [[ $v == *memory* && $v == *io* ]] && pass "$v" || fail "cgroup nesting: '${v:-missing}'"
}

chk_cluster() {
  local c=$1
  docker exec "$c" kind get clusters 2>/dev/null | grep -qx lab || cmd_cluster "$c"
  local n; n=$(docker exec "$c" kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready"' | wc -l)
  [ "$n" -eq 3 ] && pass "3 nodes Ready ($(docker exec "$c" kubectl config current-context))" || fail "Ready nodes = $n"
}

chk_examples() {
  local c=$1
  docker exec "$c" bash -c 'cd /workspace/examples && kubectl apply -f hello-pod.yaml -f web-deployment.yaml' >/dev/null 2>&1
  cmd_expect "$c" 'Hello from Kubernetes pod hello' 180 -- 'kubectl logs hello'
  docker exec "$c" kubectl rollout status deploy/web --timeout=180s >/dev/null 2>&1
  cmd_expect "$c" '<title>Welcome to nginx!</title>' 120 -- 'curl -s localhost:30080'
  docker exec "$c" bash -c 'cd /workspace/examples && docker build -q -t myapp:1.0 myapp && kind load docker-image myapp:1.0 --name lab && kubectl apply -f myapp/myapp.yaml' >/dev/null 2>&1 \
    || fail "build/kind load myapp"
  docker exec "$c" kubectl rollout status deploy/myapp --timeout=180s >/dev/null 2>&1
  cmd_expect "$c" '<h1>Hello from myapp:1.0</h1>' 120 -- 'curl -s localhost:30081'
}

chk_host() {
  local c=$1
  [ -n "$(hostport "$c" 30080)" ] || { echo "SKIP  host NodePort (not published, use --nodeport)"; return; }
  cmd_expect_host "$c" 30080 '<title>Welcome to nginx!</title>' 90
  cmd_expect_host "$c" 30081 '<h1>Hello from myapp:1.0</h1>' 90
}

chk_ssh() {
  local c=$1 hp; hp=$(hostport "$c" 22)
  [ -n "$hp" ] || { echo "SKIP  ssh (not published, use --ssh)"; return; }
  command -v ssh >/dev/null || { echo "SKIP  ssh (no ssh client)"; return; }
  local d; d=$(mktemp -d); local o=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -p "$hp")
  printf '#!/bin/sh\necho passwd\n' >"$d/askpass"; chmod +x "$d/askpass"
  local out
  out=$(SSH_ASKPASS="$d/askpass" SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid ssh "${o[@]}" \
        -o PubkeyAuthentication=no root@"$HOST" 'hostname; kubectl config current-context 2>/dev/null || true' </dev/null 2>&1)
  [[ $out == *k8s-lab* ]] && pass "ssh password root@localhost:$hp -> $(tr '\n' ' ' <<<"$out")" || fail "ssh password: $out"
  if docker cp "$c:/etc/devtools/ssh/devtoolSSH" "$d/key" >/dev/null 2>&1; then
    chmod 600 "$d/key"
    out=$(ssh -i "$d/key" -o BatchMode=yes -o IdentitiesOnly=yes "${o[@]}" root@"$HOST" hostname </dev/null 2>&1)
    [[ $out == *k8s-lab* ]] && pass "ssh key devtoolSSH localhost:$hp" || fail "ssh key: $out"
  else
    echo "SKIP  ssh key (no generated key in container; mounted .pub only)"
  fi
  rm -rf "$d"
}

chk_jupyter() {
  local c=$1 hp; hp=$(hostport "$c" 8888)
  [ -n "$hp" ] || { echo "SKIP  jupyter (not published, use --jupyter)"; return; }
  local code="" t0=$SECONDS
  while [ $((SECONDS-t0)) -lt 60 ]; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://$HOST:$hp/lab"); [ "$code" = 200 ] && break; sleep 2
  done
  [ "$code" = 200 ] && pass "jupyter http://localhost:$hp/lab -> 200" || fail "jupyter /lab -> $code"
}

cmd_check() {
  local c=$1; shift; need_c "$c"
  local what=("$@"); [ ${#what[@]} -eq 0 ] && what=(all)
  [ "${what[0]}" = all ] && what=(tools cluster examples host ssh jupyter)
  echo "== check $c (image $(docker inspect -f '{{.Image}}' "$c" | cut -c8-19))"
  for w in "${what[@]}"; do
    case $w in
      tools|cluster|examples|host|ssh|jupyter) chk_$w "$c";;
      *) die "unknown check $w";;
    esac
  done
  echo "== $c: $FAILED failed"
  [ $FAILED -eq 0 ]
}

cmd_cp() {
  need_c "$1"; local dest=${3:-/workspace/lab/}
  docker exec "$1" mkdir -p "$dest" && docker cp "$2" "$1:$dest" >/dev/null && log "copied $2 -> $1:$dest"
}

cmd_info() {
  need_c "$1"
  docker inspect -f 'name={{.Name}} owner={{index .Config.Labels "k8s-lab.owner"}} hashid={{index .Config.Labels "k8s-lab.hashid"}} image={{.Image}} status={{.State.Status}}' "$1" | sed 's#name=/#name=#'
  docker port "$1" | sed 's/^/  /'
}

cmd_ls() {
  docker ps -a --filter "name=^${PREFIX}" \
    --format 'table {{.Names}}\t{{.Label "k8s-lab.owner"}}\t{{.Status}}\t{{.Ports}}'
}

cmd_down() {
  [ $# -gt 0 ] || die "usage: down <C>..."
  local c rc=0
  for c in "$@"; do
    [[ $c == ${PREFIX}* ]] || { log "refusing to remove '$c' (not ${PREFIX}*)"; rc=1; continue; }
    docker rm -fv "$c" >/dev/null 2>&1
    if docker inspect "$c" >/dev/null 2>&1; then log "STILL PRESENT: $c"; rc=1; else log "removed $c"; fi
  done
  return $rc
}

cmd_run() {
  local exp=${1:?experiment}; shift
  RUN_C=$(cmd_up "$exp" "$@") || exit 1
  trap 'rc=$?; cmd_down "$RUN_C"; exit $rc' EXIT
  trap 'exit 130' INT TERM
  cmd_info "$RUN_C"
  cmd_wait "$RUN_C" && cmd_cluster "$RUN_C" && cmd_check "$RUN_C" all
}

case ${1:-} in
  up) shift; cmd_up "$@";;
  wait) shift; cmd_wait "$@";;
  cluster) shift; cmd_cluster "$@";;
  check) shift; cmd_check "$@";;
  expect) shift; cmd_expect "$@";;
  expect-host) shift; cmd_expect_host "$@";;
  cp) shift; cmd_cp "$@";;
  info) shift; cmd_info "$@";;
  ls) cmd_ls;;
  down) shift; cmd_down "$@";;
  run) shift; cmd_run "$@";;
  ""|-h|--help|help) usage;;
  *) usage; exit 2;;
esac
```
