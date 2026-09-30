import sys, re, json, time, os
sys.path.insert(0, "/workspace")
from mcp_client import MCP

OUT = "/workspace/lab2"
m = MCP(f"{OUT}/rpc.jsonl")
resp_log = open(f"{OUT}/responses.txt", "w")
raw_content = {}


def call(tool, args=None):
    args = args or {}
    # raw call so we can see content block types and sizes
    r = m._request("tools/call", {"name": tool, "arguments": args})
    if "error" in r:
        res = {"content": [{"type": "text", "text": r["error"].get("message", "")}], "isError": True}
    else:
        res = r["result"]
    content = res.get("content", [])
    text = "\n".join(c["text"] for c in content if c.get("type") == "text")
    import base64
    images = [base64.b64decode(c["data"]) for c in content if c.get("type") == "image"]
    size = len(json.dumps(res, ensure_ascii=False).encode())
    heads = re.findall(r"^### .*$", text, re.M)
    resp_log.write(f"== {tool}\n  arguments: {json.dumps(args)}\n  headings: {heads}\n"
                   f"  content types: {[c.get('type') for c in content]}\n"
                   f"  isError: {bool(res.get('isError'))}\n  size: {size} bytes "
                   f"(text {len(text.encode())}, images {[len(i) for i in images]})\n\n")
    resp_log.flush()
    return text, images, bool(res.get("isError")), heads


def section(text, name):
    mt = re.search(rf"^### {name}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    return mt.group(1) if mt else None


def get_yaml(text):
    """Return (yaml, mode) from a response's ### Snapshot section: inline fence or file link."""
    s = section(text, "Snapshot")
    if s is None:
        return None, "none"
    f = re.search(r"```(?:yaml)?\n(.*?)```", s, re.S)
    if f:
        return f.group(1), "inline"
    lk = re.search(r"\]\(([^)]+)\)", s)
    if lk:
        p = lk.group(1)
        if not os.path.isabs(p):
            p = os.path.join("/workspace/mcp-out", p)
        return open(p).read(), "file:" + lk.group(1)
    return s, "unknown"


print(m.initialize())
t, _, _, _ = call("browser_navigate", {"url": "https://www.google.com/travel/flights?hl=en"})
y, mode = get_yaml(t)
print("navigate snapshot mode:", mode)
if y and re.search(r'button "Reject all"', y):
    ref = re.search(r'button "Reject all".*?\[ref=(\w+)\]', y).group(1)
    call("browser_click", {"element": "Reject all", "ref": ref})
time.sleep(2)

# 2 back-to-back
t, _, _, _ = call("browser_snapshot", {"boxes": True})
y, mode = get_yaml(t)
open(f"{OUT}/flights.yml", "w").write(y or "")
snap_mode = mode
_, imgs, _, _ = call("browser_take_screenshot", {"type": "png", "scale": "device"})
if imgs:
    open(f"{OUT}/flights.png", "wb").write(imgs[0])
else:
    lk = re.search(r"\]\(([^)]+\.png)\)", _ if isinstance(_, str) else "")

# 3
lines = y.splitlines()
with open(f"{OUT}/form.txt", "w") as f:
    for i, l in enumerate(lines, 1):
        if "combobox" in l or "textbox" in l or 'button "1 passenger' in l:
            f.write(f"{i}: {l}\n")

# 4
t, _, _, _ = call("browser_find", {"text": "ticket type"})
open(f"{OUT}/find.txt", "w").write(t)

# 5 ancestor with role search
idx = next(i for i, l in enumerate(lines) if 'combobox "Where from?"' in l)
ind = lambda l: len(l) - len(l.lstrip())
cur = ind(lines[idx]); anc = None
for j in range(idx - 1, -1, -1):
    if ind(lines[j]) < cur:
        cur = ind(lines[j])
        if re.match(r"\s*- search\b", lines[j]):
            anc = lines[j]; break
print("ancestor:", anc)
aref = re.search(r"\[ref=(\w+)\]", anc).group(1)
t, _, _, _ = call("browser_snapshot", {"target": aref})
py, pmode = get_yaml(t)
open(f"{OUT}/form-partial.yml", "w").write(py or "")

call("browser_close")
m.close()
resp_log.close()
print("modes: full", snap_mode, "partial", pmode)
print("lines", len(lines), len((py or "").splitlines()))
