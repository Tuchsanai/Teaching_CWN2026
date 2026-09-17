import os, sys
from playwright.sync_api import sync_playwright

path = os.path.abspath("output.html")
results = {}
errors = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("file://" + path)
    pg.wait_for_selector("#room-list .room")

    # F1: แสดงห้องประชุม (0 คลิก - เห็นจากหน้าแรก)
    rooms = pg.locator("#room-list .room").count()
    results["F1_rooms_visible"] = rooms
    results["F1_clicks"] = 0

    # F2: ดูเวลาว่าง (1 คลิก: ปุ่ม 'ดูเวลาว่าง' ห้อง A)
    pg.click("button[data-action='view-availability'][data-room='R1']")
    free_before = pg.locator("#slot-grid .slot[data-status='free']").count()
    busy_before = pg.locator("#slot-grid .slot[data-status='busy']").count()
    results["F2_free_slots"] = free_before
    results["F2_busy_slots"] = busy_before
    results["F2_title"] = pg.text_content("#avail-title")
    results["F2_clicks"] = 1

    # F3: จองห้อง (2 คลิก: 'ดูเวลาว่าง' -> คลิกช่อง 10:00-11:00 -> พิมพ์ชื่อ -> ยืนยัน)
    pg.click("#slot-grid .slot[data-slot='10:00-11:00']")
    results["F3_form_visible"] = pg.is_visible("#booking-form")
    results["F3_clicks_to_reach"] = 2
    pg.fill("#booker-name", "สมชาย")
    pg.fill("#booking-purpose", "ประชุมทีม")
    pg.click("#confirm-booking")
    results["F3_message"] = pg.text_content("#message")
    results["F3_busy_after"] = pg.locator("#slot-grid .slot[data-status='busy']").count()
    results["F3_slot_status"] = pg.get_attribute("#slot-grid .slot[data-slot='10:00-11:00']", "data-status")

    # F5: แสดงสถานะการจอง (0 คลิก - ตารางในหน้าแรก)
    row = pg.locator("#booking-table tr[data-booking='BK001']")
    results["F5_status_before_cancel"] = row.get_attribute("data-status")
    results["F5_badge_before"] = row.locator(".badge").text_content()
    results["F5_clicks"] = 0

    # F4: ยกเลิกการจอง (1 คลิก: ปุ่ม 'ยกเลิกการจอง' ในตาราง)
    pg.click("button[data-action='cancel'][data-booking='BK001']")
    results["F4_clicks"] = 1
    results["F4_message"] = pg.text_content("#message")
    results["F5_status_after_cancel"] = row.get_attribute("data-status")
    results["F5_badge_after"] = row.locator(".badge").text_content()
    results["F4_slot_status_after"] = pg.get_attribute("#slot-grid .slot[data-slot='10:00-11:00']", "data-status")
    results["F4_cancel_button_gone"] = pg.locator("button[data-action='cancel'][data-booking='BK001']").count() == 0

    pg.screenshot(path="critic_final.png", full_page=True)
    b.close()

results["console_errors"] = errors
for k, v in results.items():
    print(f"{k}: {v}")
ok = (results["F1_rooms_visible"] >= 1 and results["F2_free_slots"] > 0 and results["F3_form_visible"]
      and results["F3_slot_status"] == "busy" and results["F5_status_before_cancel"] == "confirmed"
      and results["F5_status_after_cancel"] == "cancelled" and results["F4_slot_status_after"] == "free"
      and not errors)
print("OVERALL:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
