from pathlib import Path
from markdown_it import MarkdownIt
import re,json,html
root=Path('/root/workspace/CWN/Teaching/Basic_AI_WORFLOW');roots=json.loads((root/'work/loop-rerun.json').read_text())
md=MarkdownIt('commonmark',{'html':True}).enable('table')
style='''body{margin:0;background:#f3f5f8;color:#1c3043;font:17px/1.8 Tahoma,sans-serif}main{max-width:1180px;margin:32px auto;padding:32px 42px;background:white;border-radius:16px}h1{font-size:30px;color:#163d54}h2{font-size:24px;border-top:1px solid #dde5ec;padding-top:24px;margin-top:35px}h3{font-size:20px}table{width:100%;border-collapse:collapse;font-size:15px}th,td{padding:12px;text-align:left;vertical-align:top;border:1px solid #dde5ec}th{background:#edf4f8}img{max-width:100%;height:auto}code{background:#eef3f6}pre{white-space:pre-wrap}a{color:#09687e}.diagram{overflow:auto;padding:20px;border:1px solid #dde5ec;border-radius:12px;margin:18px 0}section{padding-bottom:6px}@media(max-width:700px){main{padding:18px}table{font-size:13px}}'''
for name in ['2_expense_claim','3_clinic_migration']:
 p=Path(roots[name]);s=(p/'output.md').read_text();i=[0]
 def diagram(m):
  i[0]+=1;return '\n<div class="diagram">'+(p/f'diagram-{i[0]}.svg').read_text()+'</div>\n'
 s=re.sub(r'```mermaid\s*\n(.*?)```',diagram,s,flags=re.S)
 body=md.render(s)
 # Wrap each H2 section for evidence captures, preserving all rendered content.
 pieces=re.split(r'(?=<h2>)',body);body=pieces[0]+''.join(f'<section data-section="{i}">{part}</section>' for i,part in enumerate(pieces[1:],1))
 (p/'output.render.html').write_text('<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loop Lab ผลงาน</title><style>'+style+'</style><main>'+body+'</main></html>')
print('Rendered expense and clinic documents with embedded SVGs')
