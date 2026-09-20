from pathlib import Path
from datetime import datetime, timezone
import subprocess,json
root=Path.cwd(); run=root/'lab-results'/'codex-setup'/('run-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')); run.mkdir(parents=True)
prompt=f'''Verify the existing MCP tools for this teaching lesson using Codex. Work only in {root}. Store evidence under {run}. Do not edit lesson or source code. Do not install packages or change persistent configuration. Do not spawn agents. Use the configured MCP tools, not direct browser libraries or simulated results.
1. Playwright MCP: open the real public URL https://www.python.org/ in a new tab, get accessibility snapshot, record final URL, title and a visible heading. Save a full-page screenshot to {run}/playwright-python-org.png. If unavailable record actual error and try https://www.wikipedia.org/ instead. Save snapshot and concise actual tool results in evidence.md.
2. Excalidraw MCP: read diagram guide, inspect existing scene and export a backup before changing anything. Open its canvas at http://127.0.0.1:8892 using Playwright MCP and keep tab open. Create a small isolated diagram with 3 boxes labeled Codex, MCP Server, Tool linked by arrows without clearing or deleting preexisting elements. Frame those new elements, screenshot inspect and fix if necessary. Export PNG and .excalidraw to allowed export directory /root/workspace/.mcp/excalidraw/diagrams with unique codex-setup-test prefix; copy exported artifacts to {run}/excalidraw-codex.png and {run}/excalidraw-codex.excalidraw. Report actual tool calls and errors. If export includes existing content, make that limitation explicit. Do not claim a file exists without checking.
3. hello-lab MCP: call add with 17 and 25 and record actual result.
4. kokoro-tts MCP: call speak for Hello students. This is a real Codex MCP test. with voice af_heart. Copy the actual returned audio file to {run}/kokoro-codex.wav and record duration and sample rate from tool result.
Write evidence.md with results, actual URLs, artifact paths, errors and precise pass/fail per check. Do not expose secrets or environment values. Final response concise Thai. These are tests of existing installed services, not a fresh installation test.'''
(run/'prompt.txt').write_text(prompt)
configs={
'mcp_servers.playwright.command':'/usr/local/bin/playwright-mcp',
'mcp_servers.playwright.args':['--cdp-endpoint','http://127.0.0.1:9222'],
'mcp_servers.excalidraw.command':'/usr/local/bin/mcp-excalidraw-server',
'mcp_servers.excalidraw.env':{'EXPRESS_SERVER_URL':'http://127.0.0.1:8892','EXCALIDRAW_NO_AUTOSTART':'1','EXCALIDRAW_EXPORT_DIR':'/root/workspace/.mcp/excalidraw/diagrams'},
'mcp_servers.hello-lab.command':'/opt/venv/bin/python',
'mcp_servers.hello-lab.args':[str(root/'labs/my-mcp-server/hello_server.py')],
'mcp_servers.kokoro-tts.command':'/opt/venv/bin/python',
'mcp_servers.kokoro-tts.args':[str(root/'labs/my-mcp-server/tts_server.py')],
'mcp_servers.kokoro-tts.env':{'KOKORO_DEVICE':'cpu'}}
def toml(v):
 if isinstance(v,dict): return '{'+', '.join(json.dumps(k)+' = '+toml(x) for k,x in v.items())+'}'
 return json.dumps(v)
cmd=['codex','exec','--skip-git-repo-check','--ephemeral','-s','workspace-write','--add-dir','/root/workspace/.mcp/excalidraw/diagrams','--json','-o',str(run/'summary.md')]
for k,v in configs.items(): cmd+=['-c',k+'='+toml(v)]
cmd+=['-']
(run/'test-config.json').write_text(json.dumps(configs,indent=2))
with (run/'events.jsonl').open('w') as out,(run/'stderr.log').open('w') as err:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True)
 (root/'work/codex-verification-state.json').write_text(json.dumps({'run':str(run),'pid':proc.pid}))
 proc.communicate(prompt)
(run/'exit-code.txt').write_text(str(proc.returncode))
print('CODEX_VERIFICATION_EXIT',proc.returncode,'RUN',run)
