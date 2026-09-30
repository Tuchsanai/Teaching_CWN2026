# อายุเบราว์เซอร์: ปิดเมื่อ process จบ? kill -9 แล้วเหลือ orphan ไหม? --isolated vs ไม่ isolated เก็บ profile ที่ไหน
import os, subprocess, time, glob, signal
from mcp_client import MCPClient
def procs(): return subprocess.run("ps -eo pid,ppid,cmd | grep -E '[c]hrom|[p]laywright-mcp' | wc -l", shell=True, capture_output=True, text=True).stdout.strip()
def profiles(): return sorted(glob.glob("/root/.cache/ms-playwright/mcp-*") + glob.glob("/tmp/playwright_chromiumdev_profile-*"))
out = open("p08_lifetime.md", "w")
def w(*a): s = " ".join(map(str, a)); print(s); out.write(s + "\n")
base = ["/usr/bin/playwright-mcp", "--browser", "chromium", "--headless", "--no-sandbox", "--output-dir", "/workspace/.probe_mcp/out_p08"]
w("before:", "procs", procs(), "profiles", profiles())
# A: สุภาพ — ปิด stdin
c = MCPClient(base + ["--isolated"], "p08_A.jsonl"); c.initialize(); c.call("browser_navigate", {"url": "https://example.com"})
w("A isolated, after navigate: procs", procs(), "profiles", profiles())
rc = c.close(); time.sleep(1); w("A after stdin close: rc", rc, "procs", procs())
# B: kill -9 server
c = MCPClient(base + ["--isolated"], "p08_B.jsonl"); c.initialize(); c.call("browser_navigate", {"url": "https://example.com"})
w("B before kill: procs", procs())
os.kill(c.proc.pid, signal.SIGKILL); time.sleep(3)
w("B after SIGKILL server: procs", procs(), subprocess.run("ps -eo pid,ppid,etime,cmd | grep -E '[c]hrom' | head -3 | cut -c1-160", shell=True, capture_output=True, text=True).stdout)
subprocess.run("pkill -f 'chrome-linux64/chrome|headless_shell' ; sleep 1", shell=True)
w("B after manual cleanup: procs", procs())
# C: ไม่ isolated
c = MCPClient(base, "p08_C.jsonl"); c.initialize(); c.call("browser_navigate", {"url": "https://example.com"})
w("C not isolated, after navigate: profiles", profiles())
c.call("browser_close", {}); c.close(); time.sleep(1)
w("C after close: procs", procs(), "profiles", profiles())
