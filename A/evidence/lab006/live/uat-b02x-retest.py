import json
import sys

from playwright.sync_api import sync_playwright

URL = sys.argv[3] if len(sys.argv) > 3 else "http://172.17.0.3:8080/index.html"
OUT_OF_SET = "<LEARNER_X>"
ALLOWED = ["<LEARNER_A>", "<LEARNER_B>", "<LEARNER_C>", "<LEARNER_D>"]
EXTRA_REJECT = ["<LEARNER_X>", "<LEARNER_E>", "LEARNER_A", "STU-9999", "<learner_x>"]


def snapshot(page):
    return page.evaluate(
        """() => ({
            booked: document.getElementById('seat-booked').textContent,
            left: document.getElementById('seat-left').textContent,
            total: document.getElementById('seat-total').textContent,
            title: document.getElementById('workshop-title').textContent,
            status: document.getElementById('status').textContent,
            kind: document.getElementById('status').getAttribute('data-kind'),
            codes: Array.from(document.querySelectorAll('#booking-list .row-code'))
                     .map(n => n.textContent.trim()),
            storage: localStorage.getItem('aiDesignWorkshop.bookings.v1'),
            scrollDiff: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        })"""
    )


def run(label, allowed_checks):
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/opt/ms-playwright/chromium-1243/chrome-linux64/chrome",
            args=["--no-sandbox"],
        )
        ctx = browser.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

        page.goto(URL, wait_until="load")
        print(f"### {label}")
        print("before-reset:", json.dumps(snapshot(page), ensure_ascii=False))

        # B02-X: press "เริ่มใหม่" then type the out-of-set code and book
        page.click("#reset-btn")
        after_reset = snapshot(page)
        print("after-reset :", json.dumps(
            {k: after_reset[k] for k in ("booked", "left", "codes", "storage")}, ensure_ascii=False))

        page.fill("#learner-code", OUT_OF_SET)
        page.click("#book-btn")
        s = snapshot(page)
        print("B02-X typed :", repr(OUT_OF_SET))
        print("B02-X result:", json.dumps(
            {k: s[k] for k in ("booked", "left", "codes", "status", "kind", "storage")}, ensure_ascii=False))
        rejected = s["booked"] == "0" and s["left"] == "3" and s["codes"] == []
        print("B02-X verdict:", "REJECTED (expected)" if rejected else "ACCEPTED (bug)")

        # reset again, then check each allowed code is still accepted one-by-one
        page.click("#reset-btn")
        if allowed_checks:
            ok_rows = []
            for code in ALLOWED:
                page.click("#reset-btn")
                page.fill("#learner-code", code)
                page.click("#book-btn")
                cur = snapshot(page)
                ok_rows.append({
                    "code": code,
                    "booked": cur["booked"],
                    "left": cur["left"],
                    "codes": cur["codes"],
                    "kind": cur["kind"],
                    "accepted": cur["booked"] == "1" and cur["left"] == "2" and cur["codes"] == [code],
                })
            print("allowed A-D :", json.dumps(ok_rows, ensure_ascii=False, indent=1))

            # 3 seats full with A,B,C -> D must be rejected as FULL (B04 must survive the fix)
            page.click("#reset-btn")
            for code in ALLOWED[:3]:
                page.fill("#learner-code", code)
                page.click("#book-btn")
            page.fill("#learner-code", ALLOWED[3])
            page.click("#book-btn")
            s3 = snapshot(page)
            print("full-case   :", json.dumps(
                {k: s3[k] for k in ("booked", "left", "codes", "status")}, ensure_ascii=False))

            # duplicate of an allowed code must still be rejected as DUPLICATE (B03)
            page.click("#reset-btn")
            page.fill("#learner-code", ALLOWED[0])
            page.click("#book-btn")
            page.fill("#learner-code", ALLOWED[0])
            page.click("#book-btn")
            s4 = snapshot(page)
            print("dup-case    :", json.dumps(
                {k: s4[k] for k in ("booked", "left", "codes", "status")}, ensure_ascii=False))

            # blank / space-only must still be rejected (B03)
            page.click("#reset-btn")
            blanks = []
            for value in ("", "   "):
                page.fill("#learner-code", value)
                page.click("#book-btn")
                cur = snapshot(page)
                blanks.append({"value": repr(value), "booked": cur["booked"], "left": cur["left"], "kind": cur["kind"]})
            print("blank-case  :", json.dumps(blanks, ensure_ascii=False))

            # out-of-set values must be rejected
            page.click("#reset-btn")
            rows = []
            for code in EXTRA_REJECT:
                page.fill("#learner-code", code)
                page.click("#book-btn")
                cur = snapshot(page)
                rows.append({
                    "code": code,
                    "booked": cur["booked"],
                    "left": cur["left"],
                    "codes": cur["codes"],
                    "kind": cur["kind"],
                    "status": cur["status"],
                })
                page.click("#reset-btn")
            print("out-of-set  :", json.dumps(rows, ensure_ascii=False, indent=1))

            # 375px must not overflow after the fix (B08 guard)
            print("scrollDiff  :", snapshot(page)["scrollDiff"])

        print("errors      :", json.dumps(errors, ensure_ascii=False))
        print("scrollDiff  :", s["scrollDiff"])
        ctx.close()
        browser.close()


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2] == "full")
