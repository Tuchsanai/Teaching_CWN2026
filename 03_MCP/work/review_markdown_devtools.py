from pathlib import Path
import asyncio,json,base64,subprocess,urllib.request,time
from markdown_it import MarkdownIt
from playwright.async_api import async_playwright
root=Path.cwd(); out=root/'work'/'final-devtools-review';out.mkdir(exist_ok=True)
s=(root/'readme.md').read_text(); md=MarkdownIt('commonmark',{'html':True}).enable('table'); tokens=md.parse(s); code=[x.content for x in tokens if x.type=='fence']
html='''<!doctype html><html lang="th"><meta charset="utf-8"><base href="/"><title>MCP lesson — Markdown review</title><style>body{font-family:Arial,"Noto Sans Thai",sans-serif;line-height:1.65;max-width:1120px;margin:32px auto;padding:0 24px;color:#17202a}pre{padding:18px;background:#f3f5f7;border:1px solid #dce1e6;white-space:pre-wrap;overflow-wrap:anywhere}code{font-family:monospace;font-size:14px}table{border-collapse:collapse;width:100%;display:block;overflow-x:auto}th,td{padding:9px;border:1px solid #ccd2d8}img{max-width:100%;height:auto}audio{width:100%}h2{border-bottom:2px solid #ddd;padding-top:25px}a{color:#075db8}</style><body>'''+md.render(s)+'</body></html>'
(out/'readme.html').write_text(html)
port=8877
try: urllib.request.urlopen(f'http://127.0.0.1:{port}/work/final-devtools-review/readme.html',timeout=2)
except Exception:
 log=(out/'http-server.log').open('a');p=subprocess.Popen(['/opt/venv/bin/python','-m','http.server',str(port),'--bind','127.0.0.1','--directory',str(root)],stdout=log,stderr=log,start_new_session=True);(out/'http-server.pid').write_text(str(p.pid));time.sleep(1)
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.connect_over_cdp('http://127.0.0.1:9222');context=browser.contexts[0];page=await context.new_page();await page.set_viewport_size({'width':1440,'height':1100})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(f'http://127.0.0.1:{port}/work/final-devtools-review/readme.html',wait_until='networkidle')
  cdp=await context.new_cdp_session(page)
  check='''JSON.stringify({title:document.title,codes:Array.from(document.querySelectorAll('pre code'),x=>x.textContent),images:Array.from(document.images,x=>({src:x.getAttribute('src'),ok:x.complete&&x.naturalWidth>0})),audio:Array.from(document.querySelectorAll('audio'),x=>({src:x.getAttribute('src'),readyState:x.readyState})),overflow:document.documentElement.scrollWidth>innerWidth,headings:Array.from(document.querySelectorAll('h2,h3,h4'),x=>x.textContent)})'''
  d=await cdp.send('Runtime.evaluate',{'expression':check,'returnByValue':True});result=json.loads(d['result']['value']);result['code_count_expected']=len(code);result['code_content_matches']=result.pop('codes')==code;result['page_errors']=errors
  for chapter in ['ch3','ch4']:
   await cdp.send('Runtime.evaluate',{'expression':f'document.getElementById({json.dumps(chapter)}).scrollIntoView()'});await page.wait_for_timeout(300)
   pic=await cdp.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False});(out/(chapter+'.png')).write_bytes(base64.b64decode(pic['data']))
  (out/'devtools-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:result[k] for k in ['code_count_expected','code_content_matches','overflow','page_errors']}));print('IMAGES',len(result['images']),'BROKEN',sum(not x['ok'] for x in result['images']))
  await page.close();await browser.close()
asyncio.run(main())
