from pathlib import Path
import json
from playwright.sync_api import sync_playwright
r=json.loads(Path('work/loop-rerun.json').read_text())
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox'])
 for name,sections in {'2_expense_claim':{'requirements':'Functional Requirements','traceability':'Traceability Matrix'},'3_clinic_migration':{'findings':'Data Quality Findings','impact':'Impact Analysis / Reuse และ Gap ส่วนเพิ่ม (updated: change request)','plan':'Plan Version Log ฉบับต่อเนื่อง (updated: change request)'}}.items():
  p=Path(r[name]);page=b.new_page(viewport={'width':1440,'height':1100});page.goto((p/'output.render.html').as_uri())
  for slug,title in sections.items():
   section=page.locator('section').filter(has=page.get_by_role('heading',name=title,exact=True));assert section.count()==1,(slug,section.count());section.screenshot(path=str(p/f'screen-{slug}.png'))
  page.close()
 b.close()
print('Document evidence screenshots captured')
