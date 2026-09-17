"""Build a genuinely offline, single-file teaching book from readme.md."""
from pathlib import Path
import base64,hashlib,json,mimetypes,re
from html import escape
import mistune
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'AI_Workflow_Interactive_Book.html'
md=mistune.create_markdown(plugins=['table','strikethrough'])
assets={};asset_paths={};artifacts={};pending=[];queued=set();issues=[]
def local(base,url):
 from urllib.parse import unquote
 if url.startswith(('data:','http:','https:','mailto:','javascript:','#','blob:')):return None
 p=(base/unquote(url.split('#')[0])).resolve()
 if not p.is_relative_to(ROOT) or not p.is_file():issues.append('Missing/outside: '+url);return None
 return p
def asset(p):
 key=hashlib.sha256(p.read_bytes()).hexdigest()[:20]
 if key not in assets:
  mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
  assets[key]='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
 asset_paths[p.relative_to(ROOT).as_posix()]=key
 return key
def queue(p):
 key=p.relative_to(ROOT).as_posix()
 if key not in queued:queued.add(key);pending.append(p)
 return key
mermaid_runtime=None
rendered_diagrams=0
diagram_failures=[]
def render_mermaid(code):
 global mermaid_runtime,rendered_diagrams
 if mermaid_runtime is None:
  from playwright.sync_api import sync_playwright
  pw=sync_playwright().start();browser=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox']);page=browser.new_page();page.set_content('<html><meta charset="utf-8"><body></body></html>');page.add_script_tag(path='/usr/local/lib/node_modules/mcp-excalidraw-server/node_modules/mermaid/dist/mermaid.min.js');page.evaluate("mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'strict'})");mermaid_runtime=(pw,browser,page)
 rendered_diagrams+=1
 svg=mermaid_runtime[2].evaluate('async ({code,id})=>(await mermaid.render(id,code)).svg',{'code':code,'id':'bookDiagram'+str(rendered_diagrams)})
 key=hashlib.sha256(svg.encode()).hexdigest()[:20];assets[key]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode();return key
def transform(html,base):
 soup=BeautifulSoup(html,'html.parser')
 for code in list(soup.select('pre > code.language-mermaid')):
  pre=code.parent
  try:
   key=render_mermaid(code.get_text());img=soup.new_tag('img');img['data-asset']=key;img['alt']='แผนภาพจากเอกสาร';pre.insert_before(img)
  except Exception:
   diagram_failures.append({'directory':base.relative_to(ROOT).as_posix(),'source_start':code.get_text()[:80]})
   warning=soup.new_tag('p');warning.string='แผนภาพต้นฉบับในไฟล์นี้มีข้อผิดพลาด จึงแสดงโค้ดเดิมให้ตรวจสอบ โดยไม่แก้ผลทดลองย้อนหลัง';pre.insert_before(warning)
  details=soup.new_tag('details');summary=soup.new_tag('summary');summary.string='ดูโค้ด Mermaid';details.append(summary);pre.insert_before(details);details.append(pre.extract())
 for tag in soup.find_all(['img','script','link','source','iframe']):
  attr='href' if tag.name=='link' else 'src';url=tag.get(attr)
  if not url:continue
  if url.startswith(('http:','https:','//')):raise ValueError('External resource '+url)
  p=local(base,url)
  if p:
   if tag.name=='img':tag['data-asset']=asset(p);del tag[attr];tag['loading']='lazy';tag['decoding']='async'
   elif tag.name=='script':tag.string=p.read_text();del tag['src']
   elif tag.name=='link':tag.name='style';tag.attrs={};tag.string=p.read_text()
   else:raise ValueError('Unsupported resource '+url)
 for a in soup.find_all('a',href=True):
  url=a['href'];p=local(base,url)
  if p:
   a['data-artifact']=queue(p);a['href']='#open-artifact';a['title']='เปิดดูในหนังสือ'
  elif url.startswith(('http:','https:','mailto:')):
   # Keep source attribution visible but do not require external navigation.
   a['data-external']=url;a['href']='#';a['title']='ลิงก์ภายนอก ไม่จำเป็นต่อการใช้งานหนังสือ'
 for style in soup.find_all('style'):
  if re.search(r'@import|url\(\s*[\"\']?(?:https?:|//)',style.get_text(),re.I):raise ValueError('External CSS resource')
 return str(soup)
source=(ROOT/'readme.md').read_text();main=BeautifulSoup(transform(md(source),ROOT),'html.parser')
# Stable heading identifiers, retaining hand-authored anchors such as loop-lab-1.
used=set(a.get('id') for a in main.find_all(id=True));headings=[]
for i,h in enumerate(main.find_all(re.compile('^h[1-6]$'))):
 if not h.get('id'):h['id']='heading-'+str(i)
 headings.append({'id':h['id'],'level':int(h.name[1]),'title':h.get_text(' ',strip=True)})
chapters=[];current={'id':'introduction','title':'ภาพรวมบทเรียน','html':''}
for element in list(main.contents):
 if getattr(element,'name',None)=='h2':
  chapters.append(current);current={'id':element['id'],'title':element.get_text(' ',strip=True),'html':''}
 current['html']+=str(element)
chapters.append(current)
# Explicit gallery uses current result links, never old experiment folders.
gallery=[]
for kind,label in [('loop','Loop'),('graph','Graph'),('dynamic','Dynamic')]:
 for num,title in [(1,'จองห้องประชุม'),(2,'เบิกค่าใช้จ่าย'),(3,'ย้ายระบบคลินิก')]:
  candidates=[ROOT/x for x in queued if f'lab-results/{kind}/' in x and f'/{num}_' in x and Path(x).name==('output.html' if num==1 else 'mockup.html')]
  assert len(candidates)==1,(kind,num,candidates)
  p=candidates[0];entry={'workflow':label,'title':title,'number':num,'demo':queue(p),'document':None}
  doc=p.parent/'output.md'
  if doc.exists():entry['document']=queue(doc)
  gallery.append(entry)
# Process linked documents transitively. Images are deduplicated globally.
while pending:
 p=pending.pop(0);key=p.relative_to(ROOT).as_posix();ext=p.suffix.lower();raw=p.read_text() if ext not in ['.png','.jpg','.jpeg','.webp'] else ''
 if ext in ['.png','.jpg','.jpeg','.webp','.svg']:
  html=f'<div class="image-view"><img data-asset="{asset(p)}" alt="{escape(p.name)}"></div>';kind='image'
 elif ext=='.html':html=transform(raw,p.parent);kind='html'
 elif ext=='.md':
  # Use existing verified Mermaid render when the README artifact has one.
  rendered=p.with_name(p.stem+'.render.html')
  if rendered.exists():html=transform(rendered.read_text(),p.parent)
  else:html='<main class="document">'+transform(md(raw),p.parent)+'</main>'
  kind='document'
 else:html='<main class="document"><h1>'+escape(p.name)+'</h1><pre><code>'+escape(raw)+'</code></pre></main>';kind='text'
 artifacts[key]={'title':p.name,'type':kind,'html':html,'source':raw if ext in ['.md','.json','.py'] else ''}
assert not issues,issues
if mermaid_runtime:mermaid_runtime[1].close();mermaid_runtime[0].stop()
payload={'assets':assets,'artifacts':artifacts,'chapters':chapters,'headings':headings,'gallery':gallery,'readme_sha256':hashlib.sha256(source.encode()).hexdigest()}
ui=(ROOT/'tools/teaching-book-shell.html').read_text();ui=ui.replace('<!--BOOK_DATA-->',json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
OUT.write_text(ui)
report={'file':OUT.name,'readme_sha256':payload['readme_sha256'],'chapters':len(chapters),'artifacts':len(artifacts),'embedded_images':len(assets),'gallery_demos':len(gallery),'bytes':OUT.stat().st_size,'external_resources':0,'additional_diagrams_rendered':rendered_diagrams-len(diagram_failures),'historical_diagram_errors':diagram_failures}
(ROOT/'tools/teaching-book-build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
