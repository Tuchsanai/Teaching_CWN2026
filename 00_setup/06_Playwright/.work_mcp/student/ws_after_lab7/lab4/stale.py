import sys, re, json, time, os, base64
sys.path.insert(0, "/workspace")
from mcp_client import MCP

OUT = "/workspace/lab4"
URL = "https://www.google.com/travel/flights?hl=en"
m = MCP(f"{OUT}/rpc.jsonl")
txt = open(f"{OUT}/stale.txt", "w")
errors = []  # (tool, rpc id, isError)


def section(text, name):
    mt = re.search(rf"^### {name}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    return mt.group(1) if mt else None


def call(tool, args=None):
    args = args or {}
    rid = m.next_id
    r = m._request("tools/call", {"name": tool, "arguments": args})
    if "error" in r:
        res = {"content": [{"type": "text", "text": r["error"].get("message", "")}], "isError": True}
    else:
        res = r["result"]
    content = res.get("content", [])
    text = "\n".join(c["text"] for c in content if c.get("type") == "text")
    images = [base64.b64decode(c["data"]) for c in content if c.get("type") == "image"]
    err = bool(res.get("isError")) or "error" in r
    txt.write(f"→ tools/call {tool} {json.dumps(args, ensure_ascii=False)}\n{text}\n[isError: {str(err).lower()}]\n\n")
    txt.flush()
    if err:
        errors.append((tool, rid))
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
    if name:
        open(f"{OUT}/{name}", "w").write(y)
    return y


def find_ref(yml, role, name_pat, require=None):
    for l in yml.splitlines():
        mt = re.match(rf'\s*- {role} "({name_pat})"(.*)', l)
        if mt and (require is None or require in l):
            r = re.search(r"\[ref=(\w+)\]", l)
            if r:
                return r.group(1)
    raise SystemExit(f"ref not found: {role} /{name_pat}/")


m.initialize()

# 1
t, _, _ = call("browser_navigate", {"url": URL})
y = get_yaml(t)
if y is None or 'button "Reject all"' not in y:
    y = snap(None)
try:
    call("browser_click", {"element": "Reject all", "target": find_ref(y, "button", "Reject all")})
    time.sleep(2)
except SystemExit as e:
    print("no cookie dialog:", e)
old = snap("old.yml", {"boxes": True})
OLD = find_ref(old, "combobox", r"Change ticket type[^\"]*")
print("OLD =", OLD)

# 2
call("browser_click", {"element": "Change ticket type", "target": OLD})
s2 = snap(None)
call("browser_click", {"element": "One way", "target": find_ref(s2, "option", "One way")})

# 3 (stale ref)
call("browser_click", {"element": "Change ticket type", "target": OLD})

# 4
new = snap("new.yml", {"boxes": True})
_, imgs, _ = call("browser_take_screenshot", {"type": "png", "scale": "device"})
if imgs:
    open(f"{OUT}/new.png", "wb").write(imgs[0])
NEW = find_ref(new, "combobox", r"Change ticket type[^\"]*")
print("NEW =", NEW)

# 5
call("browser_click", {"element": "Change ticket type", "target": NEW})
call("browser_press_key", {"key": "Escape"})
call("browser_close")
m.close()

print("--- old.yml"); print("\n".join(l for l in old.splitlines() if "Change ticket type" in l))
print("--- new.yml"); print("\n".join(l for l in new.splitlines() if "Change ticket type" in l))
print("--- errors:", errors)
lines = [json.loads(l) for l in open(f"{OUT}/rpc.jsonl")]
for tool, rid in errors:
    for l in open(f"{OUT}/rpc.jsonl"):
        d = json.loads(l)
        if d["dir"] == "recv" and d["msg"].get("id") == rid:
            print(f"--- raw response id={rid} ({tool})"); print(l.strip())
