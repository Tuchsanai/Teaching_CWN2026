const LAB_DIRS={"lab1": "001_LAB_System_Analysis", "lab2": "002_LAB_DevOps_Recovery", "lab3": "003_LAB_LLM_Business"};
const {test,expect}=require('@playwright/test');const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../..'), E=path.join(ROOT,'evidence/browser'),BASE='http://127.0.0.1:18761';
for(const [label,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]])test('slides '+label+' navigation, copy, overflow and links',async({page,context})=>{
 await page.setViewportSize(viewport);await context.grantPermissions(['clipboard-read','clipboard-write']);const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto(BASE+'/index.html');await expect(page.getByRole('heading',{level:1})).toContainText('แก้ปัญหา');await expect(page.locator('.slide')).toHaveCount(23);
 await page.screenshot({path:path.join(E,`slides-${label}-hero.png`)});
 const overflow=[];for(const id of await page.locator('.slide').evaluateAll(ss=>ss.map(s=>s.id))){await page.locator('#sections').selectOption(id);await expect(page.locator('#sections')).toHaveValue(id);const over=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(over)overflow.push(id)}
 expect(overflow).toEqual([]);
 await page.locator('#sections').selectOption('workflow');await page.screenshot({path:path.join(E,`slides-${label}-diagram.png`)});
 await page.locator('#sections').selectOption('starter');await page.locator('#starter .copy').first().click();await expect(page.getByRole('status')).toHaveText('คัดลอกแล้ว');expect(await page.evaluate(()=>navigator.clipboard.readText())).toContain('./learn prepare lab1 A P');
 await page.getByRole('button',{name:'หน้าถัดไป'}).click();await expect(page.locator('#sections')).toHaveValue('native');await page.getByRole('button',{name:'หน้าก่อน'}).click();await expect(page.locator('#sections')).toHaveValue('starter');
 await page.locator('body').click({position:{x:5,y:500}});await page.keyboard.press('ArrowRight');await expect(page.locator('#sections')).toHaveValue('native');
 const links=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')));const checks=[];for(const href of [...new Set(links)]){if(href.startsWith('http'))continue;if(href.startsWith('#')){expect(await page.locator(href).count()).toBe(1);continue}const r=await page.request.get(new URL(href,BASE+'/index.html').href);checks.push({href,status:r.status()});expect(r.ok(),href).toBeTruthy()}
 expect(errors).toEqual([]);fs.writeFileSync(path.join(E,`slides-${label}.json`),JSON.stringify({utc:new Date().toISOString(),url:BASE+'/index.html',viewport,overflow,errors,linkChecks:checks,nav:true,copy:true,index_sha256:require('crypto').createHash('sha256').update(fs.readFileSync(path.join(ROOT,'index.html'))).digest('hex')},null,2));
});
test('scorecard persists and downloads real CSV',async({page})=>{
 await page.goto(BASE+'/scorecard.html');await page.getByLabel('group row 1',{exact:true}).fill('ทีมทดสอบ');await page.getByLabel('lab row 1',{exact:true}).fill('lab1');await page.getByLabel('raw_12 row 1',{exact:true}).fill('9');await page.reload();await expect(page.getByLabel('group row 1',{exact:true})).toHaveValue('ทีมทดสอบ');
 await page.getByRole('button',{name:'เพิ่มแถว'}).click();await page.getByLabel('group row 2',{exact:true}).fill('=SUM(1,2)');
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'ดาวน์โหลด CSV'}).click();const download=await downloadPromise;await download.saveAs(path.join(E,'scorecard-download.csv'));const csv=fs.readFileSync(path.join(E,'scorecard-download.csv'),'utf8');expect(csv).toContain('ทีมทดสอบ');expect(csv).toContain('not-measured');expect(csv).toContain("'=SUM(1,2)");
 await page.screenshot({path:path.join(E,'scorecard.png')});fs.writeFileSync(path.join(E,'scorecard-test.json'),JSON.stringify({utc:new Date().toISOString(),url:BASE+'/scorecard.html',persist:true,download:true,formulaEscaped:true},null,2));
});
test('print layout and offline slides have no remote assets',async({page})=>{
 const requests=[];page.on('request',r=>requests.push(r.url()));await page.goto('file://'+path.join(ROOT,'index.html'));await expect(page.locator('.slide')).toHaveCount(23);expect(requests.filter(u=>/^https?:/.test(u))).toEqual([]);
 await page.emulateMedia({media:'print'});await expect(page.locator('nav')).toBeHidden();await page.pdf({path:path.join(E,'slides-print.pdf'),printBackground:true,preferCSSPageSize:true});await page.screenshot({path:path.join(E,'slides-print.png')});
});
test('lab guides desktop and mobile remain readable',async({page})=>{
 const records=[];
 for(const width of [1440,390])for(const lab of ['lab1','lab2','lab3']){
  await page.setViewportSize({width,height:900});await page.goto(BASE+`/${LAB_DIRS[lab]}/README.html`);await expect(page.getByRole('heading',{level:1})).toContainText('Lab');
  const over=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);expect(over,`${lab} width ${width}`).toBeFalsy();
  await page.screenshot({path:path.join(E,`${lab}-guide-${width}.png`)});records.push({lab,width,overflow:over});
 }
 fs.writeFileSync(path.join(E,'lab-guide-checks.json'),JSON.stringify({utc:new Date().toISOString(),records},null,2));
});
test('evidence viewer reveals raw observed output',async({page})=>{
 await page.goto(BASE+'/evidence/index.html');expect(await page.locator('article').count()).toBeGreaterThanOrEqual(16);await page.locator('article').first().getByText('อ่านคำตอบดิบ',{exact:true}).click();await expect(page.locator('article').first().locator('details').first().locator('pre')).toBeVisible();
 await page.screenshot({path:path.join(E,'evidence-viewer.png')});
});
