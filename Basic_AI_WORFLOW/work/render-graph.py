from pathlib import Path
from playwright.sync_api import sync_playwright
src='''flowchart TB
 IN["INPUT — โจทย์และข้อมูลต้นทาง"] --> N1["N1 · สกัดข้อกำหนด FR / BR"]
 N1 --> N2["N2 · Use Case<br/>แผนภาพการใช้งาน"]
 N1 --> N3["N3 · ERD<br/>แผนภาพข้อมูล"]
 N1 --> N4["N4 · Sequence<br/>แผนภาพลำดับงาน"]
 N1 -. "พบข้อกำหนดขัดแย้ง" .-> N1b["N1b · ระบุประเด็นที่ยังสรุปไม่ได้<br/>ทางเลือกตามเงื่อนไข"]
 N2 --> N5["N5 · MERGER<br/>ตรวจความสอดคล้องและรวมผล"]
 N3 --> N5
 N4 --> N5
 N1b -. "ต้องเสร็จก่อนรวม หากถูกเรียกใช้" .-> N5
 N5 --> OUT["หยุดเมื่อ N5 = DONE<br/>ส่งผลงาน + Execution Trace + ข้อขัดแย้งและหลักฐาน"]
 subgraph RULES["กติกาของ Template 2.2"]
 direction TB
 R1["ทำ Node เมื่อ Dependency ทุกตัว DONE<br/>N2–N4 ใช้ผลจาก N1 และไม่เห็นผลของกันและกัน"]
 R2["ทุก Node ส่ง node / status / output / assumptions<br/>MERGER รับเฉพาะ DONE และ contract ครบ"]
 R3["ล้มเหลว → ลองใหม่อีก 1 ครั้ง<br/>ล้มเหลวซ้ำ → FAILED · ทำต่อเฉพาะงานที่ไม่พึ่ง Node นั้น"]
 R4["ถ้าไม่มี Node ที่ทำต่อได้ → หยุดและรายงานงานที่ขาด<br/>ข้อมูลขัดกันใช้หลักฐานจาก INPUT · หลักฐานไม่พอให้คงข้อขัดแย้ง"]
 end
 classDef input fill:#f1eee8,stroke:#77716b,color:#3e3934
 classDef worker fill:#eeeafa,stroke:#8474aa,color:#473967
 classDef merge fill:#e3f3ec,stroke:#689581,color:#245946
 classDef optional fill:#fff2db,stroke:#b99862,color:#77501e
 classDef rule fill:#fafafa,stroke:#c8cdd2,color:#46525e
 class IN,N1 input
 class N2,N3,N4 worker
 class N5,OUT merge
 class N1b optional
 class R1,R2,R3,R4 rule
 style RULES fill:#ffffff,stroke:#d5dbe0
'''
p=Path('img/graph-workflow-template.mmd');p.write_text(src)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox']);page=b.new_page(viewport={'width':1600,'height':1400},device_scale_factor=1.5)
 page.set_content('<html><meta charset="utf-8"><style>body{margin:24px;background:white}svg{width:1500px;max-width:100%;height:auto}</style><body></body></html>')
 page.add_script_tag(path='/usr/local/lib/node_modules/mcp-excalidraw-server/node_modules/mermaid/dist/mermaid.min.js')
 page.evaluate("mermaid.initialize({startOnLoad:false,theme:'base',themeVariables:{fontFamily:'Noto Sans Thai, Tahoma, sans-serif',fontSize:'19px',lineColor:'#687078',edgeLabelBackground:'#ffffff'},flowchart:{curve:'stepBefore',nodeSpacing:35,rankSpacing:48,padding:20}})")
 svg=page.evaluate('async src=>(await mermaid.render("graphTemplate",src)).svg',src)
 Path('img/graph-workflow-template.svg').write_text(svg)
 page.evaluate('svg=>document.body.innerHTML=svg',svg);page.evaluate('document.fonts.ready');page.locator('svg').screenshot(path='img/graph-workflow-template.png');b.close()
p=Path('readme.md');s=p.read_text();s=s.replace('![Graph แยกงานจากข้อมูลตั้งต้น แล้วรอรวมผล](img/05-graph-fanout-fanin.png)','![Graph ตาม Template 2.2: N1 ส่งข้อกำหนดให้ N2–N4 ทำงานอิสระ N5 รวมผล พร้อมทางเลือก N1b และกติกาหยุด](img/graph-workflow-template.png)\n\n*ภาพตรงกับ Template 2.2: ลูกศรทึบคือ Dependency (งานที่ต้องรอ) และลูกศรประคือทางเลือกเมื่อพบข้อขัดแย้ง N2–N4 เป็นงานอิสระ ส่วนการรันพร้อมกันจริงขึ้นอยู่กับเครื่องมือ*')
p.write_text(s)
print('Graph diagram rendered: PNG + SVG + Mermaid source; README updated.')
