"""CRITIC: inspect the delivered file through Python Playwright, without a server."""
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent
URL = (ROOT / 'output.html').as_uri()
errors, network, checks, paths = [], [], [], []
report = {'iteration': 1, 'browser': 'headless Chromium', 'url': URL}

def check(label):
    checks.append(label)
    print('PASS:', label)

def open_page(browser, width=1440, height=1100):
    context = browser.new_context(viewport={'width': width, 'height': height}, offline=True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('request', lambda req: network.append(req.url) if not req.url.startswith('file:') else None)
    page.goto(URL, wait_until='load')
    return context, page

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context, page = open_page(browser)
            print('DOM:', json.dumps(page.locator('main').inner_text(), ensure_ascii=False))
            page.get_by_role('link', name='ห้องประชุม', exact=True).click()
            expect(page.get_by_role('article')).to_have_count(3)
            check('แสดงห้องประชุม: คลิกเมนูแล้วพบ 3 ห้อง')
            room = page.get_by_role('article', name='ห้องต้นไม้', exact=True)
            expect(room.get_by_role('button')).to_have_count(4)
            slot = page.get_by_role('button', name='ว่าง · จอง ห้องต้นไม้ 09:00–10:00', exact=True)
            expect(slot).to_be_enabled()
            expect(page.get_by_role('button', name='ไม่ว่าง ห้องแสงตะวัน 10:00–11:00', exact=True)).to_be_disabled()
            expect(page.locator('#free-count')).to_have_text('11')
            check('เวลาว่าง: พบ 11 ช่วงว่าง และ 1 ช่วงไม่ว่างที่กดจองไม่ได้')
            slot.click()
            expect(page.get_by_role('dialog')).to_contain_text('ห้องต้นไม้')
            expect(page.get_by_role('dialog')).to_contain_text('09:00–10:00')
            page.get_by_role('button', name='ยืนยันการจอง', exact=True).click()
            booking = page.get_by_role('group', name='การจอง ห้องต้นไม้ 09:00–10:00', exact=True)
            expect(booking).to_contain_text('ยืนยันแล้ว')
            expect(page.locator('#booking-list .booking-row')).to_have_count(2)
            expect(page.locator('#free-count')).to_have_text('10')
            expect(page.get_by_role('button', name='ไม่ว่าง ห้องต้นไม้ 09:00–10:00', exact=True)).to_be_disabled()
            check('สร้างการจอง: 2 คลิก, สถานะยืนยันแล้ว, เวลาว่าง 11 → 10, ป้องกันจองซ้ำ')
            booking_id = booking.get_attribute('data-booking-id')
            page.screenshot(path=str(ROOT / 'evidence-booked.png'), full_page=True)
            booking.get_by_role('button', name='ยกเลิกการจอง ห้องต้นไม้ 09:00–10:00', exact=True).click()
            page.get_by_role('button', name='ยืนยันการยกเลิก', exact=True).click()
            expect(booking).to_have_attribute('data-booking-id', booking_id)
            expect(booking).to_contain_text('ยกเลิกแล้ว')
            expect(booking.get_by_role('button')).to_have_count(0)
            expect(slot).to_be_enabled()
            expect(page.locator('#free-count')).to_have_text('11')
            check('ยกเลิกรายการเดียวกับที่เพิ่งสร้าง: 2 คลิก, ยืนยันแล้ว → ยกเลิกแล้ว, เวลาว่าง 10 → 11')
            page.get_by_role('link', name='การจองของฉัน', exact=True).click()
            expect(booking).to_be_visible()
            check('แสดงสถานะ: คลิกเมนูการจองของฉันแล้วเห็นยกเลิกแล้ว')
            page.screenshot(path=str(ROOT / 'evidence-cancelled.png'), full_page=True)
            page.reload()
            expect(page.get_by_role('group', name='การจอง ห้องต้นไม้ 09:00–10:00', exact=True)).to_contain_text('ยกเลิกแล้ว')
            check('รีโหลดไฟล์: สถานะการยกเลิกยังคงอยู่')
            context.close()

            # Each feature starts with a separate fresh browser context on the first page.
            for feature in ['rooms', 'availability', 'book', 'cancel', 'status']:
                context, page = open_page(browser)
                steps = []
                def click(locator, label):
                    locator.click()
                    steps.append(label)
                if feature == 'rooms':
                    click(page.get_by_role('link', name='ห้องประชุม', exact=True), 'ห้องประชุม')
                    expect(page.get_by_role('article')).to_have_count(3)
                    name = 'แสดงห้องประชุม'
                elif feature == 'availability':
                    click(page.get_by_role('link', name='ห้องประชุม', exact=True), 'ห้องประชุม')
                    expect(page.get_by_role('button', name='ว่าง · จอง ห้องต้นไม้ 09:00–10:00', exact=True)).to_be_visible()
                    expect(page.get_by_role('button', name='ไม่ว่าง ห้องแสงตะวัน 10:00–11:00', exact=True)).to_be_disabled()
                    name = 'ดูเวลาว่าง'
                elif feature == 'book':
                    click(page.get_by_role('button', name='ว่าง · จอง ห้องต้นไม้ 09:00–10:00', exact=True), 'ช่วงว่าง ห้องต้นไม้ 09:00–10:00')
                    click(page.get_by_role('button', name='ยืนยันการจอง', exact=True), 'ยืนยันการจอง')
                    expect(page.get_by_role('group', name='การจอง ห้องต้นไม้ 09:00–10:00', exact=True)).to_contain_text('ยืนยันแล้ว')
                    name = 'สร้างการจอง'
                elif feature == 'cancel':
                    click(page.get_by_role('button', name='ยกเลิกการจอง ห้องแสงตะวัน 10:00–11:00', exact=True), 'ยกเลิกการจองรายการเริ่มต้น')
                    click(page.get_by_role('button', name='ยืนยันการยกเลิก', exact=True), 'ยืนยันการยกเลิก')
                    expect(page.get_by_role('group', name='การจอง ห้องแสงตะวัน 10:00–11:00', exact=True)).to_contain_text('ยกเลิกแล้ว')
                    name = 'ยกเลิกการจอง'
                else:
                    click(page.get_by_role('link', name='การจองของฉัน', exact=True), 'การจองของฉัน')
                    expect(page.get_by_role('group', name='การจอง ห้องแสงตะวัน 10:00–11:00', exact=True)).to_contain_text('ยืนยันแล้ว')
                    name = 'แสดงสถานะ'
                assert len(steps) <= 2
                paths.append({'feature': name, 'clicks': len(steps), 'path': 'หน้าแรก → ' + ' → '.join(steps)})
                check(f'C3 {name}: {len(steps)} คลิก; {paths[-1]["path"]}')
                context.close()

            context, page = open_page(browser, 390, 844)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.get_by_role('button', name='ว่าง · จอง ห้องต้นไม้ 09:00–10:00', exact=True).click()
            page.get_by_role('button', name='กลับ', exact=True).click()
            expect(page.locator('#booking-list .booking-row')).to_have_count(1)
            page.get_by_role('button', name='ว่าง · จอง ห้องต้นไม้ 09:00–10:00', exact=True).click()
            page.get_by_role('button', name='ยืนยันการจอง', exact=True).click()
            mobile_booking = page.get_by_role('group', name='การจอง ห้องต้นไม้ 09:00–10:00', exact=True)
            expect(mobile_booking).to_contain_text('ยืนยันแล้ว')
            mobile_booking.get_by_role('button').click()
            page.get_by_role('button', name='ยืนยันการยกเลิก', exact=True).click()
            expect(mobile_booking).to_contain_text('ยกเลิกแล้ว')
            page.screenshot(path=str(ROOT / 'evidence-mobile.png'), full_page=True)
            check('หน้าจอ 390×844: ไม่ล้นแนวนอน, กลับโดยไม่จอง, จองและยกเลิกได้')
            context.close()
            assert not errors, errors
            assert not network, network
            check('console errors=0; page errors=0; network requests=0; offline=True')
        finally:
            browser.close()
    report['criteria'] = {'C1': 'PASS', 'C2': 'PASS', 'C3': 'PASS'}
except Exception as exc:
    report['failure'] = f'{type(exc).__name__}: {exc}'
    report['criteria'] = {'C1': 'FAIL', 'C2': 'FAIL', 'C3': 'FAIL'}
    print('FAIL:', report['failure'])
finally:
    report.update(checks=checks, click_paths=paths, console_and_page_errors=errors, network_requests=network)
    (ROOT / 'critic-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    all_pass = all(v == 'PASS' for v in report['criteria'].values())
    evidence = {
        'C1': 'ทดลองครบ: แสดง 3 ห้อง, ดูเวลาว่าง, จอง, ยกเลิก, แสดงสถานะเปลี่ยน ยืนยันแล้ว → ยกเลิกแล้ว',
        'C2': f'รัน python critic_test.py ด้วย Python Playwright / headless Chromium / file:// / offline=True; console+page errors={len(errors)}, network requests={len(network)}; จองแล้ว取消รายการเดียวกันสำเร็จ; หลักฐาน critic-results.json และ evidence-booked.png / evidence-cancelled.png',
        'C3': '; '.join(f'{r["feature"]}: {r["path"]} ({r["clicks"]} คลิก)' for r in paths)
    }
    # Append immediately after the critic finishes this iteration; never overwrite history.
    with (ROOT / 'trace.md').open('a', encoding='utf-8') as trace:
        trace.write(f'\n## Iteration 1 — {datetime.now(timezone.utc).isoformat()}\n')
        trace.write('GENERATOR: สร้าง output.html แบบไฟล์เดียว ใช้ CSS/JavaScript inline มี 3 ห้องจำลอง ตารางเวลาว่าง การยืนยันจองและยกเลิก สถานะ และ localStorage; ระบุสมมติฐานในหน้าเว็บ\n')
        for c, verdict in report['criteria'].items():
            trace.write(f'CRITIC {c}: {verdict} — {evidence[c] if all_pass else report.get("failure", "ตรวจไม่ครบ")}\n')
        trace.write('วิธีนับ: เริ่มแต่ละฟีเจอร์จากหน้าแรกใน context ใหม่ นับทุกคลิกรวมปุ่มยืนยัน; ยกเลิกใช้รายการสมมติเริ่มต้น ส่วน C2 ยกเลิกรายการที่เพิ่งสร้างจริง (จอง 2 + ยกเลิก 2 = 4 คลิกรวมวงจร); การเลื่อนหน้าไม่นับเป็นคลิก\n')
        trace.write('สมมติฐาน: ข้อมูลห้อง/อุปกรณ์/ความจุ/รายการเริ่มต้นเป็นข้อมูลสมมติ ผู้ใช้ 1 คน ช่วงละ 1 ชั่วโมง 09:00–13:00 น. เริ่มวันพรุ่งนี้ตามเครื่อง และบันทึกเฉพาะเบราว์เซอร์\n')
        trace.write('หยุด: ทุกเกณฑ์ PASS\n' if all_pass else 'ต้องพิจารณา Iteration ถัดไปตามเกณฑ์ที่ FAIL\n')
    print('CRITERIA:', json.dumps(report['criteria']))
    if not all_pass:
        raise SystemExit(1)
