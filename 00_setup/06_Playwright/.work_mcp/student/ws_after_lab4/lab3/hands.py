import sys, re, json, time, os
sys.path.insert(0, "/workspace")
from mcp_client import MCP

OUT = "/workspace/lab3"
URL = "https://www.google.com/travel/flights?hl=en"
m = MCP(f"{OUT}/rpc.jsonl")
act = open(f"{OUT}/actions.txt", "w")
n = 0


def section(text, name):
    mt = re.search(rf"^### {name}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    return mt.group(1) if mt else None


def call(tool, args=None):
    global n
    args = args or {}
    n += 1
    r = m._request("tools/call", {"name": tool, "arguments": args})
    if "error" in r:
        res = {"content": [{"type": "text", "text": r["error"].get("message", "")}], "isError": True}
    else:
        res = r["result"]
    content = res.get("content", [])
    text = "\n".join(c["text"] for c in content if c.get("type") == "text")
    images = [__import__("base64").b64decode(c["data"]) for c in content if c.get("type") == "image"]
    err = bool(res.get("isError"))
    ran = section(text, "Ran Playwright code") or ""
    code = [l for l in ran.splitlines() if l.startswith("await page")]
    has_snap = section(text, "Snapshot") is not None
    act.write(f"#{n} {tool}\n  arguments: {json.dumps(args, ensure_ascii=False)}\n"
              f"  code: {code}\n  isError: {err}\n  has_Snapshot: {has_snap}\n\n")
    act.flush()
    return text, images, err


def get_yaml(text):
    s = section(text, "Snapshot")
    if s is None:
        return None
    f = re.search(r"```(?:yaml)?\n(.*?)```", s, re.S)
    if f:
        return f.group(1)
    lk = re.search(r"\]\(([^)]+)\)", s)
    if lk:
        p = lk.group(1)
        if not os.path.isabs(p):
            p = next((c for c in (os.path.join("/workspace", p), os.path.join("/workspace/mcp-out", p)) if os.path.exists(c)), p)
        return open(p).read()
    return s


def snap(name, args=None):
    t, _, err = call("browser_snapshot", args)
    y = get_yaml(t)
    if err or y is None:
        raise SystemExit(f"snapshot {name} failed: {t[:300]}")
    open(f"{OUT}/{name}", "w").write(y)
    return y


def find_ref(yml, role, name_pat, require=None):
    """Return ref of the first line `- role "name..."` matching regex name_pat (and containing `require`)."""
    for l in yml.splitlines():
        mt = re.match(rf'\s*- {role} "({name_pat})"(.*)', l)
        if mt and (require is None or require in l):
            r = re.search(r"\[ref=(\w+)\]", l)
            if r:
                return r.group(1)
    raise SystemExit(f"ref not found: {role} /{name_pat}/ require={require}")


m.initialize()

# 1
t, _, _ = call("browser_navigate", {"url": URL})
y = get_yaml(t)
if y is None or 'button "Reject all"' not in y:
    y = snap("_pre.yml")
try:
    ref = find_ref(y, "button", "Reject all")
    call("browser_click", {"element": "Reject all", "target": ref})
except SystemExit as e:
    print("no cookie dialog:", e)
time.sleep(2)
s1 = snap("s1.yml")

# 2
ref = find_ref(s1, "combobox", r"Change ticket type[^\"]*")
call("browser_click", {"element": "Change ticket type", "target": ref})
s2 = snap("s2.yml")
ref = find_ref(s2, "option", "One way")
call("browser_click", {"element": "One way", "target": ref})
s3 = snap("s3.yml")

# 3
ref = find_ref(s3, "combobox", r"Where from\?[^\"]*")
call("browser_click", {"element": "Where from?", "target": ref})
s4 = snap("s4.yml")
ref = find_ref(s4, "combobox", r"[^\"]*", require="[expanded]")
call("browser_type", {"element": "origin input", "target": ref, "text": "BKK"})
time.sleep(1)
s5 = snap("s5.yml")
ref = find_ref(s5, "option", r"Suvarnabhumi Airport \(BKK\)")
call("browser_click", {"element": "Suvarnabhumi Airport (BKK)", "target": ref})

# 4
final = snap("final.yml", {"boxes": True})
_, imgs, err = call("browser_take_screenshot", {"type": "png", "scale": "device"})
if imgs:
    open(f"{OUT}/final.png", "wb").write(imgs[0])

# verify
L = final.splitlines()
a = [l for l in L if re.search(r'combobox "Change ticket type\. One way"', l)]
b = [l for l in L if re.search(r'combobox "Where from\?.*BKK', l)]
c = [l for l in L if "[expanded]" in l]
print("ticket type:", a)
print("where from:", b)
print("[expanded] lines:", c)
print("PASS" if a and b and not c else "FAIL")
call("browser_close")
m.close()
act.close()
