#!/usr/bin/env python3
"""wikiskill.py - วงรอบ WikiSkill (Tang et al., 2026 · arXiv:2608.27454 · Algorithm 1) บนชุดโจทย์รูปแบบ skill-optimizer

  wikiskill.py init     <ws> --suite suite --skillopt skill-optimizer/scripts/skillopt.py --accounts yolo1,yolo2
                        [--iters 8] [--reps 3] [--par 6] [--model sonnet] [--effort medium]
                        [--opt-model sonnet] [--opt-effort high] [--task-desc "..."] [--no-wiki]
  wikiskill.py baseline <ws>      บรรทัด 3      วัด Validation ด้วยชุดสกิลว่าง  -> R_best
  wikiskill.py rollout  <ws>      บรรทัด 8      Inference Agent ทำโจทย์ Training ด้วยสกิลปัจจุบัน -> raw/
  wikiskill.py maintain <ws>      บรรทัด 9-10   Wiki Maintainer สรุป Trace ลง wiki/
  wikiskill.py propose  <ws>      บรรทัด 11     Skill Proposer อ่าน wiki + Trace แล้วเสนอแก้สกิล 1 ตัว
  wikiskill.py gate     <ws>      บรรทัด 12-19  วัด Validation ของสกิลที่เสนอ -> รับ หรือ ย้อนกลับ · จดลง wiki/skill-impact.md
  wikiskill.py loop     <ws>      บรรทัด 4-20   ทำ rollout -> maintain -> propose -> gate ซ้ำจนครบ --iters หรือ R_best = 100%
  wikiskill.py status   <ws>      ตารางสรุปทุกรอบ
  wikiskill.py eval     <ws> --label L --skills <โฟลเดอร์ skills | active | none> [--split test]   วัดชุดสกิลใดก็ได้

โครงของ workspace (3 ชั้น):
  <ws>/raw/iter-01/traces/<โจทย์>-r<รอบ>.md   Raw Layer   Trace ของ Training (เขียนครั้งเดียว ไม่แก้)
  <ws>/wiki/{index.md,log.md,skill-impact.md,patterns/*.md}   Wiki Layer  ความรู้สะสม (ไม่ถูกย้อนกลับ)
  <ws>/skills/<ชื่อ>/{SKILL.md,PURPOSE.md}    Skills Layer ชุดสกิลที่ใช้งาน (ย้อนกลับได้)
  <ws>/history/iter-01/                       หลักฐานของแต่ละรอบ (สิ่งที่แต่ละ Agent ได้รับและตอบ)
  <ws>/state.json                             สถานะของวงรอบ

Inference Agent รันด้วย run_trial ของ skillopt.py (โจทย์ ตัวตรวจ และพรอมต์ชุดเดียวกับ skill-optimizer)
Python 3.8+ stdlib เท่านั้น
"""
import argparse, difflib, importlib.util, json, os, random, re, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE_CAP = 15000          # ตัวอักษรสูงสุดต่อ Trace (ค่าเดียวกับเปเปอร์ ภาคผนวก C)
MAX_FAIL, MAX_PASS = 5, 3  # Trace ที่ส่งให้ Wiki Maintainer ต่อรอบ (ภาคผนวก C)
MIN_TRACES = 4             # Skill Proposer ต้องอ่าน Trace อย่างน้อยเท่านี้ก่อนเสนอ


# ------------------------------------------------------------------ state
def P(ws, *a):
    return os.path.join(ws, *a)


def load(ws):
    return json.load(open(P(ws, "state.json"), encoding="utf-8"))


def save(ws, st):
    json.dump(st, open(P(ws, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def read(p, default=""):
    try:
        return open(p, encoding="utf-8").read()
    except OSError:
        return default


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


def skillopt(st):
    spec = importlib.util.spec_from_file_location("skillopt", st["cfg"]["skillopt"])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def idir(ws, k):
    return P(ws, "history", "iter-%02d" % k)


def skill_names(d):
    return sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "SKILL.md"))) if os.path.isdir(d) else []


def pct(x):
    return "%.1f%%" % (x * 100)


# ------------------------------------------------------------------ Inference Agent (rollouts)
def rollouts(st, label, split, skills_dir):
    """รันโจทย์ของ split นั้นทุกข้อ x reps ด้วยชุดสกิลใน skills_dir (โฟลเดอร์ชื่อ skills · ว่าง = ไม่มีสกิล)
    Inference Agent เห็นเฉพาะ ./skills ใน sandbox ไม่เห็น wiki/ และ raw/"""
    so, cfg = skillopt(st), st["cfg"]
    suite = so.load_suite(cfg["suite"])
    if skill_names(skills_dir):
        assert os.path.basename(os.path.normpath(skills_dir)) == "skills"
        suite = dict(suite, files=suite.get("files", []) + [os.path.abspath(skills_dir)])
    a = argparse.Namespace(label=label, skill="none", model=cfg["model"], effort=cfg["effort"])
    tasks = [t for t in suite["tasks"] if split == "all" or t.get("split", "train") == split]
    jobs = []
    for r in range(1, cfg["reps"] + 1):
        for t in tasks:
            d = os.path.join(cfg["suite"], "runs", label, "%s-r%d" % (t["id"], r))
            if not (os.path.isfile(os.path.join(d, "grade.json")) and os.path.isfile(os.path.join(d, "metrics.json"))):
                jobs.append((t, r))                       # รอบที่ทำเสร็จแล้วไม่รันซ้ำ (รันต่อจากที่ค้างได้)
    lock, loadn = threading.Lock(), {x: 0 for x in cfg["accounts"]}

    def one(j):
        with lock:
            acc = min(loadn, key=loadn.get)
            loadn[acc] += 1
        try:
            return so.run_trial(cfg["suite"], suite, j[0], j[1], a, acc)
        finally:
            with lock:
                loadn[acc] -= 1
    with ThreadPoolExecutor(cfg["par"]) as ex:
        list(ex.map(one, jobs))
    rows = so.collect(cfg["suite"], label)
    return [r for r in rows if split == "all" or r["split"] == split]


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def cost_of(rows):
    return {"trials": len(rows), "cost_usd": round(sum(r.get("cost_usd", 0) for r in rows), 3),
            "context_tokens": round(mean(r.get("input_tokens", 0) + r.get("cache_read", 0) + r.get("cache_write", 0) for r in rows)),
            "tool_calls": round(mean(r.get("tool_calls", 0) for r in rows), 2),
            "skill_read": sum(1 for r in rows if r.get("skill_read"))}


# ------------------------------------------------------------------ Raw Layer: transcript -> trace
def clip(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "\n…(ตัด %d ตัวอักษร)" % (len(s) - n)


def tool_text(name, inp, n):
    if name == "Bash":
        return clip(inp.get("command", ""), n)
    if name in ("Write", "Edit"):
        return "%s\n%s" % (inp.get("file_path", ""), clip(inp.get("content") or inp.get("new_string") or "", n))
    if name == "Read":
        return inp.get("file_path", "")
    return clip(inp, n)


def render_trace(row, k, cmd_cap=5000, out_cap=1200):
    """แปลง transcript.jsonl ของ 1 Trial เป็น Trace ที่อ่านได้: โจทย์ · ผลของตัวตรวจ · ทุกขั้นที่ Agent ทำ · คำตอบสุดท้าย"""
    task = json.load(open(os.path.join(row["dir"], "task.json"), encoding="utf-8"))
    steps, results, final = [], {}, row.get("result", "")
    for line in open(os.path.join(row["dir"], "transcript.jsonl"), encoding="utf-8", errors="replace"):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        for c in (m.get("message") or {}).get("content", []) if m.get("type") in ("assistant", "user") else []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text" and m["type"] == "assistant" and c.get("text", "").strip():
                steps.append(("say", c["text"].strip(), None))
            elif c.get("type") == "tool_use":
                steps.append(("tool", c["name"], (c.get("id"), c.get("input") or {})))
            elif c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list):
                    body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                results[c.get("tool_use_id")] = ("ERROR " if c.get("is_error") else "") + (body or "")
    ok = row["score"] >= 0.999
    L = ["# Trace %s-r%d · iteration %d" % (row["task"], row["rep"], k), "",
         "- ผล: **%s** · คะแนน %.2f (ผ่าน %d จาก %d ข้อตรวจ)" % ("PASS" if ok else "FAIL", row["score"],
                                                          sum(1 for c in row["checks"] if c["pass"]), len(row["checks"])),
         "- คำสั่งที่ใช้ %d ครั้ง · คำสั่งล้ม %d ครั้ง · อ่านสกิล: %s" % (row["tool_calls"], row["tool_errors"],
                                                              "ใช่" if row.get("skill_read") else "ไม่"), "",
         "## โจทย์", "", task.get("brief", json.dumps(task, ensure_ascii=False)), "", "## ผลของตัวตรวจ (Grader)", ""]
    for c in row["checks"]:
        L.append("- %s `%s`%s" % ("✓" if c["pass"] else "✗", c["id"], "" if c["pass"] else ": " + c.get("note", "")))
    L += ["", "## สิ่งที่ Agent ทำ", ""]
    n = 0
    for kind, a, b in steps:
        if kind == "say":
            L += ["**Agent พูด:** " + clip(a, 800), ""]
        else:
            n += 1
            L += ["### ขั้น %d · %s" % (n, a), "", "```", tool_text(a, b[1], cmd_cap), "```", "",
                  "ผลที่ได้:", "", "```", clip(results.get(b[0], "(ไม่มีผล)"), out_cap), "```", ""]
    L += ["## คำตอบสุดท้ายของ Agent", "", clip(final, 1500), ""]
    txt = "\n".join(L)
    if len(txt) > TRACE_CAP and cmd_cap > 1500:           # ยาวเกิน -> ย่อคำสั่งและผลก่อน แล้วค่อยตัดท้าย
        return render_trace(row, k, cmd_cap // 2, out_cap // 2)
    return txt if len(txt) <= TRACE_CAP else txt[:TRACE_CAP] + "\n…(ตัดที่ %d ตัวอักษร)" % TRACE_CAP


def trace_id(r):
    return "%s-r%d" % (r["task"], r["rep"])


def summary_md(rows, k):
    L = ["# ผลของ Training rollouts · iteration %d" % k, "",
         "คะแนนเฉลี่ย %s · ผ่านครบทุกข้อ %d/%d Trace" % (pct(mean(r["score"] for r in rows)),
                                                    sum(1 for r in rows if r["score"] >= 0.999), len(rows)), "",
         "| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |", "|---|---|---|---|"]
    for r in rows:
        bad = [c["id"] for c in r["checks"] if not c["pass"]]
        L.append("| %s | %s | %.2f | %s |" % (trace_id(r), "PASS" if not bad else "FAIL", r["score"], " ".join(bad) or "-"))
    L += ["", "## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)", ""]
    for r in rows:
        for c in r["checks"]:
            if not c["pass"]:
                L.append("- %s · `%s`: %s" % (trace_id(r), c["id"], c.get("note", "")))
    return "\n".join(L) + "\n"


def sample_traces(rows, k):
    """สุ่มแบบแบ่งชั้น: Trace ที่ไม่ผ่านไม่เกิน 5 (คะแนนต่ำก่อน กระจายทุกโจทย์) + Trace ที่ผ่านไม่เกิน 3"""
    rnd = random.Random(k)

    def spread(rs, limit):
        by = {}
        for r in sorted(rs, key=lambda r: (r["score"], rnd.random())):
            by.setdefault(r["task"], []).append(r)
        out, order = [], sorted(by, key=lambda t: by[t][0]["score"])
        while len(out) < limit and any(by.values()):
            for t in order:
                if by[t] and len(out) < limit:
                    out.append(by[t].pop(0))
        return out
    fails = spread([r for r in rows if r["score"] < 0.999], MAX_FAIL)
    passes = spread([r for r in rows if r["score"] >= 0.999], MAX_PASS)
    return fails, passes


# ------------------------------------------------------------------ LLM call (Wiki Maintainer / Skill Proposer)
def llm(st, system, user, tools, cwd, out_path):
    """เรียกโมเดล 1 ครั้ง (หรือ 1 เซสชันแบบ ReAct เมื่อมี tools) -> metrics ของ skillopt.parse_transcript"""
    cfg = st["cfg"]
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("CLAUDE") or key.startswith("MA_"):
            env.pop(key)
    acc = cfg["accounts"][0]
    home = os.path.join(os.environ.get("WIKISKILL_ACCOUNT_ROOT", os.path.expanduser("~/ai-accounts/.Claude")), acc)
    if os.path.isdir(home):
        # เรียก claude ตรง ๆ ด้วยบัญชีเดียวกัน โดยไม่แนบ MCP ของ wrapper: Maintainer ไม่ใช้เครื่องมือ · Proposer ใช้ Read อย่างเดียว
        # (ถ้าแนบ MCP พร้อม --tools เครื่องมือ MCP ทั้งหมดจะถูกโหลดเข้าบริบททุกครั้ง ราว 108,000 โทเคน)
        env.update(CLAUDE_CONFIG_DIR=home, IS_SANDBOX="1")
        head = ["claude", "--dangerously-skip-permissions", "--disable-slash-commands"]
    else:
        head = [acc]
    cmd = head + ["-p", "--system-prompt", system, "--model", cfg["opt_model"], "--effort", cfg["opt_effort"],
                  "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--strict-mcp-config",
                  "--tools", tools]
    os.makedirs(cwd, exist_ok=True)
    t0 = time.time()
    with open(out_path, "wb") as out, open(out_path + ".stderr", "wb") as err:
        subprocess.run(cmd, cwd=cwd, env=env, input=user.encode("utf-8"), stdout=out, stderr=err, timeout=1800)
    m = skillopt(st).parse_transcript(out_path)
    m["wall_s"] = round(time.time() - t0, 1)
    return m


def parse_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < 0:
        raise ValueError("ไม่พบ JSON object ในคำตอบ")
    return json.loads(t[i:j + 1])


def apply_edits(text, edits):
    """แก้ข้อความแบบ patch: append / replace / insert_after -> (ข้อความใหม่, รายการที่แก้ไม่ได้)"""
    bad = []
    for e in edits or []:
        op, tgt, con = e.get("op"), e.get("target", ""), e.get("content", "")
        if op == "append":
            text = text.rstrip("\n") + "\n" + con.strip("\n") + "\n"
        elif op in ("replace", "insert_after") and tgt and tgt in text:
            text = text.replace(tgt, con if op == "replace" else tgt + "\n" + con.strip("\n"), 1)
        else:
            bad.append("%s: ไม่พบ target %r" % (op, tgt[:60]))
    return text, bad


def safe_name(n, ext=""):
    n = os.path.basename(str(n).strip().replace("\\", "/"))
    if ext and not n.endswith(ext):
        n += ext
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", n):
        raise ValueError("ชื่อไฟล์ไม่ถูกต้อง: %r" % n)
    return n


def opt_cost(m):
    return {"calls": m.get("num_turns"), "tool_calls": m.get("tool_calls"), "cost_usd": m.get("cost_usd"),
            "wall_s": m.get("wall_s"), "output_tokens": m.get("output_tokens"),
            "context_tokens": m.get("input_tokens", 0) + m.get("cache_read", 0) + m.get("cache_write", 0)}


# ------------------------------------------------------------------ commands
def cmd_init(a):
    ws = a.ws
    if os.path.exists(P(ws, "state.json")):
        print("มี workspace นี้อยู่แล้ว: %s (ลบโฟลเดอร์ก่อนถ้าต้องการเริ่มใหม่)" % ws)
        return 1
    for d in ("raw", "skills", "history") + (() if a.no_wiki else ("wiki/patterns",)):
        os.makedirs(P(ws, d), exist_ok=True)
    if not a.no_wiki:                                       # W0 = ว่าง (มีแต่หัวไฟล์)
        write(P(ws, "wiki", "index.md"), "# Wiki Index\n\nยังไม่มี pattern\n")
        write(P(ws, "wiki", "log.md"), "# Evolution Log\n")
        write(P(ws, "wiki", "skill-impact.md"), "# Skill Impact\n\nบันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ\n")
    st = {"cfg": {"name": os.path.basename(os.path.normpath(ws)), "suite": os.path.abspath(a.suite),
                  "skillopt": os.path.abspath(a.skillopt), "accounts": a.accounts.split(","), "iters": a.iters,
                  "reps": a.reps, "par": a.par, "model": a.model, "effort": a.effort, "opt_model": a.opt_model,
                  "opt_effort": a.opt_effort, "task_desc": a.task_desc, "use_wiki": not a.no_wiki},
          "k": 0, "phase": "init", "r_best": None, "history": []}
    save(ws, st)
    print("สร้าง workspace %s · S0 = ว่าง · W0 = %s" % (ws, "ว่าง" if not a.no_wiki else "(ไม่ใช้ wiki)"))
    return 0


def cmd_baseline(a):
    ws, st = a.ws, load(a.ws)
    if st["phase"] != "init":
        print("baseline ทำไปแล้ว (R_best = %s)" % pct(st["r_best"]))
        return 0
    rows = rollouts(st, "%s-k00-val" % st["cfg"]["name"], "val", P(ws, "skills"))
    st["r_best"], st["phase"] = mean(r["score"] for r in rows), "gate"
    st["baseline"] = dict(cost_of(rows), val_score=st["r_best"])
    save(ws, st)
    print("\nBaseline (ชุดสกิลว่าง) Validation = %s  ->  R_best = %s" % (pct(st["r_best"]), pct(st["r_best"])))
    return 0


def need(st, phase, cmd):
    if st["phase"] != phase:
        order = {"init": "baseline", "gate": "rollout", "rollout": "maintain", "maintain": "propose", "propose": "gate"}
        print("ยังรัน %s ไม่ได้: ขั้นถัดไปคือ `%s` (ตอนนี้ k=%d phase=%s)" % (cmd, order[st["phase"]], st["k"], st["phase"]))
        sys.exit(1)


def cmd_rollout(a):
    ws, st = a.ws, load(a.ws)
    need(st, "gate", "rollout")
    if st["r_best"] >= 1.0 - 1e-9:
        print("R_best = 100% แล้ว -> จบวงรอบ (Algorithm 1 บรรทัด 5-6)")
        return 0
    k = st["k"] + 1
    rows = rollouts(st, "%s-k%02d-train" % (st["cfg"]["name"], k), "train", P(ws, "skills"))
    tdir = P(ws, "raw", "iter-%02d" % k, "traces")
    for r in rows:
        write(os.path.join(tdir, trace_id(r) + ".md"), render_trace(r, k))
    write(P(ws, "raw", "iter-%02d" % k, "summary.md"), summary_md(rows, k))
    checks = {}
    for r in rows:
        for c in r["checks"]:
            v = checks.setdefault(c["id"], [0, 0])
            v[0] += 1 if c["pass"] else 0
            v[1] += 1
    st["k"], st["phase"] = k, "rollout"
    st["history"].append({"k": k, "skills_in": skill_names(P(ws, "skills")), "train_score": mean(r["score"] for r in rows),
                          "train_perfect": sum(1 for r in rows if r["score"] >= 0.999), "train_n": len(rows),
                          "train_checks": {c: "%d/%d" % tuple(v) for c, v in checks.items()}, "train": cost_of(rows)})
    save(ws, st)
    print("\n[iter %d] Training = %s · ผ่านครบ %d/%d Trace -> raw/iter-%02d/traces/" % (
        k, pct(st["history"][-1]["train_score"]), st["history"][-1]["train_perfect"], len(rows), k))
    return 0


def wiki_context(ws):
    L = []
    for f in ("index.md", "log.md", "skill-impact.md"):
        L += ["### wiki/%s" % f, "", read(P(ws, "wiki", f)).strip() or "(ว่าง)", ""]
    pd = P(ws, "wiki", "patterns")
    for f in sorted(os.listdir(pd)):
        L += ["### wiki/patterns/%s" % f, "", read(os.path.join(pd, f)).strip(), ""]
    return "\n".join(L)


def cmd_maintain(a):
    ws, st = a.ws, load(a.ws)
    need(st, "rollout", "maintain")
    k, h, cfg = st["k"], st["history"][-1], st["cfg"]
    hd = idir(ws, k)
    if not cfg["use_wiki"]:
        st["phase"] = "maintain"
        save(ws, st)
        print("[iter %d] ไม่ใช้ wiki (--no-wiki) -> ข้าม Wiki Maintainer" % k)
        return 0
    rows = [r for r in skillopt(st).collect(cfg["suite"], "%s-k%02d-train" % (cfg["name"], k)) if r["split"] == "train"]
    fails, passes = sample_traces(rows, k)
    U = ["# Iteration %d" % k, "", "คะแนน Training ของรอบนี้: %s (ผ่านครบ %d/%d Trace)" % (
        pct(h["train_score"]), h["train_perfect"], h["train_n"]), "", "## Active skills (ชุดสกิลที่ Agent ใช้ในรอบนี้)", ""]
    for n in skill_names(P(ws, "skills")) or []:
        U += ["### skills/%s/SKILL.md" % n, "", read(P(ws, "skills", n, "SKILL.md")).strip(), ""]
    if not skill_names(P(ws, "skills")):
        U += ["(ยังไม่มีสกิล)", ""]
    U += ["## Current wiki", "", wiki_context(ws), "", "## Execution traces (sampled: %d failing + %d passing)" % (len(fails), len(passes)), ""]
    for r in fails + passes:
        U += ["<trace id=\"%s\">" % trace_id(r), read(P(ws, "raw", "iter-%02d" % k, "traces", trace_id(r) + ".md")), "</trace>", ""]
    U.append("ตอบเป็น JSON object ตามรูปแบบที่กำหนด")
    user = "\n".join(U)
    system = read(os.path.join(HERE, "prompts", "maintainer.md")).replace("{task_desc}", cfg["task_desc"])
    write(os.path.join(hd, "maintainer_input.md"), user)
    out, err, m = None, "", None
    for attempt in (1, 2, 3):
        m = llm(st, system, user + ("\n\nคำตอบก่อนหน้าใช้ไม่ได้: %s · ตอบใหม่เป็น JSON object เดียว" % err if err else ""),
                "", os.path.join(hd, "_wm"), os.path.join(hd, "maintainer_transcript_%d.jsonl" % attempt))
        try:
            out = parse_json(m["result"])
            if not isinstance(out.get("update_index"), str) or not isinstance(out.get("append_log"), str):
                raise ValueError("ต้องมี update_index และ append_log")
            break
        except (ValueError, AttributeError) as e:
            out, err = None, str(e)[:200]
    if out is None:
        print("Wiki Maintainer ตอบไม่เป็น JSON 3 ครั้ง: %s" % err)
        return 1
    write(os.path.join(hd, "maintainer_output.json"), json.dumps(out, ensure_ascii=False, indent=1))
    pd, created, updated, skipped = P(ws, "wiki", "patterns"), [], [], []
    for p in out.get("create_patterns") or []:
        n = safe_name(p["name"], ".md")
        if os.path.exists(os.path.join(pd, n)):             # มีอยู่แล้ว -> ถือเป็นการเพิ่มหลักฐาน ไม่เขียนทับ
            write(os.path.join(pd, n), read(os.path.join(pd, n)).rstrip("\n") + "\n\n" + p["content"].strip() + "\n")
            updated.append(n)
        else:
            write(os.path.join(pd, n), p["content"].strip() + "\n")
            created.append(n)
    for p in out.get("update_patterns") or []:
        n = safe_name(p["name"], ".md")
        if not os.path.exists(os.path.join(pd, n)):
            skipped.append("%s: ไม่มีไฟล์นี้" % n)
            continue
        txt, bad = apply_edits(read(os.path.join(pd, n)), p.get("edits"))
        write(os.path.join(pd, n), txt)
        skipped += ["%s %s" % (n, b) for b in bad]
        if len(bad) < len(p.get("edits") or []):
            updated.append(n)
    write(P(ws, "wiki", "index.md"), out["update_index"].strip() + "\n")
    write(P(ws, "wiki", "log.md"), read(P(ws, "wiki", "log.md")).rstrip("\n") + "\n\n## Iteration %d · Training %s\n\n%s\n" % (
        k, pct(h["train_score"]), re.sub(r"^\s*#+\s*Iteration[^\n]*\n+", "", out["append_log"]).strip()))
    h.update(sampled={"fail": [trace_id(r) for r in fails], "pass": [trace_id(r) for r in passes]},
             patterns_created=created, patterns_updated=sorted(set(updated)), edits_skipped=skipped,
             patterns_total=len(os.listdir(pd)), maintainer=opt_cost(m))
    st["phase"] = "maintain"
    save(ws, st)
    print("[iter %d] Wiki Maintainer: อ่าน %d Trace (ไม่ผ่าน %d + ผ่าน %d) · pattern ใหม่ %d · แก้ %d · รวม %d หน้า · %.0f วินาที" % (
        k, len(fails) + len(passes), len(fails), len(passes), len(created), len(set(updated)), h["patterns_total"], m["wall_s"]))
    for n in created:
        print("   + wiki/patterns/%s" % n)
    for n in sorted(set(updated)):
        print("   ~ wiki/patterns/%s" % n)
    return 0


def build_candidate(ws, hd, prop):
    """Apply(S_{k-1}, P_k) -> โฟลเดอร์ candidate/skills · คืน (ชื่อสกิล, ข้อความ diff ของ SKILL.md)"""
    cand = os.path.join(hd, "candidate", "skills")
    shutil.rmtree(os.path.join(hd, "candidate"), ignore_errors=True)
    shutil.copytree(P(ws, "skills"), cand)
    act = prop.get("action")
    if act == "no_action":
        return None, ""
    name = safe_name(prop.get("name", ""))
    sp = os.path.join(cand, name, "SKILL.md")
    old = read(sp)
    if act == "create":
        if not str(prop.get("skill_md", "")).lstrip().startswith("---"):
            raise ValueError("skill_md ต้องขึ้นต้นด้วย YAML frontmatter (---)")
        shutil.rmtree(os.path.join(cand, name), ignore_errors=True)
        write(sp, prop["skill_md"].strip() + "\n")
        write(os.path.join(cand, name, "PURPOSE.md"), str(prop.get("purpose_md", "")).strip() + "\n")
    elif act == "patch":
        if not old:
            raise ValueError("patch สกิลที่ไม่มีอยู่: %s (สกิลที่มี: %s)" % (name, ", ".join(skill_names(cand)) or "ไม่มี"))
        new, bad = apply_edits(old, prop.get("edits"))
        if bad or new == old:
            raise ValueError("patch ใช้ไม่ได้: %s" % ("; ".join(bad) or "ไม่มีอะไรเปลี่ยน"))
        write(sp, new)
        if prop.get("purpose_append"):
            pp = os.path.join(cand, name, "PURPOSE.md")
            write(pp, read(pp).rstrip("\n") + "\n\n" + str(prop["purpose_append"]).strip() + "\n")
    else:
        raise ValueError("action ต้องเป็น create / patch / no_action")
    diff = "\n".join(difflib.unified_diff(old.splitlines(), read(sp).splitlines(), "a/skills/%s/SKILL.md" % name,
                                          "b/skills/%s/SKILL.md" % name, lineterm=""))
    return name, diff


def cmd_propose(a):
    ws, st = a.ws, load(a.ws)
    need(st, "maintain", "propose")
    k, h, cfg = st["k"], st["history"][-1], st["cfg"]
    hd = idir(ws, k)
    view = os.path.join(hd, "proposer_view")              # สิ่งที่ Skill Proposer มองเห็น: wiki/ traces/ skills/ summary.md
    shutil.rmtree(view, ignore_errors=True)
    os.makedirs(view)
    if cfg["use_wiki"]:
        shutil.copytree(P(ws, "wiki"), os.path.join(view, "wiki"))
    shutil.copytree(P(ws, "raw", "iter-%02d" % k, "traces"), os.path.join(view, "traces"))
    shutil.copytree(P(ws, "skills"), os.path.join(view, "skills"))
    shutil.copy(P(ws, "raw", "iter-%02d" % k, "summary.md"), view)
    U = ["# Iteration %d" % k, "", "Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): %s" % pct(st["r_best"]), ""]
    if cfg["use_wiki"]:
        U += ["## wiki/index.md", "", read(P(ws, "wiki", "index.md")).strip(), "",
              "## wiki/skill-impact.md", "", read(P(ws, "wiki", "skill-impact.md")).strip(), ""]
    U += ["## summary.md", "", read(os.path.join(view, "summary.md")).strip(), "", "## Active skills", ""]
    U += ["- skills/%s/SKILL.md" % n for n in skill_names(P(ws, "skills"))] or ["(ยังไม่มีสกิล)"]
    U += ["", "สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย"]
    user = "\n".join(U)
    pf = "proposer.md" if cfg["use_wiki"] else "proposer_nowiki.md"
    system = read(os.path.join(HERE, "prompts", pf)).replace("{task_desc}", cfg["task_desc"])
    write(os.path.join(hd, "proposer_input.md"), user)
    prop, err, attempts, costs = None, "", 0, []
    for attempt in (1, 2, 3):
        attempts = attempt
        m = llm(st, system, user + ("\n\nข้อเสนอก่อนหน้าใช้ไม่ได้: %s · สำรวจต่อแล้วเสนอใหม่" % err if err else ""),
                "Read", view, os.path.join(hd, "proposer_transcript_%d.jsonl" % attempt))
        costs.append(opt_cost(m))
        reads = [re.sub(r"^.*proposer_view/", "", json.loads(c.split(" ", 1)[1]).get("file_path", ""))
                 for c in m["commands"] if c.startswith("Read ") and c.rstrip().endswith("}")]
        try:
            prop = parse_json(m["result"])
            ntr = len({r for r in reads if r.startswith("traces/")})
            if prop.get("action") != "no_action" and ntr < MIN_TRACES:
                raise ValueError("อ่าน Trace แค่ %d ไฟล์ (ต้องอย่างน้อย %d) ก่อนเสนอ" % (ntr, MIN_TRACES))
            name, diff = build_candidate(ws, hd, prop)
            break
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            prop, err = None, str(e)[:300]
    if prop is None:
        prop, name, diff = {"action": "no_action", "rationale": "ข้อเสนอใช้ไม่ได้ 3 ครั้ง: " + err}, None, ""
        build_candidate(ws, hd, prop)
    write(os.path.join(hd, "proposal.json"), json.dumps(prop, ensure_ascii=False, indent=1))
    write(os.path.join(hd, "proposal.diff"), diff + "\n")
    h.update(proposal={"action": prop.get("action"), "name": name, "rationale": prop.get("rationale", "")},
             proposer={"attempts": attempts, "reads": reads, "traces_read": len({r for r in reads if r.startswith("traces/")}),
                       "patterns_read": len({r for r in reads if r.startswith("wiki/patterns/")}),
                       "calls": sum(c["calls"] or 0 for c in costs), "cost_usd": round(sum(c["cost_usd"] or 0 for c in costs), 3),
                       "wall_s": round(sum(c["wall_s"] or 0 for c in costs), 1),
                       "context_tokens": sum(c["context_tokens"] or 0 for c in costs)})
    st["phase"] = "propose"
    save(ws, st)
    print("[iter %d] Skill Proposer: %d รอบ ReAct · อ่าน %d ไฟล์ (pattern %d · Trace %d) -> %s %s" % (
        k, h["proposer"]["calls"], len(reads), h["proposer"]["patterns_read"], h["proposer"]["traces_read"],
        prop.get("action"), name or ""))
    print("   เหตุผล: %s" % prop.get("rationale", ""))
    return 0


def cmd_gate(a):
    ws, st = a.ws, load(a.ws)
    need(st, "propose", "gate")
    k, h, cfg = st["k"], st["history"][-1], st["cfg"]
    hd = idir(ws, k)
    prop = json.load(open(os.path.join(hd, "proposal.json"), encoding="utf-8"))
    before, act, name = st["r_best"], prop.get("action"), h["proposal"]["name"]
    if act == "no_action":
        r_val, accepted, rows = None, False, []
    else:
        rows = rollouts(st, "%s-k%02d-val" % (cfg["name"], k), "val", os.path.join(hd, "candidate", "skills"))
        r_val = mean(r["score"] for r in rows)
        accepted = r_val > before + 1e-9                      # สมการ (4): รับเมื่อดีกว่า R_best เท่านั้น
    if accepted:
        shutil.rmtree(P(ws, "skills"))
        shutil.copytree(os.path.join(hd, "candidate", "skills"), P(ws, "skills"))
        st["r_best"] = r_val
    outcome = "ACCEPTED" if accepted else ("NO_ACTION" if act == "no_action" else "REJECTED")
    if cfg["use_wiki"]:                                       # บรรทัด 19: โปรแกรมจดผลลง wiki (wiki ไม่ถูกย้อนกลับ)
        E = ["", "## Iteration %d · %s `%s` · %s" % (k, act, name or "-", outcome), "",
             "- Validation ของสกิลที่เสนอ: %s · R_best ก่อนหน้า: %s -> %s" % (
                 pct(r_val) if r_val is not None else "(ไม่ได้วัด)", pct(before),
                 "รับ (R_best ใหม่ %s)" % pct(r_val) if accepted else "ไม่รับ ย้อนกลับไปใช้ชุดสกิลเดิม"),
             "- เหตุผลของข้อเสนอ: %s" % prop.get("rationale", ""), ""]
        if act != "no_action":
            E += ["Diff ของ SKILL.md ที่เสนอ:", "", "```diff", read(os.path.join(hd, "proposal.diff")).rstrip("\n"), "```"]
        write(P(ws, "wiki", "skill-impact.md"), read(P(ws, "wiki", "skill-impact.md")).rstrip("\n") + "\n" + "\n".join(E) + "\n")
        shutil.rmtree(os.path.join(hd, "wiki"), ignore_errors=True)
        shutil.copytree(P(ws, "wiki"), os.path.join(hd, "wiki"))   # สำเนา W_k ของรอบนี้ ไว้ดูย้อนหลัง
    shutil.rmtree(os.path.join(hd, "skills"), ignore_errors=True)
    shutil.copytree(P(ws, "skills"), os.path.join(hd, "skills"))   # สำเนา S_k ของรอบนี้
    h.update(val_score=r_val, r_best_before=before, accepted=accepted, outcome=outcome, r_best_after=st["r_best"],
             skills_out=skill_names(P(ws, "skills")), val=cost_of(rows))
    write(os.path.join(hd, "gate.json"), json.dumps({"k": k, "val_score": r_val, "r_best_before": before,
                                                     "outcome": outcome, "val_trials": [
                                                         {"trace_id": trace_id(r), "score": r["score"]} for r in rows]},
                                                    ensure_ascii=False, indent=1))
    st["phase"] = "gate"
    save(ws, st)
    print("\n[iter %d] Gate: Validation %s เทียบ R_best %s -> %s%s" % (
        k, pct(r_val) if r_val is not None else "-", pct(before), outcome,
        " · R_best ใหม่ %s" % pct(st["r_best"]) if accepted else " · ใช้ชุดสกิลเดิม (wiki ยังอยู่ครบ)"))
    return 0


def cmd_loop(a):
    ws = a.ws
    st = load(ws)
    if st["phase"] == "init":
        cmd_baseline(a)
    steps = {"gate": cmd_rollout, "rollout": cmd_maintain, "maintain": cmd_propose, "propose": cmd_gate}
    while True:
        st = load(ws)
        iters = a.iters or st["cfg"]["iters"]
        if st["phase"] == "gate" and st["r_best"] >= 1.0 - 1e-9:
            print("\nจบ: R_best = 100%% ที่ iteration %d (หยุดก่อนครบ %d รอบ)" % (st["k"], iters))
            break
        if st["phase"] == "gate" and st["k"] >= iters:
            print("\nจบ: ครบ %d รอบ · R_best = %s" % (iters, pct(st["r_best"])))
            break
        rc = steps[st["phase"]](a)
        if rc:
            return rc
    return cmd_status(a)


def cmd_status(a):
    st = load(a.ws)
    cfg = st["cfg"]
    print("\nworkspace %s · โมเดลที่ทำโจทย์ %s/%s · โมเดลของ Maintainer และ Proposer %s/%s · wiki: %s" % (
        cfg["name"], cfg["model"], cfg["effort"], cfg["opt_model"], cfg["opt_effort"], "ใช้" if cfg["use_wiki"] else "ไม่ใช้"))
    if st["r_best"] is None:
        print("ยังไม่ได้วัด baseline")
        return 0
    print("Baseline Validation (ชุดสกิลว่าง): %s · R_best ตอนนี้: %s · สกิลที่ใช้งาน: %s\n" % (
        pct(st["baseline"]["val_score"]), pct(st["r_best"]), ", ".join(skill_names(P(a.ws, "skills"))) or "(ไม่มี)"))
    H = ["รอบ", "Training (สกิลก่อนแก้)", "pattern ใหม่", "pattern ที่แก้", "pattern รวม", "Proposer อ่าน (pattern/Trace)",
         "ข้อเสนอ", "Validation", "R_best ก่อน", "ผล"]
    print("| " + " | ".join(H) + " |\n|" + "---|" * len(H))
    for h in st["history"]:
        pr, po = h.get("proposal") or {}, h.get("proposer") or {}
        print("| %d | %s (%d/%d) | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            h["k"], pct(h["train_score"]), h["train_perfect"], h["train_n"],
            len(h["patterns_created"]) if "patterns_created" in h else "-",
            len(h["patterns_updated"]) if "patterns_updated" in h else "-", h.get("patterns_total", "-"),
            "%s/%s" % (po.get("patterns_read", "-"), po.get("traces_read", "-")) if po else "-",
            ("%s `%s`" % (pr.get("action"), pr.get("name") or "-")) if pr else "-",
            pct(h["val_score"]) if h.get("val_score") is not None else "-",
            pct(h["r_best_before"]) if "r_best_before" in h else "-", h.get("outcome", "(ยังไม่ตัดสิน)")))
    tr = sum(h["train"]["trials"] for h in st["history"]) + sum((h.get("val") or {}).get("trials", 0) for h in st["history"]) + st["baseline"]["trials"]
    inf = sum(h["train"]["cost_usd"] for h in st["history"]) + sum((h.get("val") or {}).get("cost_usd", 0) for h in st["history"]) + st["baseline"]["cost_usd"]
    opt = sum((h.get("maintainer") or {}).get("cost_usd") or 0 for h in st["history"]) + sum((h.get("proposer") or {}).get("cost_usd") or 0 for h in st["history"])
    calls = sum(1 for h in st["history"] if h.get("maintainer")) + sum((h.get("proposer") or {}).get("calls") or 0 for h in st["history"])
    print("\nรวม: Trial ของ Inference Agent %d ครั้ง ($%.2f) · การเรียกโมเดลของ Maintainer + Proposer %d ครั้ง ($%.2f)" % (tr, inf, calls, opt))
    return 0


def cmd_eval(a):
    ws, st = a.ws, load(a.ws)
    src = P(ws, "skills") if a.skills == "active" else a.skills
    if a.skills == "none":
        sk = P(ws, "tmp", a.label, "skills")
        shutil.rmtree(sk, ignore_errors=True)
        os.makedirs(sk)
    else:
        sk = P(ws, "tmp", a.label, "skills")
        shutil.rmtree(os.path.dirname(sk), ignore_errors=True)
        shutil.copytree(src, sk)
    rows = rollouts(st, a.label, a.split, sk)
    print("\n%s · %s · %d Trial · คะแนน %s · ผ่านครบ %d/%d · สกิล: %s" % (
        a.label, a.split, len(rows), pct(mean(r["score"] for r in rows)), sum(1 for r in rows if r["score"] >= 0.999),
        len(rows), ", ".join(skill_names(sk)) or "(ไม่มี)"))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init")
    p.add_argument("ws"); p.add_argument("--suite", required=True); p.add_argument("--skillopt", required=True)
    p.add_argument("--accounts", required=True); p.add_argument("--iters", type=int, default=8)
    p.add_argument("--reps", type=int, default=3); p.add_argument("--par", type=int, default=6)
    p.add_argument("--model", default="sonnet"); p.add_argument("--effort", default="medium")
    p.add_argument("--opt-model", default="sonnet"); p.add_argument("--opt-effort", default="high")
    p.add_argument("--task-desc", default="เขียนโค้ด Python ตามโจทย์ (ตัวตรวจอัตโนมัติให้คะแนนผลงาน)")
    p.add_argument("--no-wiki", action="store_true", help="Ablation: ไม่มี Wiki Maintainer และ Proposer ไม่เห็น wiki")
    for c in ("baseline", "rollout", "maintain", "propose", "gate", "status"):
        sp.add_parser(c).add_argument("ws")
    p = sp.add_parser("loop"); p.add_argument("ws"); p.add_argument("--iters", type=int)
    p = sp.add_parser("eval"); p.add_argument("ws"); p.add_argument("--label", required=True)
    p.add_argument("--skills", required=True); p.add_argument("--split", default="test", choices=["train", "val", "test", "all"])
    a = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    a.ws = os.path.abspath(a.ws)
    return {"init": cmd_init, "baseline": cmd_baseline, "rollout": cmd_rollout, "maintain": cmd_maintain,
            "propose": cmd_propose, "gate": cmd_gate, "loop": cmd_loop, "status": cmd_status, "eval": cmd_eval}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
