import subprocess
from pathlib import Path
r=Path(__file__).parent
with (r/'result.json').open('w') as out,(r/'stderr.log').open('w') as err:
 p=subprocess.run(['yolo2','-p','--model','opus','--effort','medium','--strict-mcp-config','--output-format','json','--no-session-persistence',(r/'request.txt').read_text()],stdin=subprocess.DEVNULL,stdout=out,stderr=err,cwd='/root/workspace/CWN/Teaching/03_MCP')
(r/'exit-code.txt').write_text(str(p.returncode))
