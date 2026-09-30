# ยืนยันว่า snapshot หลัง action เป็น "ลิงก์ไฟล์" ทุกโหมด config หรือไม่
import json, os, subprocess
from mcp_client import MCPClient
variants = {
  "yolo1_style": ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox", "--output-dir", "/workspace/.probe_mcp/out_v1"],
  "no_browser_flag": ["--headless", "--isolated", "--no-sandbox"],
  "no_output_dir": ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox"],
  "snapshot_none": ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox", "--snapshot-mode", "none", "--output-dir", "/workspace/.probe_mcp/out_v3"],
  "snapshot_boxes": ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox", "--snapshot-boxes", "--output-dir", "/workspace/.probe_mcp/out_v4"],
  "codegen_none_imgomit": ["--browser", "chromium", "--headless", "--isolated", "--no-sandbox", "--codegen", "none", "--image-responses", "omit", "--output-dir", "/workspace/.probe_mcp/out_v5"],
}
out = open("p03_modes.md", "w")
for name, args in variants.items():
    c = MCPClient(["/usr/bin/playwright-mcp"] + args, f"p03_{name}.jsonl")
    c.initialize()
    out.write(f"## {name}\nargs: `{' '.join(args)}`\n\n")
    for tool, a in [("browser_navigate", {"url": "https://example.com"}),
                    ("browser_click", {"target": "e13", "element": "Learn more"}),
                    ("browser_evaluate", {"function": "() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio, lang: navigator.language})"}),
                    ("browser_snapshot", {}),
                    ("browser_take_screenshot", {"scale": "css"})]:
        r = c.call(tool, a)
        t = MCPClient.text(r)
        types = [x["type"] for x in r["result"]["content"]]
        out.write(f"### {tool} {json.dumps(a)}\nbytes={r['_bytes']} content={types} isError={r['result'].get('isError')}\n```text\n{t[:900]}\n```\n")
    c.close()
    out.write(f"cwd files: {subprocess.run('ls -d /workspace/.probe_mcp/.playwright-mcp 2>/dev/null; ls /tmp | grep -i playwright | head', shell=True, capture_output=True, text=True).stdout}\n\n")
