from pathlib import Path
import mistune
from playwright.sync_api import sync_playwright
r=Path(Path('work/dynamic-current-run.txt').read_text());md=mistune.create_markdown(plugins=['table'])
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox'])
 for p in sorted(r.glob('[123]_*')):
  content=(p/'plan-current.md').read_text();html='<html lang="th"><meta charset="utf-8"><style>body{font:19px/1.7 "Noto Sans Thai",sans-serif;color:#243e4a;padding:36px;background:#f5f8fa}main{background:white;border-radius:16px;padding:30px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #d5e3e7;padding:12px;text-align:left}th{background:#e3f1eb}h1{color:#126455}</style><main>'+md(content)+'</main></html>'
  (p/'plan.render.html').write_text(html);page=b.new_page(viewport={'width':1400,'height':1150});page.goto((p/'plan.render.html').as_uri());page.evaluate('document.fonts.ready');page.locator('main').screenshot(path=str(p/'screen-plan.png'));page.close()
 b.close()
print('Captured final Plan v1/v2 tables')
