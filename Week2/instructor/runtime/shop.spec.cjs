const {test,expect}=require('@playwright/test');
const cp=require('child_process'),fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'../..'), E=path.join(ROOT,'evidence/browser');
const observations={};
function command(args){let r=cp.spawnSync(path.join(ROOT,'shop'),args.split(' '),{encoding:'utf8'});return {utc:new Date().toISOString(),command:'./shop '+args,exit:r.status,stdout:r.stdout.trim(),stderr:r.stderr.trim()};}
for(const v of ['A','B'])for(const mode of ['basic','advanced'])test(`${mode}-${v} recovery through real browser`,async({page})=>{
 const rec={scenario:`${mode}-${v}`,utc:new Date().toISOString(),viewport:{width:1440,height:1000},before:[],after:[],console:[],pageErrors:[]};
 page.on('console',m=>{if(m.type()==='error')rec.console.push(m.text())});page.on('pageerror',e=>rec.pageErrors.push(e.message));
 try{
  rec.before.push(command(`reset ${mode}-${v}`),command('preflight'),command('status'),command('check'),command('logs'));
  expect(rec.before[0].exit).toBe(0);expect(rec.before[1].stdout).toContain('PREFLIGHT OK');expect(rec.before[3].exit).toBe(1);
  rec.url=command('open').stdout;
  if(mode==='basic'){
   let error='';try{await page.goto(rec.url,{timeout:7000})}catch(e){error=e.message}
   expect(error).toContain('ERR_CONNECTION_REFUSED');rec.browser_before=error;
   await page.screenshot({path:path.join(E,`${mode}-${v}-before.png`)});
  }else{
   await page.goto(rec.url);await expect(page.locator('#version')).toHaveText('v2');await page.getByRole('button',{name:'จองสินค้า'}).click();
   await expect(page.getByRole('status')).toContainText('จองไม่สำเร็จ');rec.browser_before=await page.getByRole('status').innerText();
   await page.screenshot({path:path.join(E,`${mode}-${v}-before.png`)});
   // start does not resolve a broken update; only one root cause remains.
   const x=command('start');expect(x.stdout).toContain('ALREADY RUNNING version=v2');rec.before.push(x);
  }
  rec.after.push(command(mode==='basic'?'start':'rollback'),command('status'),command('check'));
  expect(rec.after[1].stdout).toContain('RUNNING version=v1');expect(rec.after[2].exit).toBe(0);
  await page.goto(rec.url);await expect(page.locator('#version')).toHaveText('v1');await page.getByRole('button',{name:'จองสินค้า'}).click();
  await expect(page.getByRole('status')).toContainText('จองสำเร็จ เลข W2-');rec.browser_after=await page.getByRole('status').innerText();
  const response=await page.request.get(rec.url+'/api/bookings');const b=await response.json();expect(b.items.some(x=>rec.browser_after.includes(x.booking))).toBeTruthy();rec.persisted_booking_verified=true;
  await page.screenshot({path:path.join(E,`${mode}-${v}-after.png`)});
  rec.after.push(command('logs'),command(mode==='basic'?'start':'rollback'));expect(rec.after.at(-1).stdout).toContain('ALREADY');
  expect(rec.pageErrors).toEqual([]);rec.result='PASS';
 }finally{
  rec.cleanup=[command('stop'),command('status')];fs.writeFileSync(path.join(E,`${mode}-${v}.json`),JSON.stringify(rec,null,2));
 }
});
test('reset transfer-C and final cleanup',async({page})=>{
 const r=[command('reset transfer-C'),command('status'),command('rollback')];expect(r[1].stdout).toContain('v2');
 await page.goto(command('open').stdout);await page.getByRole('button',{name:'จองสินค้า'}).click();await expect(page.getByRole('status')).toContainText('จองสำเร็จ');
 r.push(command('stop'),command('stop'),command('preflight'),command('status'));
 expect(r.at(-1).stdout).toContain('STOPPED');fs.writeFileSync(path.join(E,'transfer-C.json'),JSON.stringify(r,null,2));
});
test('instructor can provision a separate port without touching the main shop',async({page})=>{
 const os=require('os'),state=fs.mkdtempSync(path.join(os.tmpdir(),'week2-provision-test-')),env={...process.env,WEEK2_SHOP_STATE:state};
 const call=args=>{const r=cp.spawnSync(path.join(ROOT,'shop'),args.split(' '),{encoding:'utf8',env});return {args,exit:r.status,out:r.stdout.trim(),err:r.stderr.trim()}};
 const rows=[];try{
  const provision=cp.spawnSync('python3',[path.join(__dirname,'provision_shop.py'),'--port','18763'],{encoding:'utf8',env});expect(provision.status).toBe(0);rows.push({provision:provision.stdout});
  rows.push(call('reset basic-A'),call('start'));expect(rows.at(-1).exit).toBe(0);await page.goto('http://127.0.0.1:18763');await page.getByRole('button',{name:'จองสินค้า'}).click();await expect(page.getByRole('status')).toContainText('จองสำเร็จ');
  rows.push({browser:await page.getByRole('status').innerText(),main_status:command('status').stdout});expect(rows.at(-1).main_status).toContain('STOPPED');
 }finally{rows.push(call('stop'));fs.writeFileSync(path.join(E,'port-isolation.json'),JSON.stringify({utc:new Date().toISOString(),rows},null,2));fs.rmSync(state,{recursive:true,force:true})}
});
