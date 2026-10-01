---
name: vastai
description: เช่า GPU และจัดการ Template บน Vast.ai ผ่าน Python SDK (`vastai`) — ค้นหา offer/template, สร้าง/หยุด/ทำลาย instance, สร้าง/แก้ไข/ลบ template, ต่อ SSH, copy ไฟล์, ดู logs และคุมค่าใช้จ่าย ใช้เมื่อผู้ใช้ขอเช่า GPU, เปิด/ปิดเครื่อง Vast, ใช้หรือจัดการ Vast Template, รัน workload บน Vast หรือเช็คเครดิต
allowed-tools: Bash, Read, Write, Edit
---

ไฟล์เดียวจบ — toolkit อยู่ในนี้ ไม่มีไฟล์ประกอบอื่น

**Verified: Python 3.12.3 · vastai 1.8.2 · 2026-09-30** (ทดสอบซ้ำครบทุกเส้นทางบน 1.8.2 ด้วย 3 instance พร้อมกัน ค่าใช้จ่ายจริง ~$0.044 — ดูท้ายไฟล์) · รุ่นก่อน: vastai 1.5.5 · 2026-08-27

**ขั้นแรกสุดของทุก session — เช็คว่าติดตั้ง `vastai` แล้วหรือยัง แล้วแจ้งผู้ใช้ก่อนทำอย่างอื่น:**

```bash
python -c "import importlib.metadata as m; print(m.version('vastai'))" 2>/dev/null || echo NOT_INSTALLED
```

- ได้เลขเวอร์ชัน → แจ้งผู้ใช้สั้น ๆ ว่า "vastai ติดตั้งแล้ว (เวอร์ชัน X)" แล้วไปต่อ
- `NOT_INSTALLED` → **แจ้งผู้ใช้ก่อนเริ่มติดตั้ง** ว่ายังไม่ได้ติดตั้ง vastai และอาจใช้เวลาสักพัก
- อย่ารวม `pip install` ไว้ในคำสั่งเดียวกับ `env`/`keys`/`sweep` — ผู้ใช้จะไม่รู้ว่าช้าเพราะอะไร

```bash
pip install 'vastai~=1.8'        # ได้ทั้ง SDK และ CLI ; ลงที่ /opt/venv ซึ่งไม่ถาวร
```

# .env — เก็บ credential เท่านั้น

toolkit หาไฟล์เองตามลำดับ (อันแรกที่เจอชนะ) — **ไม่มี path ส่วนตัว hardcode ในสกิล**

1. `$VASTAI_ENV`  2. `~/.config/vastai/vastai.env`  ← แนะนำ  3. `./.env` ใน cwd

```dotenv
VAST_API_KEY=<key จาก https://cloud.vast.ai/manage-keys/>
VAST_SSH_KEY_FILE=~/.ssh/id_vastai      # **private** key เท่านั้น (สัมพัทธ์ = อิงโฟลเดอร์ .env)
VAST_HTTP_TIMEOUT=30                    # timeout ต่อ 1 request (SDK default 120s ซึ่งนานเกิน)
```

```bash
mkdir -p ~/.config/vastai && chmod 700 ~/.config/vastai
$EDITOR ~/.config/vastai/vastai.env && chmod 600 ~/.config/vastai/vastai.env
```

**ทำไมไม่มีตัวแปรของ public key?** `ssh`/`scp` ใช้แค่ private ส่วน public ต้องใช้เฉพาะตอน
"ผูกคีย์กับบัญชี" ครั้งเดียว — toolkit หาเอง: ลอง `<private>.pub` ก่อน ถ้าไม่มีก็ derive ด้วย
`ssh-keygen -y -f <private>` จึงไม่ต้องเก็บ path ของ `.pub` ไว้ที่ไหนเลย

```bash
python /tmp/vast.py keys            # คีย์ผูกกับบัญชีหรือยัง (ต้องได้ registered:true)
python /tmp/vast.py keys --attach   # ถ้ายัง — ผูกให้ instance ใหม่รับคีย์นี้อัตโนมัติ
```

**ไม่ต้อง `source` และไม่ต้อง `export`** — toolkit อ่านให้ทุกครั้งที่รัน
ลำดับค่า: ตัวแปรที่ `export` ใน shell **>** `.env` **>** default ในโค้ด
รองรับ `export KEY=…`, ค่าใน quote, inline comment, ค่าว่าง · เตือนถ้าไฟล์ `chmod` เปิดกว้าง

**เพดานเงิน/ความปลอดภัยไม่ต้องใส่ใน `.env`** — default อยู่ในโค้ด (บล็อกท้าย `SDK CONTRACT`)
override เฉพาะครั้งได้ทาง flag หรือ env:

| ตัวแปร | default | ความหมาย |
|:--|--:|:--|
| `VAST_MAX_DPH` | `0.20` | เพดาน $/hr — แพงกว่านี้ต้องสั่ง `--max-dph` เอง (กันเผลอเช่า H100 ทั้งคืน) |
| `VAST_MAX_INSTANCES` | `10` | เพดานจำนวนเครื่องพร้อมกัน |
| `VAST_MAX_DESTROY` | `10` | เพดานเครื่องที่ลบได้ต่อคำสั่งเดียว |
| `VAST_LABEL_PREFIX` | *(ว่าง)* | ตั้งเป็น prefix ของงาน → **ห้ามแตะ/ลบเครื่องที่ label ไม่ตรง** |

**ตรวจ config ก่อนเริ่มงานเสมอ:**

```bash
python /tmp/vast.py env      # โชว์ว่าอ่านไฟล์ไหน + ได้ค่าอะไร (ไม่โชว์ค่า secret) ; exit 1 ถ้าไม่ครบ
```

---

# ขอยืนยันเมื่อไหร่ / ทำเองได้เลยเมื่อไหร่

| ทำเองได้เลย ไม่ต้องถาม | ต้องขอยืนยันจากผู้ใช้ |
|:--|:--|
| `plan` `sweep` `bill` `status` `logs` `template-search` `template-show` — หาข้อมูลให้จบก่อน | ขึ้นเพดานราคา `--max-dph` เกินที่ผู้ใช้/`.env` กำหนด |
| **`rent` / `create` — เช่าเครื่องได้ทันที ไม่ต้องถาม** (เลือก offer ดีที่สุดเอง ภายใต้เพดานราคา) | |
| `template-delete --dry-run` | `template-create` / `template-update` — เปลี่ยนข้อมูลบัญชี |
| `run` `push` `pull` เข้าเครื่องที่ผู้ใช้สั่งสร้างไว้แล้ว | **`destroy`** — ลบข้อมูลถาวร กู้ไม่ได้ |
| `stop` `start` เครื่องที่ผู้ใช้ขอให้จัดการอยู่แล้ว | ขยาย disk |
| `destroy` เครื่องทดสอบของตัวเองที่เกินเพดานเวลา | `template-delete` — ลบ template ถาวร |
|  | แตะ instance/template ที่ผู้ใช้ไม่ได้พูดถึง |

**เวลาผู้ใช้ขอเช่า — ห้ามถามว่าจะเอา offer ไหน ให้ตัดสินใจเองแล้วเช่าเลย** ด้วย `rent`
(offer อายุสั้นระดับวินาที–นาที ถามคนก่อน = offer หายเกือบทุกครั้ง — เจอจริง 2 ครั้งติดใน 2026-09-30)
เกณฑ์ "ดีที่สุด" ของ `rent`: กรอง `BASE_FILTER` + CUDA + เพดานราคา → ให้ reliability ≥ 0.995 มาก่อน →
ถูกสุด → เน็ตเร็วสุด; offer หายระหว่างยิงก็ลองตัวถัดไปอัตโนมัติ (ไม่เกิน `--tries`, default 5)
เพดานราคายังบังคับเสมอ: ผู้ใช้ระบุราคา/GPU ที่แพงกว่า `VAST_MAX_DPH` มาแล้ว (เช่น ขอ 4090) = ส่ง `--max-dph`
ให้พอกับราคาตลาดของ GPU นั้นได้ แต่ถ้าไม่ได้ระบุ GPU ห้ามขยายเพดานเอง
หลังเช่าแล้ว**รายงาน**: `instance_id` · `gpu` · `$/hr` (แยก gpu+storage) · ที่ตั้ง · เหตุผลที่เลือก · วิธีต่อ SSH

🔒 **ห้ามพิมพ์ API key ออกมาไม่ว่ากรณีใด** — `create` คืน `instance_api_key`, instance row ทุกตัวมี
`jupyter_token` → `print(r)` ตรง ๆ = key หลุด (toolkit เรียก `redact()` ให้แล้ว)
public key ต้องผูกกับบัญชีก่อน (`vast.py keys --attach`) instance ใหม่จึงต่อได้ทันที
`vastai set api-key` เขียนลง `~/.config/vastai/vast_api_key` ซึ่งไม่ถาวรใน container → อย่าใช้ ให้ส่ง key ทุกครั้งแทน

---

# Toolkit — เขียนไฟล์นี้ครั้งเดียวต่อ session แล้วใช้ทุกคำสั่ง

```bash
cat > /tmp/vast.py <<'VASTPY'
#!/usr/bin/env python3
"""vast.py — toolkit เดียวของ skill vastai (verified: Python 3.12.3 · vastai 1.8.2 · 2026-09-30)

  plan|rent|create|status|stop|start|destroy|sweep|bill|run|push|pull|drift
  template-search|template-show|template-create|template-update|template-delete

อ่าน key จาก env VAST_API_KEY เท่านั้น · log ไป stderr · ผลลัพธ์ JSON ไป stdout
"""
import argparse, io, json, os, re, subprocess, sys, time

# ===== SDK CONTRACT — แก้ที่นี่ที่เดียวเมื่อ SDK เปลี่ยน (ดู `drift`) =====================
VERIFIED = {"python": "3.12.3", "vastai": "1.8.2", "date": "2026-09-30"}
OFFER = {"id":"id","gpu":"gpu_name","num_gpus":"num_gpus","price":"dph_total","price_gpu":"dph_base",
         "reliability":"reliability","perf":"dlperf_per_dphtotal","cuda":"cuda_max_good","disk":"disk_space",
         "storage_cost":"storage_cost","inet":"inet_down","geo":"geolocation","ports":"direct_port_count",
         "gpu_ram":"gpu_ram","machine":"machine_id","duration":"duration","verification":"verification"}
TEMPLATE = {"id":"id","hash":"hash_id","name":"name","image":"image","tag":"tag",
            "disk":"recommended_disk_space","recommended":"recommended","creator":"creator_id",
            "count":"count_created","ssh":"use_ssh","ssh_direct":"ssh_direct",
            "jup_direct":"jup_direct","private":"private"}
INST  = {"id":"id","label":"label","status":"actual_status","intended":"intended_status","cur":"cur_state",
         "msg":"status_msg","gpu":"gpu_name","price":"dph_total","price_gpu":"dph_base",
         "storage_ph":"storage_total_cost","storage_cost":"storage_cost","image":"image_uuid","disk":"disk_space",
         "start":"start_date","duration":"duration","ssh_host":"ssh_host","ssh_port":"ssh_port",
         "ip":"public_ipaddr","ports":"ports","machine":"machine_id","gpu_ram":"gpu_ram"}
SECRETS = ("instance_api_key","jupyter_token","api_key","ssh_key","password","token")
CREATE_KWARGS = ("image","disk","env","price","label","extra","onstart_cmd","login","python_utf8","lang_utf8",
                 "jupyter_lab","jupyter_dir","force","cancel_unavail","template_hash","user","runtype","args",
                 "volume_info","bid_price","ssh","jupyter","direct","create_volume","link_volume","volume_size",
                 "mount_path","volume_label")
RUNTYPE = {"ssh_direct":"ssh_direc ssh_proxy","ssh_proxy":"ssh_proxy",
           "jupyter_direct":"jupyter_direc ssh_direc ssh_proxy","jupyter_proxy":"jupyter_proxy ssh_proxy"}
# drift เทียบ "ชื่อพารามิเตอร์" ของแต่ละเมธอด (จับ rename/เพิ่ม/ลบ ได้ครบโดยไม่ต้องเก็บ signature ยาว ๆ)
_TF = "name,image,image_tag,href,repo,login,env,ssh,jupyter,direct,jupyter_dir,jupyter_lab,onstart_cmd,search_params,no_default,disk_space,readme,hide_readme,desc,public,runtype,use_ssh,jup_direct,ssh_direct,use_jupyter_lab,docker_login_repo,extra_filters,readme_visible,private"
SIGS = {"search_offers":"query,type,order,limit,storage,no_default",
 "create_instance":"id,"+",".join(CREATE_KWARGS), "show_instance":"id", "show_instances":"",
 "stop_instance":"id", "start_instance":"id", "destroy_instance":"id", "ssh_url":"id",
 "execute":"id,command", "copy":"src,dst", "logs":"instance_id,tail,filter,daemon_logs",
 "show_user":"", "show_invoices_v1":"kwargs", "label_instance":"id,label", "attach_ssh":"instance_id,ssh_key",
 "search_templates":"query", "create_template":_TF, "update_template":"hash_id,"+_TF,
 "delete_template":"template_id,hash_id", "show_ssh_keys":"", "create_ssh_key":"ssh_key",
 "recycle_instance":"id",
 "api.instances.create_instance":"client,id,"+",".join(CREATE_KWARGS)}
BEHAVIOUR = {"default_retry": 3, "retryable_status": [429,502,503,504], "default_timeout_s": 120,
             "search_hard_cap": 64, "hours_per_month": 720.0}
UP, DOWN, DEAD = {"running"}, {"exited","stopped"}, {"offline","unknown"}
TRANSIENT = {None,"created","loading","rebooting"}
BASE_FILTER = "rentable=true verified=true reliability>0.99 direct_port_count>=4 duration>2"
DEFAULT_IMAGE = "nvidia/cuda:12.4.1-runtime-ubuntu22.04"
SSH_OPTS = ["-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null",
            "-o","ConnectTimeout=15","-o","LogLevel=ERROR"]

# ===== .env — เก็บ "credential เท่านั้น" ================================================
# หาไฟล์ตามลำดับนี้ อันแรกที่เจอชนะ (ไม่มี path ส่วนตัว hardcode ในสกิล):
#   1) $VASTAI_ENV        2) ~/.config/vastai/vastai.env       3) ./.env ใน cwd
# ลำดับค่า: ตัวแปรที่ export ไว้ใน shell > ค่าใน .env > default ในโค้ดข้างล่าง
ENV_CANDIDATES = ("~/.config/vastai/vastai.env", "./.env")

def env_paths():
    p = os.environ.get("VASTAI_ENV")
    return ([p] if p else []) + [os.path.expanduser(x) for x in ENV_CANDIDATES]

def load_env(path=None):
    """อ่าน .env แบบไม่ override ค่าที่ shell ตั้งไว้ · คืน (path, คำเตือนเรื่อง permission)"""
    warn = None
    for p in ([path] if path else env_paths()):
        if not p or not os.path.isfile(p):
            continue
        try:                                   # ไฟล์ที่มี key ไม่ควรให้คนอื่นอ่านได้
            mode = os.stat(p).st_mode & 0o077
            if mode: warn = "%s เปิดให้ group/other อ่านได้ (chmod 600 %s)" % (p, p)
        except OSError: pass
        for raw in io.open(p, encoding="utf-8", errors="replace"):
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, val = line.partition("=")
            k = k.strip()
            if k.startswith("export "):
                k = k[7:].strip()
            if not k or not k.replace("_", "").isalnum():
                continue
            val = val.strip()
            if val[:1] in ("'", '"') and val[:1] == val[-1:] and len(val) > 1:
                val = val[1:-1]                                  # quote ไว้ = เก็บทั้งก้อน
            else:
                val = re.split(r"(?:^|\s)#", val, 1)[0].strip()   # ตัด inline comment
            os.environ.setdefault(k, val)
        return p, warn
    return None, None

ENV_FILE, ENV_WARN = load_env()
if ENV_WARN: sys.stderr.write("WARN: %s\n" % ENV_WARN)

def _num(k, d, cast):
    try:
        return cast(os.environ.get(k) or d)
    except (TypeError, ValueError):
        sys.stderr.write("WARN: %s=%r ไม่ใช่ตัวเลข ใช้ค่า default %s\n"
                         % (k, os.environ.get(k), d))
        return cast(d)

def _keyfile():
    """VAST_SSH_KEY_FILE ที่เป็น path สัมพัทธ์ ให้อิงโฟลเดอร์ของ .env"""
    v = os.environ.get("VAST_SSH_KEY_FILE", "")
    if v and not os.path.isabs(v) and ENV_FILE:
        cand = os.path.join(os.path.dirname(os.path.abspath(ENV_FILE)), v)
        if os.path.isfile(cand): return cand
    return os.path.expanduser(v) if v else ""

# ---- ค่าคุมเงิน/ความปลอดภัย: default อยู่ในโค้ด ไม่ต้องใส่ใน .env -----------------------
# override ชั่วคราวได้ทาง env หรือ flag ของแต่ละคำสั่ง (--max-dph / --max-instances)
MAX_INSTANCES = _num("VAST_MAX_INSTANCES", 10, int)     # เพดานจำนวนเครื่องพร้อมกัน
MAX_DPH       = _num("VAST_MAX_DPH", 0.20, float)       # เพดาน $/hr — แพงกว่านี้ต้อง --max-dph เอง
MAX_DESTROY   = _num("VAST_MAX_DESTROY", 10, int)       # เพดานเครื่องที่ลบได้ต่อคำสั่ง
HTTP_TIMEOUT  = _num("VAST_HTTP_TIMEOUT", 30, float)    # timeout ต่อ 1 request (SDK default 120)
SEARCH_PASSES = max(2, _num("VAST_SEARCH_PASSES", 2, int))      # search offers ขนานกันกี่รอบ (ขั้นต่ำ 2)
SEARCH_GAP    = max(3.0, _num("VAST_SEARCH_GAP", 3.0, float))  # แต่ละรอบเริ่มห่างกันกี่วินาที (ขั้นต่ำ 3)
LABEL_PREFIX  = os.environ.get("VAST_LABEL_PREFIX", "") # ตั้งแล้วห้ามแตะเครื่องที่ label ไม่ตรง
SSH_KEY_ENV   = _keyfile()

# ===== พื้นฐาน ===========================================================================
def log(m): print("[%s] %s" % (time.strftime("%H:%M:%S"), m), file=sys.stderr, flush=True)
def die(m, c=2): print("ERROR: %s" % m, file=sys.stderr); raise SystemExit(c)
def out(o): print(json.dumps(o, ensure_ascii=False))
def g(row, t, k, d=None):
    v = (row or {}).get(t[k]); return d if v is None else v
def gf(row, t, k, d=0.0):
    try: return float(g(row, t, k, d))
    except (TypeError, ValueError): return float(d)
def redact(r):
    return r if not isinstance(r, dict) else {
        k: ("<redacted>" if any(s in k.lower() for s in SECRETS) else v) for k, v in r.items()}

def http_err(e):
    """str(HTTPError) ไม่มี msg ของ Vast — ต้องอ่าน body เอง"""
    r = getattr(e, "response", None)
    if r is None: return {"code": None, "error": type(e).__name__, "msg": str(e)[:300]}
    o = {"code": r.status_code, "url": getattr(r, "url", None)}
    try:
        j = r.json(); o["error"] = j.get("error"); o["msg"] = j.get("msg") or j.get("message")
    except ValueError: o["msg"] = (r.text or "").strip()[:200]
    return o

def client(retry=3):
    key = os.environ.get("VAST_API_KEY")
    if not key:
        die("ไม่พบ VAST_API_KEY — ใส่ใน .env แล้ว chmod 600 (หาไฟล์จาก: %s)"
            % ", ".join(env_paths()))
    from vastai import VastAI
    v = VastAI(api_key=key, retry=retry)
    try: v.client.timeout = HTTP_TIMEOUT      # default 120s × retry = รอนานเกิน
    except AttributeError: pass
    return v

def fmt_inst(i):
    return "inst %-9s %-20s %-9s %-13s $%.4f/hr up %dm" % (
        g(i,INST,"id","-"), str(g(i,INST,"label","-"))[:20], str(g(i,INST,"status","provisioning")),
        g(i,INST,"gpu","-"), gf(i,INST,"price"), gf(i,INST,"duration")/60)

def rates(row):
    """instance dph_total = dph_base + storage_total_cost และ **ไม่ลดลงตอน stop**"""
    st = gf(row,INST,"storage_ph") or gf(row,INST,"storage_cost")*gf(row,INST,"disk")/BEHAVIOUR["hours_per_month"]
    gpu = gf(row,INST,"price_gpu") or max(gf(row,INST,"price") - st, 0.0)
    run = g(row,INST,"status") == "running"
    return {"gpu_per_hr": round(gpu,5), "storage_per_hr": round(st,5),
            "effective_per_hr": round(gpu+st if run else st, 5),
            "billed_now": "gpu+storage" if run else "storage only"}

# ===== offer =============================================================================
def build_query(a):
    p = [BASE_FILTER, "num_gpus=%d" % a.num_gpus, "disk_space>%d" % (int(a.disk)+10),
         "inet_down>%d" % a.min_inet]
    # อย่าส่ง cuda_vers เข้า Offer API: พบว่า server คืน 0 แถวสำหรับ RTX 5090 แม้
    # raw offer มี cuda_max_good=13.x. ตรวจค่าจาก response ใน cmd_plan แทน.
    if a.gpu:          p.append("gpu_name=%s" % a.gpu.replace(" ","_"))
    if a.max_dph:      p.append("dph<%s" % a.max_dph)
    if a.min_gpu_ram:  p.append("gpu_ram>=%s" % a.min_gpu_ram)      # หน่วย GB!
    if a.extra_query:  p.append(a.extra_query)
    return " ".join(p)

def _search_once(v, q, disk):
    """ต้องส่ง storage=disk ไม่งั้น dph_total คิด storage แค่ 5 GiB (default)"""
    return [o for o in (v.search_offers(query=q, order="dph_total",
            limit=BEHAVIOUR["search_hard_cap"], storage=float(disk)) or []) if o.get("dph_total") is not None]

def search(v, q, disk):
    """ยิง search_offers ขนานกัน SEARCH_PASSES รอบ (≥2) แต่ละรอบเริ่มห่างกัน SEARCH_GAP วินาที (≥3)
    แล้วรวมผล ตัด offer id ซ้ำ (เก็บแถวจากรอบหลังสุดเพราะราคาสดกว่า) — ผลแต่ละรอบไม่ตรงกัน 100%
    และติด cap 64 แถว การรวมหลายรอบจึงได้ offer มากกว่า; รอบที่ error ข้ามได้ ถ้าพังหมดค่อย raise"""
    from concurrent.futures import ThreadPoolExecutor
    def one(i):
        time.sleep(i * SEARCH_GAP)
        return _search_once(v, q, disk)
    with ThreadPoolExecutor(SEARCH_PASSES) as ex:
        futs = [ex.submit(one, i) for i in range(SEARCH_PASSES)]
    merged, counts, err = {}, [], None
    for f in futs:
        try: rows = f.result()
        except Exception as e: err = e; counts.append("err"); continue
        counts.append(len(rows))
        for o in rows: merged[g(o,OFFER,"id")] = o
    if not any(c != "err" for c in counts): raise err
    log("search %d รอบ (ห่าง %.0fs): %s แถว → รวมไม่ซ้ำ %d offers"
        % (SEARCH_PASSES, SEARCH_GAP, "+".join(map(str, counts)), len(merged)))
    return sorted(merged.values(), key=lambda o: gf(o,OFFER,"price",9e9))

def rank3(offers, cap):
    pool = [o for o in offers if gf(o,OFFER,"price",9e9) <= cap]
    if not pool: return []
    picks = [("ถูกสุด",       min(pool, key=lambda o: gf(o,OFFER,"price",9e9))),
             ("คุ้มสุด perf/$", max(pool, key=lambda o: gf(o,OFFER,"perf"))),
             ("นิ่งสุด",       max(pool, key=lambda o: (round(gf(o,OFFER,"reliability"),3),
                                                        gf(o,OFFER,"inet"), -gf(o,OFFER,"price"))))]
    seen, res = set(), []
    for tag, o in picks:
        if g(o,OFFER,"id") not in seen: seen.add(g(o,OFFER,"id")); res.append((tag,o))
    return res

def cuda_compatible(o, minimum):
    """ตรวจ CUDA ฝั่ง client เพราะ server-side cuda_vers filter มี false negative บน RTX 5090."""
    try: return float(g(o,OFFER,"cuda",0)) >= float(minimum)
    except (TypeError, ValueError): return False

# ===== template ==========================================================================
def template_safe(t):
    """ไม่คืน env/login/onstart/readme เพราะอาจมี secret"""
    return {"template_id":g(t,TEMPLATE,"id"), "hash_id":g(t,TEMPLATE,"hash"),
            "name":g(t,TEMPLATE,"name"), "image":g(t,TEMPLATE,"image"), "tag":g(t,TEMPLATE,"tag"),
            "recommended_disk_gb":gf(t,TEMPLATE,"disk"), "recommended":bool(g(t,TEMPLATE,"recommended",False)),
            "creator_id":g(t,TEMPLATE,"creator"), "count_created":int(g(t,TEMPLATE,"count",0) or 0),
            "use_ssh":bool(g(t,TEMPLATE,"ssh",False)), "ssh_direct":bool(g(t,TEMPLATE,"ssh_direct",False)),
            "jupyter_direct":bool(g(t,TEMPLATE,"jup_direct",False)), "private":bool(g(t,TEMPLATE,"private",False)),
            "extra_filters":template_filters(t)}

def template_filters(t):
    """API คืน extra_filters เป็น JSON string และของที่เคย update ผิดอาจถูก encode ซ้ำหลายชั้น."""
    x=(t or {}).get("extra_filters")
    for _ in range(3):
        if x is None or x == "" or x == "null": return {}
        if isinstance(x,dict): return x
        if not isinstance(x,str): die("extra_filters ของ template ไม่ใช่ dict/JSON string")
        try: x=json.loads(x)
        except (TypeError,ValueError): die("extra_filters ของ template เป็น JSON ไม่ถูกต้อง")
    if isinstance(x,dict): return x
    die("extra_filters ของ template ถูก encode ซ้อนเกิน 3 ชั้น")

def template_query_parts(t):
    """แปลงหน่วย field ของ Template API เป็น query syntax ของ search offers."""
    fields={"cuda_max_good":"cuda_vers"}; ops={"gte":">=","lte":"<=","gt":">","lt":"<","eq":"=","neq":"!=","in":"in","notin":"notin"}
    parts=[]
    for field,rule in template_filters(t).items():
        if not isinstance(rule,dict): continue
        if field=="cuda_max_good": continue   # server-side cuda_vers มี false negative (#23) → ตรวจฝั่ง client ใน template_offer_mismatches
        for op,val in rule.items():
            if op not in ops: continue
            qfield=fields.get(field,field)
            if field in ("gpu_ram","gpu_total_ram") and isinstance(val,(int,float)): val=float(val)/1000.0
            if isinstance(val,list): val="["+",".join(str(x).replace(" ","_") for x in val)+"]"
            elif isinstance(val,str): val=val.replace(" ","_")
            parts.append(("%s %s %s" if op in ("in","notin") else "%s%s%s")%(qfield,ops[op],val))
    return parts

def template_offer_mismatches(t,o):
    """ตรวจซ้ำด้วยหน่วย response จริง (GPU RAM เป็น MiB) หลัง server-side filtering."""
    aliases={"cuda_max_good":"cuda_max_good"}; bad=[]
    for field,rule in template_filters(t).items():
        lhs=o.get(aliases.get(field,field))
        if lhs is None or not isinstance(rule,dict):
            if lhs is None: bad.append("ไม่มี field %s"%field)
            continue
        for op,rhs in rule.items():
            try:
                if op in ("in","notin"):
                    vals=[str(x) for x in rhs]; ok=(str(lhs) in vals); ok=ok if op=="in" else not ok
                else:
                    a,b=float(lhs),float(rhs); ok={"gte":a>=b,"lte":a<=b,"gt":a>b,"lt":a<b,"eq":a==b,"neq":a!=b}.get(op,True)
                if not ok: bad.append("%s %s %s (offer=%s)"%(field,op,rhs,lhs))
            except (TypeError,ValueError): bad.append("เทียบ %s ไม่ได้"%field)
    return bad

def template_find(v, tid):
    rows = v.search_templates(query={"id":{"eq":int(tid)}}) or []
    row = next((x for x in rows if int(x.get("id") or 0) == int(tid)), None)
    if row is None: die("ไม่พบ template id %s" % tid)
    return row

def template_require_owned(v,t):
    uid=int((v.show_user() or {}).get("id") or 0); creator=int(t.get("creator_id") or 0)
    if not uid or creator != uid: die("template id %s ไม่ได้เป็นของบัญชีนี้ — ปฏิเสธการแก้ไข/ลบ" % t.get("id"))

def owned_templates(v):
    uid=int((v.show_user() or {}).get("id") or 0)
    if not uid: die("อ่าน creator id ของบัญชีไม่ได้")
    return v.search_templates(query={"creator_id":{"eq":uid}}) or []

def cmd_template_search(a):
    v = client(); q = {}
    if a.mine:
        uid = int((v.show_user() or {}).get("id") or 0)
        if not uid: die("อ่าน creator id ของบัญชีไม่ได้")
        q["creator_id"] = {"eq":uid}
    elif not a.all:
        q["recommended"] = {"eq":True}
    rows = v.search_templates(query=q) or []
    if a.name: rows = [x for x in rows if a.name.lower() in str(x.get("name") or "").lower()]
    rows.sort(key=lambda x:(not bool(x.get("recommended")), -int(x.get("count_created") or 0), str(x.get("name") or "")))
    out({"mode":"template-search","count":len(rows),"templates":[template_safe(x) for x in rows[:a.limit]]})
    return 0

def cmd_template_show(a):
    out({"mode":"template-show","template":template_safe(template_find(client(),a.id))}); return 0

def cmd_template_create(a):
    if not a.yes: die("template-create เปลี่ยนข้อมูลในบัญชี ต้องมี --yes หลังผู้ใช้ยืนยัน")
    if a.ssh and a.jupyter: die("เลือก --ssh และ --jupyter พร้อมกันไม่ได้")
    v = client()
    before=owned_templates(v)
    if any(str(x.get("name"))==a.name for x in before): die("template ชื่อ %r มีอยู่แล้ว — ปฏิเสธการสร้างซ้ำ"%a.name)
    ids={x.get("id") for x in before}; t0=time.time()
    kw=dict(name=a.name,image=a.image,image_tag=a.image_tag,disk_space=a.disk,
            desc=a.desc,env=a.env,onstart_cmd=a.onstart_cmd,ssh=a.ssh,jupyter=a.jupyter,
            direct=a.direct,jupyter_lab=a.jupyter_lab,jupyter_dir=a.jupyter_dir,
            hide_readme=a.hide_readme,public=a.public)
    err=None
    try:
        r=client(retry=1).create_template(**kw)  # POST ยิงครั้งเดียว ป้องกัน duplicate เมื่อ response หาย
        if isinstance(r,dict) and r.get("success") is False: err=r
    except Exception as e: err=http_err(e)
    found=[]
    for _ in range(6):
        found=[x for x in owned_templates(v) if x.get("id") not in ids and x.get("name")==a.name
               and x.get("image")==a.image and x.get("tag")==a.image_tag]
        if found: break
        time.sleep(2)
    if len(found)!=1:
        safe_err=({k:err.get(k) for k in ("code","error","msg","success") if k in err}
                  if isinstance(err,dict) else {"error":str(err)[:200]})
        out({"mode":"template-create","ok":False,"error":safe_err,"matches":len(found)})
        die("ยืนยัน template ที่สร้างไม่ได้ (matches=%d) — ห้าม retry; ค้น --mine ก่อน"%len(found))
    row=found[0]
    out({"mode":"template-create","ok":True,"seconds":round(time.time()-t0,1),"template":template_safe(row)}); return 0

def _template_update_payload(t,a):
    runtype = str(t.get("runtype") or "args")
    mode_change=any(x is not None for x in (a.ssh,a.jupyter,a.direct))
    if not mode_change:
        use_ssh=bool(t.get("use_ssh")); ssh_direct=bool(t.get("ssh_direct")); jup_direct=bool(t.get("jup_direct"))
    else:
        ssh=(runtype=="ssh") if a.ssh is None else a.ssh
        jupyter=(runtype=="jupyter") if a.jupyter is None else a.jupyter
        if ssh and jupyter: die("เลือก --ssh และ --jupyter พร้อมกันไม่ได้")
        direct=bool(t.get("jup_direct") or t.get("ssh_direct")) if a.direct is None else a.direct
        runtype="jupyter" if jupyter else ("ssh" if ssh else "args")
        use_ssh=bool(ssh or jupyter); jup_direct=bool(jupyter and direct); ssh_direct=bool(use_ssh and direct)
    return {"name":a.name if a.name is not None else t.get("name"),
      "image":a.image if a.image is not None else t.get("image"),
      "image_tag":a.image_tag if a.image_tag is not None else t.get("tag"),
      "href":t.get("href"),"repo":t.get("repo"),
      "env":a.env if a.env is not None else t.get("env"),
      "onstart_cmd":a.onstart_cmd if a.onstart_cmd is not None else t.get("onstart"),
      "jup_direct":jup_direct,"ssh_direct":ssh_direct,
      "use_jupyter_lab":t.get("use_jupyter_lab",False) if a.jupyter_lab is None else a.jupyter_lab,
      "runtype":runtype,"use_ssh":use_ssh,
      "jupyter_dir":a.jupyter_dir if a.jupyter_dir is not None else t.get("jupyter_dir"),
      "docker_login_repo":t.get("docker_login_repo"),"extra_filters":template_filters(t),
      "disk_space":a.disk if a.disk is not None else t.get("recommended_disk_space"),
      "readme":t.get("readme"),"readme_visible":t.get("readme_visible",True),
      "desc":a.desc if a.desc is not None else t.get("desc"),
      "private":t.get("private",True) if a.public is None else not a.public}

def cmd_template_update(a):
    if not a.yes: die("template-update เปลี่ยนข้อมูลในบัญชี ต้องมี --yes หลังผู้ใช้ยืนยัน")
    v=client(); t=template_find(v,a.id); template_require_owned(v,t); h=t.get("hash_id")
    if not h: die("template id %s ไม่มี hash_id จึง update ไม่ได้" % a.id)
    payload=_template_update_payload(t,a); r=v.update_template(hash_id=h,**payload)
    if isinstance(r,dict) and r.get("success") is False: die("template-update success=False")
    bad=[]; after={}
    for _ in range(6):
        after=template_find(v,a.id); bad=[]
        for k,field in (("name","name"),("image","image"),("image_tag","tag"),("disk_space","recommended_disk_space"),
                        ("runtype","runtype"),("use_ssh","use_ssh"),("ssh_direct","ssh_direct"),("jup_direct","jup_direct")):
            if payload.get(k)!=after.get(field): bad.append("%s expected=%r got=%r"%(field,payload.get(k),after.get(field)))
        if template_filters(after)!=payload["extra_filters"]: bad.append("extra_filters ไม่ตรงหลัง update")
        if not bad: break
        time.sleep(2)
    out({"mode":"template-update","ok":not bad,"template":template_safe(after),"mismatches":bad}); return 1 if bad else 0

def cmd_template_delete(a):
    v=client(); t=template_find(v,a.id); template_require_owned(v,t); summary=template_safe(t)
    if a.dry_run: out({"mode":"template-delete","dry_run":True,"would_delete":summary}); return 0
    if not a.yes: die("template-delete ลบถาวร ต้องมี --yes หลังผู้ใช้ยืนยัน")
    r=v.delete_template(template_id=a.id)
    gone=False
    for _ in range(12):
        gone=not (v.search_templates(query={"id":{"eq":int(a.id)}}) or [])
        if gone: break
        time.sleep(2)
    out({"mode":"template-delete","ok":gone,"deleted":summary}); return 0 if gone else 1

# ===== instance ==========================================================================
def instances(v): return v.show_instances() or []
def by_label(v, lb): return [i for i in instances(v) if g(i,INST,"label","") == lb]

def preflight(v, label, max_inst, cap, offer=None):
    if not label: die("ต้องมี label เสมอ — label คือ idempotency key ตัวเดียวที่ Vast มี")
    if LABEL_PREFIX and not label.startswith(LABEL_PREFIX):
        die("label %r ต้องขึ้นต้นด้วย %r" % (label, LABEL_PREFIX))
    cur = instances(v)
    dup = [g(i,INST,"id") for i in cur if g(i,INST,"label","") == label]
    if dup: die("label %r ถูกใช้แล้วโดย %s — ปฏิเสธการสร้างซ้ำ" % (label, dup))
    if len(cur) >= max_inst: die("มี %d เครื่องแล้ว เพดาน %d" % (len(cur), max_inst))
    if offer is not None and gf(offer,OFFER,"price",9e9) > cap:
        die("offer %s $%.4f/hr เกินเพดาน $%.4f/hr — ห้ามขยายเพดานเอง"
            % (g(offer,OFFER,"id"), gf(offer,OFFER,"price"), cap))
    return cur

def reconcile(v, label, window=90, poll=10):
    """create error → ห้าม retry เรียกตัวนี้แทน; คืน instance id ถ้าเครื่องเกิดจริง"""
    t0 = time.time()
    while True:
        try:
            h = by_label(v, label)
            if h: return g(sorted(h, key=lambda i: gf(i,INST,"start"), reverse=True)[0], INST, "id")
        except Exception as e: log("reconcile: %s — ลองใหม่" % type(e).__name__)
        if time.time()-t0 >= window: return None
        time.sleep(poll)

def wait_for(v, iid, want, timeout=900, poll=8, grace=420):
    t0, deadline, stuck, last = time.time(), time.time()+timeout, None, "<none>"
    row = {}
    while True:
        try: row = v.show_instance(id=iid) or {}
        except Exception as e: log("  show_instance %s — ลองใหม่" % type(e).__name__)
        st = g(row,INST,"status")
        if st in want: return True, row, "ok"
        if st in DEAD: return False, row, "instance %s" % st
        if st in TRANSIENT:
            stuck = stuck or time.time()
            if time.time()-stuck > grace: return False, row, "ค้างที่ %r เกิน %ds" % (st, grace)
        else: stuck = None
        if st != last:
            log("  status=%r msg=%s (%ds)" % (st, str(g(row,INST,"msg",""))[:70], time.time()-t0)); last = st
        if time.time()+poll >= deadline: return False, row, "timeout %ds (สถานะสุดท้าย %r)" % (timeout, st)
        time.sleep(poll)

def verify_gone(v, iid, tries=12, poll=5):
    for _ in range(tries):
        try:
            if iid not in [g(i,INST,"id") for i in instances(v)]: return True
        except Exception: pass
        time.sleep(poll)
    return False

def ssh_target(row):
    # Template แบบ direct อาจคืน proxy ssh_host/ssh_port ที่เสีย แต่ direct 22/tcp ใช้ได้จริง
    ip=g(row,INST,"ip"); p=(g(row,INST,"ports",{}) or {}).get("22/tcp") or []
    if ip and p and p[0].get("HostPort"): return ip,int(p[0]["HostPort"])
    host=g(row,INST,"ssh_host"); port=g(row,INST,"ssh_port")
    return (host,int(port)) if host and port else (None,None)

def sh(cmd, timeout=600):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def ssh_ready(host, port, key, tries=20, poll=10):
    """running != ต่อ SSH ได้ — Vast apt-install sshd เข้า image ที่ไม่มี ต้องรออีก 10-20s"""
    for k in range(tries):
        if sh(["ssh","-i",key,"-p",str(port)]+SSH_OPTS+["root@%s"%host,"true"], 45)[0] == 0:
            return True, k*poll
        time.sleep(poll)
    return False, tries*poll

def pubkey(priv=None):
    """คืน (เนื้อ public key, ที่มา) — ไม่ต้องเก็บ path ของ .pub ใน .env

    ssh/scp ใช้แค่ private; public ต้องใช้เฉพาะตอน "ผูกคีย์กับบัญชี" (attach_ssh/create_ssh_key)
    ลอง <private>.pub ก่อน ถ้าไม่มีก็ derive จาก private ด้วย ssh-keygen -y
    """
    p = priv or SSH_KEY_ENV
    if not p: return None, "ไม่มี VAST_SSH_KEY_FILE"
    if os.path.isfile(p + ".pub"):
        return io.open(p + ".pub", encoding="utf-8").read().strip(), p + ".pub"
    rc, o_, e_ = sh(["ssh-keygen", "-y", "-f", p], 30)
    if rc == 0 and o_.strip():
        return o_.strip(), "derived จาก %s (ssh-keygen -y)" % p
    return None, "ดึง public จาก %s ไม่ได้: %s" % (p, e_.strip()[:120])


def fingerprint(priv=None):
    rc, o_, _ = sh(["ssh-keygen", "-lf", priv or SSH_KEY_ENV], 30)
    return o_.split()[1] if rc == 0 and len(o_.split()) > 1 else None


def need_key(a):
    k = a.key or SSH_KEY_ENV
    if not k: die("ต้องมี --key หรือ VAST_SSH_KEY_FILE ใน .env")
    return k

def running_target(v, a):
    row = v.show_instance(id=a.id)
    if row is None: die("ไม่มี instance %s" % a.id)
    if g(row,INST,"status") != "running": die("instance %s = %r ไม่ใช่ running" % (a.id, g(row,INST,"status")))
    h, p = ssh_target(row)
    if not h: die("instance %s ยังไม่มี ssh_host/ssh_port" % a.id)
    return h, p, need_key(a)

# ===== subcommands =======================================================================
def cmd_plan(a):
    v = client(); template = template_find(v,a.template_id) if a.template_id else None
    if template:
        a.disk=max(a.disk,gf(template,TEMPLATE,"disk"))
        tq=" ".join(template_query_parts(template)); a.extra_query=" ".join(x for x in (a.extra_query,tq) if x)
    q = build_query(a); log("query: %s" % q)
    offers = search(v, q, a.disk)
    before_cuda = len(offers)
    offers = [o for o in offers if cuda_compatible(o, a.min_cuda)]
    log("CUDA >= %s: ผ่าน %d/%d offers หลังตรวจ cuda_max_good ฝั่ง client"
        % (a.min_cuda, len(offers), before_cuda))
    if template: offers=[o for o in offers if not template_offer_mismatches(template,o)]
    log("พบ %d offers หลังตรวจ template compatibility (API cap %d ต่อรอบ × %d รอบ)" % (len(offers), BEHAVIOUR["search_hard_cap"], SEARCH_PASSES))
    picks = rank3(offers, a.max_dph)
    if not picks: die("ไม่มี offer <= $%.2f/hr ที่ตรงเกณฑ์ — ห้ามขยายเพดานเอง ให้รายงานผู้ใช้" % a.max_dph)
    rows = []
    print("\n%-3s %-15s %-11s %-10s %-6s %-7s %-6s %-18s %s"
          % ("#","เกณฑ์","offer_id","$/hr","cuda","rel","net","geo","gpu"), file=sys.stderr)
    for n,(tag,o) in enumerate(picks,1):
        gpu_ph = gf(o,OFFER,"price_gpu")
        st_ph  = gf(o,OFFER,"storage_cost")*a.disk/BEHAVIOUR["hours_per_month"]
        tot    = gf(o,OFFER,"price") or gpu_ph+st_ph
        print("%-3d %-15s %-11s $%-9.4f %-6s %-7.4f %-6d %-18s %s (gpu $%.4f + stor $%.4f)"
              % (n,tag,g(o,OFFER,"id"),tot,g(o,OFFER,"cuda","-"),gf(o,OFFER,"reliability"),
                 gf(o,OFFER,"inet"),str(g(o,OFFER,"geo","-"))[:18],g(o,OFFER,"gpu","-"),gpu_ph,st_ph),
              file=sys.stderr)
        rows.append({"rank":n,"why":tag,"offer_id":g(o,OFFER,"id"),"machine_id":g(o,OFFER,"machine"),
                     "gpu":g(o,OFFER,"gpu"),"gpu_ram_mib":g(o,OFFER,"gpu_ram"),"cuda":g(o,OFFER,"cuda"),
                     "reliability":gf(o,OFFER,"reliability"),"inet_down_mbps":gf(o,OFFER,"inet"),
                     "geo":g(o,OFFER,"geo"),"perf_per_dollar":gf(o,OFFER,"perf"),
                     "gpu_per_hr":round(gpu_ph,5),"storage_per_hr":round(st_ph,5),"total_per_hr":round(tot,5)})
    th=g(template,TEMPLATE,"hash") if template else None
    image_name=("%s:%s"%(g(template,TEMPLATE,"image"),g(template,TEMPLATE,"tag"))) if template else a.image
    print("\nimage=%s disk=%sGB label=%s template=%s\nเลือกแล้วรันต่อ:" % (image_name,a.disk,a.label,g(template,TEMPLATE,"name") if template else "-"), file=sys.stderr)
    for r in rows:
        print("  #%d  create --label %s --offer-id %s --machine-id %s --expect-dph %.4f%s --yes"
              % (r["rank"],a.label,r["offer_id"],r["machine_id"],r["total_per_hr"],
                 " --template-id %s --template-hash %s"%(g(template,TEMPLATE,"id"),th) if th else ""), file=sys.stderr)
    out({"mode":"plan","image":image_name,"disk":a.disk,"label":a.label,
         "template":template_safe(template) if template else None,"offers":rows}); return 0

def cmd_create(a):
    v = client()
    ex = by_label(v, a.label)
    if ex:                                              # idempotent
        iid = g(ex[0],INST,"id"); log("label %r มีอยู่แล้ว -> adopt %s (ไม่สร้างใหม่)" % (a.label,iid))
        return _settle(v, iid, a)
    if not a.yes: die("create ต้องมี --yes (ผู้ใช้ยืนยันการเสียเงินแล้ว)")
    offer = None
    if a.machine_id:   # ⚠ id=<offer_id> กรองไม่ได้ server เมินเงียบ ๆ → ต้องใช้ machine_id
        offer = next((o for o in search(v, "machine_id=%d" % a.machine_id, a.disk)
                      if g(o,OFFER,"id") == a.offer_id), None)
        if offer is None: die("offer %s บน machine %s หายไปแล้ว — search ใหม่" % (a.offer_id,a.machine_id))
    else:
        log("ไม่ได้ส่ง --machine-id จึงยืนยัน offer ล่วงหน้าไม่ได้ (ถ้าหายไปแล้ว create จะได้ 400 แล้วเข้า reconcile)")
    if a.expect_dph and a.expect_dph > a.max_dph:
        die("ราคาที่อนุมัติ $%.4f/hr เกินเพดาน $%.4f/hr" % (a.expect_dph, a.max_dph))
    template=None
    if a.template_hash:
        if not a.template_id: die("ใช้ --template-hash ต้องมี --template-id เพื่อ validate hash/disk/compatibility")
        template=template_find(v,a.template_id)
        if template.get("hash_id")!=a.template_hash: die("template hash เปลี่ยนแล้ว — plan ใหม่")
        if a.disk < gf(template,TEMPLATE,"disk"): die("disk %.1fGB ต่ำกว่า template แนะนำ %.1fGB"%(a.disk,gf(template,TEMPLATE,"disk")))
        if offer:
            bad=template_offer_mismatches(template,offer)
            if bad: die("offer ไม่ตรง template: %s"%"; ".join(bad))
    preflight(v, a.label, a.max_instances, a.max_dph, offer)
    if a.template_hash:
        kw = dict(template_hash=a.template_hash,disk=a.disk,label=a.label,cancel_unavail=True)
    else:
        kw = dict(image=a.image, disk=a.disk, label=a.label, runtype=RUNTYPE[a.runtype],
                  onstart_cmd=a.onstart_cmd, env=_env(a.env), cancel_unavail=True)
    bad = [k for k in kw if k not in CREATE_KWARGS]
    if bad: die("kwargs ที่ SDK ไม่รับ: %s" % bad)
    log("create_instance(id=%s, %s)" % (a.offer_id, {k:v_ for k,v_ in kw.items() if k not in ("env","login")}))
    t0 = time.time()
    try:
        r = client(retry=1).create_instance(id=a.offer_id, **kw)   # retry=1 = ยิงครั้งเดียว
    except Exception as e:
        log("create ล้มเหลว: %s" % json.dumps(http_err(e), ensure_ascii=False))
        log("ห้าม retry — ตรวจก่อนว่าเครื่องเกิดขึ้นแล้วหรือยัง (จาก label)")
        iid = reconcile(v, a.label)
        if iid: log("เกิดขึ้นจริงแล้ว: %s -> adopt" % iid); return _settle(v, iid, a, t0)
        out({"mode":"create","ok":False,"instance_id":None,"error":http_err(e),
             "reason":"create failed, no instance created"})
        die("create ไม่สำเร็จ และไม่มีเครื่องเกิดขึ้น — search offer ใหม่")
    if not r.get("success"): out({"mode":"create","ok":False,"response":redact(r)}); die("success=False")
    iid = r.get("new_contract")                        # ⚠ ไม่ใช่ r["id"]; r มี instance_api_key
    if not iid: out({"mode":"create","ok":False,"response":redact(r)}); die("ไม่มี new_contract")
    log("created instance %s (%.1fs)" % (iid, time.time()-t0))
    return _settle(v, iid, a, t0)

def _env(s):
    if not s: return {}
    from vastai.cli.util import parse_env
    return parse_env(s)

def _settle(v, iid, a, t0=None):
    o = {"mode":"create","instance_id":iid,"ok":False}
    try:
        ok,row,why = wait_for(v, iid, UP, timeout=a.timeout)
        o["status"] = g(row,INST,"status")
        if not ok:
            o["reason"] = why
            log("ยังไม่ running: %s — ทำต่อ: destroy --id %s --yes แล้วเลือก offer ใหม่" % (why,iid))
            out(o); return 1
        host,port = ssh_target(row)
        o.update({"ok":True,"gpu":g(row,INST,"gpu"),"gpu_ram_mib":g(row,INST,"gpu_ram"),
                  "dph_total":gf(row,INST,"price"),"rates":rates(row),"ssh_url":v.ssh_url(id=iid),
                  "ssh_host":host,"ssh_port":port,"label":g(row,INST,"label"),"image":g(row,INST,"image"),
                  "seconds_to_running": round(time.time()-t0,1) if t0 else None})
        key = a.key or SSH_KEY_ENV
        if key and host:
            r_,w_ = ssh_ready(host,port,key); o["ssh_ready"]=r_; o["ssh_ready_after_s"]=w_
            if not r_: o["ok"]=False; o["reason"]="running แต่ต่อ SSH ไม่ได้"
        log("RUNNING %s %s  ssh -p %s root@%s  ($%.4f/hr)" % (iid,o["gpu"],port,host,o["dph_total"]))
        out(o); return 0 if o["ok"] else 1
    except Exception as e:
        o["reason"]="exception หลัง create: %s" % type(e).__name__; o["error"]=http_err(e)
        log("‼ instance %s ถูกสร้างแล้วและกำลังคิดเงิน — ตรวจด้วย sweep" % iid); out(o); return 1

def cmd_rent(a):
    """เลือก offer ที่ดีที่สุดเองแล้ว create — offer หายก็ลองตัวถัดไป (ไม่ต้องถามผู้ใช้)"""
    v = client(); a.yes = True; a.template_id = a.template_hash = None
    if by_label(v, a.label):                           # idempotent → cmd_create จะ adopt ให้
        a.offer_id, a.machine_id, a.expect_dph = 0, None, None; return cmd_create(a)
    preflight(v, a.label, a.max_instances, a.max_dph)   # guard ที่ไม่ขึ้นกับ offer → fail ทันที ไม่วนลอง offer
    q = build_query(a); log("query: %s" % q)
    pool = [o for o in search(v, q, a.disk)
            if cuda_compatible(o, a.min_cuda) and gf(o,OFFER,"price",9e9) <= a.max_dph]
    if not pool: die("ไม่มี offer <= $%.2f/hr ที่ตรงเกณฑ์" % a.max_dph)
    cand = sorted(pool, key=lambda o: (gf(o,OFFER,"reliability") < 0.995,
                                       gf(o,OFFER,"price",9e9), -gf(o,OFFER,"inet")))[:a.tries]
    for n, o in enumerate(cand, 1):
        a.offer_id, a.machine_id, a.expect_dph = g(o,OFFER,"id"), g(o,OFFER,"machine"), gf(o,OFFER,"price")
        log("ลอง #%d offer %s %s %s $%.4f/hr rel %.4f net %d" % (n, a.offer_id, g(o,OFFER,"gpu"),
            g(o,OFFER,"geo","-"), a.expect_dph, gf(o,OFFER,"reliability"), gf(o,OFFER,"inet")))
        try:
            return cmd_create(a)
        except SystemExit:
            if by_label(v, a.label): die("มีเครื่อง label %r เกิดแล้ว — หยุดลองต่อ ตรวจด้วย sweep" % a.label)
            log("offer %s ใช้ไม่ได้ → ลองตัวถัดไป" % a.offer_id)
    die("ลองครบ %d offers แล้วไม่สำเร็จ และไม่มีเครื่องเกิด — rent ใหม่อีกรอบ" % len(cand))

def cmd_life(a):
    v = client()
    try: row = v.show_instance(id=a.id)
    except Exception as e:
        if http_err(e).get("code") == 404: out({"id":a.id,"exists":False}); return 0
        die("show_instance: %s" % json.dumps(http_err(e), ensure_ascii=False))
    if row is None: out({"id":a.id,"exists":False}); return 0
    st = g(row,INST,"status"); log("before: " + fmt_inst(row))
    if a.action == "status":
        out({"id":a.id,"exists":True,"actual_status":st,"intended_status":g(row,INST,"intended"),
             "cur_state":g(row,INST,"cur"),"status_msg":g(row,INST,"msg"),"rates":rates(row),
             "uptime_s":round(gf(row,INST,"duration"))}); return 0
    want = DOWN if a.action=="stop" else UP     # ⚠ 'created'/None ไม่นับเป็น "หยุดแล้ว"
    if st in want:
        log("already %r -> no-op"%st); out({"id":a.id,"actual_status":st,"ok":True,"noop":True}); return 0
    getattr(v, "%s_instance" % a.action)(id=a.id)
    ok,row,why = wait_for(v, a.id, want, timeout=a.timeout)
    log("after: %s (%s)" % (fmt_inst(row), why))
    if a.action=="stop" and ok:
        log("⚠ stopped แล้วยังเสียค่า storage $%.5f/hr — destroy เท่านั้นที่หยุดทุกอย่าง"
            % rates(row)["storage_per_hr"])
    out({"id":a.id,"actual_status":g(row,INST,"status"),"ok":bool(ok),"reason":why,"rates":rates(row)})
    return 0 if ok else 1

def cmd_destroy(a):
    ids = a.id or []
    if not (ids or a.label or a.label_prefix): die("ต้องระบุ --id / --label / --label-prefix")
    v = client(); rows = instances(v); byid = {g(r,INST,"id"): r for r in rows}
    tgt, gone = [], []
    for i in ids: (tgt.append(byid[i]) if i in byid else gone.append(i))
    if a.label:        tgt += [r for r in rows if g(r,INST,"label","")==a.label]
    if a.label_prefix: tgt += [r for r in rows if str(g(r,INST,"label","")).startswith(a.label_prefix)]
    seen, uniq = set(), []
    for r in tgt:
        if g(r,INST,"id") not in seen: seen.add(g(r,INST,"id")); uniq.append(r)
    if LABEL_PREFIX:
        blocked = [g(r,INST,"id") for r in uniq if not str(g(r,INST,"label","")).startswith(LABEL_PREFIX)]
        if blocked: die("VAST_LABEL_PREFIX=%r แต่เป้าหมาย %s ไม่ตรง — ปฏิเสธการลบ" % (LABEL_PREFIX, blocked))
    if not uniq: out({"destroyed":[],"already_gone":gone,"note":"ไม่มีอะไรต้องลบ"}); return 0
    if len(uniq) > MAX_DESTROY: die("เป้าหมาย %d เครื่อง เกินเพดาน %d" % (len(uniq), MAX_DESTROY))
    log("จะลบถาวร %d เครื่อง (ข้อมูลหายหมด กู้ไม่ได้):" % len(uniq))
    for r in uniq: log("  " + fmt_inst(r))
    if a.dry_run: out({"dry_run":True,"would_destroy":[g(r,INST,"id") for r in uniq]}); return 0
    if not a.yes: die("ต้องใส่ --yes (ผู้ใช้ยืนยันแล้ว)")
    done, failed = [], []
    for r in uniq:
        iid = g(r,INST,"id")
        try: v.destroy_instance(id=iid)
        except Exception as e: log("destroy %s: %s" % (iid, json.dumps(http_err(e), ensure_ascii=False)))
        ok = verify_gone(v, iid); (done if ok else failed).append(iid)
        log("destroy %s -> %s" % (iid, "หายจาก show_instances() แล้ว" if ok else "ยังเห็นอยู่"))
    out({"destroyed":done,"failed":failed,"already_gone":gone}); return 1 if failed else 0

def cmd_sweep(a):
    v = client(); user = v.show_user() or {}; rows = instances(v)
    if a.label_prefix: rows = [r for r in rows if str(g(r,INST,"label","")).startswith(a.label_prefix)]
    burn = spent = 0.0; items = []
    for r in rows:
        rt = rates(r); up = gf(r,INST,"duration")/3600.0
        burn += rt["effective_per_hr"]; spent += rt["effective_per_hr"]*up
        items.append({"id":g(r,INST,"id"),"label":g(r,INST,"label"),"status":g(r,INST,"status"),
                      "gpu":g(r,INST,"gpu"),"uptime_h":round(up,2),
                      "approx_spent_usd":round(rt["effective_per_hr"]*up,4), **rt})
    stale = [i["id"] for i in items if a.older_than is not None and i["uptime_h"]*60 > a.older_than]
    cred = float(user.get("credit") or 0)
    o = {"instances":len(items),"items":items,"burn_rate_per_hr":round(burn,5),
         "approx_spent_since_start_usd":round(spent,4),"credit_remaining_usd":round(cred,2),
         "hours_of_credit_left": round(cred/burn,1) if burn else None,"stale":stale}
    if a.json: out(o)
    elif not items: print("instances: 0 — ไม่มีเครื่องค้าง\ncredit เหลือ ~$%.2f" % cred)
    else:
        print("instances: %d" % len(items))
        for r in rows: print("  " + fmt_inst(r))
        print("burn ~$%.5f/hr | ใช้ไปแล้ว ~$%.4f | credit ~$%.2f" % (burn, spent, cred))
        if o["hours_of_credit_left"]: print("เครดิตพอไปอีก ~%.1f ชม." % o["hours_of_credit_left"])
        if stale: print("[!] เกิน %s นาที: %s" % (a.older_than, stale))
        print("stopped ยังเสียค่า storage — destroy เท่านั้นที่หยุดทุกอย่าง")
    return 1 if (items or stale) else 0

def charges(v, days):
    """ค่าใช้จ่ายจริงจาก show_invoices_v1(charges=True) — แยก gpu/disk/bwd/bwu ต่อ instance, มี label แม้เครื่องถูกลบแล้ว
    (show_invoices() เก่า deprecated ใน 1.8 และ bucket อัปเดตช้ากว่า)"""
    end = int(time.time()) + 86400; start = end - int((days or 7) * 86400) - 86400
    rows, tok = [], None
    for _ in range(50):
        kw = dict(charges=True, start_date=start, end_date=end, limit=100, latest_first=True)
        if tok: kw["next_token"] = tok
        r = v.show_invoices_v1(**kw) or {}
        rows += r.get("results") or []; tok = r.get("next_token")
        if not tok: break
    return rows

def cmd_bill(a):
    """สรุปค่าใช้จ่ายจริง แยก GPU/storage/download/upload ต่อ instance + สถิติรวม"""
    v = client(); user = v.show_user() or {}
    ids = set(a.id or []); kinds = ("gpu","storage","download","upload")
    kmap = {"gpu":"gpu","disk":"storage","bwd":"download","bwu":"upload"}
    per, total = {}, {k:0.0 for k in kinds}
    for x in charges(v, a.days):
        m = re.match(r"instance-(\d+)$", str(x.get("source") or ""))
        if x.get("type") != "instance" or not m: continue
        iid = int(m.group(1)); lb = str((x.get("metadata") or {}).get("label") or "")
        if ids or a.label or a.label_prefix:
            if not (iid in ids or (a.label and lb == a.label)
                    or (a.label_prefix and lb.startswith(a.label_prefix))): continue
        d = per.setdefault(iid, {"instance_id":iid, "label":lb, **{k:0.0 for k in kinds},
                                 "gpu_hours":0.0, "download_gb":0.0, "gpu_rate":None, "download_rate":None})
        for it in x.get("items") or []:
            k = kmap.get(it.get("type"))
            if not k: continue
            amt = float(it.get("amount") or 0); d[k] += amt; total[k] += amt
            desc = str(it.get("description") or "")
            n = re.match(r"([\d.]+) (?:hours|GB)[^$]*\$([\d.]+)", desc)
            if n and k == "gpu": d["gpu_hours"] += float(n.group(1)); d["gpu_rate"] = float(n.group(2))
            if n and k == "download": d["download_gb"] += float(n.group(1)); d["download_rate"] = float(n.group(2))
    for d in per.values(): d["total"] = round(sum(d[k] for k in kinds), 3)
    grand = round(sum(total.values()), 3)
    o = {"instances":[per[k] for k in sorted(per)], "total":{**{k:round(v_,3) for k,v_ in total.items()}, "usd":grand},
         "credit_remaining_usd": round(float(user.get("credit") or 0), 2),
         "note": "charges เป็น bucket รายวัน ยอดล่าสุดอาจช้ากว่าเวลาจริงหลักนาที"}
    if a.json: out(o); return 0
    if not per: print("ไม่พบรายการ charge ตามตัวกรองในช่วง %s วัน" % (a.days or 7)); return 0
    print("%-10s %-22s %7s %8s %9s %8s %8s %7s  %s" % ("instance","label","gpu_h","GPU$","storage$","down_GB","down$","up$","total$"))
    for d in o["instances"]:
        print("%-10d %-22s %7.3f %8.3f %9.3f %8.2f %8.3f %7.3f  %.3f" % (d["instance_id"], d["label"][:22], d["gpu_hours"],
              d["gpu"], d["storage"], d["download_gb"], d["download"], d["upload"], d["total"]))
        if d["download"] > d["gpu"]: print("   [!] ค่าดาวน์โหลด ($%.3f/GB) แพงกว่าค่า GPU — ครั้งหน้าใส่ inet_down_cost<0.01" % (d["download_rate"] or 0))
    print("รวม: GPU $%.3f + storage $%.3f + download $%.3f + upload $%.3f = **$%.3f** | credit เหลือ ~$%.2f"
          % (total["gpu"], total["storage"], total["download"], total["upload"], grand, o["credit_remaining_usd"]))
    print(o["note"]); return 0

def cmd_run(a):
    v = client(); host, port, key = running_target(v, a)
    ok, w = ssh_ready(host, port, key, tries=6)
    if not ok: die("ต่อ SSH ไม่ได้ใน %ds" % w)
    rc, o_, e_ = sh(["ssh","-i",key,"-p",str(port)]+SSH_OPTS+["root@%s"%host, a.cmd], a.timeout)
    sys.stderr.write(e_); sys.stdout.write(o_); return rc

def cmd_xfer(a):
    v = client(); host, port, key = running_target(v, a)
    ok, w = ssh_ready(host, port, key, tries=6)
    if not ok: die("ต่อ SSH ไม่ได้ใน %ds" % w)
    base = ["-i", key] + SSH_OPTS
    if a.action == "push":
        # ⚠ image ตระกูล nvidia/cuda ไม่มี /workspace — ต้อง mkdir ก่อน
        rdir = a.dst if a.dst.endswith("/") else (os.path.dirname(a.dst) or "/")
        rc,_,e_ = sh(["ssh"]+base+["-p",str(port),"root@%s"%host,"mkdir -p %s"%rdir], 120)
        if rc: die("mkdir -p %s ล้มเหลว: %s" % (rdir, e_.strip()[:200]))
        rc,_,e_ = sh(["scp","-r"]+base+["-P",str(port),a.src,"root@%s:%s"%(host,a.dst)], a.timeout)
        probe = a.dst.rstrip("/") + ("/"+os.path.basename(a.src.rstrip("/")) if a.dst.endswith("/") else "")
        vrc,vo,_ = sh(["ssh"]+base+["-p",str(port),"root@%s"%host,"ls -ld %s"%probe], 120)
        out({"action":"push","rc":rc,"verified":vrc==0,"remote":probe,
             "ls":vo.strip()[:200],"err":e_.strip()[:300]})
        return 0 if (rc==0 and vrc==0) else 1
    os.makedirs(a.dst if a.dst.endswith("/") else (os.path.dirname(a.dst) or "."), exist_ok=True)
    rc,_,e_ = sh(["scp","-r"]+base+["-P",str(port),"root@%s:%s"%(host,a.src),a.dst], a.timeout)
    guess = os.path.join(a.dst, os.path.basename(a.src.rstrip("/")))
    landed = guess if os.path.exists(guess) else a.dst
    out({"action":"pull","rc":rc,"verified":os.path.exists(landed),"local":landed,"err":e_.strip()[:300]})
    return 0 if (rc==0 and os.path.exists(landed)) else 1

def cmd_drift(a):
    """รันหลัง pip install -U vastai — รายงานเฉพาะจุดที่เปลี่ยน"""
    import inspect, importlib.metadata as md
    from vastai import VastAI
    from vastai.api import instances as I, client as C
    cur = {"python": "%d.%d.%d" % sys.version_info[:3], "vastai": md.version("vastai")}
    d = []
    for k, want in (("python",VERIFIED["python"]), ("vastai",VERIFIED["vastai"])):
        if cur[k] != want: d.append((k.upper(), want, cur[k]))
    for m, want in SIGS.items():
        f = I.create_instance if m.startswith("api.") else getattr(VastAI, m, None)
        got = (",".join(p for p in inspect.signature(f).parameters if p != "self")
               if f else "MISSING")
        if got != want: d.append((m, want, got))
    beh = {"default_retry": inspect.signature(C.VastClient.__init__).parameters["retry"].default,
           "retryable_status": sorted(getattr(C,"_RETRYABLE_STATUS",[])),
           "default_timeout_s": getattr(C,"_DEFAULT_TIMEOUT_SECONDS",None)}
    for k, got in beh.items():
        if BEHAVIOUR.get(k) != got: d.append(("behaviour."+k, BEHAVIOUR.get(k), got))
    live = None
    if a.live:
        v = client()
        o = search(v, "rentable=true num_gpus=1", 40)
        if o: d += [("live offer_fields[%s]"%k, f, "<<ไม่มีใน response>>")
                    for k,f in OFFER.items() if f not in o[0]]
        r = instances(v)
        if r: d += [("live instance_fields[%s]"%k, f, "<<ไม่มีใน response>>")
                    for k,f in INST.items() if f not in r[0] and k != "ports"]
        live = {"offers_checked": bool(o), "instances_checked": bool(r)}
    if a.json: out({"drift":[{"what":x[0],"was":x[1],"now":x[2]} for x in d],"live":live,"current":cur})
    elif not d:
        print("no drift — python %s / vastai %s ตรงกับ snapshot" % (cur["python"], cur["vastai"]))
        if live and not live["instances_checked"]: print("(ไม่มี instance รันอยู่ จึงไม่ได้เช็ค instance_fields)")
    else:
        print("DRIFT %d จุด (python %s / vastai %s):" % (len(d), cur["python"], cur["vastai"]))
        for w,a_,b_ in d: print("  - %s\n      was: %s\n      now: %s" % (w,a_,b_))
        print("\nแก้ที่ส่วน 'SDK CONTRACT' ด้านบนของไฟล์นี้ แล้วอัปเดต SKILL.md")
    return 1 if d else 0

def cmd_keys(a):
    """ตรวจ/ผูก ssh key กับบัญชี — instance ใหม่จะรับคีย์นี้อัตโนมัติ"""
    pub, src = pubkey()
    if not pub: die(src)
    v = client()
    reg = v.show_ssh_keys() or []
    def norm(k): return " ".join(str(k or "").split()[:2])      # type+base64 (ตัด comment)
    mine = [k for k in reg if norm(k.get("public_key")) == norm(pub)]
    o = {"pubkey_source": src, "fingerprint": fingerprint(),
         "registered": bool(mine), "key_id": (mine[0].get("id") if mine else None),
         "keys_on_account": len(reg)}
    if not mine and a.attach:
        r = v.create_ssh_key(ssh_key=pub)
        time.sleep(3)
        reg = v.show_ssh_keys() or []
        mine = [k for k in reg if norm(k.get("public_key")) == norm(pub)]
        o["attached"] = bool(mine); o["key_id"] = mine[0].get("id") if mine else None
        o["response"] = redact(r if isinstance(r, dict) else {"resp": str(r)[:200]})
    elif not mine:
        o["hint"] = "ยังไม่ผูกกับบัญชี — รัน: python vast.py keys --attach"
    out(o)
    return 0 if o.get("registered") or o.get("attached") else 1


def cmd_env(a):
    """แสดงว่าโหลด .env จากไหนและได้ค่าอะไร — ไม่โชว์ค่า secret"""
    o = {"env_file": ENV_FILE or "<ไม่พบไฟล์>", "env_file_exists": bool(ENV_FILE),
         "searched": env_paths(), "permission_warning": ENV_WARN,
         "VAST_API_KEY": "<set len=%d>" % len(os.environ.get("VAST_API_KEY","")) 
                          if os.environ.get("VAST_API_KEY") else "<MISSING>",
         "VAST_SSH_KEY_FILE": SSH_KEY_ENV or "<unset>",
         "ssh_key_readable": bool(SSH_KEY_ENV and os.path.isfile(SSH_KEY_ENV)),
         "ssh_fingerprint": fingerprint() if SSH_KEY_ENV else None,
         "ssh_pubkey_from": pubkey()[1] if SSH_KEY_ENV else None,
         "VAST_LABEL_PREFIX": LABEL_PREFIX or "<unset — ไม่มี guard กันแตะเครื่องอื่น>",
         "VAST_MAX_DPH": MAX_DPH, "VAST_MAX_INSTANCES": MAX_INSTANCES,
         "VAST_MAX_DESTROY": MAX_DESTROY, "VAST_HTTP_TIMEOUT": HTTP_TIMEOUT}
    out(o)
    return 0 if (os.environ.get("VAST_API_KEY") and ENV_FILE) else 1

# ===== argparse ==========================================================================
def main():
    p = argparse.ArgumentParser(prog="vast.py"); s = p.add_subparsers(dest="action", required=True)
    def common(q, ssh=False):
        q.add_argument("--timeout", type=int, default=900)
        if ssh: q.add_argument("--key", default=None)
    for name in ("plan","create"):
        q = s.add_parser(name); q.add_argument("--label", required=True)
        q.add_argument("--image", default=DEFAULT_IMAGE); q.add_argument("--disk", type=float, default=40)
        q.add_argument("--max-dph", type=float, default=MAX_DPH); q.add_argument("--key", default=None)
        q.add_argument("--timeout", type=int, default=900)
        if name == "plan":
            q.add_argument("--gpu"); q.add_argument("--num-gpus", type=int, default=1)
            q.add_argument("--min-cuda", default="12.4"); q.add_argument("--min-inet", type=int, default=500)
            q.add_argument("--min-gpu-ram", type=int, help="หน่วย GB"); q.add_argument("--extra-query", default="")
            q.add_argument("--template-id",type=int,help="ใช้ disk ขั้นต่ำและ template_hash จาก template นี้")
        else:
            q.add_argument("--offer-id", type=int, required=True); q.add_argument("--machine-id", type=int)
            q.add_argument("--expect-dph", type=float); q.add_argument("--yes", action="store_true")
            q.add_argument("--template-id",type=int); q.add_argument("--template-hash")
            q.add_argument("--runtype", default="ssh_direct", choices=sorted(RUNTYPE))
            q.add_argument("--onstart-cmd", default="env | grep _ >> /etc/environment;")
            q.add_argument("--env", default=""); q.add_argument("--max-instances", type=int, default=MAX_INSTANCES)
    q = s.add_parser("rent"); q.add_argument("--label", required=True)
    q.add_argument("--gpu"); q.add_argument("--num-gpus", type=int, default=1)
    q.add_argument("--min-cuda", default="12.4"); q.add_argument("--min-inet", type=int, default=500)
    q.add_argument("--min-gpu-ram", type=int, help="หน่วย GB"); q.add_argument("--extra-query", default="")
    q.add_argument("--image", default=DEFAULT_IMAGE); q.add_argument("--disk", type=float, default=40)
    q.add_argument("--max-dph", type=float, default=MAX_DPH); q.add_argument("--key", default=None)
    q.add_argument("--timeout", type=int, default=900); q.add_argument("--tries", type=int, default=5)
    q.add_argument("--runtype", default="ssh_direct", choices=sorted(RUNTYPE))
    q.add_argument("--onstart-cmd", default="env | grep _ >> /etc/environment;")
    q.add_argument("--env", default=""); q.add_argument("--max-instances", type=int, default=MAX_INSTANCES)
    for name in ("status","stop","start"):
        q = s.add_parser(name); q.add_argument("--id", type=int, required=True)
        q.add_argument("--timeout", type=int, default=420)
    q = s.add_parser("destroy"); q.add_argument("--id", type=int, action="append")
    q.add_argument("--label"); q.add_argument("--label-prefix")
    q.add_argument("--yes", action="store_true"); q.add_argument("--dry-run", action="store_true")
    q = s.add_parser("sweep"); q.add_argument("--json", action="store_true")
    q.add_argument("--older-than", type=float); q.add_argument("--label-prefix")
    q = s.add_parser("run"); q.add_argument("--id", type=int, required=True)
    q.add_argument("--cmd", required=True); common(q, ssh=True)
    for name in ("push","pull"):
        q = s.add_parser(name); q.add_argument("--id", type=int, required=True)
        q.add_argument("--src", required=True); q.add_argument("--dst", required=True); common(q, ssh=True)
    q = s.add_parser("bill"); q.add_argument("--id", type=int, action="append", help="instance id (ระบุได้หลายครั้ง)")
    q.add_argument("--label"); q.add_argument("--label-prefix"); q.add_argument("--days", type=float, help="ย้อนหลัง N วัน (default 7)")
    q.add_argument("--json", action="store_true")
    q = s.add_parser("drift"); q.add_argument("--live", action="store_true")
    q.add_argument("--json", action="store_true")
    q = s.add_parser("env")          # ตรวจว่าอ่าน .env ได้ครบไหม (ไม่โชว์ค่า secret)
    q = s.add_parser("keys"); q.add_argument("--attach", action="store_true",
                                             help="ผูก public key กับบัญชีถ้ายังไม่ได้ผูก")
    q=s.add_parser("template-search"); q.add_argument("--mine",action="store_true")
    q.add_argument("--all",action="store_true"); q.add_argument("--name")
    q.add_argument("--limit",type=int,default=100)
    q=s.add_parser("template-show"); q.add_argument("--id",type=int,required=True)
    q=s.add_parser("template-create"); q.add_argument("--name",required=True); q.add_argument("--image",required=True)
    q.add_argument("--image-tag",required=True); q.add_argument("--disk",type=float,required=True)
    q.add_argument("--desc"); q.add_argument("--env"); q.add_argument("--onstart-cmd")
    q.add_argument("--ssh",action=argparse.BooleanOptionalAction,default=True)
    q.add_argument("--jupyter",action=argparse.BooleanOptionalAction,default=False)
    q.add_argument("--direct",action=argparse.BooleanOptionalAction,default=True)
    q.add_argument("--jupyter-lab",action=argparse.BooleanOptionalAction,default=False)
    q.add_argument("--jupyter-dir"); q.add_argument("--hide-readme",action="store_true")
    q.add_argument("--public",action="store_true"); q.add_argument("--yes",action="store_true")
    q=s.add_parser("template-update"); q.add_argument("--id",type=int,required=True)
    q.add_argument("--name"); q.add_argument("--image"); q.add_argument("--image-tag"); q.add_argument("--disk",type=float)
    q.add_argument("--desc"); q.add_argument("--env"); q.add_argument("--onstart-cmd")
    q.add_argument("--ssh",action=argparse.BooleanOptionalAction,default=None)
    q.add_argument("--jupyter",action=argparse.BooleanOptionalAction,default=None)
    q.add_argument("--direct",action=argparse.BooleanOptionalAction,default=None)
    q.add_argument("--jupyter-lab",action=argparse.BooleanOptionalAction,default=None)
    q.add_argument("--jupyter-dir"); q.add_argument("--public",action=argparse.BooleanOptionalAction,default=None)
    q.add_argument("--yes",action="store_true")
    q=s.add_parser("template-delete"); q.add_argument("--id",type=int,required=True)
    q.add_argument("--dry-run",action="store_true"); q.add_argument("--yes",action="store_true")
    a = p.parse_args()
    return {"env":cmd_env,"keys":cmd_keys,"plan":cmd_plan,"rent":cmd_rent,"create":cmd_create,"status":cmd_life,"stop":cmd_life,"start":cmd_life,"bill":cmd_bill,
            "destroy":cmd_destroy,"sweep":cmd_sweep,"run":cmd_run,"push":cmd_xfer,"pull":cmd_xfer,
            "drift":cmd_drift,"template-search":cmd_template_search,"template-show":cmd_template_show,
            "template-create":cmd_template_create,"template-update":cmd_template_update,
            "template-delete":cmd_template_delete}[a.action](a)

if __name__ == "__main__":
    raise SystemExit(main())
VASTPY
python /tmp/vast.py env            # ต้องเห็น env_file_exists:true และ VAST_API_KEY:<set …>
```

ทุก subcommand อ่าน `.env` เองแล้ว — ไม่ต้อง `source` และไม่ต้อง `export` อะไรก่อนรัน

---

# RUNBOOK 1 — CREATE

> เป้า: "อยากได้ GPU X" → running + SSH ต่อได้ ใน **คำสั่งเดียว ไม่ต้องถามผู้ใช้** และไม่มีเครื่องซ้ำแม้ error

| # | รัน | ต้องเห็นจึงไปต่อ | ถ้าไม่เห็น |
|--:|:--|:--|:--|
| 0 | `python /tmp/vast.py env && python /tmp/vast.py keys` | `env_file_exists:true` · `VAST_API_KEY:<set …>` · `ssh_key_readable:true` · `registered:true` | ตั้งค่าใน `.env` ให้ครบ แล้ว `keys --attach` (ดูหัวไฟล์) |
| 1 | `python /tmp/vast.py sweep` | จำนวนเครื่อง + เครดิต > ค่าใช้จ่ายที่คาด × 2 | เครดิตไม่พอ → หยุด แจ้งผู้ใช้ |
| 2 | `python /tmp/vast.py rent --label <unique> [--gpu RTX_4090] [--min-gpu-ram 24] [--max-dph 0.45]` | เลือก offer ดีสุดเอง + create + wait running + SSH → `{"ok":true,"instance_id":N,"ssh_ready":true,"chosen":{…}}` — ของจริง **41–96 s** | `ไม่มี offer <= $X` → ผ่อนเกณฑ์อื่นหรือรายงานผู้ใช้ · ลองครบ `--tries` แล้ว offer หายหมด → `rent` ใหม่อีกรอบ · `"ok":false`+`reason` → ดูตาราง state machine |
| 3 | (ทางเลือก) `plan` + `create --offer-id …` | ใช้เมื่อผู้ใช้อยากเลือก offer เองเท่านั้น | |
| 5 | `python /tmp/vast.py run --id N --cmd "nvidia-smi"` | ชื่อ GPU + VRAM **ตรงกับ offer** | ดู error playbook |

preflight อัตโนมัติ — ผ่านครบถึงจะยิง create: label ไม่ซ้ำ (ซ้ำ = **adopt ตัวเดิม**) · จำนวนเครื่อง < เพดาน ·
`machine_id=` ยืนยัน offer ยังอยู่ **และราคา ≤ เพดาน** · kwargs ทุกตัวอยู่ใน `CREATE_KWARGS`

**create พัง = ห้าม retry** → `reconcile()` หาเครื่องจาก label ก่อน (เกิดแล้ว→adopt / ไม่เกิด→`plan` ใหม่)
label คือ **idempotency key ตัวเดียวที่ Vast มี** → ทุก create ต้องมี label unique

## TEMPLATE — Python SDK

```bash
python /tmp/vast.py template-search                         # recommended templates
python /tmp/vast.py template-search --mine                  # templates ของบัญชีนี้
python /tmp/vast.py template-search --name PyTorch --limit 10
python /tmp/vast.py template-show --id 561636
python /tmp/vast.py plan --label job-1 --template-id 561636 # ใช้ disk ขั้นต่ำ + template_hash
```

`vastai 1.5.5` มี type annotation ของ `search_templates(query)` เป็น string (1.8.2 แก้เป็น `str|dict` แล้ว) แต่ implementation จริงส่ง
`query` ตรงเข้า `select_filters` และต้องเป็น dict เช่น `{"recommended":{"eq":True}}`; toolkit ใช้ dict แล้ว

`extra_filters` จาก API เป็น JSON string (บางรายการเก่าถูก encode ซ้ำ) แต่ `update_template()` ต้องการ dict:
toolkit decode ได้ถึง 3 ชั้น, แปลง `cuda_max_good→cuda_vers` และ GPU RAM จาก MB→GB สำหรับ query,
ใส่ filter เข้า offer search แล้วตรวจซ้ำกับ response หน่วย MiB ก่อนอนุญาต create

การเปลี่ยน Template ต้องถามผู้ใช้ก่อนทุกครั้ง และแสดง name/image:tag/disk/visibility/launch mode:

```bash
python /tmp/vast.py template-create --name NAME --image REPO --image-tag TAG --disk 32 --ssh --direct --yes
python /tmp/vast.py template-update --id N --image-tag TAG --yes
python /tmp/vast.py template-delete --id N --dry-run
# ถามยืนยันพร้อม id + name แล้วจึง:
python /tmp/vast.py template-delete --id N --yes
```

`template-create` ใช้ `retry=1`, ห้ามชื่อซ้ำ และ reconcile ด้วย creator/name/image/tag เพราะ response สำเร็จอาจไม่คืน id/hash ·
`update_template()` ส่งค่า default ทับ field ที่ไม่ระบุได้ จึงต้องอ่าน template เดิม, preserve launch flags ทุกตัว,
merge ทุก field ก่อน PUT และอ่านกลับ verify · output ไม่คืน `env`, docker login, onstart หรือ readme เพราะอาจมี secret ·
สร้าง instance จาก template ยังต้อง `plan` ราคา offer และถามยืนยันค่าใช้จ่ายเหมือน create ปกติ
โดย `create` ต้องรับทั้ง `--template-id` และ `--template-hash` เพื่อยืนยันว่า hash ไม่เปลี่ยน, disk พอ และ offer compatible

# RUNBOOK 2 — STOP / START (verify จริงทุกครั้ง อย่าเชื่อ return value)

| # | รัน | ต้องเห็น | ถ้าไม่เห็น |
|--:|:--|:--|:--|
| 1 | `… status --id N` | `actual_status` ปัจจุบัน | `exists:false` → เครื่องหายแล้ว |
| 2 | `… stop --id N` | `{"ok":true,"actual_status":"exited"}` (จริง **30–44 s**) | ค้าง → `recycle_instance` → ยังค้าง → destroy |
| 3 | `… start --id N` | `{"ok":true,"actual_status":"running"}` (จริง **40–47 s**) | host เอาไปให้คนอื่นแล้ว → สร้างใหม่จาก offer อื่น |
| 4 | `… run --id N --cmd "true"` | rc 0 | sshd ยังไม่ขึ้น รออีก 10–20 s |

`stop` หยุดค่า GPU แต่ **ยังเสียค่า storage** — `destroy` เท่านั้นที่หยุดทุกอย่าง (toolkit เตือนให้ทุกครั้ง)
ข้อมูลใน disk รอด stop→start (ทดสอบแล้ว)

# RUNBOOK 3 — DESTROY

| # | รัน | ต้องเห็น | ถ้าไม่เห็น |
|--:|:--|:--|:--|
| 1 | `… destroy --id N --dry-run` | รายการที่จะโดนลบ | เป้าหมายผิด → แก้ตัวกรอง |
| 2 | **ถามผู้ใช้** พร้อมเลข id + เตือนข้อมูลหายถาวร | ตอบตกลง | ไม่ตอบ = ไม่ลบ |
| 3 | `… destroy --id N --yes` | `{"destroyed":[N],"failed":[]}` — verify แล้วว่าหายจาก `show_instances()` (จริง ≤ 5 s) | ยังเห็นอยู่ → สั่งซ้ำ (idempotent) แล้วเช็ค console |
| 4 | `… sweep` | เครื่องที่เหลือตรงกับที่ตั้งใจ | ตามลบ |

`--id` ที่ไม่มีแล้ว = นับว่าสำเร็จ · ตั้ง `VAST_LABEL_PREFIX` แล้วจะ**ปฏิเสธการลบเครื่องที่ label ไม่ตรง** ·
เพดาน 10 เครื่อง/ครั้ง (`VAST_MAX_DESTROY`)

# RUNBOOK 4 — SWEEP & AUDIT (บังคับก่อนจบทุก session)

```bash
python /tmp/vast.py sweep --older-than 60      # exit 1 ถ้ายังมีเครื่องเหลือ
```

แล้ว**รายงานผู้ใช้เสมอ** แม้เป็น 0: กี่เครื่องรันอยู่ / burn rate / ใช้ไปประมาณเท่าไร / เครดิตเหลือ
คิดถูกต้อง: `running` = `dph_base + storage`, `exited/stopped` = **storage อย่างเดียว**

# RUNBOOK 5 — BILL (บังคับหลัง destroy ทุกครั้ง: สรุปค่าใช้จ่ายและสถิติให้ผู้ใช้)

```bash
python /tmp/vast.py bill --id N [--id M …]      # ระบุ id ตรง ๆ
python /tmp/vast.py bill --label-prefix job-     # เลือกจาก label ได้ทั้งเครื่องที่ยังอยู่และที่ลบแล้ว
python /tmp/vast.py bill --days 1 --json         # ย้อนหลัง N วัน (default 7) / รูปแบบเครื่องอ่าน
```

`bill` ใช้ `show_invoices_v1(charges=True)` (1.8+; `show_invoices()` เดิม deprecated) — ได้ `metadata.label` มาด้วย
จึงกรอง `--label`/`--label-prefix` ได้**แม้เครื่องถูกลบไปแล้ว** · ยอดของเครื่องที่เพิ่งลบยัง**โตต่ออีกหลายนาที**หลัง destroy
(เคสจริง 2026-09-30: รันจริง 2.6 นาที แต่ settle ที่ 0.119 ชม. ≈ 7 นาที) ให้รัน `bill` ซ้ำหลัง ~10 นาทีก่อนสรุปยอดสุดท้าย

รายงานผู้ใช้เป็น **ตารางต่อเครื่อง**: ชั่วโมง GPU · ค่า GPU · storage · GB ที่ดาวน์โหลด · ค่าดาวน์โหลด · upload · รวม
ตามด้วยบรรทัดรวมทั้งงานและเครดิตที่เหลือ พร้อมสถิติของงาน (เวลาตั้งแต่ create ถึง destroy, จำนวนเครื่องที่เช่า/เปลี่ยน,
ความเร็วดาวน์โหลดที่วัดได้, offer ที่เลือกและเหตุผล) ตัวเลขจาก `sweep` เป็นค่าประมาณจาก `dph_total × uptime` เท่านั้น
ส่วน `bill` คือค่าจริงจาก invoice ซึ่ง **รวมค่าดาวน์โหลดต่อ GB** ที่ `sweep` มองไม่เห็น (เคสจริง 2026-09-20: โหลดโมเดล 11.8 GB
ที่ $0.029/GB = $0.34 มากกว่าค่า GPU $0.16 ของเครื่องเดียวกัน) invoice ออกเป็น bucket รายวัน ชั่วโมงล่าสุดอาจยังไม่ครบ
ให้บอกผู้ใช้ด้วย

**ป้องกันตั้งแต่ตอน plan:** ใส่ `--extra-query "inet_down_cost<0.01"` เมื่องานต้องดาวน์โหลดหลาย GB และหลัง `create`
วัดความเร็วจริงทันที (`curl -o /dev/null -m 10 -w "%{speed_download}" <url ไฟล์ใหญ่>`) ค่า `inet_down` ที่ประกาศเชื่อไม่ได้
(เคสจริง: ประกาศ 1391 Mbps ได้จริง 1.8 MB/s) ถ้าช้ากว่า ~20 MB/s ให้ destroy แล้วเช่าเครื่องอื่นก่อนเริ่มติดตั้ง

---

# State machine + timeout (ตัวเลขจากการวัดจริง)

```
create ──► None(provisioning) ──► created/loading ──► running ──► exited/stopped ──► (destroy) หาย
                                       │                  │
                                       └── offline/unknown ┘  = ตาย ไปต่อไม่ได้
```

| ขั้น | วัดได้จริง | timeout | ครบแล้วทำอะไร |
|:--|:--|:--|:--|
| `create` ตอบกลับ | 1.3–1.8 s | — | error → reconcile **ห้าม retry** |
| → `running` (image cache แล้ว / ต้อง pull 2.4 GB) | 21–22 s / 30–138 s | 900 s | |
| ค้าง `loading`/provisioning | — | **420 s** | **destroy ทันที เปลี่ยน offer** (เจอจริง 1 ครั้ง) |
| `running` → sshd รับ connection | +0–20 s | poll 10 s × 20 | ดู error playbook ข้อ 6 |
| `stop` → `exited` / `start` → `running` | 30–44 s / 40–47 s | 420 s | `recycle_instance` แล้ววัดใหม่ |
| `destroy` → หายจาก `show_instances()` | ≤ 5 s | 60 s | สั่งซ้ำ |

**`running` ≠ ใช้งานได้** — นิยาม "พร้อม" ที่ใช้ได้จริง = `actual_status=="running"` **และ** `ssh … true` rc 0

# เลือก offer ให้ดีกว่า "ถูกสุด"

`BASE_FILTER` = `rentable=true verified=true reliability>0.99 direct_port_count>=4 duration>2`

`reliability>0.99` ต่ำกว่านี้เจอ host หลุด · `inet_down>500` pull เร็ว = จ่ายค่ารอน้อย (30 s vs 138 s) ·
`cuda_vers>=12.4` image ใหม่ต้องการ · `disk_space>` disk+10 · `direct_port_count>=4` เผื่อ map port ·
`duration>2` (**วัน**) host รับเช่าต่อได้อีก ≥2 วัน · `gpu_ram>=N` (**GB**) · `dlperf_per_dphtotal` สูง = คุ้มจริงไม่ใช่แค่ถูก

⚠ **ห้ามใช้ `georegion=true` / `chunked=true`** — ตัวแปลงฝั่ง client ตัดส่วนที่เหลือของ query ทิ้งเงียบ ๆ
(`georegion=true geolocation=EU dph<0.5 num_gpus=2` → `geolocation in [...] dph < 0`, `num_gpus` หาย)

**การค้นทุกครั้งยิงขนานอย่างน้อย 2 รอบ** (`search()` ใน toolkit): รอบถัดไปเริ่มหลังรอบก่อน ≥3 วินาที
แล้วรวมผลและตัด offer id ที่ซ้ำ ทำให้ได้ offer มากกว่า cap 64 แถวต่อรอบ และจับ offer ที่เพิ่งขึ้นได้
ปรับได้ด้วย `VAST_SEARCH_PASSES` (≥2) และ `VAST_SEARCH_GAP` (≥3 วินาที ตั้งต่ำกว่านี้จะถูกปัดขึ้นเป็น 3) ·
ถ้าเรียก `search_offers` เองนอก toolkit ก็ต้องทำแบบเดียวกัน

ฟิลด์ query ทั้งหมด: `vastai search offers --help` = source of truth ที่แม่นกว่าเอกสารเว็บ
ชื่อ/หน่วยที่ต่างกันสองฝั่ง อยู่ในบล็อก `SDK CONTRACT` (`OFFER` / `INST`) ต้น toolkit แล้ว

---

# Error playbook — อาการ → สาเหตุ → ทางแก้

✅ = เจอของจริงในการทดสอบ · ⚠️ = รู้จากซอร์ส/เอกสาร ยังไม่ได้ทำให้เกิดจริง (UNVERIFIED)

| # | อาการ | สาเหตุ | ทางแก้ |
|--:|:--|:--|:--|
| 1 ✅ | create timeout / network ขาด → **เครื่องซ้ำ** | `VastAI()` default `retry=3` และ retry **ครอบ `PUT /asks/<offer>/`** → create ที่ response หายถูกยิงซ้ำเงียบ ๆ ได้ 3 ครั้ง (พิสูจน์ด้วย HTTP server จำลอง: retry=3→3 ครั้ง, retry=1→1, retry=0→0 ครั้ง + `AttributeError`) | `VastAI(api_key=…, retry=1)` เฉพาะตอน create แล้ว `reconcile()` — **ห้าม retry ด้วยมือซ้ำอีก** (toolkit ทำให้แล้ว) |
| 2 ✅ | `HTTPError 400 … /api/v0/asks/<OFFER_ID>/` | offer หมดอายุ/ถูกแย่งระหว่าง search→create (อายุหลักวินาที–นาที ใช้ได้ครั้งเดียว) | `reconcile()` ยืนยันไม่มีเครื่องเกิด → `plan` ใหม่ **ห้ามใช้ id เดิม** · โดนซ้ำ ≥3 ครั้ง = ของหายาก ให้ผ่อนเกณฑ์ **ห้ามขยายเพดานราคา** · ลดโอกาสด้วย `cancel_unavail=True` + ถามผู้ใช้ก่อน search รอบสุดท้าย |
| 3 ✅ | `HTTPError 400 … /instances/command/<ID>/` | `execute()` รองรับแค่ `ls`/`rm`/`du` ตาม help และของจริง **ตอบ 400 หมด** บน `nvidia/cuda:*-runtime` | ใช้ `run --cmd` (SSH) · ⚠️ ยังไม่ได้ลองบน `vastai/base-image:*` |
| 4 ✅ | `copy()` คืน `success:True` แต่ไฟล์ไม่ไป | ขา local = แค่จอง rsync endpoint (`cli/commands/storage.py:92-116` รัน rsync ต่อเอง) | ใช้ `push`/`pull` (scp) · `copy()` ใช้ได้เฉพาะ remote→remote |
| 5 ✅ | `vastai_kaalia@…: Permission denied` + `rsync error (code 5)` แต่ **exit 0** | rsync relay ปฏิเสธคีย์ที่ลงทะเบียนไว้ + CLI ไม่เช็ค returncode (`cli/main.py` จับ exception แล้ว break → `sys.exit(None)`) | **`vastai` CLI exit 0 แม้ API error** — `set -e`/`$?` จับไม่ได้ ใช้ SDK แทน หรือ verify ปลายทางเสมอ |
| 6 ✅ | ค้าง `loading` / `running` แล้วแต่ ssh ไม่ติด | host pull image ไม่ไหว; Vast apt-install `openssh-server` เข้า container เอง | poll `ssh … true` แทนที่จะเชื่อ `actual_status` · ดู `logs(instance_id=…, tail="200")` · **ค้างเกิน 420 s = destroy เปลี่ยน offer** (เจอจริง: RTX 4070S HK, inet 1377 Mbps, rel 0.9957 ก็ยังค้าง — reliability สูงไม่การันตี) |
| 7 ✅ | `scp: dest open "/workspace/x": No such file` | image `nvidia/cuda:*` **ไม่มี `/workspace`** | `mkdir -p` ก่อน (toolkit ทำให้แล้ว) หรือใช้ `/root/` — อย่า copy ลง `/root` หรือ `/` ทั้ง dir จะพัง permission `.ssh` |
| 8 ✅ | ราคาที่โดนจริง > ที่ประเมิน ($0.0947→$0.1044) | `search_offers(storage=5.0)` เป็น default | ส่ง `storage=<disk จริง>` ทุกครั้ง |
| 9 ✅ | `search_offers(query="id=…")` คืน 0 แถวทั้งที่ offer ยังอยู่ | server ไม่ honor `id` (ผ่าน `parse_query` แต่ถูกเมิน) | ค้นด้วย `machine_id=` แล้วหา offer id ในผลลัพธ์ — เอา `id=` ไปทำ preflight จะ **บล็อกการสร้างทุกครั้ง** |
| 10 ✅ | `search_offers(limit=500)` คืน 64 | cap ฝั่ง server | **แคบ query** ไม่ใช่เพิ่ม limit |
| 11 ✅ | `ssh_url()` ปกติ แต่ `Permission denied (publickey)` | public key ยังไม่ผูกกับบัญชี (หรือผูกคนละคีย์กับที่ `VAST_SSH_KEY_FILE` ชี้) | `vast.py keys` ดู `registered` + `fingerprint` → ยังไม่ผูกก็ `keys --attach` แล้วรอ ~10 s · เครื่องที่สร้างไปแล้วใช้ `attach_ssh(instance_id=…, ssh_key=<เนื้อ public>)` · ยืนยันจาก `logs()` ที่จะขึ้น `Accepted key … authorized_keys` |
| 12 ✅ | `actual_status == "offline"` / ไม่อัปเดต | host หลุด | ถือว่าล้มเหลวทันที อย่ารอ → destroy แล้วเลือก offer ที่ `reliability` สูงกว่า |
| 13 ✅ | error message ไม่มีรายละเอียด | `str(HTTPError)` มีแค่ code+url | อ่าน `e.response.json()["msg"]` (toolkit มี `http_err()`) |
| 14 ⚠️ | `no space left on device` / `manifest unknown` / `pull access denied` | disk เล็กไป, tag ผิด, private repo | disk ≥ ขนาด image × 2 + data (`nvidia/cuda:*-runtime` ≈ 3.6 GB บนดิสก์) · private repo: `login="-u USER -p TOKEN docker.io"` · **ขยาย disk ทีหลังยาก ตั้งให้พอแต่แรก** |
| 15 ⚠️ | create ถูกปฏิเสธ / เครื่องถูก stop เอง | เครดิตหมด | เช็ค `show_user()["credit"]` ก่อนสร้างเสมอ · `stop` ยังเสียค่า storage มีแต่ `destroy` ที่หยุดทุกอย่าง |
| 16 ⚠️ | `running` แต่ container ตาย | `actual_status` บอกสถานะ *contract* ไม่ใช่สุขภาพ process | ดู `status_msg` + `logs()` · `recycle_instance()` (รี container ไม่เสียดิสก์) → ยังพัง → destroy |
| 17 ⚠️ | `HTTPError 429` | rate limit (SDK retry เอง: 429/502/503/504) | poll ไม่ถี่กว่า 5 s **แต่ห้าม backoff-retry บน create** |
| 18 ✅ | `show_invoices()` deprecated / `fetch_contracts()` 401 | API เก่า / ต้องสิทธิ์อื่น | `show_invoices_v1(**params)` · ประเมินค่าใช้จ่ายจาก `sweep` แทน |
| 19 ✅ | `template-create` ตอบ success แต่ไม่มี id/hash | response ของ API ไม่คืน identity | snapshot template ids ก่อน POST, ใช้ `retry=1`, แล้ว reconcile จาก creator+name+image+tag; ห้าม retry ถ้า match ไม่เท่ากับ 1 |
| 20 ✅ | update แค่ description แล้ว `extra_filters` จาก `{}` กลายเป็น `"{}"` | API คืน JSON string แต่ SDK PUT ต้องการ dict | decode JSON (รองรับค่าที่ encode ซ้ำ) ก่อน merge และอ่านกลับ verify |
| 21 ✅ | PyTorch Template `running` แต่ proxy SSH ต่อไม่ได้ ขณะที่ direct 22/tcp ใช้ได้ | `ssh_host/ssh_port` ชี้ proxy แม้มี direct mapping | ถ้ามี `public_ipaddr` + `ports["22/tcp"]` ให้ใช้ direct endpoint ก่อน |
| 22 ✅ | `plan --template-id` เสนอ GPU ที่ผิด requirement | ไม่ได้นำ Template `extra_filters` เข้า offer query | แปลง filter+หน่วยเข้า query และตรวจ raw offer ซ้ำก่อน plan/create |
| 23 ✅ | `plan --gpu RTX_5090` คืน 0 offers แต่ query ที่ตัด `cuda_vers` คืนเครื่องจำนวนมากซึ่งมี `cuda_max_good=13.x` | Offer API มี false negative เมื่อใช้ server-side `cuda_vers` ร่วมกับ RTX 5090 | ห้ามส่ง `cuda_vers` ใน offer query; กรอง `cuda_max_good >= --min-cuda` จาก raw response ฝั่ง client (toolkit ทำให้แล้ว) |
| 24 ✅ | `rent` ที่ label ผิด prefix / เครื่องเต็มเพดาน วนลอง 5 offers แล้วรายงานว่า "offer หาย" | guard ใน `preflight` ถูกเรียกใน loop ต่อ offer | แก้แล้ว: `rent` เรียก `preflight` ก่อน search → fail ทันทีพร้อมเหตุผลจริง |
| 25 ✅ | template ที่ `template-update` แล้ว ได้ `hash_id` ใหม่ | Vast ออก hash ใหม่ทุก update | `plan --template-id` ใหม่หลัง update ทุกครั้ง — `create` ด้วย hash เก่าจะถูกปฏิเสธ ("template hash เปลี่ยนแล้ว") |
| 26 ✅ | ยอดใน `bill` ของเครื่องที่ลบแล้วยังเพิ่มขึ้น | billing ฝั่ง Vast settle ช้า/ปัดเวลา | `show_invoices_v1()['current']` / `sweep` ยืนยันว่าไม่มีอะไรคิดเงินอยู่ แล้วรัน `bill` ซ้ำภายหลัง |
| 27 ✅ | `plan --template-id` ของ template ที่มี `cuda_max_good` ส่ง `cuda_vers` ไป server | `template_query_parts` แปลง filter ตรง ๆ (ชน #23) | แก้แล้ว: ข้าม `cuda_max_good` ใน query แล้วตรวจฝั่ง client ใน `template_offer_mismatches` |

---

# ผลทดสอบซ้ำบน vastai 1.8.2 (2026-09-30)

SDK 1.8.2 เปลี่ยน signature เป็น explicit params (`create_instance`, `create_template`, `update_template`, `show_invoices`)
และเพิ่ม `ssh`/`jupyter`/`direct`/volume/`bid_price` — raw `runtype` string เดิมยังใช้ได้ (ห้ามส่งคู่กับ flag ใหม่ → ValueError)
· default `retry=3`, timeout 120 s, retryable 429/502/503/504 **ไม่เปลี่ยน** → กฎ `retry=1` ตอน create ยังจำเป็น

3 instance พร้อมกัน (`rent` · `plan`+`create --runtype ssh_proxy` · `plan --template-id`+`create` จาก private template) ·
รวม ~8 นาที · ค่าใช้จ่ายจริง ~$0.044 · **ผ่าน**: `drift --live` · `plan` (default/4090+RAM/5090 CUDA client-side/template/เพดานต่ำ→ปฏิเสธ)
· SSH direct+proxy ทั้ง 5 endpoint · `nvidia-smi` ตรง offer · `push` ลง `/workspace` ที่ไม่มี + `pull` byte-match · `stop`→`exited`
(no-op ซ้ำ, storage-only) → `start`→`running` ข้อมูลรอด · adopt label ซ้ำ (`rent`/`create`) · guard prefix/max-instances/expect-dph
· `destroy --dry-run`/guard prefix/idempotent · `template-create`+กันชื่อซ้ำ · `template-update` verify · `template-delete` verify · `bill` v1
· offer หายระหว่าง plan→create 1 ครั้ง → preflight `machine_id` ปฏิเสธถูกต้อง ไม่มีเครื่องเกิด · แก้บั๊ก #24 #27

# ผลทดสอบจริง (2026-08-26)

ทุกเครื่อง: `nvidia/cuda:12.4.1-runtime-ubuntu22.04` (~2.4 GB compressed) · disk 40 GB · on-demand (ไม่ใช้ bid)
· เพดาน $0.20/hr และ 20 นาที/เครื่อง · **8 instance รวม ~27 นาที ค่าใช้จ่ายจริงจากใบแจ้งหนี้ ~$0.04**
(GPU ~75% · storage ~22% · bandwidth ~3%) — ยอดตรงกับเครดิตที่ลดลงจริง

**ผ่านครบทุกเส้นทาง**: `plan` · `create`+anti-duplicate · `loading→running` · `ssh nvidia-smi` (GPU + VRAM ตรงกับ offer)
· `push`/`pull` สองทาง · `logs` · `label_instance` · `stop`+verify `exited` · `start`+verify `running` (ข้อมูลรอด)
· `destroy`+verify หายจริง · adopt เมื่อ label ซ้ำ · guard ปฏิเสธลบเครื่องผิด prefix · `drift`

**สองเคสล้มเหลวที่เจอจริงและระบบจัดการถูก**: offer หมดอายุ → HTTP 400, reconcile ยืนยันไม่มีเครื่องเกิด ไม่ retry
· host ค้าง `loading` 428 s → ตัดตามเพดาน 420 s, destroy, เปลี่ยน offer → running ใน 22 s

**Template live test (2026-08-26)**: สร้าง private template → search/readback → update → launch จริงบน RTX 3060 →
SSH+GPU ผ่าน → stop/destroy → delete template+verify · official PyTorch Template launch ผ่านและรัน
PyTorch 2.11.0+cu128 บน GPU จริง; พบและแก้ 4 จุดตาม error playbook ข้อ 19–22 ·
official vLLM offer ราคาถูกหายก่อน create 3 ครั้ง จึงหยุดตาม stopping condition และไม่มี instance ซ้ำ

**ยัง UNVERIFIED**: `execute()` บน `vastai/base-image:*` · สาเหตุที่ rsync relay ปฏิเสธคีย์ ·
พฤติกรรมตอนเครดิตหมด / 429 / disk เต็ม · เส้นทาง `bid`/spot · `fetch_contracts()` 401

---

# 🔐 ก่อนส่งสกิลนี้ให้คนอื่น

ไฟล์นี้ออกแบบให้**ส่งต่อได้ทันทีโดยไม่รั่วอะไรเลย** — key อยู่ใน `.env` ที่ไม่ได้อยู่ในสกิล
และไม่มี path ส่วนตัว / account id / เลข instance / ยอดเครดิต อยู่ในไฟล์

ถ้าแก้ไฟล์นี้เอง ให้เช็คก่อนส่งทุกครั้งว่าไม่มีสิ่งเหล่านี้หลุดเข้ามา:

```bash
grep -nE '(VAST_API_KEY|ssh-(rsa|ed25519))[= ]|/home/[a-z]|/Users/|[A-Za-z0-9]{40,}' SKILL.md
```

| อย่าใส่ | เพราะ | ใส่แทนด้วย |
|:--|:--|:--|
| ค่า `VAST_API_KEY` | ใครได้ไปก็เช่าเครื่องด้วยเครดิตคุณได้ | ชื่อตัวแปรเฉย ๆ |
| path เต็มของ `.env` / โฟลเดอร์โปรเจกต์ | เผยโครงสร้างเครื่องและชื่องาน | ลำดับการค้นหา (`$VASTAI_ENV` → `~/.config/vastai/…`) |
| account id / ssh key id | ใช้ระบุตัวตนคุณบน Vast | ตัดออก หรือบอกวิธีหาเอง (`show_user()` / `show_ssh_keys()`) |
| เลข instance / machine id ที่เคยเช่า | ผูกกับบัญชีคุณ | ตัวเลขสรุปรวม |
| ยอดเครดิต / ยอดเงินคงเหลือ | ข้อมูลการเงิน | ตัดออก |
| private key (`tp`, `id_rsa`) | ไม่ต้องพูดถึงเลย | อ้างผ่าน `VAST_SSH_KEY_FILE` |

ฝั่งผู้รับต้องทำแค่: `pip install 'vastai~=1.8'` → สร้าง `~/.config/vastai/vastai.env` (chmod 600)
→ `python /tmp/vast.py env` ต้องขึ้น `env_file_exists:true`

เพิ่มเติมสำหรับความปลอดภัยของตัวเอง:
- `.env` ต้อง `chmod 600` และอยู่ใน `.gitignore` — toolkit เตือนให้ถ้า group/other อ่านได้
- อย่าเก็บ `VAST_API_KEY` ปนกับ token อื่น (GitHub/Docker) ในไฟล์เดียว — สกิลนี้จะได้ไม่ต้องอ่านไฟล์ที่มีความลับอื่น
- ออก **API key แยกใบต่องาน** ที่ https://cloud.vast.ai/manage-keys/ แล้วเพิกถอนใบเดียวได้เมื่อรั่ว
- `/tmp/vast.py` ไม่มีความลับอยู่ในตัว (อ่าน key ตอน runtime) — แต่บนเครื่องที่ใช้ร่วมกันให้เขียนลงโฟลเดอร์ส่วนตัวแทน
- ตั้ง `VAST_LABEL_PREFIX` ทุกงาน แล้วสกิลจะปฏิเสธการลบเครื่องของงานอื่นให้เอง

---

# ✅ Checklist ก่อนจบงานทุกครั้ง

- [ ] `python /tmp/vast.py sweep` แล้ว **รายงานผู้ใช้**: กี่เครื่องรันอยู่ / burn rate / ใช้ไปประมาณเท่าไร / เครดิตเหลือ
- [ ] หลัง destroy รัน `python /tmp/vast.py bill --id …` แล้ว **สรุปค่าใช้จ่ายจริง + สถิติของงาน** (ตาราง GPU/storage/download/upload ต่อเครื่อง, รวม, เครดิตเหลือ, เวลา create→destroy, จำนวนเครื่องที่เช่า, ความเร็วเน็ตที่วัดได้)
- [ ] เครื่องที่ไม่ตั้งใจให้ค้าง → destroy แล้ว **verify ว่าหายจาก `show_instances()`** จริง
- [ ] ทุก `stop`/`start`/`destroy` อ่านสถานะซ้ำหลังทำ ไม่ได้เชื่อ return value
- [ ] ไม่มี API key / `instance_api_key` / `jupyter_token` โผล่ใน output หรือไฟล์
- [ ] ถ้ามี `create` ที่ error → ยืนยันแล้วว่า **ไม่มีเครื่องซ้ำเกิดขึ้น** (เช็คจาก label)
- [ ] ชื่อ field / signature ที่ใช้ตรงกับบล็อก `SDK CONTRACT` — เดาไม่ได้ให้เขียน **UNVERIFIED**
- [ ] ไม่แตะ instance ที่ label ไม่ตรง `VAST_LABEL_PREFIX` ของงานนี้
- [ ] `.env` มีแต่ private key path — ไม่ต้องมี `.pub` (toolkit derive เอง)
- [ ] ค่า config ทั้งหมดอยู่ใน `.env` — ไม่มี key หรือเพดานราคา hardcode อยู่ในคำสั่งที่รัน
- [ ] Template create/update/delete อ่านกลับ verify แล้ว; test template ไม่ค้างในบัญชี
- [ ] Instance จาก Template ผ่านทั้ง template id+hash, recommended disk และ `extra_filters` compatibility
