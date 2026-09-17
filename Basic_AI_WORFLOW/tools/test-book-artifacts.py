from pathlib import Path
import json
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];results=[];errors=[];requests=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox']);c=b.new_context(offline=True,viewport={'width':1440,'height':1000});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda req:requests.append(req.url[:180]));p.goto((ROOT/'work/book-offline-test/book.html').as_uri());keys=p.evaluate('Object.keys(DATA.artifacts)')
 for i,key in enumerate(keys):
  p.evaluate('key=>openArtifact(key)',key)
  root=p.frame_locator('#viewer').locator('html');expect(root).to_have_attribute('data-book-artifact',key)
  f=[x for x in p.frames if x!=p.main_frame][0];f.wait_for_load_state('load')
  ok=f.evaluate('Array.from(document.images).every(x=>x.complete && x.naturalWidth>0)');results.append({'artifact':key,'images_loaded':ok})
  p.locator('#viewerClose').click()
  if (i+1)%20==0:print('Checked artifacts',i+1,flush=True)
 p.evaluate('showChapter(5)');p.locator('#chapter img').first.scroll_into_view_if_needed();p.screenshot(path=str(ROOT/'work/book-preview/dynamic-chapter.png'))
 b.close()
report={'artifacts_checked':len(results),'all_images_loaded':all(x['images_loaded'] for x in results),'page_errors':errors,'network_requests':[x for x in requests if x.startswith(('http:','https:'))],'results':results};(ROOT/'tools/teaching-book-artifact-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Artifact audit',len(results),report['all_images_loaded'],'errors',len(errors));assert report['all_images_loaded'] and not errors and not report['network_requests']
