#!/usr/bin/env python3
"""Independent N4 UI acceptance checks; run only after N5 creates output.html.

Uses installed Python Playwright and Chromium only. Fixed test date 2030-06-18
is deliberate: N1 declares no past-date rule. No app API/storage injection.
"""
from __future__ import annotations

import json
import shutil
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
TARGET = ROOT / "output.html"
TEST_DATE = "2030-06-18"
RESULTS = {
    "node": "N4", "status": "RUNNING", "target": TARGET.as_uri(),
    "test_date": TEST_DATE, "cases": [], "access_clicks": {},
    "completion_clicks": {}, "js_errors": [], "network_requests": [],
    "measurement": {
        "access": "Trusted DOM click events; reset at home before each feature route.",
        "completion": "Includes navigation and submit/cancel clicks, excludes precondition setup.",
        "data_entry": "Native fill/select_option changes are counted separately as field operations; picker/focus gestures vary by device and are not claimed as clicks.",
        "cancel_precondition": "An existing confirmed booking created through the UI before the home/counter reset.",
        "mobile": "360x800 viewport emulation; desktop 1280x900; not a physical device test.",
    },
}

CLICK_RECORDER = """(() => {
  window.__n4Clicks = [];
  document.addEventListener('click', event => {
    if (event.isTrusted) {
      const target = event.target.closest('button, a, input, select') || event.target;
      window.__n4Clicks.push({id: target.id || '', text: (target.textContent || '').trim()});
    }
  }, true);
})();"""


def save_results():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "results.json").write_text(
        json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_from_home(page):
    page.locator("#nav-rooms").click()
    expect(page.locator("#screen-rooms")).to_be_visible()
    page.evaluate("window.__n4Clicks = []")


def events(page):
    return page.evaluate("window.__n4Clicks")


def record_access(page, feature, expected):
    observed = events(page)
    RESULTS["access_clicks"][feature] = {"count": len(observed), "events": observed}
    assert len(observed) == expected, (feature, observed, expected)
    assert len(observed) <= 2, (feature, observed)


def record_completion(page, feature, expected, fields=0):
    observed = events(page)
    RESULTS["completion_clicks"][feature] = {
        "count": len(observed), "events": observed, "data_entry_operations": fields,
    }
    assert len(observed) == expected, (feature, observed, expected)


def booking_fields(page, title, start="10:00", end="11:00", room="room-a"):
    page.locator("#booking-room").select_option(room)
    page.locator("#booking-date").fill(TEST_DATE)
    page.locator("#booking-start").fill(start)
    page.locator("#booking-end").fill(end)
    page.locator("#booking-title").fill(title)


def create_ui(page, title, start="10:00", end="11:00", room="room-a"):
    page.locator("#nav-book").click()
    booking_fields(page, title, start, end, room)
    page.locator("#booking-submit").click()
    expect(page.locator("#booking-result")).to_contain_text("จองสำเร็จ")


def availability_fields(page, start="10:00", end="11:00", room="room-a"):
    page.locator("#availability-room").select_option(room)
    page.locator("#availability-date").fill(TEST_DATE)
    page.locator("#availability-start").fill(start)
    page.locator("#availability-end").fill(end)


def check_ui(page, available, start="10:00", end="11:00"):
    page.locator("#nav-availability").click()
    availability_fields(page, start, end)
    page.locator("#availability-submit").click()
    result = page.locator("#availability-result")
    expect(result).to_contain_text("ว่าง" if available else "ไม่ว่าง")
    if available:
        expect(result).not_to_contain_text("ไม่ว่าง")


def booking_card(page, title):
    card = page.locator("#booking-list .booking-card").filter(has_text=title)
    expect(card).to_have_count(1)
    return card


def cancel_card(page, card):
    booking_id = card.get_attribute("data-booking-id")
    assert booking_id, "Booking card must expose data-booking-id"
    page.locator('[id="cancel-booking-' + booking_id + '"]').click()
    expect(card.locator(".status-badge")).to_have_text("ยกเลิกแล้ว")
    expect(page.locator('[id="cancel-booking-' + booking_id + '"]')).to_have_count(0)
    expect(page.locator("#app-notice")).to_contain_text("ยกเลิกการจองแล้ว")


def empty_state(page):
    expect(page.locator("#room-list .room-card")).to_have_count(3)
    expect(page.locator("body")).to_contain_text("ข้อมูลห้องตัวอย่าง")
    page.locator("#nav-bookings").click()
    expect(page.locator("#booking-list .empty-state")).to_be_visible()
    expect(page.locator("#booking-list .booking-card")).to_have_count(0)
    check_ui(page, True)
    expect(page.locator("#availability-schedule")).to_contain_text("ยังไม่มีการจอง")


def access_and_completion(page):
    reset_from_home(page)
    expect(page.locator("#room-list .room-card")).to_have_count(3)
    record_access(page, "rooms", 0)
    record_completion(page, "rooms", 0)

    reset_from_home(page)
    page.locator("#nav-availability").click()
    expect(page.locator("#screen-availability")).to_be_visible()
    record_access(page, "availability", 1)
    availability_fields(page)
    page.locator("#availability-submit").click()
    expect(page.locator("#availability-result")).to_contain_text("ว่าง")
    expect(page.locator("#availability-result")).not_to_contain_text("ไม่ว่าง")
    record_completion(page, "availability", 2, 4)

    reset_from_home(page)
    page.locator("#nav-book").click()
    expect(page.locator("#screen-book")).to_be_visible()
    record_access(page, "booking", 1)
    booking_fields(page, "N4-access-booking")
    page.locator("#booking-submit").click()
    expect(page.locator("#booking-result")).to_contain_text("จองสำเร็จ")
    expect(page.locator("#screen-book")).to_be_visible()
    record_completion(page, "booking", 2, 5)

    reset_from_home(page)
    page.locator("#nav-bookings").click()
    card = booking_card(page, "N4-access-booking")
    expect(card.locator(".status-badge")).to_have_text("ยืนยันแล้ว")
    record_access(page, "status", 1)
    record_completion(page, "status", 1)

    reset_from_home(page)
    page.locator("#nav-bookings").click()
    cancel_card(page, booking_card(page, "N4-access-booking"))
    expect(page.locator("#screen-bookings")).to_be_visible()
    record_access(page, "cancellation", 2)
    record_completion(page, "cancellation", 2)
    page.screenshot(path=str(ARTIFACTS / "desktop-cancelled.png"), full_page=True)


def overlaps(page):
    create_ui(page, "N4-overlap-seed")
    for number, (start, end) in enumerate([
        ("09:30", "10:30"), ("10:30", "11:30"),
        ("10:15", "10:45"), ("09:00", "12:00"), ("10:00", "11:00"),
    ]):
        check_ui(page, False, start, end)
        page.locator("#nav-book").click()
        booking_fields(page, f"N4-rejected-{number}", start, end)
        page.locator("#booking-submit").click()
        expect(page.locator("#booking-result")).to_contain_text("ช่วงเวลานี้ถูกจองแล้ว")
    page.locator("#nav-bookings").click()
    expect(page.locator("#booking-list .booking-card")).to_have_count(1)
    expect(booking_card(page, "N4-overlap-seed").locator(".status-badge")).to_have_text("ยืนยันแล้ว")


def adjacent(page):
    create_ui(page, "N4-adjacent-seed")
    for title, start, end in [("N4-adjacent-before", "09:00", "10:00"),
                              ("N4-adjacent-after", "11:00", "12:00")]:
        check_ui(page, True, start, end)
        create_ui(page, title, start, end)
    page.locator("#nav-bookings").click()
    expect(page.locator("#booking-list .booking-card")).to_have_count(3)
    expect(page.locator("#booking-list .status-confirmed")).to_have_count(3)


def invalid_intervals(page):
    message = "เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น"
    for start, end in [("10:00", "10:00"), ("11:00", "10:00")]:
        page.locator("#nav-book").click()
        booking_fields(page, "N4-invalid", start, end)
        page.locator("#booking-submit").click()
        expect(page.locator("#booking-result")).to_contain_text(message)
        page.locator("#nav-availability").click()
        availability_fields(page, start, end)
        page.locator("#availability-submit").click()
        expect(page.locator("#availability-result")).to_contain_text(message)
    page.locator("#nav-bookings").click()
    expect(page.locator("#booking-list .booking-card")).to_have_count(0)
    expect(page.locator("#booking-list .empty-state")).to_be_visible()


def persistence_and_release(page):
    title = "N4-persist-and-release"
    create_ui(page, title)
    page.reload()
    page.locator("#nav-bookings").click()
    expect(booking_card(page, title).locator(".status-badge")).to_have_text("ยืนยันแล้ว")
    check_ui(page, False)
    expect(page.locator("#availability-schedule")).to_contain_text("10:00")
    expect(page.locator("#availability-schedule")).to_contain_text("11:00")
    page.locator("#nav-bookings").click()
    cancel_card(page, booking_card(page, title))
    check_ui(page, True)
    expect(page.locator("#availability-schedule")).to_contain_text("ยังไม่มีการจอง")
    page.reload()
    page.locator("#nav-bookings").click()
    card = booking_card(page, title)
    expect(card.locator(".status-badge")).to_have_text("ยกเลิกแล้ว")
    expect(card.locator('button[id^="cancel-booking-"]')).to_have_count(0)
    check_ui(page, True)
    create_ui(page, "N4-rebook-released-slot")


def room_shortcuts(page):
    for room in ("room-a", "room-b", "room-c"):
        page.locator("#nav-rooms").click()
        page.locator(f"#room-book-{room}").click()
        expect(page.locator("#screen-book")).to_be_visible()
        expect(page.locator("#booking-room")).to_have_value(room)
        page.locator("#nav-rooms").click()
        page.locator(f"#room-availability-{room}").click()
        expect(page.locator("#screen-availability")).to_be_visible()
        expect(page.locator("#availability-room")).to_have_value(room)


def check_mobile_bounds(page):
    dimensions = page.evaluate("""() => ({
      width: window.innerWidth,
      document: document.documentElement.scrollWidth,
      body: document.body.scrollWidth,
      controls: [...document.querySelectorAll('button, input, select, .room-card, .booking-card')]
        .filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden')
        .map(el => ({id:el.id, left:el.getBoundingClientRect().left,
                     right:el.getBoundingClientRect().right}))
    })""")
    assert dimensions["document"] <= dimensions["width"] + 1, dimensions
    assert dimensions["body"] <= dimensions["width"] + 1, dimensions
    for bounds in dimensions["controls"]:
        assert bounds["left"] >= -1 and bounds["right"] <= dimensions["width"] + 1, bounds


def mobile(page):
    original_document = page.evaluate("performance.timeOrigin")
    for screen in ("rooms", "availability", "book", "bookings"):
        for nav in ("rooms", "availability", "book", "bookings"):
            expect(page.locator(f"#nav-{nav}")).to_be_visible()
        page.locator(f"#nav-{screen}").click()
        expect(page.locator(f"#screen-{screen}")).to_be_visible()
        expect(page.locator(f"#nav-{screen}")).to_have_attribute("aria-current", "page")
        for other in ("rooms", "availability", "book", "bookings"):
            if other != screen:
                expect(page.locator(f"#screen-{other}")).to_be_hidden()
        check_mobile_bounds(page)
        page.screenshot(path=str(ARTIFACTS / f"mobile-{screen}.png"), full_page=True)
    assert page.evaluate("performance.timeOrigin") == original_document, "Navigation reloaded document"
    create_ui(page, "N4-mobile-booking")
    check_ui(page, False)
    page.locator("#nav-bookings").click()
    check_mobile_bounds(page)
    cancel_card(page, booking_card(page, "N4-mobile-booking"))
    check_mobile_bounds(page)
    page.screenshot(path=str(ARTIFACTS / "mobile-cancelled.png"), full_page=True)


def run_case(browser, name, test, viewport):
    context = None
    page = None
    case = {"name": name, "status": "RUNNING", "viewport": viewport,
            "js_errors": [], "network_requests": []}
    RESULTS["cases"].append(case)
    try:
        context = browser.new_context(viewport=viewport, service_workers="block")
        context.add_init_script(CLICK_RECORDER)
        # Abort any attempted web request: this test must never depend on network.
        def route_request(route):
            if route.request.url.startswith(("http:", "https:")):
                route.abort()
            else:
                route.continue_()
        context.route("**/*", route_request)
        def on_request(request):
            if not request.url.startswith(("file:", "data:", "blob:", "about:")):
                case["network_requests"].append(request.url)
        context.on("request", on_request)
        page = context.new_page()
        page.set_default_timeout(6000)
        page.on("pageerror", lambda error: case["js_errors"].append(str(error)))
        page.on("websocket", lambda socket: case["network_requests"].append(socket.url))
        page.goto(TARGET.as_uri(), wait_until="load")
        # Inspect live DOM before selecting controls or performing any UI action.
        snapshot = page.locator("body").evaluate("element => element.outerHTML")
        (ARTIFACTS / f"{name}-initial-dom.html").write_text(snapshot, encoding="utf-8")
        case["initial_dom"] = f"artifacts/{name}-initial-dom.html"
        assert 'id="screen-rooms"' in snapshot and 'id="nav-book"' in snapshot, "Contract DOM missing"
        expect(page.locator("#screen-rooms")).to_be_visible()
        test(page)
        assert not case["js_errors"], case["js_errors"]
        assert not case["network_requests"], case["network_requests"]
        page.screenshot(path=str(ARTIFACTS / f"{name}-final.png"), full_page=True)
        case["status"] = "PASS"
    except Exception as error:
        case["status"] = "FAIL"
        case["error"] = str(error)
        case["traceback"] = traceback.format_exc()
        if page is not None:
            try:
                page.screenshot(path=str(ARTIFACTS / f"{name}-failure.png"), full_page=True)
            except Exception as screenshot_error:
                case["screenshot_error"] = str(screenshot_error)
    finally:
        if context is not None:
            try:
                context.close()
            except Exception as close_error:
                case["cleanup_error"] = str(close_error)
                case["status"] = "FAIL"
        RESULTS["js_errors"].extend({"case": name, "error": error} for error in case["js_errors"])
        RESULTS["network_requests"].extend({"case": name, "url": url} for url in case["network_requests"])
        save_results()


def main():
    browser = None
    playwright = None
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    try:
        global expect
        from playwright.sync_api import sync_playwright, expect
        assert TARGET.is_file(), "N5 must create output.html before this test runs"
        playwright = sync_playwright().start()
        executable = Path(playwright.chromium.executable_path)
        launch_options = {"headless": True}
        if executable.is_file():
            launch_options["executable_path"] = str(executable)
        else:
            installed = next((shutil.which(command) for command in
                              ("chromium", "chromium-browser", "google-chrome")
                              if shutil.which(command)), None)
            if installed:
                launch_options["executable_path"] = installed
            # Default launch also recognizes an installed Playwright headless shell.
        browser = playwright.chromium.launch(**launch_options)
        RESULTS["browser"] = {"engine": "chromium", "version": browser.version,
                              "executable": launch_options.get("executable_path", "playwright-installed-default")}
        desktop = {"width": 1280, "height": 900}
        for name, test in [
            ("empty-state", empty_state), ("access-and-completion", access_and_completion),
            ("overlap-blocked", overlaps), ("adjacent-permitted", adjacent),
            ("invalid-intervals", invalid_intervals),
            ("persistence-and-release", persistence_and_release),
            ("room-shortcuts", room_shortcuts),
        ]:
            run_case(browser, name, test, desktop)
        run_case(browser, "mobile", mobile, {"width": 360, "height": 800})
        RESULTS["status"] = "PASS" if all(case["status"] == "PASS" for case in RESULTS["cases"]) else "FAIL"
    except Exception as error:
        RESULTS["status"] = "FAIL"
        RESULTS["setup_error"] = str(error)
        RESULTS["traceback"] = traceback.format_exc()
    finally:
        for name, resource, close in [("browser", browser, "close"), ("playwright", playwright, "stop")]:
            if resource is not None:
                try:
                    getattr(resource, close)()
                except Exception as error:
                    RESULTS.setdefault("cleanup_errors", []).append({"resource": name, "error": str(error)})
                    RESULTS["status"] = "FAIL"
        RESULTS["passed"] = sum(case["status"] == "PASS" for case in RESULTS["cases"])
        RESULTS["failed"] = sum(case["status"] == "FAIL" for case in RESULTS["cases"])
        save_results()
        print(json.dumps(RESULTS, ensure_ascii=False, indent=2))
    return 0 if RESULTS["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
