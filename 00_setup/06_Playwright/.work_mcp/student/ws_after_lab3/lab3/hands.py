import sys, re, json, time
sys.path.insert(0, "/workspace")
from mcp_client import MCP

OUT = "/workspace/lab3/"
m = MCP(OUT + "mcp_log.jsonl")
m.initialize()
actions = open(OUT + "actions.txt", "w")
latest = {"snap": ""}


def yaml_of(text):
    mm = re.search(r"### Snapshot\s*```yaml\n(.*?)```", text, re.S)
    return mm.group(1) if mm else None


def call(tool, args=None):
    r = m.call(tool, args or {})
    t = r["text"]
    code = re.findall(r"^await page.*$", t, re.M)
    has = "### Snapshot" in t
    actions.write(f"TOOL: {tool}\nARGS: {json.dumps(args or {}, ensure_ascii=False)}\n"
                  f"CODE: {json.dumps(code, ensure_ascii=False)}\nisError: {r['is_error']}\n"
                  f"has_snapshot: {has}\n---\n")
    actions.flush()
    y = yaml_of(t)
    if y is not None:
        latest["snap"] = y
    if r["is_error"]:
        print("ERROR", tool, t[:500])
    return r


def snap(name, args=None):
    r = call("browser_snapshot", args)
    y = yaml_of(r["text"])
    if y is None:
        raise SystemExit("no snapshot in response: " + r["text"][:500])
    open(OUT + name, "w").write(y)
    return y


def find_ref(yml, pattern, must=None, avoid=None):
    for line in yml.splitlines():
        if re.search(pattern, line) and (must is None or must in line) and (avoid is None or avoid not in line):
            mm = re.search(r"\[ref=([^\]]+)\]", line)
            if mm:
                return mm.group(1), line.strip()
    raise SystemExit(f"ref not found for {pattern!r}")


def click(yml, pattern, desc, **kw):
    ref, line = find_ref(yml, pattern, **kw)
    print("click", desc, ref, "<-", line)
    return call("browser_click", {"element": desc, "target": ref})


# 1
call("browser_navigate", {"url": "https://www.google.com/travel/flights?hl=en"})
time.sleep(2)
pre = snap("s1.yml")
try:
    ref, line = find_ref(pre, r'button "Reject all"')
    print("reject", ref, line)
    call("browser_click", {"element": "Reject all", "target": ref})
    time.sleep(2)
    y1 = snap("s1.yml")
except SystemExit:
    print("no cookie dialog")
    y1 = pre
# 2
click(y1, r'combobox "Change ticket type', "Change ticket type")
y2 = snap("s2.yml")
click(y2, r'option "One way"', "One way")
y3 = snap("s3.yml")
# 3
click(y3, r'combobox "Where from\?', "Where from?")
y4 = snap("s4.yml")
ref, line = find_ref(y4, r"combobox", must="[expanded]")
print("type", ref, "<-", line)
call("browser_type", {"element": "Where from? input", "target": ref, "text": "BKK"})
time.sleep(1)
y5 = snap("s5.yml")
click(y5, r'option "Suvarnabhumi Airport \(BKK\)', "Suvarnabhumi Airport (BKK)")
# 4
snap("final.yml", {"boxes": True})
r = call("browser_take_screenshot", {"type": "png", "scale": "device"})
if r["images"]:
    open(OUT + "final.png", "wb").write(r["images"][0])
else:
    print("no image", r["text"][:300])
print("close code", m.close())
