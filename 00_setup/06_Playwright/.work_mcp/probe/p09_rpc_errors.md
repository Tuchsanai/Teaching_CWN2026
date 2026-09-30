## tools/call {"name": "browser_nope", "arguments": {}}
```json
{"result": {"content": [{"type": "text", "text": "### Error\nTool \"browser_nope\" not found"}], "isError": true}, "jsonrpc": "2.0", "id": 2}
```
## foo/bar {}
```json
{"jsonrpc": "2.0", "id": 3, "error": {"code": -32601, "message": "Method not found"}}
```
## tools/call {"name": "browser_click", "arguments": {"ref": "e1"}}
```json
{"result": {"content": [{"type": "text", "text": "### Error\nInvalid arguments for tool \"browser_click\":\n✖ Invalid input: expected string, received undefined\n  → at target"}], "isError": true}, "jsonrpc": "2.0", "id": 4}
```
## tools/call {"name": "browser_navigate", "arguments": {"url": "https://example.com", "extra": 1}}
```json
{"result": {"content": [{"type": "text", "text": "### Ran Playwright code\n```js\nawait page.goto('https://example.com');\n```\n### Page\n- Page URL: https://example.com/\n- Page Title: Example Domain\n### Snapshot\n- [Snapshot](out/page-2026-09-30T05-07-42-553Z.yml)"}]}, "jsonrpc": "2.0", "id": 5}
```
