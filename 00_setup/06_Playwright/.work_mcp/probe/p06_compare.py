# วัดเทียบ playwright-cli vs playwright-mcp: action เดียวกันบน Google Flights (open/navigate, snapshot, click ticket type)
import json, os, re, subprocess, time
from mcp_client import MCPClient
CLI_DIR = "/workspace/.probe_mcp/cli"
os.makedirs(CLI_DIR + "/.playwright", exist_ok=True)
json.dump({"outputDir": CLI_DIR + "/pwcli-out", "browser": {"browserName": "chromium",
           "launchOptions": {"chromiumSandbox": False},
           "contextOptions": {"viewport": {"width": 1920, "height": 1080}, "deviceScaleFactor": 2, "locale": "en-US"}}},
          open(CLI_DIR + "/.playwright/cli.config.json", "w"), indent=2)
URL = "https://www.google.com/travel/flights?hl=en"
rows = []
def meas(kind, run, action, out, dt, extra=""):
    b = len(out.encode()); l = out.count("\n") + (0 if out.endswith("\n") or not out else 1)
    rows.append({"kind": kind, "run": run, "action": action, "bytes": b, "lines": l, "sec": round(dt, 3), "extra": extra})
    with open(f"p06_{kind}_run{run}_{action}.txt", "w") as f: f.write(out)

def cli(*args):
    t = time.time()
    r = subprocess.run(["playwright-cli", *args], cwd=CLI_DIR, capture_output=True, text=True, timeout=180)
    return r.stdout + r.stderr, time.time() - t, r.returncode

for run in (1, 2):
    # ---- CLI ----
    out, dt, rc = cli("open", URL); meas("cli", run, "open", out, dt, f"rc={rc}")
    out, dt, rc = cli("snapshot"); meas("cli", run, "snapshot", out, dt, f"rc={rc}")
    ref = re.search(r'combobox "Change ticket type[^\n]*\[ref=(\w+)\]', out)
    # CLI snapshot พิมพ์ลิงก์ไฟล์? ถ้าใช่ อ่านไฟล์
    m = re.search(r"\[Snapshot\]\(([^)]+)\)", out)
    snapfile = open(os.path.join(CLI_DIR, m.group(1))).read() if m else ""
    if m: meas("cli", run, "snapshot_file", snapfile, 0)
    ref = ref or re.search(r'combobox "Change ticket type[^\n]*\[ref=(\w+)\]', snapfile)
    out, dt, rc = cli("snapshot", "--filename=snap_named.yml"); meas("cli", run, "snapshot_filename", out, dt, f"rc={rc}")
    out, dt, rc = cli("click", ref.group(1)); meas("cli", run, "click", out, dt, f"rc={rc} ref={ref.group(1)}")
    m = re.search(r"\[Snapshot\]\(([^)]+)\)", out)
    if m: meas("cli", run, "click_autofile", open(os.path.join(CLI_DIR, m.group(1))).read(), 0)
    out, dt, rc = cli("close"); meas("cli", run, "close", out, dt, f"rc={rc}")
    # ---- MCP ----
    t = time.time()
    c = MCPClient(["/usr/bin/playwright-mcp", "--config", "/workspace/.probe_mcp/mcp.config.json"], f"p06_mcp_run{run}.jsonl")
    c.initialize(); c.list_tools()
    rows.append({"kind": "mcp", "run": run, "action": "spawn+initialize+tools/list", "bytes": None, "lines": None, "sec": round(time.time() - t, 3), "extra": ""})
    r = c.call("browser_navigate", {"url": URL}); tx = MCPClient.text(r); meas("mcp", run, "navigate", tx, r["_elapsed"], f"rpc_bytes={r['_bytes']}")
    m = re.search(r"\[Snapshot\]\(([^)]+)\)", tx)
    if m: meas("mcp", run, "navigate_autofile", open(os.path.join("/workspace/.probe_mcp", m.group(1))).read(), 0)
    r = c.call("browser_snapshot", {}); tx = MCPClient.text(r); meas("mcp", run, "snapshot", tx, r["_elapsed"], f"rpc_bytes={r['_bytes']}")
    ref = re.search(r'combobox "Change ticket type[^\n]*\[ref=(\w+)\]', tx)
    r = c.call("browser_snapshot", {"filename": "p06_named.yml"}); tx = MCPClient.text(r); meas("mcp", run, "snapshot_filename", tx, r["_elapsed"], f"rpc_bytes={r['_bytes']}")
    r = c.call("browser_click", {"target": ref.group(1), "element": "Change ticket type"}); tx = MCPClient.text(r); meas("mcp", run, "click", tx, r["_elapsed"], f"rpc_bytes={r['_bytes']} ref={ref.group(1)}")
    m = re.search(r"\[Snapshot\]\(([^)]+)\)", tx)
    if m: meas("mcp", run, "click_autofile", open(os.path.join("/workspace/.probe_mcp", m.group(1))).read(), 0)
    r = c.call("browser_close", {}); tx = MCPClient.text(r); meas("mcp", run, "close", tx, r["_elapsed"])
    t = time.time(); c.close(); rows.append({"kind": "mcp", "run": run, "action": "process exit", "bytes": None, "lines": None, "sec": round(time.time() - t, 3), "extra": ""})
json.dump(rows, open("p06_compare.json", "w"), indent=1)
with open("p06_compare.md", "w") as f:
    f.write("| kind | run | action | bytes | lines | sec | extra |\n|---|---|---|---|---|---|---|\n")
    for x in rows: f.write(f"| {x['kind']} | {x['run']} | {x['action']} | {x['bytes']} | {x['lines']} | {x['sec']} | {x['extra']} |\n")
print(open("p06_compare.md").read())
