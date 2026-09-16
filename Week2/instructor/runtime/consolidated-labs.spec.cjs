const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../..');
const E=path.join(ROOT,'evidence/build/two-file-browser');fs.mkdirSync(E,{recursive:true});
const BASE='http://127.0.0.1:18761';
const LABS=['001_LAB_System_Analysis','002_LAB_DevOps_Recovery','003_LAB_LLM_Business'];
for(const folder of LABS)for(const width of [1440,390])test(`${folder} guide ${width}`,async({page,context})=>{
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.setViewportSize({width,height:900});await page.goto(`${BASE}/${folder}/README.html`);
 await expect(page.locator('h1')).toHaveCount(1);await expect(page.getByRole('heading',{name:'สารบัญภายใน Lab',exact:true})).toBeVisible();expect(await page.locator('body').textContent()).not.toContain('[กลับ Week2](');await expect(page.locator('details[open]')).toHaveCount(0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
 await page.screenshot({path:path.join(E,folder+'-'+width+'.png')});
 const links=await page.locator('a[href]').evaluateAll(nodes=>nodes.map(a=>a.getAttribute('href')));
 for(const href of new Set(links)){if(href.startsWith('#'))expect(await page.locator(href).count(),href).toBe(1);else if(!/^[a-z]+:/i.test(href)){const response=await page.request.get(new URL(href,page.url()).href);expect(response.ok(),href).toBeTruthy()}}
 await page.getByRole('link',{name:'คำใบ้สามระดับ',exact:true}).click();await expect(page.locator('#hints + details')).toHaveAttribute('open','');
 await page.getByRole('link',{name:'เฉลยผู้สอน',exact:true}).click();await expect(page.locator('#key + details')).toHaveAttribute('open','');
 await page.locator('#contents + h2 + p').getByRole('link',{name:'Prompt พร้อมใช้',exact:true}).click();const pre=page.locator('#prompts').locator('xpath=following::pre[1]');const value=await pre.textContent();
 await pre.locator('xpath=following-sibling::button[1]').click();await expect(page.locator('#copy-status')).toHaveText('คัดลอกข้อความแล้ว');expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe(value);
 expect(errors).toEqual([]);
});
test('business CSV downloads remain available without extra files',async({page})=>{
 await page.goto(`${BASE}/${LABS[2]}/README.html#orders`);await expect(page.getByRole('button',{name:/ดาวน์โหลดคำสั่งซื้อชุด/})).toHaveCount(3);
 for(const variant of ['A','B','C']){const waiting=page.waitForEvent('download');await page.getByRole('button',{name:`ดาวน์โหลดคำสั่งซื้อชุด ${variant} (CSV)`}).click();const download=await waiting;expect(download.suggestedFilename()).toBe(`orders-${variant}.csv`);await download.saveAs(path.join(E,`orders-${variant}.csv`));}
});
test('consolidated guides work offline and keep exactly two files',async({page})=>{
 for(const folder of LABS){const remote=[];const listener=req=>{if(/^https?:/.test(req.url()))remote.push(req.url())};page.on('request',listener);await page.goto('file://'+path.join(ROOT,folder,'README.html'));await expect(page.locator('h1')).toHaveCount(1);expect(remote).toEqual([]);page.off('request',listener);expect(fs.readdirSync(path.join(ROOT,folder)).sort()).toEqual(['README.html','README.md']);}
});

for(const [index,folder] of LABS.entries())test(`${folder} copies all embedded datasets exactly`,async({page,context})=>{
 await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.goto(`${BASE}/${folder}/README.html`);
 const report=JSON.parse(fs.readFileSync(path.join(ROOT,'evidence/build/two-file-runtime.json'),'utf8'));
 const crypto=require('crypto');
 for(const variant of ['A','B','C']){
  await page.goto(`${BASE}/${folder}/README.html#data-${variant}`);
  const pre=page.locator(`#data-${variant}`).locator('xpath=following::pre[1]');
  const expected=await pre.textContent();
  expect(crypto.createHash('sha256').update(expected).digest('hex')).toBe(report.data_sha256[`lab${index+1}`][variant]);
  await pre.locator('xpath=following-sibling::button[1]').click();
  expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe(expected);
  if(variant==='A')await page.screenshot({path:path.join(E,folder+'-copy-data.png')});
 }
 await page.goto(`${BASE}/${folder}/README.html#expected`);
 await expect(page.getByRole('heading',{name:'ผลลัพธ์ที่คาดหวังและวิธีตรวจ',exact:true})).toBeVisible();
});
test('DevOps command copy keeps only the chosen command',async({page,context})=>{
 await context.grantPermissions(['clipboard-read','clipboard-write']);await page.goto(`${BASE}/${LABS[1]}/README.html#manual`);
 const buttons=page.getByRole('button',{name:'คัดลอกคำสั่ง',exact:true});expect(await buttons.count()).toBeGreaterThanOrEqual(12);
 for(const button of await buttons.all()){
  const command=await button.locator('..').locator('code').textContent();await button.click();
  expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe(command);expect(command).toMatch(/^\.\/shop /);
 }
});
test('copy fallback works when Clipboard API write is unavailable',async({page,context})=>{
 await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.addInitScript(()=>{navigator.clipboard.writeText=()=>Promise.reject(new Error('test unavailable'))});
 await page.goto(`${BASE}/${LABS[0]}/README.html#data-A`);
 const pre=page.locator('#data-A').locator('xpath=following::pre[1]');const expected=await pre.textContent();
 await pre.locator('xpath=following-sibling::button[1]').click();await expect(page.locator('#copy-status')).toHaveText('คัดลอกข้อความแล้ว');
 expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe(expected);
});
