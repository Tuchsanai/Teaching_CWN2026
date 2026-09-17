from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,shutil
ROOT=Path(__file__).resolve().parents[1];testdir=ROOT/'work/book-offline-test';testdir.mkdir(parents=True,exist_ok=True);file=testdir/'book.html';shutil.copyfile(ROOT/'AI_Workflow_Interactive_Book.html',file)
result={'isolated_single_file':True,'network_offline':True,'checks':{},'requests':[],'page_errors':[],'console_errors':[]};screens=ROOT/'work/book-preview';screens.mkdir(exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/opt/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox']);c=b.new_context(viewport={'width':1440,'height':1000},offline=True,accept_downloads=True);p=c.new_page()
 p.on('request',lambda req:result['requests'].append(req.url[:180]));p.on('pageerror',lambda e:result['page_errors'].append(str(e)));p.on('console',lambda msg:result['console_errors'].append(msg.text[:250]) if msg.type=='error' else None)
 p.goto(file.as_uri());p.wait_for_selector('.card');p.screenshot(path=str(screens/'home.png'),full_page=True)
 result['checks']['nine_demos']=p.locator('.card').count()==9
 p.get_by_role('button',name='Graph',exact=True).click();result['checks']['filter_graph']=p.locator('.card').count()==3;p.get_by_role('button',name='ทั้งหมด',exact=True).click()
 demos=p.evaluate('DATA.gallery');result['demos']=[]
 for item in demos:
  p.locator('#gallery button[data-artifact="'+item['demo']+'"]').click();f=p.frame_locator('#viewer');f.locator('body').wait_for();f.locator('h1').wait_for()
  entry={'workflow':item['workflow'],'task':item['number'],'opened':f.locator('h1').count()>0}
  if item['number']==1:
   if item['workflow'] in ['Graph','Dynamic']:
    f.locator('#title').fill('Offline book test');f.locator('#room').select_option('GARDEN');f.locator('#start').fill('13:00');f.locator('#end').fill('14:00');f.get_by_role('button',name='ยืนยันการจอง',exact=True).click();entry['booked']='Offline book test' in f.locator('#bookings').inner_text();f.get_by_role('button',name='ยกเลิก Offline book test',exact=True).click();entry['cancelled']='ยกเลิกแล้ว' in f.locator('#bookings').inner_text()
   else:
    f.locator('#title').fill('Offline loop test');f.locator('#room').select_option('river');f.locator('#date').fill('2026-09-18');f.locator('#start').fill('13:00');f.locator('#end').fill('14:00');f.get_by_role('button',name='ยืนยันการจอง',exact=True).click();entry['booked']='Offline loop test' in f.locator('#bookings').inner_text();f.get_by_role('button',name='ยกเลิก Offline loop test',exact=True).click();entry['cancelled']='ยกเลิกแล้ว' in f.locator('#bookings').inner_text()
  entry['images_loaded']=f.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete && x.naturalWidth>0)')
  result['demos'].append(entry);p.locator('#viewerClose').click()
 p.locator('#toc button').filter(has_text='บทที่ 1 เขียน').first.click();p.locator('.reader img').first.scroll_into_view_if_needed();p.wait_for_timeout(300)
 result['checks']['chapter_images']=p.locator('#chapter img').evaluate_all('(xs)=>xs.every(x=>x.getAttribute("src").startsWith("data:"))')
 p.locator('#chapter .copy-btn').first.click();expect(p.locator('#toast')).to_have_text('คัดลอกแล้ว');result['checks']['copy_prompt']=p.locator('#toast').inner_text()=='คัดลอกแล้ว'
 p.locator('#chapter img').first.click();result['checks']['image_zoom']=p.locator('#artifactDialog').evaluate('(d)=>d.open');p.locator('#viewerFull').click();p.wait_for_timeout(150);result['checks']['viewer_fullscreen']=p.evaluate('document.fullscreenElement?.id==="viewerWrap"');p.locator('#viewerClose').click()
 p.locator('#search').fill('3.3');result['checks']['search']=p.locator('#searchResults button').count()>=4;p.locator('#searchResults button').filter(has_text='3.3 Lab:').click();result['checks']['search_navigation']=p.locator('#chapter').inner_text().find('3.3 Lab')>=0;p.locator('#search').fill('')
 p.locator('#bookFull').click();p.wait_for_timeout(150);result['checks']['book_fullscreen']=p.evaluate('document.fullscreenElement===document.documentElement');p.locator('#bookFull').click()
 p.evaluate('showChapter(0)');p.locator('#gallery button[data-artifact]').first.click()
 with p.expect_download() as info:p.locator('#viewerDownload').click()
 download=info.value;download.save_as(str(testdir/'downloaded-demo.html'));result['checks']['download_artifact']=(testdir/'downloaded-demo.html').stat().st_size>1000;p.locator('#viewerClose').click()
 p.set_viewport_size({'width':390,'height':844});p.evaluate('showChapter(0)');p.screenshot(path=str(screens/'mobile.png'),full_page=True);result['checks']['mobile_no_overflow']=p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.locator('#menu').click();p.locator('#toc button').filter(has_text='บทที่ 3 เขียน').first.click();result['checks']['mobile_chapter']=p.locator('#chapter').is_visible() and not p.locator('#side').is_visible();p.screenshot(path=str(screens/'mobile-chapter.png'))
 result['checks']['no_network_or_companion_files']=all(url==file.as_uri() or url.startswith(('data:','about:','blob:')) for url in result['requests']);result['checks']['no_page_errors']=not result['page_errors'];result['checks']['all_demo_interactions']=all(x.get('booked',True) and x.get('cancelled',True) and x['opened'] for x in result['demos'])
 b.close()
(ROOT/'tools/teaching-book-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
assert all(result['checks'].values()),'Some checks failed'
