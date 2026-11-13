#!/usr/bin/env python3
"""evoskill.py - วงรอบ EvoSkill v2 (Huang, Nama, Alzubi 2026 · arXiv:2610.25931) บนตัวรัน Trial ของ skill-optimizer

  evoskill.py init   <ws> --instruction bench/instruction.md --data bench/data/baankafe --split bench/split.json
                     --grader bench/benchmark_grader.py --solver-prompt bench/solver_prompt.txt
                     --skillopt skill-optimizer/scripts/skillopt.py --accounts yolo1,yolo2
                     [--solver-model sonnet] [--solver-effort medium] [--evolver-model sonnet] [--evolver-effort high]
                     [--adaptor-model sonnet] [--par 6] [--turn-minutes 30] [--fresh-session]
  evoskill.py adapt  <ws>    Benchmark Adaptor: คำสั่งของผู้ใช้ + ข้อมูล + ตัวตรวจ -> plug-in + reference/ แล้วล็อก (hash)
  evoskill.py audit  <ws>    ตรวจว่า reference/ ไม่มีของชุด Validation ชุด Test และตัวตรวจ
  evoskill.py base   <ws>    Solver ทำโจทย์ทุกชุดโดยไม่มีสกิล (epoch 0)
  evoskill.py turn   <ws>    ตาของ Evolver 1 ครั้ง: อ่าน rollout ของ Training -> เขียน skills_vK
  evoskill.py rollout <ws>   Solver ทำโจทย์ด้วย skills_vK (Validation ทุก epoch · Training ทุก epoch ยกเว้น epoch สุดท้าย)
  evoskill.py evolve <ws>    turn + rollout ของ 1 epoch
  evoskill.py test   <ws>    วัดชุดสกิลของ epoch สุดท้ายกับ Test Set (held-out) 1 ครั้ง
  evoskill.py run    <ws> [--stop-after adapt|base|turn|rollout]   ทำทุกขั้นที่เหลือจนจบ (ทำต่อจากขั้นที่ค้าง)
  evoskill.py status <ws>    ตารางสรุปทุก epoch
  evoskill.py noise  <ws>    ความแกว่งของ rollout: โจทย์ที่ผ่านบางครั้ง และผลของประตูรับแบบวัดครั้งเดียว (ไม่ใช้โทเคน)
  evoskill.py eval   <ws> --label L --skills <vK | none | โฟลเดอร์ skills> [--split test] [--model M]

โฟลเดอร์ของ 1 การรัน:
  <ws>/RUN.json state.json     สิ่งที่ผู้ใช้ส่งมา (hash) · ขนาดของการรัน · สถานะ
  <ws>/setup/                  benchmark_plugin.py tasks.json benchmark_grader.py freeze.json (ล็อกหลัง adapt)
  <ws>/reference/              สิ่งที่ Evolver อ่านได้เกี่ยวกับ benchmark (เฉพาะชุด Training)
  <ws>/skills_v1 ... vE/       ชุดสกิลหลังตาที่ K ของ Evolver (เก็บทุกชุด ไม่มีชุดใดถูกปฏิเสธ)
  <ws>/evo/                    "เครื่องของ Evolver" = สิ่งที่ถูก mount เป็น /evo ตอนตาของ Evolver
  <ws>/turns/turn_K/           ข้อความที่ส่ง · transcript · actions.md · stats.json ของตาที่ K
  <ws>/legs/runs/<label>/      ผลของทุก rollout (base_train base_val base_test v1_val v1_train ... vE_test)

Solver รันด้วย run_trial ของ skillopt.py (โจทย์ ตัวตรวจ และพรอมต์ชุดเดียวกับบท 05 และ 06)
Benchmark Adaptor และ Evolver รันใน mount namespace แยก (unshare -m): มองไม่เห็น /workspace
Python 3.8+ stdlib เท่านั้น
"""
import argparse, ast, datetime, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PASS = 0.999                                   # คะแนนตั้งแต่ 0.999 = ผ่าน (เกณฑ์เดียวกับเปเปอร์)
EVO_DIRS = ("traces", "scores", "solver_workspaces", "skills", "reference", "staging", "evolver_workspace")
EVO_RO = ("traces", "scores", "solver_workspaces", "skills", "reference")       # Evolver อ่านได้อย่างเดียว (Table 1)
STD_OK = {"json", "os", "pathlib", "re", "typing", "dataclasses", "collections", "itertools", "functools", "plugin_api"}
SPLIT_SO = {"train": "train", "validation": "val", "test": "test"}             # ชื่อชุดของ skillopt.py
IGN = shutil.ignore_patterns("__pycache__", ".ipynb_checkpoints", "*.pyc")


# ------------------------------------------------------------------ helpers
def P(ws, *a):
    return os.path.join(ws, *a)


def load(ws):
    return json.load(open(P(ws, "state.json"), encoding="utf-8"))


def save(ws, st):
    json.dump(st, open(P(ws, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def read(p, default=""):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return default


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pct(x):
    return "-" if x is None else "%.1f%%" % (x * 100)


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def skillopt(st):
    spec = importlib.util.spec_from_file_location("skillopt", st["cfg"]["skillopt"])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def skill_names(d):
    return sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "SKILL.md"))) if os.path.isdir(d) else []


def tree(d):
    out = []
    for root, dirs, files in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for f in sorted(files):
            out.append(os.path.relpath(os.path.join(root, f), d).replace(os.sep, "/"))
    return out


def tasks_of(ws):
    return json.load(open(P(ws, "setup", "tasks.json"), encoding="utf-8"))


# ------------------------------------------------------------------ การแยกเครื่อง (orchestration-level isolation)
NS_SCRIPT = r'''
set -e
CWD="$1"; shift
NB="$1"; shift
i=0
while [ "$i" -lt "$NB" ]; do
  SRC="$1"; DST="$2"; MODE="$3"; shift 3
  mkdir -p "$DST"
  mount --bind "$SRC" "$DST"
  if [ "$MODE" = "ro" ]; then mount -o remount,bind,ro "$DST"; fi
  i=$((i+1))
done
mount -t tmpfs tmpfs /workspace
cd "$CWD"
exec "$@"
'''


def agent(st, role, binds, cwd, system, user, out_path, model, effort, session=None, resume=False, timeout=1800):
    """เรียก Claude Code 1 เซสชันใน mount namespace แยก: เห็นเฉพาะโฟลเดอร์ใน binds · /workspace ถูกแทนด้วยโฟลเดอร์ว่าง
    binds = [(โฟลเดอร์จริง, path ที่ Agent เห็น, "rw"|"ro"), ...] · session=None -> ไม่เก็บเซสชัน (ใช้ครั้งเดียว)"""
    cfg = st["cfg"]
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("CLAUDE") or key.startswith("MA_"):
            env.pop(key)
    acc = cfg["accounts"][0]
    home = os.path.join(os.environ.get("EVOSKILL_ACCOUNT_ROOT", os.path.expanduser("~/ai-accounts/.Claude")), acc)
    env.update(CLAUDE_CONFIG_DIR=home, IS_SANDBOX="1")
    cmd = ["claude", "--dangerously-skip-permissions", "--disable-slash-commands", "-p",
           "--append-system-prompt", system, "--model", model, "--effort", effort,
           "--disallowedTools", "WebSearch,WebFetch", "--output-format", "stream-json", "--verbose", "--strict-mcp-config"]
    if session is None:
        cmd.append("--no-session-persistence")
    else:
        cmd += ["--resume", session] if resume else ["--session-id", session]
    flat = []
    for src, dst, mode in binds:
        flat += [os.path.abspath(src), dst, mode]
    full = ["unshare", "-m", "--propagation", "private", "bash", "-c", NS_SCRIPT, "ns", cwd, str(len(binds))] + flat + cmd
    t0, timed_out = time.time(), False
    with open(out_path, "wb") as out, open(out_path + ".stderr", "wb") as err:
        p = subprocess.Popen(full, env=env, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True)
        try:
            p.communicate(user.encode("utf-8"), timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(p.pid, 9)
            except OSError:
                pass
            p.wait()
    m = skillopt(st).parse_transcript(out_path)
    m.update(wall_s=round(time.time() - t0, 1), timed_out=timed_out, role=role)
    return m


def evo_binds(ws):
    b = [(P(ws, "evo"), "/evo", "rw")]
    return b + [(P(ws, "evo", d), "/evo/" + d, "ro") for d in EVO_RO]


# ------------------------------------------------------------------ transcript ของ Agent -> สถิติ + บันทึกที่อ่านได้
AREAS = ("traces", "solver_workspaces", "reference", "scores", "skills", "staging", "evolver_workspace")


def clip(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "\n…(ตัด %d ตัวอักษร)" % (len(s) - n)


def tool_text(name, inp):
    if name == "Bash":
        return inp.get("command", "")
    if name in ("Write", "Edit"):
        return "%s\n%s" % (inp.get("file_path", ""), inp.get("content") or inp.get("new_string") or "")
    if name in ("Read", "Glob", "Grep"):
        return " ".join(str(inp.get(k)) for k in ("file_path", "pattern", "path") if inp.get(k))
    return json.dumps(inp, ensure_ascii=False)


def turn_stats(path, pre_scripts=()):
    """อ่าน transcript (stream-json) ของ 1 ตา -> (สถิติ, ข้อความ actions.md)"""
    tools, bash, results, steps = {}, [], {}, []
    compact, sub, final, res = 0, 0, "", None
    areas = {a: 0 for a in AREAS}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        t = m.get("type")
        if t == "system" and "compact" in str(m.get("subtype", "")):
            compact += 1
        if t == "result":
            res = m
            final = m.get("result") or final
        inner = bool(m.get("parent_tool_use_id"))                # ข้อความของ subagent
        for c in (m.get("message") or {}).get("content", []) if t in ("assistant", "user") else []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text" and t == "assistant" and c.get("text", "").strip():
                steps.append(("say", c["text"].strip(), inner))
            elif c.get("type") == "tool_use":
                name, inp = c["name"], c.get("input") or {}
                tools[name] = tools.get(name, 0) + 1
                txt = tool_text(name, inp)
                if name == "Bash":
                    bash.append(txt)
                if name in ("Task", "Agent"):
                    sub += 1
                for a in AREAS:
                    if "/evo/%s" % a in txt:
                        areas[a] += 1
                steps.append(("tool", name, (c.get("id"), txt, inner)))
            elif c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list):
                    body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                results[c.get("tool_use_id")] = ("ERROR " if c.get("is_error") else "") + (body or "")
    rerun = sum(1 for b in bash if any(os.path.basename(s) in b for s in pre_scripts))
    u = (res or {}).get("usage") or {}
    st = {"ok": bool(res) and not res.get("is_error"), "tool_calls": sum(tools.values()), "tools": tools,
          "bash": len(bash), "bash_python": sum(1 for b in bash if re.search(r"\bpython3?\b", b)),
          "rerun_old_scripts": rerun, "subagents": sub, "compactions": compact, "touch": areas,
          "num_turns": (res or {}).get("num_turns"), "cost_usd": round((res or {}).get("total_cost_usd") or 0, 4),
          "output_tokens": u.get("output_tokens") or 0,
          "context_tokens": (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)}
    L, n = [], 0
    for kind, a, b in steps:
        if kind == "say":
            L += ["**%s:** %s" % ("subagent พูด" if b else "Agent พูด", clip(a, 1500)), ""]
        else:
            n += 1
            L += ["### ขั้น %d · %s%s" % (n, a, " (subagent)" if b[2] else ""), "", "```", clip(b[1], 2500), "```", "",
                  "ผลที่ได้:", "", "```", clip(results.get(b[0], "(ไม่มีผล)"), 1200), "```", ""]
    if not (steps and steps[-1][0] == "say" and steps[-1][1].strip() == final.strip()):
        L += ["## คำตอบสุดท้าย", "", clip(final, 4000), ""]
    return st, "\n".join(L)


# ------------------------------------------------------------------ Solver (rollouts)
def leg_stats(rows):
    by = {}
    for r in sorted(rows, key=lambda r: (r["task"], r["rep"])):
        by.setdefault(r["task"], []).append(r["score"])
    ok = {t: [s >= PASS for s in v] for t, v in by.items()}
    return {"n": len(rows), "tasks": len(by), "score": mean(r["score"] for r in rows),
            "passes": sum(sum(v) for v in ok.values()), "pass3": sum(1 for v in ok.values() if any(v)),
            "all3": sum(1 for v in ok.values() if all(v)), "none3": sum(1 for v in ok.values() if not any(v)),
            "mixed": sum(1 for v in ok.values() if any(v) and not all(v)), "by_task": by,
            "cost_usd": round(sum(r.get("cost_usd", 0) for r in rows), 3),
            "context_tokens": round(mean(r.get("input_tokens", 0) + r.get("cache_read", 0) + r.get("cache_write", 0) for r in rows)),
            "tool_calls": round(mean(r.get("tool_calls", 0) for r in rows), 2),
            "skill_read": sum(1 for r in rows if r.get("skill_read")),
            "grader_failed": sum(1 for r in rows if r["checks"] and r["checks"][0].get("id") == "grader")}


def verify(ws):
    """ก่อนใช้ตัวตรวจและรายการโจทย์ทุกครั้ง: ต้องตรงกับที่ล็อกไว้หลัง adapt"""
    fz = json.load(open(P(ws, "setup", "freeze.json"), encoding="utf-8"))
    for f, h in fz["sha256"].items():
        if sha(P(ws, "setup", f)) != h:
            print("หยุด: %s ถูกแก้หลังจากล็อก (hash ไม่ตรงกับ setup/freeze.json)" % f)
            sys.exit(1)


def rollouts(ws, st, label, split, skills_src, model=None):
    """Solver ทำโจทย์ของชุดนั้นทุกข้อ x N ครั้ง ด้วยชุดสกิลใน skills_src (None หรือโฟลเดอร์ว่าง = ไม่มีสกิล)
    Solver เห็นเฉพาะ ./skills ใน sandbox ของตัวเอง · ตัวตรวจของผู้ใช้ให้คะแนนจากโฟลเดอร์ทำงานตอนจบ"""
    verify(ws)
    so, cfg = skillopt(st), st["cfg"]
    suite_dir = P(ws, "legs")
    os.makedirs(suite_dir, exist_ok=True)
    suite = {"name": cfg["name"], "skill_name": "-", "timeout": 600, "grader": "../setup/benchmark_grader.py",
             "prompt": cfg["solver_prompt"]}
    if skills_src and skill_names(skills_src):
        sk = P(ws, "tmp", label, "skills")
        shutil.rmtree(os.path.dirname(sk), ignore_errors=True)
        shutil.copytree(skills_src, sk, ignore=IGN)
        suite["files"] = [sk]
    tasks = [{"id": t["id"], "split": SPLIT_SO[t["split"]], "brief": t["instruction"], "grading": t.get("grading") or {}}
             for t in tasks_of(ws) if split == "all" or t["split"] == split]
    a = argparse.Namespace(label=label, skill="none", model=model or cfg["solver_model"], effort=cfg["solver_effort"])
    jobs = []
    for r in range(1, st["n"] + 1):
        for t in tasks:
            d = os.path.join(suite_dir, "runs", label, "%s-r%d" % (t["id"], r))
            if not (os.path.isfile(os.path.join(d, "grade.json")) and os.path.isfile(os.path.join(d, "metrics.json"))):
                jobs.append((t, r))                        # rollout ที่เสร็จแล้วไม่รันซ้ำ (รันต่อจากที่ค้างได้)
    lock, loadn = threading.Lock(), {x: 0 for x in cfg["accounts"]}

    def one(j):
        with lock:
            acc = min(loadn, key=loadn.get)
            loadn[acc] += 1
        try:
            return so.run_trial(suite_dir, suite, j[0], j[1], a, acc)
        finally:
            with lock:
                loadn[acc] -= 1
    with ThreadPoolExecutor(cfg["par"]) as ex:
        list(ex.map(one, jobs))
    rows = so.collect(suite_dir, label)
    s = leg_stats(rows)
    s.update(label=label, split=split, skills=skill_names(skills_src) if skills_src else [], model=a.model)
    st.setdefault("legs", {})[label] = s
    write(P(ws, "legs", label + ".json"), json.dumps(s, ensure_ascii=False, indent=1))
    print("  leg %-11s %-10s คะแนน %s · ผ่าน %d/%d rollout · โจทย์ที่ผ่านทั้ง %d ครั้ง %d/%d" % (
        label, split, pct(s["score"]), s["passes"], s["n"], st["n"], s["all3"], s["tasks"]))
    return rows


# ------------------------------------------------------------------ init
def cmd_init(a):
    ws = a.ws
    if os.path.exists(P(ws, "state.json")):
        print("มีการรันชื่อนี้อยู่แล้ว: %s (ใช้ชื่อใหม่ หรือลบโฟลเดอร์ก่อนถ้าต้องการเริ่มใหม่)" % ws)
        return 1
    ins = read(a.instruction)
    m = re.search(r"(\d+)\s*epochs?\s*[·x,]\s*(\d+)\s*samples?\s*per\s*task", ins)
    if not m:
        print("หยุด: คำสั่งของผู้ใช้ไม่ได้ระบุขนาดของการรัน (ต้องมีบรรทัดแบบ `3 epochs · 3 samples per task`)")
        return 1
    os.makedirs(P(ws, "inputs"), exist_ok=True)
    shutil.copy(a.instruction, P(ws, "inputs", "instruction.md"))
    shutil.copy(a.split, P(ws, "inputs", "split.json"))
    shutil.copy(a.grader, P(ws, "inputs", "benchmark_grader.py"))
    run = {"instruction": {"file": os.path.abspath(a.instruction), "sha256": sha(a.instruction)},
           "split": {"file": os.path.abspath(a.split), "sha256": sha(a.split)},
           "grader": {"file": os.path.abspath(a.grader), "sha256": sha(a.grader)},
           "data": {"dir": os.path.abspath(a.data), "files": len(tree(a.data))},
           "run_size": {"epochs": int(m.group(1)), "samples_per_task": int(m.group(2))}}
    write(P(ws, "RUN.json"), json.dumps(run, ensure_ascii=False, indent=1))
    st = {"cfg": {"name": os.path.basename(os.path.normpath(ws)), "data": os.path.abspath(a.data),
                  "skillopt": os.path.abspath(a.skillopt), "accounts": a.accounts.split(","), "par": a.par,
                  "solver_prompt": read(a.solver_prompt), "solver_model": a.solver_model, "solver_effort": a.solver_effort,
                  "evolver_model": a.evolver_model, "evolver_effort": a.evolver_effort, "adaptor_model": a.adaptor_model,
                  "turn_minutes": a.turn_minutes, "fresh_session": bool(a.fresh_session)},
          "epochs": int(m.group(1)), "n": int(m.group(2)), "phase": "init", "k": 0, "session_id": None,
          "legs": {}, "turns": []}
    save(ws, st)
    print("สร้างการรัน %s · %d epochs · %d samples per task · Solver %s/%s · Evolver %s/%s%s" % (
        st["cfg"]["name"], st["epochs"], st["n"], a.solver_model, a.solver_effort, a.evolver_model, a.evolver_effort,
        " · เซสชันใหม่ทุก epoch (--fresh-session)" if a.fresh_session else " · เซสชันเดียวตลอดการรัน"))
    return 0


def need(st, phase, cmd):
    if st["phase"] != phase:
        print("ยังรัน %s ไม่ได้: ขั้นถัดไปคือ `%s` (ตอนนี้ phase=%s epoch=%d)" % (cmd, next_step(st), st["phase"], st["k"]))
        sys.exit(1)


def next_step(st):
    ph = st["phase"]
    if ph == "init":
        return "adapt"
    if ph == "adapt":
        return "base"
    if ph == "base":
        return "turn"
    if ph == "turn":
        return "rollout"
    if ph == "rollout":
        return "turn" if st["k"] < st["epochs"] else "test"
    return "done"


# ------------------------------------------------------------------ adapt (Benchmark Adaptor) + freeze + audit
def plugin_imports(path):
    bad = []
    for node in ast.walk(ast.parse(read(path))):
        names = [n.name for n in node.names] if isinstance(node, ast.Import) else \
            [node.module or ""] if isinstance(node, ast.ImportFrom) else []
        bad += [n for n in names if n.split(".")[0] not in STD_OK]
    return sorted(set(bad))


def audit(ws):
    """ตรวจ reference/ : ต้องไม่มีสิ่งใดของชุด Validation ชุด Test และตัวตรวจ -> (ผ่านหรือไม่, รายงาน)"""
    tasks, data = tasks_of(ws), load(ws)["cfg"]["data"]
    held = [t for t in tasks if t["split"] != "train"]
    words = {}
    for t in held:
        words[t["id"]] = t["id"]
        words[t["instruction"][:60]] = "ข้อความโจทย์ของ " + t["id"]
        tf = os.path.join(data, "tasks", t["id"] + ".json")
        fn = (json.load(open(tf, encoding="utf-8")) if os.path.isfile(tf) else {}).get("function")
        if fn:
            words[fn] = "ชื่อฟังก์ชันของ " + t["id"]
    files = tree(P(ws, "reference"))
    train_text = "\n".join(read(P(ws, "reference", f)) for f in files)
    glines = {l.strip() for l in read(P(ws, "setup", "benchmark_grader.py")).splitlines() if len(l.strip()) >= 40}
    dlines = set()
    for f in tree(data):
        dlines |= {l.strip() for l in read(os.path.join(data, f)).splitlines()}
    glines -= dlines                                    # บรรทัดที่อยู่ในข้อมูลของผู้ใช้อยู่แล้ว ไม่นับเป็นของตัวตรวจ
    leaks = []
    for f in files:
        txt = f + "\n" + read(P(ws, "reference", f))
        for w, what in words.items():
            if w in txt:
                leaks.append("%s มี %s" % (f, what))
        if os.path.basename(f) == "benchmark_grader.py" or any(l in txt for l in glines):
            leaks.append("%s มีโค้ดของตัวตรวจ" % f)
    ans = [f for f in files if "/answers/" in "/" + f or f.startswith("answers/")]
    rep = ["| รายการ | ผล |", "|---|---|", "| ไฟล์ใน reference/ | %d ไฟล์ |" % len(files),
           "| มีเฉลยอ้างอิงของชุด Training | %s |" % ("ใช่ %d ไฟล์" % len(ans) if ans else "ไม่มี"),
           "| ของชุด Validation หรือ Test | %s |" % ("พบ" if any("ตัวตรวจ" not in x for x in leaks) else "ไม่พบ"),
           "| โค้ดของตัวตรวจ | %s |" % ("พบ" if any("ตัวตรวจ" in x for x in leaks) else "ไม่พบ")]
    rep += ["", "ไฟล์ทั้งหมด:"] + ["- reference/" + f for f in files]
    if leaks:
        rep += ["", "สิ่งที่รั่ว:"] + ["- " + x for x in sorted(set(leaks))]
    return not leaks, "\n".join(rep), {"files": len(files), "answers": len(ans), "leaks": sorted(set(leaks))}


def cmd_audit(a):
    ok, rep, _ = audit(a.ws)
    print(rep + "\n\nผล: %s" % ("reference/ สะอาด ✅" if ok else "reference/ มีสิ่งที่ Evolver ห้ามเห็น ❌"))
    return 0 if ok else 1


def cmd_adapt(a):
    ws, st = a.ws, load(a.ws)
    need(st, "init", "adapt")
    cfg, ad = st["cfg"], P(ws, "adapt")
    shutil.rmtree(ad, ignore_errors=True)
    for d in ("setup", "reference", "work", "data"):
        os.makedirs(os.path.join(ad, d))
    for f in ("plugin_api.py", "plugin_skeleton.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(ad, "setup", f))
    shutil.copy(P(ws, "inputs", "benchmark_grader.py"), os.path.join(ad, "setup"))
    root_name = os.path.basename(os.path.normpath(cfg["data"]))
    shutil.copytree(cfg["data"], os.path.join(ad, "data", root_name), ignore=IGN)
    shutil.copy(P(ws, "inputs", "split.json"), os.path.join(ad, "data", "split.json"))
    system = read(os.path.join(HERE, "prompts", "adaptor.md")).replace("{setup_dir}", "/ba/setup").replace("{reference_dir}", "/ba/reference")
    user = read(P(ws, "inputs", "instruction.md"))
    td = P(ws, "turns", "adaptor")
    os.makedirs(td, exist_ok=True)
    write(os.path.join(td, "system_append.md"), system)
    write(os.path.join(td, "message.md"), user)
    print("Benchmark Adaptor กำลังทำงาน (1 เซสชัน · เห็น /data /ba/setup /ba/reference เท่านั้น) ...")
    m = agent(st, "adaptor", [(ad, "/ba", "rw"), (os.path.join(ad, "data"), "/data", "ro")], "/ba/work", system, user,
              os.path.join(td, "transcript.jsonl"), cfg["adaptor_model"], "high")
    stats, actions = turn_stats(os.path.join(td, "transcript.jsonl"))
    write(os.path.join(td, "actions.md"), "# Benchmark Adaptor\n\n" + actions)
    stats["wall_s"] = m["wall_s"]
    write(os.path.join(td, "stats.json"), json.dumps(stats, ensure_ascii=False, indent=1))
    plug = os.path.join(ad, "setup", "benchmark_plugin.py")
    if not m["ok"] or not os.path.isfile(plug):
        print("หยุด: Benchmark Adaptor ไม่ได้เขียน benchmark_plugin.py (%s)" % (m.get("result") or "ไม่มีคำตอบ")[:300])
        return 1
    # ---- freeze: นำ plug-in มาเก็บ รันให้ได้รายการโจทย์ แล้วล็อกด้วย hash
    shutil.rmtree(P(ws, "setup"), ignore_errors=True)
    os.makedirs(P(ws, "setup"))
    shutil.copy(plug, P(ws, "setup"))
    shutil.copy(os.path.join(HERE, "plugin_api.py"), P(ws, "setup"))
    shutil.copy(P(ws, "inputs", "benchmark_grader.py"), P(ws, "setup"))       # ตัวตรวจ = ไฟล์ของผู้ใช้ ไม่ใช่สำเนาที่ BA แตะได้
    bad = plugin_imports(plug)
    if bad:
        print("หยุด: plug-in import สิ่งที่ไม่อนุญาต: %s" % ", ".join(bad))
        return 1
    code = ("import json, sys; sys.path.insert(0, %r); import benchmark_plugin as p; "
            "print(json.dumps([t.to_dict() for t in p.list_tasks(%r)], ensure_ascii=False))") % (
        P(ws, "setup"), os.path.join(ad, "data", root_name))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", timeout=120)
    try:
        tasks = json.loads(r.stdout)
    except ValueError:
        print("หยุด: รัน list_tasks() ของ plug-in ไม่ได้: %s" % (r.stderr or r.stdout)[-400:])
        return 1
    want = json.load(open(P(ws, "inputs", "split.json"), encoding="utf-8"))
    got = {s: sorted(t["id"] for t in tasks if t["split"] == s) for s in ("train", "validation", "test")}
    if len({t["id"] for t in tasks}) != len(tasks) or got != {s: sorted(want.get(s, [])) for s in got}:
        print("หยุด: การแบ่งชุดของ plug-in ไม่ตรงกับ split.json ของผู้ใช้\n  plug-in: %s\n  ผู้ใช้:  %s" % (got, want))
        return 1
    write(P(ws, "setup", "tasks.json"), json.dumps(tasks, ensure_ascii=False, indent=1))
    shutil.rmtree(P(ws, "reference"), ignore_errors=True)
    shutil.copytree(os.path.join(ad, "reference"), P(ws, "reference"), ignore=IGN)
    fz = {"frozen_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
          "sha256": {f: sha(P(ws, "setup", f)) for f in ("benchmark_plugin.py", "benchmark_grader.py", "tasks.json")},
          "grader_unchanged_by_adaptor": sha(os.path.join(ad, "setup", "benchmark_grader.py")) == sha(P(ws, "inputs", "benchmark_grader.py")),
          "tasks": {s: got[s] for s in got}}
    write(P(ws, "setup", "freeze.json"), json.dumps(fz, ensure_ascii=False, indent=1))
    ok, rep, info = audit(ws)
    write(P(ws, "setup", "audit.md"), rep + "\n")
    st["adapt"] = dict(stats, tasks={s: len(v) for s, v in got.items()}, reference=info, audit_ok=ok)
    print("\nBenchmark Adaptor: %.0f วินาที · เครื่องมือ %d ครั้ง · $%.2f" % (m["wall_s"], stats["tool_calls"], stats["cost_usd"]))
    print("plug-in: train %d · validation %d · test %d โจทย์ -> setup/tasks.json (ล็อกด้วย sha256 ใน setup/freeze.json)" % (
        len(got["train"]), len(got["validation"]), len(got["test"])))
    print("\n" + rep)
    if not ok:
        save(ws, st)
        print("\nหยุด: reference/ มีสิ่งที่ Evolver ห้ามเห็น ❌ (แก้คำสั่งของผู้ใช้แล้วเริ่มการรันชื่อใหม่)")
        return 1
    st["phase"] = "adapt"
    save(ws, st)
    print("\nผล: reference/ สะอาด ✅ · ขั้นถัดไป: base")
    return 0


# ------------------------------------------------------------------ base / turn / rollout / test
def cmd_base(a):
    ws, st = a.ws, load(a.ws)
    need(st, "adapt", "base")
    print("[epoch 0] Solver ทำโจทย์ทุกชุดโดยไม่มีสกิล · โจทย์ละ %d ครั้ง" % st["n"])
    for sp, lb in (("train", "base_train"), ("validation", "base_val"), ("test", "base_test")):
        rollouts(ws, st, lb, sp, None)
        save(ws, st)
    st["phase"] = "base"
    save(ws, st)
    return 0


def sync_evo(ws, st, k):
    """ส่งผลของชุด Training ของ epoch k ไปไว้ใน "เครื่องของ Evolver" (ชุด Validation และ Test ไม่ถูกส่งไปเลย)"""
    so = skillopt(st)
    label = "base_train" if k == 0 else "v%d_train" % k
    ev = P(ws, "evo")
    for d in EVO_DIRS:
        os.makedirs(os.path.join(ev, d), exist_ok=True)
    if not os.listdir(os.path.join(ev, "reference")):
        shutil.rmtree(os.path.join(ev, "reference"))
        shutil.copytree(P(ws, "reference"), os.path.join(ev, "reference"), ignore=IGN)
    scores = {}
    for r in so.collect(P(ws, "legs"), label):
        if r["split"] != "train":
            continue
        name = "%s_s%d" % (r["task"], r["rep"])
        os.makedirs(os.path.join(ev, "traces", "epoch_%d" % k), exist_ok=True)
        shutil.copy(os.path.join(r["dir"], "transcript.jsonl"), os.path.join(ev, "traces", "epoch_%d" % k, name + ".jsonl"))
        dst = os.path.join(ev, "solver_workspaces", "epoch_%d" % k, name)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(os.path.join(r["dir"], "sandbox"), dst, ignore=shutil.ignore_patterns("__pycache__", "skills", "*.pyc"))
        scores[name] = "grader_failed" if (r["checks"] and r["checks"][0].get("id") == "grader") else r["score"]
    write(os.path.join(ev, "scores", "epoch_%d.json" % k), json.dumps(scores, ensure_ascii=False, indent=1))
    sk = os.path.join(ev, "skills", "epoch_%d" % k)
    shutil.rmtree(sk, ignore_errors=True)
    if k == 0:
        os.makedirs(sk)
    else:
        shutil.copytree(P(ws, "skills_v%d" % k), sk, ignore=IGN)
    return len(scores)


def skill_info(d):
    names = skill_names(d)
    files = tree(d) if os.path.isdir(d) else []
    info = {"skills": names, "skill_md_bytes": sum(os.path.getsize(os.path.join(d, n, "SKILL.md")) for n in names),
            "other_files": [f for f in files if not f.endswith("/SKILL.md")], "descriptions": {}, "problems": []}
    for n in names:
        m = re.match(r"---\n(.*?)\n---", read(os.path.join(d, n, "SKILL.md")), re.S)
        dm = re.search(r"^description:\s*(.*)$", m.group(1), re.M) if m else None
        if not dm:
            info["problems"].append("%s: ไม่มี description ใน frontmatter" % n)
        info["descriptions"][n] = dm.group(1).strip() if dm else ""
    return info


def cmd_turn(a):
    ws, st = a.ws, load(a.ws)
    if st["phase"] not in ("base", "rollout") or (st["phase"] == "rollout" and st["k"] >= st["epochs"]):
        need(st, "base", "turn")
    cfg, k = st["cfg"], st["k"] + 1
    n = sync_evo(ws, st, k - 1)
    ev, td = P(ws, "evo"), P(ws, "turns", "turn_%d" % k)
    os.makedirs(td, exist_ok=True)
    pre = [f for f in tree(os.path.join(ev, "evolver_workspace")) if f.endswith((".py", ".sh"))]
    before = {f: sha(os.path.join(ev, "staging", f)) for f in tree(os.path.join(ev, "staging"))}
    now = datetime.datetime.now(datetime.timezone.utc)
    system = read(os.path.join(HERE, "prompts", "evolver_system.md")).replace("{n}", str(st["n"]))
    user = read(os.path.join(HERE, "prompts", "evolver_message.md")).strip().format(
        now=now.strftime("%Y-%m-%d %H:%M"), deadline=(now + datetime.timedelta(minutes=cfg["turn_minutes"])).strftime("%Y-%m-%d %H:%M"), k=k)
    write(os.path.join(td, "message.md"), user + "\n")
    write(P(ws, "turns", "evolver_system_append.md"), system)
    fresh = cfg["fresh_session"] or not st.get("session_id")
    if fresh:
        st["session_id"] = str(uuid.uuid4())
    print("[epoch %d] ตาของ Evolver: ได้รับ rollout ของ Training %d ครั้ง (epoch %d) · %s ..." % (
        k, n, k - 1, "เริ่มเซสชันใหม่" if fresh else "ทำต่อในเซสชันเดิม (--resume)"))
    tp = os.path.join(td, "transcript.jsonl")
    m = agent(st, "evolver", evo_binds(ws), "/evo", system, user, tp, cfg["evolver_model"], cfg["evolver_effort"],
              session=st["session_id"], resume=not fresh, timeout=cfg["turn_minutes"] * 60 + 60)
    stats, actions = turn_stats(tp, pre)
    total = stats["cost_usd"]                       # total_cost_usd ของ Claude Code = ยอดสะสมของทั้งเซสชัน
    prev = 0.0 if fresh else st.get("session_cost", 0.0)
    stats["cost_usd"], stats["session_cost_usd"] = round(max(0.0, total - prev), 4), total
    if stats["ok"] or m["timed_out"]:
        st["session_cost"] = total
    write(os.path.join(td, "actions.md"), "# ตาที่ %d ของ Evolver\n\nข้อความที่ได้รับ: %s\n\n" % (k, user) + actions)
    if not stats["ok"] and not m["timed_out"]:
        save(ws, st)
        print("หยุด: เซสชันของ Evolver จบไม่ปกติ: %s\n(รัน `turn` อีกครั้งเพื่อทำตานี้ใหม่)" % (m.get("result") or read(tp + ".stderr"))[-400:])
        return 1
    # ---- สิ่งที่อยู่ใน staging เมื่อจบตา = skills_vK (รับทุกชุด ไม่มีการปฏิเสธ)
    sv = P(ws, "skills_v%d" % k)
    shutil.rmtree(sv, ignore_errors=True)
    shutil.copytree(os.path.join(ev, "staging"), sv, ignore=IGN)
    after = {f: sha(os.path.join(sv, f)) for f in tree(sv)}
    info = skill_info(sv)
    stats.update(k=k, wall_s=m["wall_s"], timed_out=m["timed_out"], fresh_session=fresh, session_id=st["session_id"],
                 rollouts_given=n, old_scripts=len(pre), skills=info["skills"], skill_md_bytes=info["skill_md_bytes"],
                 skill_other_files=info["other_files"], skill_problems=info["problems"],
                 files_added=sorted(set(after) - set(before)), files_removed=sorted(set(before) - set(after)),
                 files_changed=sorted(f for f in after if f in before and after[f] != before[f]),
                 workspace_files=tree(os.path.join(ev, "evolver_workspace")))
    write(os.path.join(td, "stats.json"), json.dumps(stats, ensure_ascii=False, indent=1))
    st["turns"].append(stats)
    st["k"], st["phase"] = k, "turn"
    save(ws, st)
    print("[epoch %d] Evolver: %.0f วินาที · เครื่องมือ %d ครั้ง (Bash %d · รัน Python %d · รันสคริปต์เดิมซ้ำ %d · subagent %d) · ย่อบริบท %d ครั้ง · $%.2f" % (
        k, m["wall_s"], stats["tool_calls"], stats["bash"], stats["bash_python"], stats["rerun_old_scripts"],
        stats["subagents"], stats["compactions"], stats["cost_usd"]))
    print("   skills_v%d: %s · SKILL.md รวม %.1f KB · ไฟล์อื่น %d · เพิ่ม %d แก้ %d ลบ %d ไฟล์" % (
        k, ", ".join(info["skills"]) or "(ว่าง)", info["skill_md_bytes"] / 1024, len(info["other_files"]),
        len(stats["files_added"]), len(stats["files_changed"]), len(stats["files_removed"])))
    for p in info["problems"]:
        print("   ! " + p)
    return 0


def cmd_rollout(a):
    ws, st = a.ws, load(a.ws)
    need(st, "turn", "rollout")
    k = st["k"]
    last = k >= st["epochs"]
    print("[epoch %d] Solver ทำโจทย์ด้วย skills_v%d%s" % (k, k, " (epoch สุดท้าย: วัดเฉพาะ Validation)" if last else ""))
    rollouts(ws, st, "v%d_val" % k, "validation", P(ws, "skills_v%d" % k))
    save(ws, st)
    if not last:
        rollouts(ws, st, "v%d_train" % k, "train", P(ws, "skills_v%d" % k))
    st["phase"] = "rollout"
    save(ws, st)
    return 0


def cmd_evolve(a):
    return cmd_turn(a) or cmd_rollout(a)


def cmd_test(a):
    ws, st = a.ws, load(a.ws)
    if st["phase"] != "rollout" or st["k"] < st["epochs"]:
        need(st, "-", "test")
    k = st["k"]
    print("[test] วัด skills_v%d (ชุดของ epoch สุดท้าย) กับ Test Set 1 ครั้ง" % k)
    rollouts(ws, st, "v%d_test" % k, "test", P(ws, "skills_v%d" % k))
    st["phase"] = "test"
    save(ws, st)
    return 0


def cmd_run(a):
    steps = {"adapt": cmd_adapt, "base": cmd_base, "turn": cmd_turn, "rollout": cmd_rollout, "test": cmd_test}
    while True:
        st = load(a.ws)
        nx = next_step(st)
        if nx == "done":
            break
        rc = steps[nx](a)
        if rc:
            return rc
        if a.stop_after == nx:
            print("\nหยุดตาม --stop-after %s" % nx)
            break
    return cmd_status(a)


# ------------------------------------------------------------------ status / noise / eval
def cmd_status(a):
    st = load(a.ws)
    cfg, L, T = st["cfg"], st.get("legs", {}), st.get("turns", [])
    print("\nการรัน %s · %d epochs · %d samples per task · Solver %s/%s · Evolver %s/%s · %s" % (
        cfg["name"], st["epochs"], st["n"], cfg["solver_model"], cfg["solver_effort"], cfg["evolver_model"],
        cfg["evolver_effort"], "เซสชันใหม่ทุก epoch" if cfg["fresh_session"] else "เซสชันเดียวตลอดการรัน"))
    ad = st.get("adapt")
    if ad:
        print("Benchmark Adaptor: โจทย์ train %d · validation %d · test %d · reference/ %d ไฟล์ (เฉลยของ Training %d ไฟล์) · ตรวจการรั่ว: %s · $%.2f" % (
            ad["tasks"]["train"], ad["tasks"]["validation"], ad["tasks"]["test"], ad["reference"]["files"],
            ad["reference"]["answers"], "สะอาด" if ad["audit_ok"] else "พบการรั่ว", ad["cost_usd"]))

    def cell(lb):
        s = L.get(lb)
        return "%s (%d/%d)" % (pct(s["score"]), s["passes"], s["n"]) if s else "-"
    H = ["epoch", "ชุดสกิลที่ Solver ใช้", "SKILL.md", "ไฟล์อื่น", "Training คะแนน (ผ่าน)", "Validation คะแนน (ผ่าน)",
         "ตาของ Evolver (นาที)", "เครื่องมือ", "Bash", "รันสคริปต์เดิมซ้ำ", "ย่อบริบท", "ค่าใช้จ่าย"]
    print("\n| " + " | ".join(H) + " |\n|" + "---|" * len(H))
    print("| 0 | (ไม่มีสกิล) | - | - | %s | %s | - | - | - | - | - | - |" % (cell("base_train"), cell("base_val")))
    for t in T:
        k = t["k"]
        print("| %d | %s | %.1f KB | %d | %s | %s | %.1f | %d | %d | %d | %d | $%.2f |" % (
            k, ", ".join(t["skills"]) or "(ว่าง)", t["skill_md_bytes"] / 1024, len(t["skill_other_files"]),
            cell("v%d_train" % k), cell("v%d_val" % k), t["wall_s"] / 60, t["tool_calls"], t["bash"],
            t["rerun_old_scripts"], t["compactions"], t["cost_usd"]))
    bt, ft = L.get("base_test"), L.get("v%d_test" % st["epochs"])
    if bt:
        print("\n| Test Set (held-out) | คะแนน | pass@1 (rollout ที่ผ่าน) | pass@3 (ผ่านอย่างน้อย 1 ครั้ง) | all@3 (ผ่านทุกครั้ง) |\n|---|---|---|---|---|")
        for name, s in (("ไม่มีสกิล", bt), ("skills_v%d (epoch สุดท้าย)" % st["epochs"], ft)):
            if s:
                print("| %s | %s | %d/%d | %d/%d | %d/%d |" % (name, pct(s["score"]), s["passes"], s["n"], s["pass3"], s["tasks"], s["all3"], s["tasks"]))
    tr = sum(s["n"] for s in L.values())
    sc = sum(s["cost_usd"] for s in L.values())
    ec = sum(t["cost_usd"] for t in T)
    print("\nรวม: rollout ของ Solver %d ครั้ง ($%.2f) · Evolver %d ตา ($%.2f)%s" % (
        tr, sc, len(T), ec, " · Benchmark Adaptor $%.2f" % ad["cost_usd"] if ad else ""))
    if bt and ft:
        gain_p = (ft["passes"] / ft["n"] - bt["passes"] / bt["n"]) * 100
        gain_s = (ft["score"] - bt["score"]) * 100
        print("Test Set: คะแนนเพิ่ม %+.1f จุด · pass rate เพิ่ม %+.1f จุด · ต้นทุนของ Evolver ต่อ 1 จุดที่เพิ่ม: คะแนน %s · pass rate %s" % (
            gain_s, gain_p, "$%.3f" % (ec / gain_s) if gain_s > 0 else "ไม่เพิ่ม", "$%.3f" % (ec / gain_p) if gain_p > 0 else "ไม่เพิ่ม"))
    nx = next_step(st)
    print("สถานะ: %s" % ("จบแล้ว (วัด Test Set แล้ว)" if nx == "done" else "ยังไม่จบ · ขั้นถัดไป: %s (epoch %d)" % (nx, st["k"] + (1 if nx == "turn" else 0))))
    return 0


def cmd_noise(a):
    st = load(a.ws)
    L, n = st.get("legs", {}), st["n"]
    order = ["base_train", "base_val", "base_test"]
    for k in range(1, st["epochs"] + 1):
        order += ["v%d_train" % k, "v%d_val" % k, "v%d_test" % k]
    std = set(order)
    order = [x for x in order if x in L] + sorted(x for x in L if x not in std)
    print("\n1) โจทย์แยกตามจำนวนครั้งที่ผ่านจาก %d ครั้ง (ผ่าน = คะแนน %.3f ขึ้นไป)\n" % (n, PASS))
    print("| leg | ชุดสกิล | โจทย์ | ผ่าน %d/%d | ผ่าน 0/%d | ผ่านบางครั้ง | คะแนนต่างกันระหว่างครั้ง |\n|---|---|---|---|---|---|---|" % (n, n, n))
    for lb in order:
        s = L[lb]
        moved = sum(1 for v in s["by_task"].values() if max(v) - min(v) > 1e-9)
        print("| %s | %s | %d | %d | %d | %d | %d โจทย์ |" % (lb, ", ".join(s.get("skills") or []) or "(ไม่มี)", s["tasks"],
                                                    s["all3"], s["none3"], s["mixed"], moved))
    print("\n2) ถ้าใช้ประตูรับแบบ \"วัดโจทย์ละ 1 ครั้ง แล้วรับเมื่อคะแนนสูงกว่าเดิม\" จะตัดสินอย่างไร")
    print("   (จับคู่ครั้งที่ i ของชุดเดิม กับครั้งที่ j ของชุดใหม่ ทุกแบบ = %d คู่ต่อ 1 การตัดสิน)\n" % (n * n))
    print("| ชุด | เทียบ | ค่าเฉลี่ย %d ครั้ง (เดิม → ใหม่) | รับ | เสมอ (ไม่รับ) | ไม่รับเพราะต่ำกว่า |\n|---|---|---|---|---|---|" % n)
    for sp in ("train", "val"):
        chain = [("ไม่มีสกิล", "base_" + sp)] + [("v%d" % k, "v%d_%s" % (k, sp)) for k in range(1, st["epochs"] + 1)]
        chain = [(nm, lb) for nm, lb in chain if lb in L]
        for (n0, l0), (n1, l1) in zip(chain, chain[1:]):
            b0, b1 = L[l0]["by_task"], L[l1]["by_task"]
            acc = tie = rej = 0
            for i in range(n):
                for j in range(n):
                    s0 = mean(v[i] for v in b0.values() if len(v) > i)
                    s1 = mean(v[j] for v in b1.values() if len(v) > j)
                    acc += s1 > s0 + 1e-9
                    tie += abs(s1 - s0) <= 1e-9
                    rej += s1 < s0 - 1e-9
            print("| %s | %s → %s | %s → %s | %d/%d | %d/%d | %d/%d |" % (
                "Training" if sp == "train" else "Validation", n0, n1, pct(L[l0]["score"]), pct(L[l1]["score"]),
                acc, n * n, tie, n * n, rej, n * n))
    print("\nแถวที่ \"รับ\" ไม่ใช่ 0/%d หรือ %d/%d ทั้งหมด = การตัดสินขึ้นกับว่าสุ่มได้ rollout ครั้งไหน" % (n * n, n * n, n * n))
    return 0


def cmd_eval(a):
    ws, st = a.ws, load(a.ws)
    if a.skills == "none":
        src = None
    elif re.match(r"^v\d+$", a.skills):
        src = P(ws, "skills_" + a.skills)
    else:
        src = os.path.abspath(a.skills)
    rows = rollouts(ws, st, a.label, {"val": "validation"}.get(a.split, a.split), src, model=a.model)
    save(ws, st)
    s = st["legs"][a.label]
    print("\n%s · %s · %d rollout · คะแนน %s · ผ่าน %d/%d · pass@3 %d/%d · all@3 %d/%d · สกิล: %s" % (
        a.label, a.split, len(rows), pct(s["score"]), s["passes"], s["n"], s["pass3"], s["tasks"], s["all3"], s["tasks"],
        ", ".join(s["skills"]) or "(ไม่มี)"))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init")
    p.add_argument("ws")
    for f in ("instruction", "data", "split", "grader", "solver-prompt", "skillopt", "accounts"):
        p.add_argument("--" + f, required=True)
    p.add_argument("--solver-model", default="sonnet"); p.add_argument("--solver-effort", default="medium")
    p.add_argument("--evolver-model", default="sonnet"); p.add_argument("--evolver-effort", default="high")
    p.add_argument("--adaptor-model", default="sonnet"); p.add_argument("--par", type=int, default=6)
    p.add_argument("--turn-minutes", type=int, default=30)
    p.add_argument("--fresh-session", action="store_true", help="Ablation: Evolver เริ่มเซสชันใหม่ทุก epoch (ไม่ใช้ --resume)")
    for c in ("adapt", "audit", "base", "turn", "rollout", "evolve", "test", "status", "noise"):
        sp.add_parser(c).add_argument("ws")
    p = sp.add_parser("run"); p.add_argument("ws")
    p.add_argument("--stop-after", choices=["adapt", "base", "turn", "rollout"])
    p = sp.add_parser("eval"); p.add_argument("ws"); p.add_argument("--label", required=True)
    p.add_argument("--skills", required=True); p.add_argument("--split", default="test", choices=["train", "val", "test", "all"])
    p.add_argument("--model")
    a = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    a.ws = os.path.abspath(a.ws)
    return {"init": cmd_init, "adapt": cmd_adapt, "audit": cmd_audit, "base": cmd_base, "turn": cmd_turn,
            "rollout": cmd_rollout, "evolve": cmd_evolve, "test": cmd_test, "run": cmd_run, "status": cmd_status,
            "noise": cmd_noise, "eval": cmd_eval}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
