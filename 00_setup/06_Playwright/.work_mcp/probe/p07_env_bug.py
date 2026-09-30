# ทำซ้ำอาการของ yolo1: env PLAYWRIGHT_BROWSERS_PATH ใน shared mcp.json ชี้ไป /opt/ms-playwright (ไม่มีจริง)
import os, json
from mcp_client import MCPClient
args = ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox", "--output-dir", "/workspace/.probe_mcp/out_p07"]
with open("p07_env_bug.md", "w") as f:
    for bp in ["/opt/ms-playwright", "/ms-playwright"]:
        env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=bp)
        c = MCPClient(["/usr/bin/playwright-mcp"] + args, f"p07_env_{bp.strip('/').replace('/','_')}.jsonl", env=env)
        c.initialize()
        r = c.call("browser_navigate", {"url": "https://example.com"})
        f.write(f"## PLAYWRIGHT_BROWSERS_PATH={bp}\nisError={r['result'].get('isError')}\n```text\n{MCPClient.text(r)}\n```\n")
        c.call("browser_close", {})
        c.close()
print(open("p07_env_bug.md").read())
