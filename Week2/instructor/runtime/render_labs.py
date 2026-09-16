"""Render one self-contained HTML guide per Lab from README.md only."""
from pathlib import Path
import re,html
import mistune
from lab_paths import LAB_DIRS
ROOT=Path(__file__).resolve().parents[2]
CSS_EXTRA='''
html{scroll-behavior:auto}body{line-height:1.8}.document{max-width:1100px;margin:auto}h2,h3,a[id]{scroll-margin-top:32px}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:1.5rem 0;padding:1rem 1.2rem;border:1px solid #cfd6df;border-radius:12px;background:#f8fafc}summary{cursor:pointer;font-weight:700;font-size:1.1rem;color:#16385c}details[open]>summary{margin-bottom:1rem}table{min-width:0!important}th,td{overflow-wrap:anywhere}.copy,.csv{margin:.4rem 0 1.2rem;cursor:pointer;padding:.5rem .9rem;border:1px solid #8ca4bd;border-radius:8px;background:#edf5ff;color:#123754;font:inherit}pre code{white-space:pre-wrap}.guide-nav{display:flex;flex-wrap:wrap;gap:1rem}#copy-status{min-height:1.5em;font-size:.9rem;color:#335673}@media print{button,.guide-nav,#copy-status{display:none}details{background:white}article.document{max-width:none}a{overflow-wrap:anywhere}}
'''
JS=r'''
const status=document.getElementById('copy-status');
function copyButton(source,label){const button=document.createElement('button');button.className='copy';button.textContent=label;button.type='button';button.onclick=async()=>{const value=source.textContent;let ok=false;try{await navigator.clipboard.writeText(value);ok=true}catch{const area=document.createElement('textarea');area.value=value;area.style.position='fixed';area.style.opacity='0';document.body.append(area);area.select();ok=document.execCommand('copy');area.remove()}status.textContent=ok?'คัดลอกข้อความแล้ว':'เลือกข้อความในกรอบแล้วคัดลอกด้วยตนเอง';button.textContent=ok?'คัดลอกแล้ว ✓':label;setTimeout(()=>button.textContent=label,2000)};return button}
for(const pre of document.querySelectorAll('pre'))pre.after(copyButton(pre,'คัดลอกข้อความ'));
for(const cell of document.querySelectorAll('td:first-child')){if(/^\.\/(shop|learn) [a-zA-Z -]+$/.test(cell.textContent.trim())){const code=document.createElement('code');code.textContent=cell.textContent.trim();cell.replaceChildren(code);cell.append(document.createElement('br'),copyButton(code,'คัดลอกคำสั่ง'))}}

function reveal(){const id=decodeURIComponent(location.hash.slice(1));if(!id)return;const el=document.getElementById(id);if(!el)return;let parent=el.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement}if(el.nextElementSibling?.tagName==='DETAILS')el.nextElementSibling.open=true;el.scrollIntoView()}
addEventListener('hashchange',reveal);document.addEventListener('click',event=>{const link=event.target.closest('a[href^="#"]');if(link&&link.hash===location.hash)reveal()});reveal();
function exportCSV(table,name){const headers=['source_id','order_id','product','days_since_receipt','stated_condition_or_evidence'];const rows=[headers,...[...table.querySelectorAll('tbody tr')].map(tr=>[...tr.cells].map(td=>td.textContent.trim()))];const csv='\ufeff'+rows.map(row=>row.map(v=>'"'+v.replaceAll('"','""')+'"').join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
for(const variant of ['A','B','C']){let el=document.getElementById('orders-'+variant);while(el&&!el.querySelector('table'))el=el.nextElementSibling;if(!el)continue;const table=el.querySelector('table'),button=document.createElement('button');button.className='csv';button.textContent='ดาวน์โหลดคำสั่งซื้อชุด '+variant+' (CSV)';button.onclick=()=>exportCSV(table,'orders-'+variant+'.csv');el.after(button)}
let closed=[];addEventListener('beforeprint',()=>{closed=[...document.querySelectorAll('details:not([open])')];closed.forEach(d=>d.open=true)});addEventListener('afterprint',()=>{closed.forEach(d=>d.open=false);closed=[]});
'''
def render_all():
    style=re.search(r'<style>(.*?)</style>',(ROOT/'README.html').read_text(),re.S).group(1)
    markdown=mistune.create_markdown(escape=False,plugins=['table','strikethrough'])
    for folder in LAB_DIRS.values():
        p=ROOT/folder/'README.md';source=p.read_text();content=markdown(source)
        # Keep true dataset attachments as .md; link readable companion guides as HTML.
        def rewrite(match):
            target=match[1];other=(p.parent/target).resolve()
            if other.suffix=='.md' and other.with_suffix('.html').exists():target=target[:-3]+'.html'
            return 'href="'+target+(match[2] or '')+'"'
        content=re.sub(r'href="([^"#]+)(#[^"]*)?"',rewrite,content)
        content=content.replace('<table>','<div class="table-wrap"><table>').replace('</table>','</table></div>')
        title=source.splitlines()[0].lstrip('# ')
        output='<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>'+html.escape(title)+'</title><style>'+style+CSS_EXTRA+'</style></head><body><main><article class="document"><nav class="guide-nav"><a href="../index.html">สไลด์ Week2</a><a href="#contents">สารบัญ Lab</a><a href="README.md" download>ดาวน์โหลด Markdown</a><a href="../scorecard.html">บันทึกคะแนน</a></nav><p id="copy-status" role="status" aria-live="polite"></p>'+content+'</article></main><script>'+JS+'</script></body></html>'
        p.with_suffix('.html').write_text(output)
    print('Rendered 3 two-file Lab guides with embedded datasets and copy controls.')
if __name__=='__main__':render_all()
