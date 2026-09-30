import json
from mcp_client import MCPClient
c = MCPClient(["/usr/bin/playwright-mcp", "--config", "mcp.config.json"], "p09_rpc_errors.jsonl")
c.initialize()
with open("p09_rpc_errors.md", "w") as f:
    for method, params in [("tools/call", {"name": "browser_nope", "arguments": {}}),
                           ("foo/bar", {}),
                           ("tools/call", {"name": "browser_click", "arguments": {"ref": "e1"}}),
                           ("tools/call", {"name": "browser_navigate", "arguments": {"url": "https://example.com", "extra": 1}})]:
        r = c.request(method, params)
        r = {k: v for k, v in r.items() if not k.startswith("_")}
        f.write(f"## {method} {json.dumps(params)}\n```json\n{json.dumps(r, ensure_ascii=False)}\n```\n")
c.call("browser_close", {})
c.close()
print(open("p09_rpc_errors.md").read())
