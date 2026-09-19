#!/usr/bin/env python3
"""Reproduce offline UI observations for US-09/14/21. No LAN or money claims."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shlex
import sys
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, expect

HERE = Path(__file__).resolve().parent
STEP = HERE.parent
REF = STEP.parent
LAB = REF.parent
UPSTREAM = LAB.parent / "004_LAB_Conditional_Graph_UI_Mockup/tests/ui-check.py"
helpers = runpy.run_path(str(UPSTREAM))

def utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ui(page, name):
    return page.get_by_test_id(name)

def customer(page):
    helpers["customer"](page, "01")

def login(page, role):
    helpers["login"](page, role)

def order(page, menu="m01"):
    customer(page)
    return helpers["submit"](page, menu)

def row(page, area, oid):
    return helpers["order_row"](page, area, oid)

def amount(locator):
    return helpers["money"](locator)

def pending(page, close_stock=True):
    oid = order(page)
    if close_stock:
        helpers["stock"](page, "chicken", False)
    else:
        login(page, "kitchen")
    ui(page, "btn-item-unavailable").click()
    expect(row(page, "kitchen-queue", oid)).to_contain_text("รอลูกค้าตัดสินใจ")
    customer(page)
    expect(ui(page, "customer-unavailable-alert")).to_contain_text("วัตถุดิบหมดกลางคิว")
    return oid

def check_return(page, capture):
    oid = order(page)
    initial_payment = ui(page, "payment-status").inner_text()
    initial_order = ui(page, "customer-order-status").inner_text()
    login(page, "kitchen")
    expect(ui(page, "btn-item-unavailable")).to_be_visible()
    capture(page, "kitchen-compare", full=True)
    helpers["stock"](page, "chicken", False)
    ui(page, "btn-item-unavailable").click()
    expect(row(page, "kitchen-queue", oid)).to_contain_text("รอลูกค้าตัดสินใจ")
    capture(page, "kitchen-waiting", full=True)
    customer(page)
    expect(ui(page, "customer-unavailable-alert")).to_contain_text("วัตถุดิบหมดกลางคิว")
    expect(ui(page, "btn-change-menu")).to_be_visible()
    expect(ui(page, "btn-return-item")).to_be_visible()
    expect(ui(page, "menu-item-m01")).to_be_disabled()
    expect(ui(page, "customer-order-status")).to_have_text(initial_order)
    capture(page, "customer-alert", target="customer-item-resolutions")
    ui(page, "btn-return-item").click()
    expect(ui(page, "item-resolution").get_by_test_id("item-state")).to_contain_text("คืนรายการแล้ว")
    assert amount(ui(page, "customer-adjusted-total")) == 0
    assert amount(ui(page, "resolution-order-total")) == 0
    expect(ui(page, "btn-return-item")).to_have_count(0)
    expect(ui(page, "payment-status")).to_have_text(initial_payment)
    expect(ui(page, "customer-order-status")).to_have_text(initial_order)
    login(page, "kitchen")
    expect(row(page, "kitchen-queue", oid).get_by_test_id("item-state")).to_have_count(0)
    login(page, "front")
    front = row(page, "front-orders", oid)
    assert amount(front.get_by_test_id("front-total")) == 50
    assert amount(front.get_by_test_id("front-adjusted-total")) == 0
    expect(front.get_by_test_id("refund-policy-note")).to_contain_text("ไม่ใช่การยืนยัน")
    capture(page, "front-returned", target="front-orders")
    customer(page)
    assert amount(ui(page, "customer-adjusted-total")) == 0
    expect(ui(page, "btn-return-item")).to_have_count(0)
    return {"order_id": oid, "original_snapshot": 50, "adjusted_total": 0,
            "order_state_preserved": initial_order, "payment_state_preserved": initial_payment,
            "repeat_return_control_absent": True, "kitchen_active_item_removed": True}

def check_replacement(page, capture):
    oid = pending(page)
    ui(page, "replacement-menu").select_option("m02")
    ui(page, "btn-change-menu").click()
    expect(ui(page, "customer-unavailable-alert")).to_have_count(0)
    assert amount(ui(page, "customer-adjusted-total")) == 55
    expect(ui(page, "item-resolution")).to_contain_text("ข้าวหมูทอด")
    login(page, "kitchen")
    kitchen = row(page, "kitchen-queue", oid)
    expect(kitchen).to_contain_text("ข้าวหมูทอด")
    expect(kitchen).to_contain_text("55 บาท")
    expect(kitchen).not_to_contain_text("รอลูกค้าตัดสินใจ")
    capture(page, "kitchen-replaced", full=True)
    login(page, "front")
    front = row(page, "front-orders", oid)
    assert amount(front.get_by_test_id("front-total")) == 50
    assert amount(front.get_by_test_id("front-adjusted-total")) == 55
    return {"order_id": oid, "replacement_menu": "m02", "original_snapshot": 50,
            "adjusted_total": 55, "kitchen_updated": True}

def check_catalog_snapshot(page, capture):
    oid = order(page)
    login(page, "manager")
    ui(page, "nav-menu-admin").click()
    ui(page, "admin-menu-select").select_option("m01")
    ui(page, "admin-menu-price").fill("99")
    ui(page, "btn-save-menu").click()
    login(page, "kitchen")
    ui(page, "btn-item-unavailable").click()
    customer(page)
    assert amount(ui(page, "customer-adjusted-total")) == 50
    ui(page, "btn-return-item").click()
    assert amount(ui(page, "customer-adjusted-total")) == 0
    login(page, "front")
    front = row(page, "front-orders", oid)
    assert amount(front.get_by_test_id("front-total")) == 50
    assert amount(front.get_by_test_id("front-adjusted-total")) == 0
    return {"order_id": oid, "catalog_price_after_edit": 99,
            "preserved_order_snapshot": 50, "adjusted_after_return": 0}

def check_paid_return(page, capture):
    oid = order(page)
    ui(page, "pay-cash").click()
    login(page, "front")
    front = row(page, "front-orders", oid)
    front.get_by_test_id("btn-receive-cash").click()
    expect(front.get_by_test_id("front-payment-status")).to_have_text("จ่ายแล้ว")
    login(page, "kitchen")
    ui(page, "btn-item-unavailable").click()
    customer(page)
    ui(page, "btn-return-item").click()
    expect(ui(page, "payment-status")).to_have_text("จ่ายแล้ว")
    assert amount(ui(page, "customer-adjusted-total")) == 0
    login(page, "front")
    front = row(page, "front-orders", oid)
    expect(front.get_by_test_id("front-payment-status")).to_have_text("จ่ายแล้ว")
    assert amount(front.get_by_test_id("front-total")) == 50
    assert amount(front.get_by_test_id("front-adjusted-total")) == 0
    expect(front.get_by_test_id("refund-policy-note")).to_contain_text("ยังไม่ยืนยัน")
    return {"order_id": oid, "mock_payment_state": "จ่ายแล้ว", "adjusted_total": 0,
            "real_refund_not_confirmed": True}

def check_capacity(page, capture, round_number):
    login(page, "manager")
    ui(page, "nav-capacity").click()
    ui(page, "capacity-start").fill("11:30")
    ui(page, "capacity-end").fill("13:30")
    ui(page, "capacity-limit").fill("5")
    ui(page, "capacity-wait-minutes").fill("10")
    ui(page, "btn-save-capacity").click()
    expect(ui(page, "capacity-limit")).to_have_value("5")
    customer(page)
    ids = []
    for i in range(5):
        ids.append(helpers["submit"](page))
        if i < 4:
            expect(ui(page, "capacity-message")).to_have_count(0)
    expect(ui(page, "capacity-message")).to_have_text("ครัวเต็ม รอประมาณ 10 นาที")
    if round_number == 1:
        login(page, "manager")
        ui(page, "nav-capacity").click()
        expect(ui(page, "capacity-window")).to_contain_text("ยืนยันแล้ว 5 ออเดอร์")
        capture(page, "manager-capacity", target="capacity-settings")
        customer(page)
    helpers["add_item"](page)
    expect(ui(page, "btn-submit-order")).to_be_enabled()
    before = ui(page, "capacity-message").evaluate(
        """x => !!(x.compareDocumentPosition(
        document.querySelector('[data-testid="btn-submit-order"]'))
        & Node.DOCUMENT_POSITION_FOLLOWING)""")
    assert before, "Capacity warning must precede the confirmation button"
    if round_number == 1:
        capture(page, "customer-capacity", target="capacity-message")
    ui(page, "btn-submit-order").click()
    expect(ui(page, "order-id")).to_have_text("6")
    ui(page, "btn-advance-10m").click()
    page.get_by_role("button", name="+5 นาที", exact=True).click()
    expect(ui(page, "sim-clock")).to_contain_text("12:15:00+07:00")
    expect(ui(page, "capacity-message")).to_have_count(0)
    login(page, "manager")
    ui(page, "nav-capacity").click()
    expect(ui(page, "capacity-window")).to_contain_text("12:15:00+07:00")
    expect(ui(page, "capacity-window")).to_contain_text("ยืนยันแล้ว 0 ออเดอร์")
    boundaries = ["12:00", "12:15"]
    if round_number == 1:
        for stamp in ["12:30", "12:45"]:
            ui(page, "btn-advance-10m").click()
            page.get_by_role("button", name="+5 นาที", exact=True).click()
            expect(ui(page, "capacity-window")).to_contain_text(stamp + ":00+07:00")
            expect(ui(page, "capacity-window")).to_contain_text("ยืนยันแล้ว 0 ออเดอร์")
            boundaries.append(stamp)
    return {"round": round_number, "N": 5, "X_fixture_minutes": 10,
            "confirmed_order_ids_at_threshold": ids, "warning_before_confirm": before,
            "sixth_order_allowed_in_mock": True, "observed_window_starts": boundaries,
            "counter_reset_at_next_window": True, "timezone_fixture": "+07:00"}

def check_mobile(page, capture):
    oid = pending(page)
    expect(ui(page, "btn-change-menu")).to_be_visible()
    expect(ui(page, "btn-return-item")).to_be_visible()
    sizes = page.evaluate(
        "() => ({scrollWidth:document.documentElement.scrollWidth, innerWidth:innerWidth})")
    assert sizes["scrollWidth"] <= sizes["innerWidth"] + 1, sizes
    capture(page, "mobile-customer-alert", target="customer-item-resolutions")
    return {"order_id": oid, "viewport": {"width": 375, "height": 900},
            "horizontal_overflow": False, "measured_widths": sizes}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=REF / "session/ui-mockup-v2.html")
    parser.add_argument("--run-dir", type=Path, default=HERE / "round-2")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--shots", type=Path)
    parser.add_argument("--prefix", default="screen-v2-r2")
    args = parser.parse_args()
    html = args.html.resolve()
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    out = (args.out or run_dir / "ui-feature-check-v2.json").resolve()
    shots_dir = (args.shots or run_dir / "screens").resolve()
    shots_dir.mkdir(parents=True, exist_ok=True)
    assert not out.exists(), "Never overwrite a report"
    start, tick, digest = utc(), time.monotonic(), sha(html)
    assert html.stat().st_size > 20000 and html.read_text().rstrip().endswith("</html>")
    invocation = " ".join(shlex.quote(x) for x in [sys.executable, *sys.argv])
    (run_dir / "prompt-used.md").write_text(
        "# ตรวจฟีเจอร์ UI v2 ผ่านเบราว์เซอร์\n\n"
        "ตรวจ US-09/14/21 และผลต่อ snapshot/การจ่ายด้วยข้อมูลจำลอง แยก context ทุกกรณี "
        "รัน N=5 สามรอบตามแผน ไม่ใช่หลักฐาน LAN หรือการคืนเงินจริง "
        "เวลาในภาพเป็นนาฬิกาจำลอง ส่วนเวลารันจริงอยู่ meta.json\n\n"
        "Selectors อ้างจาก DOM ที่เปิดตรวจและ ui-contract-v2.md; ใช้ helper เดิมของ LAB 004\n\n"
        "คำสั่งที่รัน:\n\n    " + invocation + "\n", encoding="utf-8")
    results, pictures = [], []
    log = (run_dir / "log.jsonl").open("x", encoding="utf-8")
    def emit(event):
        log.write(json.dumps(event, ensure_ascii=False) + "\n")
        log.flush()
    browser_version = None
    emit({"type": "browser.run.started", "at": start, "html": str(html),
          "html_sha256": digest, "script_sha256": sha(__file__),
          "upstream_helper_sha256": sha(UPSTREAM)})
    cases = [
        ("unavailable_customer_return", "return", check_return, 1280),
        ("replacement_reaches_kitchen", "replacement", check_replacement, 1280),
        ("return_uses_original_snapshot", "snapshot", check_catalog_snapshot, 1280),
        ("paid_return_keeps_payment_state", "paid-return", check_paid_return, 1280),
        *[(f"capacity_n5_round_{n}", "capacity",
           lambda page, capture, n=n: check_capacity(page, capture, n), 1280)
          for n in (1, 2, 3)],
        ("mobile_pending_resolution", "mobile", check_mobile, 375),
    ]
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            browser_version = browser.version
            try:
                expect.set_options(timeout=2500)
                for case_id, scenario, action, width in cases:
                    context = browser.new_context(viewport={"width": width, "height": 900})
                    errors, network = [], []
                    def route(request):
                        if request.request.url.startswith(("http://", "https://")):
                            network.append(request.request.url)
                            request.abort()
                        else:
                            request.continue_()
                    context.route("**/*", route)
                    page = context.new_page()
                    page.set_default_timeout(2500)
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("dialog", lambda dialog: dialog.accept())
                    at, case_tick = utc(), time.monotonic()
                    result = {"id": case_id, "scenario": scenario, "started_at": at,
                              "passed": False, "scope": "offline mock assertions only"}
                    def capture(target_page, name, full=False, target=None):
                        if target:
                            ui(target_page, target).scroll_into_view_if_needed()
                        name = args.prefix + "-" + name + ".png"
                        raw, published = run_dir / name, shots_dir / name
                        assert not raw.exists() and not published.exists(), name
                        target_page.screenshot(path=str(raw), full_page=full)
                        data = raw.read_bytes()
                        assert len(data) > 10000, "Screenshot too small: " + name
                        with published.open("xb") as stream:
                            stream.write(data)
                        pictures.append({"case": case_id, "path": str(published),
                                         "capture_source": str(raw), "bytes": len(data),
                                         "sha256": sha(raw), "viewport": {"width": width, "height": 900},
                                         "full_page": full, "url": target_page.url})
                    try:
                        page.goto(html.as_uri())
                        ui(page, "btn-reset").click()
                        result["observed"] = action(page, capture)
                        assert not errors, errors
                        assert not network, network
                        result["passed"] = True
                    except Exception as exc:
                        result["error"] = f"{type(exc).__name__}: {exc}"
                    finally:
                        result.update({"ended_at": utc(),
                                       "duration_s": round(time.monotonic() - case_tick, 6),
                                       "page_errors": errors, "network_attempts": network})
                        context.close()
                    results.append(result)
                    emit({"type": "browser.check.completed", **result})
            finally:
                browser.close()
    finally:
        end = utc()
        unchanged = digest == sha(html)
        report = {"html": str(html), "url_scheme": "file://", "html_sha256": digest,
                  "html_unchanged": unchanged, "script_sha256": sha(__file__),
                  "browser": browser_version, "checks": results,
                  "passed": sum(x["passed"] for x in results),
                  "failed": sum(not x["passed"] for x in results),
                  "expected_executions": len(cases),
                  "unique_scenarios": len(set(x[1] for x in cases)),
                  "capacity_rounds": 3, "screenshots": pictures,
                  "scope": "Offline mock: 6 scenarios, capacity repeated in 3 fresh contexts. "
                           "No LAN timing, load, production security or real-money certification."}
        with out.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        meta = {"started_at": start, "ended_at": end,
                "duration_s": round(time.monotonic() - tick, 6),
                "tool": "Python Playwright Chromium", "browser_version": browser_version,
                "input_tokens": None, "output_tokens": None,
                "html_sha256": digest, "report": str(out)}
        with (run_dir / "meta.json").open("x", encoding="utf-8") as stream:
            json.dump(meta, stream, ensure_ascii=False, indent=2)
        emit({"type": "browser.run.completed", "report": str(out), "passed": report["passed"],
              "failed": report["failed"], "html_unchanged": unchanged})
        log.close()
    print(json.dumps({"passed": report["passed"], "failed": report["failed"],
                      "unique_scenarios": report["unique_scenarios"],
                      "capacity_rounds": 3, "screenshots": len(pictures), "out": str(out)}))
    return 0 if report["failed"] == 0 and len(results) == len(cases) and unchanged else 1

if __name__ == "__main__":
    sys.exit(main())
