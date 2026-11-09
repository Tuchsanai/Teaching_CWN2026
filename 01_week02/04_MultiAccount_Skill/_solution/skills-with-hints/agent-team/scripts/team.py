#!/usr/bin/env python3
"""ทีม multi-agent ข้ามบัญชี Claude Code / Codex: กราฟงาน คิวตามโควตา failover หัวหน้าทีมสลับตัวได้

ใช้สคริปต์ของสกิลข้างเคียง (../../yolo/scripts, ../../cyolo/scripts) · ไม่แตะไฟล์ credential · ไม่รันผลลัพธ์เป็นคำสั่ง
"""
import argparse
import json
import os
import random
import re
import string
import sys
import threading
import time

sys.dont_write_bytecode = True
_SKILLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path[:0] = [os.path.join(_SKILLS, "yolo", "scripts"), os.path.join(_SKILLS, "cyolo", "scripts")]
import ma_ledger as L  # noqa: E402
import yolo as Y  # noqa: E402
import cyolo as C  # noqa: E402

TEAM_ROOT = L.ROOT
PIN = re.compile(r"c?yolo\d+")
ID_RE = re.compile(r"[A-Za-z0-9_.-]+")
REF_RE = re.compile(r"\{\{(file:)?([A-Za-z0-9_.-]+)\}\}")
FAILOVER = {"quota", "rate_limit", "auth_expired", "not_logged_in"}
OPEN = ("pending", "running", "waiting_approval")
FAILED = ("failed", "blocked")
INLINE_LIMIT = 4000
NEAR_PCT = 60
BOARD_RE = re.compile(r"^\s*BOARD:\s*(.+)$", re.M)
IMAGE_RE = re.compile(r"สร้างภาพ|วาดภาพ|สร้างรูป|image generation|generate (an |a )?image|\.png\b", re.I)
REVIEW_RE = re.compile(r"ตรวจโค้ด|รีวิวโค้ด|code review|review (the |this )?code|audit (the )?code", re.I)
DOC_RE = re.compile(r"เอกสาร|รายงานยาว|long document|summari[sz]e .*(document|report)", re.I)


class NoAccount(Exception):
    pass


class PinnedFailed(Exception):
    pass


def side(account):
    return "cyolo" if account.startswith("cyolo") else "yolo"


def cli_of(account):
    return "codex" if side(account) == "cyolo" else "claude"


def hms():
    return time.strftime("%H:%M:%S")


def route(prompt="", task_type="", model="", kind="task"):
    """เลือกฝั่งตามชนิดงาน คืน (sides, bound, reason) sides=None แปลว่าได้ทุกบัญชี"""
    if kind == "image" or task_type == "image" or (not task_type and IMAGE_RE.search(prompt or "")):
        return ["cyolo"], True, "งานภาพ → cyolo"
    if model:
        if model in Y.MODELS:
            return ["yolo"], False, "ระบุรุ่น Claude"
        return ["cyolo"], False, "ระบุรุ่น Codex"
    if task_type in ("code_review", "review") or (not task_type and REVIEW_RE.search(prompt or "")):
        return ["cyolo", "yolo"], False, "ตรวจโค้ด → Codex"
    if task_type in ("long_doc", "doc") or (not task_type and DOC_RE.search(prompt or "")):
        return ["yolo", "cyolo"], False, "เอกสารยาว → Claude"
    return None, False, "งานทั่วไป → บัญชีที่เหลือโควตามาก"


def parse_budget(text):
    """'5000' ทุกบัญชี · 'yolo1=100,cyolo2=50' รายบัญชี"""
    if text in (None, ""):
        return {}
    if re.fullmatch(r"\d+", str(text)):
        return {"*": int(text)}
    out = {}
    for part in str(text).split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = int(v)
    return out


def loose_json(text):
    s = (text or "").strip()
    s = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", s).strip()
    try:
        return json.loads(s)
    except ValueError:
        a, b = s.find("{"), s.rfind("}")
        if a >= 0 and b > a:
            return json.loads(s[a:b + 1])
        raise


def check_expect(expect, text):
    """คืน (ok, ค่าที่จะส่งต่อ, เหตุผลที่ไม่ผ่าน)"""
    raw = (text or "").strip()
    if not expect or expect == "text":
        return bool(raw), raw, "" if raw else "คำตอบว่าง"
    if expect in ("int", "number"):
        s = re.sub(r"[`*]|,(?=\d)", "", raw).strip().rstrip(".")
        pat = r"[-+]?\d+" if expect == "int" else r"[-+]?\d+(?:\.\d+)?"
        if re.fullmatch(pat, s):
            return True, s, ""
        if "\n" not in s:
            m = re.search(r"=\s*(" + pat + r")$", s)
            if m:
                return True, m.group(1), ""
        return False, raw, "expect %s: คำตอบไม่ใช่ตัวเลขล้วนหรือสมการบรรทัดเดียวที่ลงท้าย = N" % expect
    if expect == "json":
        try:
            return True, json.dumps(loose_json(raw), ensure_ascii=False), ""
        except ValueError:
            return False, raw, "expect json: แปลงเป็น JSON ไม่ได้"
    if expect.startswith("regex:"):
        ok = re.search(expect[6:], raw, re.S) is not None
        return ok, raw, "" if ok else "expect regex ไม่ตรง: " + expect[6:]
    if expect.startswith("contains:"):
        ok = expect[9:] in raw
        return ok, raw, "" if ok else "expect contains ไม่พบ: " + expect[9:]
    return False, raw, "expect ไม่รู้จัก: " + expect


EXPECT_HINT = {"int": "ตอบเป็นจำนวนเต็มอย่างเดียว ไม่ต้องมีข้อความอื่น", "number": "ตอบเป็นตัวเลขอย่างเดียว ไม่ต้องมีข้อความอื่น",
               "json": "ตอบเป็น JSON ล้วน ไม่ต้องมี code fence"}


def run_dir_of(run_id):
    return os.path.join(TEAM_ROOT, run_id)


def latest_run():
    if not os.path.isdir(TEAM_ROOT):
        return None
    best, when = None, -1
    for d in os.listdir(TEAM_ROOT):
        p = os.path.join(TEAM_ROOT, d, "state.json")
        if os.path.isfile(p) and os.path.getmtime(p) > when:
            best, when = d, os.path.getmtime(p)
    return best


class Team:
    def __init__(self, opts, run_id=None, resume=False):
        self.o = opts
        self.run_id = run_id or time.strftime("%Y%m%d-%H%M%S-") + "".join(random.choices(string.ascii_lowercase, k=4))
        self.dir = run_dir_of(self.run_id)
        self.ledger = os.path.join(self.dir, "ledger.jsonl")
        for sub in ("out", "msgs", "approve"):
            os.makedirs(os.path.join(self.dir, sub), exist_ok=True)
        self.cv = threading.Condition(threading.RLock())
        self.g, self.specs, self.order = {}, {}, []
        self.running, self.assigned, self.tokens, self.used = {}, {}, {}, {}
        self.total_running = 0
        self.stopped = {}
        self.linked = set()
        self.threads = []
        self.last_quota = 0
        self.worker_budget = parse_budget(getattr(opts, "worker_token_budget", None))
        self.workers = [w for w in (getattr(opts, "workers", None) or "").split(",") if w]
        board = self.path("board.md")
        if not os.path.exists(board):
            with open(board, "w", encoding="utf-8") as f:
                f.write("# board\n")
        if resume:
            with open(self.path("state.json"), encoding="utf-8") as f:
                self.st = json.load(f)
            with open(self.path("graph.json"), encoding="utf-8") as f:
                graph = json.load(f)
            for n in graph["nodes"]:
                self.g[n["id"]] = n
                self.order.append(n["id"])
            for r in L.calls(L.read(self.ledger)):
                if not str(r.get("node", "")).startswith("__"):
                    self.tokens[r["account"]] = self.tokens.get(r["account"], 0) + L.tokens_used(r)
        else:
            self.st = {"run_id": self.run_id, "goal": getattr(opts, "goal", "") or "", "status": "running",
                       "created": L.now_iso(), "updated": L.now_iso(), "nodes": {}, "accounts": {},
                       "leader": None, "lead_history": [], "worker_switches": [], "budgets": {
                           "worker": self.worker_budget, "quota_stop": opts.quota_stop}}
            self.save()

    # ---------- พื้นฐาน ----------
    def path(self, *p):
        return os.path.join(self.dir, *p)

    def out(self, name):
        return self.path("out", name + ".md")

    def log(self, msg):
        print("[%s] %s" % (hms(), msg), file=sys.stderr if getattr(self.o, "json", False) else sys.stdout, flush=True)

    def save(self):
        with self.cv:
            self.st["updated"] = L.now_iso()
            tmp = self.path("state.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.st, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.path("state.json"))

    def save_graph(self):
        with self.cv:
            with open(self.path("graph.json"), "w", encoding="utf-8") as f:
                json.dump({"goal": self.st.get("goal", ""), "nodes": [self.g[i] for i in self.order]},
                          f, ensure_ascii=False, indent=1)

    def board(self, author, text, system=False):
        tag = "[system] " if system else ""
        with self.cv, open(self.path("board.md"), "a", encoding="utf-8") as f:
            f.write("- [%s] %s**%s**: %s\n" % (L.now_iso(), tag, author, text.replace("\n", " ")))

    def board_facts(self):
        with open(self.path("board.md"), encoding="utf-8") as f:
            return [ln.rstrip() for ln in f if ln.startswith("- [") and "[system]" not in ln]

    def msg(self, frm, to, text):
        with self.cv, open(self.path("msgs", "%s__%s.md" % (frm, to)), "a", encoding="utf-8") as f:
            f.write("- [%s] %s\n" % (L.now_iso(), text))

    # ---------- บัญชี ----------
    def preflight(self, sides, pinned=()):
        names = []
        if "yolo" in sides:
            names += Y.accounts()
        if "cyolo" in sides:
            names += C.accounts()
        names += [p for p in pinned if p not in names]
        rid, led = self.run_id, self.ledger

        def probe(a):
            return (Y if side(a) == "yolo" else C).check(a, run_id=rid, run_ledger=led)
        results = Y.parallel(probe, names)
        for r in results:
            self.st["accounts"][r["account"]] = {"cli": r["cli"], "ready": r["ready"], "state": r["state"],
                                                 "detail": r["detail"], "quota": None, "stopped": None}
            if not r["ready"]:
                self.log("ข้าม %s: %s" % (r["account"], r["state"]))
        ready = [r["account"] for r in results if r["ready"]]
        self.log("บัญชีพร้อม: " + (", ".join(ready) or "ไม่มี"))
        self.refresh_quota(block=True)
        self.save()
        return ready

    def is_ready(self, a):
        return bool((self.st["accounts"].get(a) or {}).get("ready"))

    def ready_accounts(self):
        return [a for a in self.st["accounts"] if self.is_ready(a)]

    def refresh_quota(self, block=False):
        self.last_quota = time.time()
        names = self.ready_accounts()
        rid, led = self.run_id, self.ledger

        def work():
            rows = Y.parallel(lambda a: (Y if side(a) == "yolo" else C).quota(a, run_id=rid, run_ledger=led), names)
            with self.cv:
                for q in rows:
                    a = q["account"]
                    self.st["accounts"][a]["quota"] = {"used_pct": q["used_pct"], "text": q["text"], "ts": q["ts"]}
                    self.used[a] = q["used_pct"] if q["used_pct"] is not None else 0
                    if q["used_pct"] is not None and q["used_pct"] >= self.o.quota_stop:
                        self.stop_account(a, "โควตา %g%% ≥ %g%%" % (q["used_pct"], self.o.quota_stop))
                self.save()
        if block:
            work()
        else:
            threading.Thread(target=work, daemon=True).start()

    def budget(self, a):
        return self.worker_budget.get(a, self.worker_budget.get("*"))

    def usable(self, a):
        return self.is_ready(a) and a not in self.stopped

    def spec_for(self, node, account=None):
        a = account or node.get("account", "any")
        if PIN.fullmatch(a):
            return {"pinned": True, "selector": a, "sides": [side(a)], "bound": True}
        if a in ("yolo", "claude"):
            return {"pinned": False, "selector": "yolo", "sides": ["yolo"], "bound": True}
        if a in ("cyolo", "codex"):
            return {"pinned": False, "selector": "cyolo", "sides": ["cyolo"], "bound": True}
        sides, bound, reason = route(node.get("prompt", ""), node.get("task_type", ""), node.get("model", ""),
                                     node.get("kind", "task"))
        return {"pinned": False, "selector": "any", "sides": sides, "bound": bound, "reason": reason}

    def candidates(self, spec, avoid=()):
        if spec["pinned"]:
            a = spec["selector"]
            return [a] if self.usable(a) and a not in avoid else []
        pool = [a for a in self.ready_accounts() if self.usable(a) and a not in avoid
                and (not self.workers or a in self.workers)]
        if spec["sides"] is None:
            return pool
        for s in spec["sides"]:
            found = [a for a in pool if side(a) == s]
            if found:
                return found
        return []

    def _pick(self, spec, avoid=()):
        cands = self.candidates(spec, avoid)
        if not cands:
            return None
        return min(cands, key=lambda a: (self.assigned.get(a, 0), self.used.get(a, 0), self.tokens.get(a, 0), a))

    def stop_account(self, a, reason):
        with self.cv:
            if a in self.stopped:
                return
            self.stopped[a] = reason
            self.st["accounts"].setdefault(a, {})["stopped"] = reason
            self.log("%s หยุดรับงาน: %s" % (a, reason))
            self.board(a, "หยุดรับงาน: " + reason, system=True)
            L.event("account_stopped", self.run_id, self.ledger, account=a, reason=reason)
            for nid, ns in self.st["nodes"].items():
                if ns["status"] in OPEN and not ns.get("acquired") and ns.get("planned") == a:
                    spec = self.specs.get(nid)
                    if spec and not spec["pinned"]:
                        new = self._pick(spec)
                        ns["planned"] = new
                        if new:
                            self.assigned[new] = self.assigned.get(new, 0) + 1
                            self.record_switch(nid, a, new, reason)
            self.save()
            self.cv.notify_all()

    def record_switch(self, nid, frm, to, reason):
        with self.cv:
            ev = {"ts": L.now_iso(), "node": nid, "from": frm, "to": to, "reason": reason}
            self.st["worker_switches"].append(ev)
            self.log("ย้ายงาน %s: %s → %s (%s)" % (nid, frm, to, reason))
            self.board(frm, "ย้ายงาน %s ไป %s: %s" % (nid, to, reason), system=True)
            self.msg(frm, to, "รับงาน %s ต่อ เหตุผล: %s" % (nid, reason))
            L.event("worker_switch", self.run_id, self.ledger, node=nid, account=frm, **{"to": to, "reason": reason})

    def acquire(self, nid, spec, avoid):
        limit = int(self.o.per_account)
        with self.cv:
            while True:
                cands = self.candidates(spec, avoid)
                if not cands:
                    if spec["pinned"]:
                        a = spec["selector"]
                        why = self.stopped.get(a) or (self.st["accounts"].get(a) or {}).get("state", "ไม่พร้อม")
                        raise PinnedFailed("บัญชี %s ที่ผู้ใช้ระบุใช้ไม่ได้ (%s) ไม่ย้ายอัตโนมัติ" % (a, why))
                    raise NoAccount("ไม่มีบัญชีที่ใช้ได้สำหรับ %s" % spec["selector"])
                planned = (self.st["nodes"].get(nid) or {}).get("planned")
                if planned in cands:
                    choice = planned if self.running.get(planned, 0) < limit else None
                else:
                    free = [a for a in cands if self.running.get(a, 0) < limit]
                    choice = min(free, key=lambda a: (self.running.get(a, 0), self.used.get(a, 0),
                                                      self.tokens.get(a, 0), a)) if free else None
                if choice and self.total_running < int(self.o.max_total):
                    self.running[choice] = self.running.get(choice, 0) + 1
                    self.total_running += 1
                    ns = self.st["nodes"].get(nid)
                    if ns is not None:
                        ns["acquired"], ns["account"] = True, choice
                    return choice
                self.cv.wait(1)

    def release(self, a, r, label):
        with self.cv:
            self.running[a] -= 1
            self.total_running -= 1
            if not label.startswith("__"):
                self.tokens[a] = self.tokens.get(a, 0) + L.tokens_used(r["ledger"])
                b = self.budget(a)
                if b is not None and self.tokens[a] >= b:
                    self.stop_account(a, "ใช้เกินงบโทเค็น (%d ≥ %d)" % (self.tokens[a], b))
            self.cv.notify_all()

    def model_for(self, node, a):
        d = int(node.get("difficulty", getattr(self.o, "difficulty", None) or 2))
        d = max(1, min(6, d))
        m, e = node.get("model"), node.get("effort")
        if side(a) == "yolo":
            dm, de = Y.DIFFICULTY[d]
            if m not in Y.MODELS:
                m = dm
            return m, (e if e in Y.EFFORTS else de)
        if m in Y.MODELS:
            m = None
        return m or C.default_model(a), (e if e in C.EFFORTS else C.DIFFICULTY[d])

    def exec_call(self, nid, label, spec, prompt, node, image_path=None):
        """เรียก 1 ครั้งพร้อม failover เฉพาะกรณีโควตา/rate limit/ล็อกอินหมดอายุ"""
        avoid, moved_from, reason = set(), None, ""
        timeout = int(node.get("timeout", self.o.timeout))
        cwd = self.node_cwd(node)
        while True:
            a = self.acquire(nid, spec, avoid)
            if moved_from:
                self.record_switch(nid, moved_from, a, reason)
                note = "\n\n(งานนี้ย้ายมาจาก %s เพราะ %s" % (moved_from, reason)
                progress = self.path("msgs", "%s__team.md" % moved_from)
                if os.path.exists(progress):
                    note += " ความคืบหน้าเดิมอยู่ที่ %s" % progress
                prompt += note + ")"
                moved_from = None
            self.link_message(nid, a, node)
            model, effort = self.model_for(node, a)
            with self.cv:
                ns = self.st["nodes"].get(nid)
                if ns is not None:
                    ns.update(model=model, effort=effort)
            self.log("เริ่ม %s บน %s (%s/%s)" % (label, a, model, effort))
            if image_path:
                r = C.image(a, prompt, image_path, timeout, self.run_id, label, self.ledger)
            elif side(a) == "yolo":
                r = Y.call(a, prompt, model, effort, timeout, cwd, node.get("schema"), self.run_id, label, self.ledger)
            else:
                r = C.call(a, prompt, model, effort, timeout, cwd, node.get("schema"), self.run_id, label, self.ledger)
            self.release(a, r, label)
            if r["ok"]:
                return r
            if r["status"] in FAILOVER:
                with self.cv:
                    self.st["accounts"].setdefault(a, {})["ready"] = False
                    self.st["accounts"][a]["state"] = r["status"]
                self.stop_account(a, "%s: %s" % (r["status"], r["error"][:80]))
                if spec["pinned"]:
                    raise PinnedFailed("บัญชี %s ที่ผู้ใช้ระบุล้ม (%s) ไม่ย้ายอัตโนมัติ" % (a, r["status"]))
                avoid.add(a)
                moved_from, reason = a, r["status"]
                continue
            return r

    def link_message(self, nid, acct, node):
        with self.cv:
            if nid in self.linked:
                return
            self.linked.add(nid)
            deps = [(d, (self.st["nodes"].get(d) or {}).get("account")) for d in node.get("depends_on", [])]
        for d, frm in deps:
            if frm:
                self.msg(frm, acct, "ส่งต่องาน %s → %s ผลอยู่ที่ %s" % (d, nid, self.out(d)))

    def node_cwd(self, node):
        c = node.get("cwd")
        if not c:
            return self.dir
        c = c if os.path.isabs(c) else self.path(c)
        os.makedirs(c, exist_ok=True)
        return c

    # ---------- สร้างงาน ----------
    def validate(self, nodes):
        seen = set(self.g)
        for n in nodes:
            nid = n.get("id")
            if not nid or not ID_RE.fullmatch(nid):
                raise ValueError("id ไม่ถูกต้อง: %r" % nid)
            if nid in seen:
                raise ValueError("id ซ้ำ: " + nid)
            seen.add(nid)
        for n in nodes:
            deps = list(n.get("depends_on", []))
            texts = " ".join(str(n.get(k, "")) for k in ("prompt", "review_prompt", "criteria"))
            for _, ref in REF_RE.findall(texts):
                if ref not in ("run_dir", "out_dir") and ref not in deps:
                    deps.append(ref)
            for d in deps:
                if d not in seen:
                    raise ValueError("งาน %s อ้างถึงงานที่ไม่มี: %s" % (n["id"], d))
            n["depends_on"] = deps
        mark, g = {}, {n["id"]: n["depends_on"] for n in nodes}

        def visit(x):
            if mark.get(x) == 1:
                raise ValueError("กราฟมีวงวน ที่งาน " + x)
            if mark.get(x) == 2 or x not in g:
                return
            mark[x] = 1
            for d in g[x]:
                visit(d)
            mark[x] = 2
        for x in g:
            visit(x)

    def add_nodes(self, nodes):
        with self.cv:
            for n in nodes:
                nid = n["id"]
                self.g[nid] = n
                self.order.append(nid)
                spec = self.spec_for(n)
                self.specs[nid] = spec
                ns = {"status": "pending", "planned": None, "account": None, "model": None, "effort": None,
                      "pinned": spec["pinned"], "error": None, "acquired": False, "started": None, "ended": None}
                if not n.get("kind") or n.get("kind") == "task" or n.get("kind") == "image":
                    if spec["pinned"]:
                        ns["planned"] = spec["selector"]
                    else:
                        p = self._pick(spec)
                        ns["planned"] = p
                        if p:
                            self.assigned[p] = self.assigned.get(p, 0) + 1
                self.st["nodes"][nid] = ns
            self.save()
            self.save_graph()

    def render(self, text, nid):
        def sub(m):
            is_file, ref = m.group(1), m.group(2)
            if ref == "run_dir":
                return self.dir
            if ref == "out_dir":
                return self.path("out")
            path = self.out(ref)
            if is_file:
                return path
            with open(path, encoding="utf-8") as f:
                val = f.read().strip()
            if len(val) > INLINE_LIMIT:
                return "(ข้อมูลยาว อ่านจากไฟล์ %s)" % path
            return val
        return REF_RE.sub(sub, text or "")

    def build_prompt(self, node, text, nid):
        parts = [text]
        facts = self.board_facts()
        if facts and node.get("board") is not False:
            joined = "\n".join(facts)
            if len(joined) > 3000:
                parts.append("ข้อค้นพบบนกระดานกลางอยู่ที่ %s อ่านก่อนเริ่ม" % self.path("board.md"))
            else:
                parts.append("ข้อค้นพบจากกระดานกลาง (ใช้ประกอบงาน):\n" + joined)
        if node.get("board"):
            parts.append("ถ้ามีข้อเท็จจริงที่งานอื่นควรรู้ ให้เพิ่มบรรทัดขึ้นต้นด้วย `BOARD: ` ในคำตอบ บรรทัดละข้อ")
        if node.get("cwd"):
            parts.append("โฟลเดอร์ทำงาน (absolute path): %s" % self.node_cwd(node))
        if node.get("progress"):
            parts.append("งานยาว: เขียนความคืบหน้าเป็นระยะลงไฟล์ %s" % self.path("msgs", "<บัญชีของคุณ>__team.md"))
        hint = EXPECT_HINT.get(node.get("expect", ""))
        if hint:
            parts.append(hint)
        return "\n\n".join(parts)

    def ref(self, path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        return text if len(text) <= INLINE_LIMIT else "(อ่านจากไฟล์ %s)" % path

    def write(self, name, text):
        p = self.out(name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    # ---------- ชนิดงาน ----------
    def do_task(self, nid, node):
        prompt = self.build_prompt(node, self.render(node["prompt"], nid), nid)
        return self.exec_call(nid, nid, self.specs[nid], prompt, node)

    def do_image(self, nid, node):
        path = node.get("path") or self.path("out", nid + ".png")
        prompt = self.render(node["prompt"], nid)
        return self.exec_call(nid, nid, self.specs[nid], prompt, node, image_path=path)

    def do_review(self, nid, node):
        wspec = self.spec_for(node, node.get("worker", "any"))
        rspec = self.spec_for(node, node.get("reviewer", "any"))
        base = self.render(node["prompt"], nid)
        criteria = self.render(node.get("review_prompt", "ตรวจความถูกต้องของงาน"), nid)
        feedback, last = "", None
        rounds = int(node.get("max_rounds", 3))
        for i in range(1, rounds + 1):
            task = base if not last else "%s\n\nงานรอบก่อน:\n%s\n\nสิ่งที่ผู้ตรวจให้แก้:\n%s\n\nแก้แล้วตอบงานฉบับสมบูรณ์" % (base, self.ref(last), feedback)
            r = self.exec_call(nid, "%s.r%d.work" % (nid, i), wspec, self.build_prompt(node, task, nid), node)
            if not r["ok"]:
                return r
            last = self.write("%s.r%d.work" % (nid, i), r["result"])
            review = "ตรวจงานต่อไปนี้\nเกณฑ์: %s\n\nงาน:\n%s\n\nถ้าผ่านทุกข้อ ตอบคำเดียวว่า APPROVED ถ้าไม่ผ่าน บอกสิ่งที่ต้องแก้เป็นข้อ ๆ และห้ามใช้คำว่า APPROVED" % (criteria, self.ref(last))
            v = self.exec_call(nid, "%s.r%d.review" % (nid, i), rspec, review, node)
            if not v["ok"]:
                return v
            self.write("%s.r%d.review" % (nid, i), v["result"])
            head = next((ln for ln in v["result"].splitlines() if ln.strip()), "")
            if "APPROVED" in head.upper() and "NOT" not in head.upper():
                with self.cv:
                    self.st["nodes"][nid]["rounds"] = i
                self.log("%s APPROVED ในรอบ %d" % (nid, i))
                return dict(r, ok=True, status="ok")
            feedback = v["result"]
        return dict(r, ok=False, status="error", error="ครบ %d รอบแล้วยังไม่ APPROVED" % rounds)

    def contest(self, nid, node, accounts, label):
        results = [None] * len(accounts)
        prompt = self.render(node["prompt"], nid)

        def one(i):
            spec = self.spec_for(node, accounts[i])
            try:
                results[i] = self.exec_call(nid, "%s.%s" % (nid, label[i]), spec,
                                            self.build_prompt(node, prompt, nid), node)
            except (NoAccount, PinnedFailed) as e:
                results[i] = {"ok": False, "status": "error", "error": str(e), "result": ""}
        ts = [threading.Thread(target=one, args=(i,)) for i in range(len(accounts))]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        for i, r in enumerate(results):
            if r["ok"]:
                self.write("%s.%s" % (nid, label[i]), r["result"])
        return results

    def do_debate(self, nid, node):
        accounts = node.get("accounts", ["yolo", "cyolo"])
        labels = [string.ascii_uppercase[i] for i in range(len(accounts))]
        results = self.contest(nid, node, accounts, labels)
        bad = [r for r in results if not r["ok"]]
        if bad:
            return dict(bad[0], error="คู่ debate ล้ม: " + bad[0]["error"])
        body = "\n\n".join("คำตอบ %s:\n%s" % (labels[i], self.ref(self.out("%s.%s" % (nid, labels[i])))) for i in range(len(results)))
        judge = "โจทย์: %s\n\n%s\n\nคุณเป็นผู้ตัดสิน เทียบคำตอบ ตรวจด้วยตนเอง แล้วตอบรูปแบบ:\nคำตอบที่ถูก: <คำตอบ>\nเหตุผล: <เหตุผล>" % (self.render(node["prompt"], nid), body)
        r = self.exec_call(nid, nid + ".judge", self.spec_for(node, node.get("judge", "any")), judge, node)
        if r["ok"]:
            with self.cv:
                self.st["nodes"][nid]["judge"] = r["result"][:400]
        return r

    def do_best_of(self, nid, node):
        accounts = node.get("accounts") or [node.get("account", "any")] * int(node.get("n", 3))
        labels = [string.ascii_uppercase[i] for i in range(len(accounts))]
        results = self.contest(nid, node, accounts, labels)
        good = [i for i, r in enumerate(results) if r["ok"]]
        if not good:
            return dict(results[0], error="ทุกตัวล้ม")
        body = "\n\n".join("ผลงาน %s:\n%s" % (labels[i], self.ref(self.out("%s.%s" % (nid, labels[i])))) for i in good)
        judge = 'โจทย์: %s\nเกณฑ์: %s\n\n%s\n\nให้คะแนนแต่ละผลงาน 0-10 ตามเกณฑ์ แล้วตอบ JSON ล้วน: {"scores":{"A":0},"winner":"A","reason":"เหตุผล"}' % (self.render(node["prompt"], nid), self.render(node.get("criteria", "คุณภาพโดยรวม"), nid), body)
        r = self.exec_call(nid, nid + ".judge", self.spec_for(node, node.get("judge", "any")), judge, node)
        if not r["ok"]:
            return r
        self.write(nid + ".judge", r["result"])
        try:
            verdict = loose_json(r["result"])
            w = str(verdict["winner"]).strip().upper()
            winner = self.ref(self.out("%s.%s" % (nid, w)))
        except (ValueError, KeyError, TypeError, OSError):
            return dict(r, ok=False, status="error", error="ผู้ตัดสินตอบผิดรูปแบบ (เก็บไว้ที่ out/%s.judge.md)" % nid)
        with self.cv:
            self.st["nodes"][nid]["judge"] = "ผู้ชนะ %s · %s · คะแนน %s" % (w, verdict.get("reason", ""), verdict.get("scores"))
        return dict(r, result=winner)

    # ---------- ตัวรัน ----------
    def run_node(self, nid):
        node = self.g[nid]
        kind = node.get("kind", "task")
        fn = {"task": self.do_task, "image": self.do_image, "review": self.do_review,
              "debate": self.do_debate, "best_of": self.do_best_of}.get(kind)
        try:
            if fn is None:
                raise NoAccount("kind ไม่รู้จัก: " + kind)
            r = fn(nid, node)
            ok, err, text = r["ok"], r.get("error", ""), r.get("result", "")
        except (NoAccount, PinnedFailed, OSError) as e:
            ok, err, text = False, str(e), ""
        status = "done"
        if ok:
            for fact in BOARD_RE.findall(text):
                self.board((self.st["nodes"][nid].get("account") or nid) + "/" + nid, fact)
            clean = BOARD_RE.sub("", text).strip()
            good, val, why = check_expect(node.get("expect"), clean)
            if good:
                self.write(nid, val)
            else:
                self.write(nid, clean)  # ผลที่ผิดรูปแบบไม่ทิ้ง
                status, err = "failed", why
        else:
            if text:
                self.write(nid, text)
            status = "failed"
        with self.cv:
            ns = self.st["nodes"][nid]
            ns.update(status=status, error=err or None, ended=L.now_iso())
            self.save()
            self.cv.notify_all()
        self.log("%s %s%s" % ("สำเร็จ" if status == "done" else "ล้ม", nid, " — " + err if err else ""))

    def approved(self, nid):
        return os.path.exists(self.path("approve", nid + ".ok"))

    def pump(self):
        with self.cv:
            start = []
            for nid in self.order:
                ns = self.st["nodes"][nid]
                if ns["status"] not in ("pending", "waiting_approval"):
                    continue
                deps = [self.st["nodes"][d]["status"] for d in self.g[nid].get("depends_on", [])]
                if any(d in FAILED for d in deps):
                    bad = [d for d in self.g[nid]["depends_on"] if self.st["nodes"][d]["status"] in FAILED]
                    ns.update(status="blocked", error="งานก่อนหน้าล้ม: " + ",".join(bad), ended=L.now_iso())
                    self.log("บล็อก %s (%s)" % (nid, ns["error"]))
                    self.save()
                    continue
                if not all(d == "done" for d in deps):
                    continue
                if self.g[nid].get("approve") and not self.approved(nid):
                    if ns["status"] != "waiting_approval":
                        ns["status"] = "waiting_approval"
                        self.log("รออนุมัติ %s: รัน team.py approve %s %s (หรือสร้างไฟล์ %s)" % (nid, self.run_id, nid, self.path("approve", nid + ".ok")))
                        self.save()
                    continue
                start.append(nid)
            start.sort(key=lambda x: 0 if self.g[x].get("kind") == "image" else 1)  # ภาพเป็นคอขวด เริ่มก่อน
            for nid in start:
                self.st["nodes"][nid].update(status="running", acquired=False, started=L.now_iso())
                t = threading.Thread(target=self.run_node, args=(nid,), daemon=True)
                t.start()
                self.threads.append(t)
            if start:
                self.save()

    def statuses(self):
        with self.cv:
            return [self.st["nodes"][n]["status"] for n in self.order]

    def tick(self):
        self.pump()
        if time.time() - self.last_quota > 60:
            self.refresh_quota()

    def drive(self, approve_timeout=3600):
        started = time.time()
        while True:
            self.tick()
            sts = self.statuses()
            if not any(s in OPEN for s in sts):
                return "finished"
            if "running" not in sts and "waiting_approval" in sts and approve_timeout >= 0 and time.time() - started > approve_timeout:
                return "waiting"
            with self.cv:
                self.cv.wait(0.5)

    def waiting_only(self):
        s = self.statuses()
        return "running" not in s and "waiting_approval" in s

    # ---------- สรุป ----------
    def rows(self):
        return L.calls(L.read(self.ledger))

    def quota_section(self, accounts):
        fetched = Y.parallel(lambda a: (Y if side(a) == "yolo" else C).quota(a, run_id=self.run_id, run_ledger=self.ledger), accounts)
        return [{"account": q["account"], "text": q["text"], "ts": q["ts"] or "-"} for q in fetched]

    def node_rows(self):
        out = []
        for nid in self.order:
            calls = [r for r in self.rows() if r.get("node") == nid or str(r.get("node", "")).startswith(nid + ".")]
            status = self.st["nodes"][nid]["status"]
            for r in calls:
                out.append([r["node"], r["account"], "%s/%s" % (r["model"], r["effort"]), r["duration_s"],
                            r["input_tokens"], r["output_tokens"], r["status"]])
            if not calls:
                out.append([nid, self.st["nodes"][nid].get("account") or "-", "-", 0, 0, 0, status])
        return out

    def summary(self, accounts=None):
        accounts = accounts if accounts is not None else sorted({r[1] for r in self.node_rows() if r[1] != "-"})
        quota = self.quota_section(accounts) if accounts else []
        return {"run_id": self.run_id, "status": self.final_status(), "run_dir": self.dir,
                "nodes": {n: {k: self.st["nodes"][n].get(k) for k in ("status", "account", "model", "effort", "error")}
                          for n in self.order},
                "judges": {n: self.st["nodes"][n]["judge"] for n in self.order if self.st["nodes"][n].get("judge")},
                "calls": self.node_rows(), "quota": quota,
                "stats_by_account": L.summarize(self.rows())["by_account"],
                "worker_switches": self.st["worker_switches"], "lead_history": self.st["lead_history"]}

    def final_status(self):
        sts = self.statuses()
        if any(s in FAILED for s in sts):
            return "failed"
        if any(s == "waiting_approval" for s in sts):
            return "waiting"
        return "done"

    def print_summary(self, s, full=False):
        if getattr(self.o, "json", False):
            print(json.dumps(s, ensure_ascii=False, indent=1))
            return
        print("\n## สรุป run %s — %s" % (s["run_id"], s["status"]))
        if full and s["lead_history"]:
            print("\n### ประวัติการสลับหัวหน้า\n" + L.table(["จาก", "ไป", "ชนิด", "เหตุผล"], [[h["from"], h["to"], h["kind"], h["reason"]] for h in s["lead_history"]]))
        if full or s["worker_switches"]:
            print("\n### การย้ายงานลูกทีม\n" + (L.table(["งาน", "จาก", "ไป", "เหตุผล"], [[w["node"], w["from"], w["to"], w["reason"]] for w in s["worker_switches"]]) if s["worker_switches"] else "ไม่มี"))
        print("\n### ผลของแต่ละงาน\n" + L.table(["งาน", "บัญชี", "รุ่น/effort", "เวลา s", "input tokens", "output tokens", "สถานะ"], s["calls"]))
        print("\n(input tokens เป็นค่าใน ledger: Claude ไม่รวม cache · Codex รวม cached แล้ว)")
        err = [[n, v["status"], v["error"]] for n, v in s["nodes"].items() if v["error"]]
        if err:
            print("\n### ปัญหา\n" + L.table(["งาน", "สถานะ", "สาเหตุ"], err))
        if s["judges"]:
            print("\n### ผู้ตัดสิน\n" + L.table(["งาน", "คำตัดสิน"], [[n, t] for n, t in s["judges"].items()]))
        if full:
            sa = s["stats_by_account"]
            print("\n### สถิติแยกตามบัญชี (รวมหัวหน้าและการตรวจ)\n" + L.table(["บัญชี", "ครั้ง", "สำเร็จ", "ล้ม", "input", "output", "$ ตามรายการ"], [[k, v["calls"], v["ok"], v["failed"], v["input_tokens"], v["output_tokens"], v["cost_usd"]] for k, v in sorted(sa.items())]))
        if s["quota"]:
            print("\n### โควตาของบัญชีที่ใช้\n" + L.table(["บัญชี", "โควตาที่ใช้ไป", "เวลาของข้อมูล"], [[q["account"], q["text"], q["ts"]] for q in s["quota"]]))


# ---------- คำสั่ง ----------
def default_opts(a):
    for k, v in (("per_account", 3), ("max_total", 8), ("timeout", 600), ("quota_stop", 80.0)):
        if getattr(a, k, None) is None:
            setattr(a, k, v)
    return a


def apply_simulation(*limit):
    cur = [x for x in os.environ.get("MA_SIMULATE_LIMIT", "").split(",") if x]
    cur += [x for item in limit if item for x in item.split(",")]
    os.environ["MA_SIMULATE_LIMIT"] = ",".join(cur)


def read_graph(src):
    if src == "-":
        raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
        thai = sum(1 for c in raw if "\u0e00" <= c <= "\u0e7f")
        junk = raw.count("เธ") + raw.count("เน")
        if "???" in raw or (thai and junk * 3 > thai):
            raise ValueError("ข้อความภาษาไทยจาก stdin เพี้ยน (เจอจาก pipe ของ PowerShell 5.1) ให้ใช้ docker cp แล้ว run <path> แทน")
    else:
        if not os.path.isfile(src):
            raise ValueError("ไม่พบไฟล์กราฟ %s (ไฟล์บน host ต้อง docker cp เข้า container ก่อน)" % src)
        with open(src, encoding="utf-8-sig") as f:
            raw = f.read()
    return json.loads(raw)


def normalize_graph(g):
    nodes = g.get("nodes") or g.get("tasks")
    if not nodes:
        raise ValueError("กราฟต้องมี nodes")
    defaults = g.get("defaults", {})
    return [dict(defaults, **n) for n in nodes]


def cmd_run(a):
    default_opts(a)
    apply_simulation(a.simulate_limit)
    if a.resume:
        if not os.path.isfile(os.path.join(run_dir_of(a.resume), "state.json")):
            print("ไม่พบ run %s" % a.resume)
            return 2
        t = Team(a, a.resume, resume=True)
        if a.graph:
            for n in normalize_graph(read_graph(a.graph)):
                if n["id"] in t.g and t.st["nodes"][n["id"]]["status"] != "done":
                    t.g[n["id"]] = n
        for item in a.set or []:
            m = re.fullmatch(r"([^.=]+(?:\.[^.=]+)*?)\.(prompt|expect|account|model|effort|difficulty|timeout|cwd)=(.*)", item, re.S)
            if not m or m.group(1) not in t.g:
                print("--set ไม่ถูกต้อง: %s (รูปแบบ NODE.prompt=ข้อความ)" % item)
                return 2
            v = m.group(3)
            t.g[m.group(1)][m.group(2)] = int(v) if m.group(2) in ("difficulty", "timeout") else v
        t.save_graph()
        for nid in t.order:
            ns = t.st["nodes"][nid]
            if ns["status"] != "done":
                ns.update(status="pending", error=None, acquired=False)
        pending = [n for n in t.order if t.st["nodes"][n]["status"] != "done"]
        t.log("resume %s: รัน %d งาน (%s)" % (t.run_id, len(pending), ",".join(pending)))
    else:
        if not a.graph:
            print("ต้องระบุไฟล์กราฟ หรือ - สำหรับ stdin")
            return 2
        g = read_graph(a.graph)
        nodes = normalize_graph(g)
        for k in ("per_account", "max_total", "timeout"):
            if k in g:
                setattr(a, k, g[k])
        a.goal = g.get("goal", "")
        a.difficulty = g.get("difficulty", a.difficulty)
        t = Team(a, a.run_id)
        t.validate(nodes)
    sides, pinned = set(), set()
    pending_nodes = [t.g[n] for n in t.order if t.st["nodes"][n]["status"] != "done"] if a.resume else nodes
    for n in pending_nodes:
        specs = [t.spec_for(n, x) for x in [n.get("worker"), n.get("reviewer"), n.get("judge")] + (n.get("accounts") or []) if x] or [t.spec_for(n)]
        for s in specs:
            sides |= set(s["sides"] or ["yolo", "cyolo"])
            if s["pinned"]:
                pinned.add(s["selector"])
    if a.resume:
        for n in t.order:
            t.specs[n] = t.spec_for(t.g[n])
            if t.st["nodes"][n]["status"] != "done":
                t.st["nodes"][n]["planned"] = None
    t.preflight(sides, pinned)
    if not a.resume:
        t.add_nodes(nodes)
    else:
        for n in t.order:
            if t.st["nodes"][n]["status"] != "done" and not t.specs[n]["pinned"]:
                p = t._pick(t.specs[n])
                t.st["nodes"][n]["planned"] = p
                if p:
                    t.assigned[p] = t.assigned.get(p, 0) + 1
            elif t.st["nodes"][n]["status"] != "done":
                t.st["nodes"][n]["planned"] = t.specs[n]["selector"]
    t.log("run_id: " + t.run_id)
    t.drive(a.approve_timeout)
    t.st["status"] = t.final_status()
    t.save()
    s = t.summary()
    t.print_summary(s)
    return {"done": 0, "failed": 1, "waiting": 3}[s["status"]]


def cmd_check(a):
    names = (Y.accounts() if a.side != "cyolo" else []) + (C.accounts() if a.side != "yolo" else [])
    rows = Y.parallel(lambda n: (Y if side(n) == "yolo" else C).check(n), names)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print(L.table(["บัญชี", "สถานะ", "เวลา s", "รายละเอียด"], [[r["account"], r["state"], r["duration_s"], r["detail"]] for r in rows]))
    return 0


def cmd_quota(a):
    names = (Y.accounts() if a.side != "cyolo" else []) + (C.accounts() if a.side != "yolo" else [])
    rows = Y.parallel(lambda n: Y.quota(n) if side(n) == "yolo" else C.quota(n, refresh=a.refresh), names)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print(L.table(["บัญชี", "โควตาที่ใช้ไป", "เวลาของข้อมูล"], [[r["account"], r["text"], r["ts"] or "-"] for r in rows]))
    return 0


def cmd_status(a):
    run = a.run or latest_run()
    if not run or not os.path.isfile(os.path.join(run_dir_of(run), "state.json")):
        print("ยังไม่มี run" + (" ชื่อ %s" % a.run if a.run else ""))
        return 0
    with open(os.path.join(run_dir_of(run), "state.json"), encoding="utf-8") as f:
        st = json.load(f)
    leader = (st.get("leader") or {}).get("account")
    tok = {}
    for r in L.calls(L.read(os.path.join(run_dir_of(run), "ledger.jsonl"))):
        if not str(r.get("node", "")).startswith("__"):
            tok[r["account"]] = tok.get(r["account"], 0) + L.tokens_used(r)
    rows = []
    for acct, info in st["accounts"].items():
        run_n = sum(1 for n in st["nodes"].values() if n["status"] == "running" and n.get("acquired") and n.get("account") == acct)
        queue = sum(1 for n in st["nodes"].values() if n["status"] in OPEN and not n.get("acquired") and n.get("planned") == acct)
        q = info.get("quota") or {}
        role = "หัวหน้า" if acct == leader else ("ลูกทีม" if tok.get(acct) or run_n or queue else "-")
        pct = q.get("used_pct")
        if not info.get("ready") and not info.get("stopped"):
            state = "ใช้ไม่ได้ (%s)" % info.get("state")
        elif info.get("stopped"):
            state = "หยุดรับงาน (%s)" % info["stopped"]
        elif pct is not None and pct >= NEAR_PCT:
            state = "ใกล้หมด"
        else:
            state = "พร้อม"
        rows.append([acct, role, run_n, queue, tok.get(acct, 0), "%s (%s)" % (q.get("text", "ไม่มีข้อมูล"), q.get("ts") or "-"), state])
    if a.json:
        print(json.dumps({"run_id": run, "status": st.get("status"), "rows": rows, "leader": st.get("leader")}, ensure_ascii=False, indent=1))
        return 0
    print("run %s · สถานะ %s · หัวหน้า %s" % (run, st.get("status"), leader or "-"))
    print(L.table(["บัญชี", "บทบาท", "งานที่รัน", "งานในคิว", "tokens ใน run", "โควตาล่าสุด (เวลา)", "สถานะ"], rows))
    print("\ntokens ใน run = input ใหม่ + cache write + output (ไม่นับ cache read และการตรวจ/หัวหน้า)")
    return 0


def cmd_stats(a):
    return L.stats_cli(a.run, a.json)


def cmd_approve(a):
    d = run_dir_of(a.run)
    if not os.path.isdir(d):
        print("ไม่พบ run %s" % a.run)
        return 2
    os.makedirs(os.path.join(d, "approve"), exist_ok=True)
    with open(os.path.join(d, "approve", a.node + ".ok"), "w", encoding="utf-8") as f:
        f.write("approved %s\n" % L.now_iso())
    print("อนุมัติ %s/%s แล้ว ถ้า run หยุดอยู่ให้ใช้ run --resume %s" % (a.run, a.node, a.run))
    return 0


def cmd_board(a):
    d = run_dir_of(a.run)
    path = os.path.join(d, "board.md")
    if not os.path.exists(path):
        print("ไม่พบ board ของ run %s" % a.run)
        return 0
    if a.text:
        with open(path, "a", encoding="utf-8") as f:
            f.write("- [%s] **%s**: %s\n" % (L.now_iso(), a.by, a.text.replace("\n", " ")))
    with open(path, encoding="utf-8") as f:
        print(f.read(), end="")
    return 0


def cmd_route(a):
    sides, bound, reason = route(a.prompt, a.task_type or "", a.model or "", "task")
    d = a.difficulty
    print(json.dumps({"sides": sides or ["yolo", "cyolo"], "bound_to_cli": bound, "reason": reason,
                      "claude": Y.DIFFICULTY[d], "codex_effort": C.DIFFICULTY[d]}, ensure_ascii=False))
    return 0


# ---------- หัวหน้าทีม ----------
LEAD_PROMPT = """คุณคือหัวหน้าทีม รอบที่ {ep} ของ run {run} (บัญชี {me})
เป้าหมาย: {goal}

handoff จากรอบก่อน:
{handoff}

สถานะงานปัจจุบัน:
{digest}

ทำหนึ่งช่วงงานแล้วตอบ JSON ล้วน ไม่มี code fence:
{{"dispatch":[{{"id":"t1","prompt":"คำสั่งงานสมบูรณ์ในตัว บอกรูปแบบคำตอบชัดเจน","difficulty":1,"depends_on":[],"expect":"text"}}],
 "merge":{{"sources":["t1"],"output":"final","title":"หัวเรื่อง"}},
 "finish":false,
 "checkpoint":{{"done":"ทำอะไรแล้ว","running":"กำลังรันอะไร","next":"ขั้นต่อไป","decisions":"การตัดสินใจสำคัญ"}}}}
กฎ: สั่งงานใหม่ได้ไม่เกิน {k} งานต่อรอบ · ห้ามใช้ id ซ้ำกับงานที่มีแล้ว ห้ามสั่งซ้ำงานที่มีอยู่ · ไม่มีงานใหม่ให้ dispatch เป็น [] · ตั้ง finish=true และใส่ merge เมื่อทุกงานเสร็จแล้วเท่านั้น · งานล้มให้สั่ง id ใหม่แทน · ต้องมี checkpoint เสมอ{extra}"""


class Lead:
    def __init__(self, team, a, order):
        self.t, self.a, self.order = team, a, order
        self.lead_budget = parse_budget(a.lead_token_budget)
        self.ep = 0
        self.cur = order[0]
        self.stint = 0
        self.down = set()
        self.crash = a.simulate_crash
        self.final = None

    def digest(self):
        t = self.t
        lines = []
        for nid in t.order:
            ns = t.st["nodes"][nid]
            preview = ""
            if ns["status"] == "done" and os.path.exists(t.out(nid)):
                with open(t.out(nid), encoding="utf-8") as f:
                    preview = f.read(120).replace("\n", " ")
            lines.append("- %s | %s | %s | %s" % (nid, ns["status"], ns.get("account") or ns.get("planned") or "-", ns.get("error") or preview))
        return "\n".join(lines) or "(ยังไม่มีงาน)"

    def handoff_text(self):
        with open(self.t.path("handoff.md"), encoding="utf-8") as f:
            return f.read()[-3000:]

    def write_handoff(self, cp, note=""):
        t = self.t
        body = "# handoff run %s\nเป้าหมาย: %s\nอัปเดต: %s โดย %s (รอบ %d)\n\n## ทำแล้ว\n%s\n\n## กำลังรัน\n%s\n\n## ขั้นต่อไป\n%s\n\n## การตัดสินใจสำคัญ\n%s\n" % (
            t.run_id, t.st["goal"], L.now_iso(), self.cur, self.ep, cp.get("done", ""), cp.get("running", ""), cp.get("next", ""), cp.get("decisions", ""))
        if note:
            body += "\n## หมายเหตุจากผู้ควบคุม\n%s\n" % note
        tmp = t.path("handoff.md.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(body)
        os.replace(tmp, t.path("handoff.md"))

    def pick_next(self, exclude):
        t = self.t
        pool = [a for a in self.order if t.is_ready(a) and a not in self.down and a not in exclude]
        if not pool:
            pool = [a for a in self.order if t.is_ready(a) and a not in self.down]
        return pool[0] if pool else None

    def switch(self, kind, reason):
        t = self.t
        frm = self.cur
        self.down.add(frm) if kind == "reactive" else None
        to = self.pick_next({frm})
        ev = {"ts": L.now_iso(), "from": frm, "to": to, "kind": kind, "reason": reason, "episode": self.ep}
        with t.cv:
            t.st["lead_history"].append(ev)
            t.save()
        t.log("สลับหัวหน้า %s → %s (%s: %s)" % (frm, to, kind, reason))
        t.board(frm, "ส่งไม้หัวหน้าให้ %s (%s): %s" % (to, kind, reason), system=True)
        L.event("lead_switch", t.run_id, t.ledger, account=frm, to=to, kind=kind, reason=reason)
        self.cur = to
        self.stint = 0
        return to is not None

    def call_leader(self, prompt, label):
        t = self.t
        model, effort = t.model_for({"difficulty": self.a.lead_difficulty}, self.cur)
        box = {}

        def work():
            if side(self.cur) == "yolo":
                box["r"] = Y.call(self.cur, prompt, model, effort, self.a.episode_timeout, t.dir, None, t.run_id, label, t.ledger)
            else:
                box["r"] = C.call(self.cur, prompt, model, effort, self.a.episode_timeout, t.dir, None, t.run_id, label, t.ledger)
        th = threading.Thread(target=work, daemon=True)
        th.start()
        while th.is_alive():
            t.tick()
            with t.cv:
                t.st["leader"]["heartbeat"] = L.now_iso()
                t.save()
            th.join(1)
        return box["r"]

    def apply(self, reply):
        t, a = self.t, self.a
        note = ""
        tasks = reply.get("dispatch") or []
        if len(tasks) > a.tasks_per_episode:
            note = "ตัดงานเกิน %d ต่อรอบ: %s ให้สั่งใหม่รอบหน้า" % (a.tasks_per_episode, ",".join(str(x.get("id")) for x in tasks[a.tasks_per_episode:]))
            tasks = tasks[:a.tasks_per_episode]
        accepted = []
        for n in tasks:
            if not isinstance(n, dict) or not ID_RE.fullmatch(str(n.get("id", ""))) or n.get("id") in t.g or not n.get("prompt"):
                note += " ข้ามงานไม่ถูกต้อง/ซ้ำ: %s;" % (n.get("id") if isinstance(n, dict) else n)
                continue
            n.setdefault("account", "any")
            n.setdefault("difficulty", a.max_worker_difficulty or 1)
            if a.max_worker_difficulty:
                n["difficulty"] = min(int(n["difficulty"]), a.max_worker_difficulty)
            accepted.append(n)
        if accepted:
            try:
                t.validate(accepted)
            except ValueError as e:
                note += " กราฟไม่ถูกต้อง: %s;" % e
                accepted = []
        if accepted:
            t.add_nodes(accepted)
            t.log("หัวหน้า %s สั่งงาน: %s" % (self.cur, ", ".join(n["id"] for n in accepted)))
        return note

    def merge(self, spec):
        t = self.t
        sources = [s for s in (spec or {}).get("sources", []) if s in t.g and t.st["nodes"][s]["status"] == "done"]
        if not sources:
            sources = [n for n in t.order if t.st["nodes"][n]["status"] == "done"]
        name = re.sub(r"[^A-Za-z0-9_.-]", "", (spec or {}).get("output", "final")).replace(".md", "") or "final"
        parts = ["# " + ((spec or {}).get("title") or t.st["goal"])]
        for s in sources:
            with open(t.out(s), encoding="utf-8") as f:
                parts.append("## %s\n\n%s" % (s, f.read().strip()))
        self.final = t.write(name, "\n\n".join(parts) + "\n")
        t.log("รวมผลเป็นไฟล์เดียว: " + self.final)

    def wait_workers(self):
        t = self.t
        while any(s in ("pending", "running") for s in t.statuses()):
            t.tick()
            with t.cv:
                t.st["leader"]["heartbeat"] = L.now_iso()
                t.cv.wait(0.5)

    def loop(self):
        t, a = self.t, self.a
        extra = "\nรอบแรกต้องสั่งอย่างน้อย 4 งานย่อยแยกกัน (โหมดสาธิต)" if a.demo else ""
        finished = False
        while self.cur and self.ep < a.max_episodes:
            self.ep += 1
            with t.cv:
                t.st["leader"] = {"account": self.cur, "since": L.now_iso(), "episode": self.ep, "heartbeat": L.now_iso()}
                t.save()
            prompt = LEAD_PROMPT.format(ep=self.ep, run=t.run_id, me=self.cur, goal=t.st["goal"], handoff=self.handoff_text(),
                                        digest=self.digest(), k=a.tasks_per_episode, extra=extra if self.ep == 1 else "")
            t.log("หัวหน้า %s เริ่มรอบที่ %d" % (self.cur, self.ep))
            r = self.call_leader(prompt, "__lead_e%d" % self.ep)
            if not r["ok"]:
                if not self.switch("reactive", "%s: %s" % (r["status"], r["error"][:100])):
                    break
                continue
            self.stint += L.tokens_used(r["ledger"])
            try:
                reply = loose_json(r["result"])
                if not isinstance(reply, dict):
                    raise ValueError("ไม่ใช่ object")
            except ValueError as e:
                if not self.switch("reactive", "ตอบผิดรูปแบบ: %s" % str(e)[:80]):
                    break
                continue
            note = self.apply(reply)
            t.pump()
            if self.crash and self.cur == self.crash:
                self.crash = None
                if not self.switch("reactive", "simulate-crash: หัวหน้าหยุดกะทันหันหลังสั่งงาน (ก่อน checkpoint)"):
                    break
                continue
            finish = reply.get("finish") is True
            active = any(s in OPEN for s in t.statuses())
            if finish and active:
                note += " finish ถูกปฏิเสธเพราะยังมีงานค้าง;"
                finish = False
            self.write_handoff(reply.get("checkpoint") or {}, note.strip())
            if finish:
                self.merge(reply.get("merge"))
                finished = True
                break
            budget = self.lead_budget.get(self.cur, self.lead_budget.get("*"))
            used = t.used.get(self.cur, 0) or 0
            if budget is not None and self.stint >= budget:
                reason = "เกินงบโทเค็นหัวหน้า (%d ≥ %d)" % (self.stint, budget)
                if not self.switch("proactive", reason):
                    break
            elif used >= a.quota_stop:
                if not self.switch("proactive", "โควตา %g%% ≥ %g%%" % (used, a.quota_stop)):
                    break
            self.wait_workers()
        if not finished:
            self.wait_workers()
            if t.order:
                self.merge(None)
                t.log("จบโดยผู้ควบคุม: หัวหน้าไม่ได้สั่ง finish (episodes=%d) รวมผลเท่าที่มี" % self.ep)
        return finished


def cmd_lead(a):
    default_opts(a)
    a.difficulty = 1
    if a.demo:
        a.goal = a.goal or "ทำตารางสูตรคูณแม่ 2 ถึง 5 แบ่งแม่ละ 1 งานให้ลูกทีม (แต่ละงานตอบเป็นตาราง 12 บรรทัด รูปแบบ 2 x 1 = 2) แล้วรวมเป็นไฟล์เดียว"
        if a.max_worker_difficulty is None:
            a.max_worker_difficulty = 1
        if a.lead_difficulty is None:
            a.lead_difficulty = 1
        a.per_account = 1
    if a.lead_difficulty is None:
        a.lead_difficulty = 2
    if not a.goal and not a.resume:
        print("ต้องระบุ --goal หรือ --demo")
        return 2
    apply_simulation(a.simulate_limit)
    resume = bool(a.resume)
    if resume and not os.path.isfile(os.path.join(run_dir_of(a.resume), "state.json")):
        print("ไม่พบ run %s" % a.resume)
        return 2
    t = Team(a, a.resume or a.run_id, resume=resume)
    if resume:
        for n in t.order:
            t.specs[n] = t.spec_for(t.g[n])
    exclude = set((a.exclude or "").split(","))
    ready = [x for x in t.preflight({"yolo", "cyolo"}) if x not in exclude]
    if not ready:
        print("ไม่มีบัญชีที่พร้อมเป็นหัวหน้า")
        return 1
    # เรียงผู้สืบทอด: ระบุเองก่อน ไม่งั้นโควตาเหลือมาก ฝั่ง Claude ก่อนข้ามฝั่ง
    order = [x for x in (a.succession or "").split(",") if x in ready] or sorted(ready, key=lambda x: (side(x) != "yolo", t.used.get(x, 0), x))
    if a.lead and a.lead in ready:
        order = [a.lead] + [x for x in order if x != a.lead]
    if a.demo:
        pool = sorted([x for x in ready if side(x) == "yolo"], key=lambda x: (t.used.get(x, 0), x))
        if len(pool) < 2:
            pool = sorted(ready, key=lambda x: (t.used.get(x, 0), x))
        if len(pool) < 2:
            print("โหมดสาธิตต้องมีบัญชีพร้อมอย่างน้อย 2 บัญชี")
            return 1
        t.workers = pool[:2]
        if a.worker_token_budget is None:
            a.worker_token_budget = "%s=1" % pool[0]
            t.worker_budget = parse_budget(a.worker_token_budget)
        if a.simulate_crash is None:
            a.simulate_crash = order[0]
        if a.lead_token_budget is None:
            a.lead_token_budget = "%s=1" % (order[1] if len(order) > 1 else order[0])
        t.log("สาธิต: หัวหน้า %s ล้มกลางคัน · หัวหน้า %s งบ 1 โทเค็น · ลูกทีม %s งบ 1 โทเค็น" % (a.simulate_crash, a.lead_token_budget.split("=")[0], pool[0]))
        with t.cv:
            t.st["budgets"]["worker"] = t.worker_budget
            t.save()
    if not resume:
        with open(t.path("handoff.md"), "w", encoding="utf-8") as f:
            f.write("# handoff run %s\nเป้าหมาย: %s\n\n(ยังไม่มี checkpoint เริ่มรอบแรก)\n" % (t.run_id, t.st["goal"]))
    t.log("run_id: " + t.run_id)
    lead = Lead(t, a, order)
    finished = lead.loop()
    t.st["status"] = "done" if finished and t.final_status() == "done" else "failed"
    t.save()
    s = t.summary(sorted(set(lead.order)))
    s["final_file"] = lead.final
    t.print_summary(s, full=True)
    if not a.json and lead.final:
        print("\nไฟล์รวม: " + lead.final)
    return 0 if t.st["status"] == "done" else 1


def main():
    ap = argparse.ArgumentParser(description="ทีมหลายบัญชี Claude Code + Codex (yolo/cyolo)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", help="ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริง")
    s.add_argument("--side", choices=["yolo", "cyolo"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("quota", help="โควตาล่าสุดทุกบัญชีพร้อมเวลาของข้อมูล")
    s.add_argument("--side", choices=["yolo", "cyolo"])
    s.add_argument("--refresh", action="store_true", help="Codex: เรียกสั้น 1 ครั้งเพื่อให้ข้อมูลใหม่")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_quota)

    s = sub.add_parser("status", help="ตารางภาพรวมบัญชีของ run (ล่าสุดถ้าไม่ระบุ)")
    s.add_argument("run", nargs="?")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("stats", help="สถิติจาก ledger กลาง")
    s.add_argument("--run")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("approve", help="อนุมัติงานที่รอ human gate")
    s.add_argument("run")
    s.add_argument("node")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("board", help="อ่าน/เพิ่มกระดานความรู้")
    s.add_argument("run")
    s.add_argument("--by", default="user")
    s.add_argument("--text")
    s.set_defaults(fn=cmd_board)

    s = sub.add_parser("route", help="ดูผล router โดยไม่เรียกโมเดล")
    s.add_argument("prompt", nargs="?", default="")
    s.add_argument("--task-type")
    s.add_argument("--model")
    s.add_argument("--difficulty", type=int, default=1, choices=range(1, 7))
    s.set_defaults(fn=cmd_route)

    def common(p):
        p.add_argument("--per-account", type=int, help="งานพร้อมกันต่อบัญชี (3)")
        p.add_argument("--max-total", type=int, help="งานพร้อมกันรวม (8)")
        p.add_argument("--timeout", type=int, help="timeout ต่องาน วินาที (600)")
        p.add_argument("--quota-stop", type=float, help="หยุดส่งงานให้บัญชีเมื่อโควตา ≥ %% นี้ (80)")
        p.add_argument("--worker-token-budget", help="งบโทเค็นลูกทีม: N ทุกบัญชี หรือ yolo1=100,cyolo2=50")
        p.add_argument("--workers", help="จำกัดบัญชีลูกทีม เช่น yolo1,yolo2")
        p.add_argument("--simulate-limit", help="จำลองบัญชีโควตาหมด เช่น yolo1 (เหมือน MA_SIMULATE_LIMIT)")
        p.add_argument("--run-id")
        p.add_argument("--json", action="store_true", help="พิมพ์ผลเป็น JSON ความคืบหน้าไป stderr")

    s = sub.add_parser("run", help="รันกราฟงาน")
    s.add_argument("graph", nargs="?", help="ไฟล์ JSON ใน container หรือ - (stdin)")
    s.add_argument("--resume", help="run_id ที่จะรันต่อ (รันเฉพาะงานที่ยังไม่สำเร็จ)")
    s.add_argument("--set", action="append", help="แก้ก่อน resume: NODE.prompt=... หรือ NODE.expect=text")
    s.add_argument("--difficulty", type=int, default=2, help="ความยากเริ่มต้น 1-6 (2)")
    s.add_argument("--approve-timeout", type=int, default=3600, help="รอ human gate กี่วินาที 0=หยุดทันที exit 3")
    common(s)
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("lead", help="ให้หัวหน้าทีมทำเป้าหมายเป็นรอบ ๆ โดยสลับตัวได้")
    s.add_argument("--goal")
    s.add_argument("--demo", action="store_true", help="เปิดตัวจำลองครบชุด: หัวหน้าล้ม สลับเชิงรุก ย้ายงานลูกทีม ใช้กับ --goal ได้")
    s.add_argument("--lead", help="หัวหน้าคนแรก")
    s.add_argument("--succession", help="รายชื่อสืบทอด เช่น yolo1,yolo2,cyolo1")
    s.add_argument("--exclude", help="บัญชีที่ห้ามเป็นหัวหน้า")
    s.add_argument("--lead-token-budget", help="งบโทเค็นหัวหน้าต่อคน: N หรือ yolo1=100")
    s.add_argument("--simulate-crash", help="จำลองหัวหน้าบัญชีนี้ล้มหลังสั่งงาน")
    s.add_argument("--lead-difficulty", type=int, help="ความยากของหัวหน้า (2)")
    s.add_argument("--max-worker-difficulty", type=int, help="จำกัดความยากงานลูกทีม")
    s.add_argument("--tasks-per-episode", type=int, default=4)
    s.add_argument("--episode-timeout", type=int, default=240)
    s.add_argument("--max-episodes", type=int, default=10)
    s.add_argument("--resume", help="รัน lead ต่อจาก run เดิม")
    common(s)
    s.set_defaults(fn=cmd_lead)

    a = ap.parse_args()
    try:
        return a.fn(a)
    except ValueError as e:
        print("ข้อผิดพลาด: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
