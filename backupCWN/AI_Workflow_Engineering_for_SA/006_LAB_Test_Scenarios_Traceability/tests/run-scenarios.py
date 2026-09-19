#!/usr/bin/env python3
"""Run isolated offline mock UI scenarios; a pass does not certify production AC."""
import argparse
import json
import os
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright, expect

TIMEOUT = 2500
ACTIONS = {"click", "fill", "expect_text", "expect_visible", "expect_hidden"}


def perform(page, step):
    action = step.get("action")
    if action not in ACTIONS or not step.get("testid"):
        raise ValueError("Unknown action or missing testid")
    target = page.get_by_test_id(step["testid"])
    if action == "click":
        target.click()
    elif action == "fill":
        # JSON uses one fill action for native input/textarea/select controls.
        value = str(step.get("value", ""))
        if target.evaluate("el => el.tagName.toLowerCase()") == "select":
            target.select_option(value)
        else:
            target.fill(value)
    elif action == "expect_text":
        if "value" not in step:
            raise ValueError("expect_text requires value")
        expect(target).to_be_visible(timeout=TIMEOUT)
        expect(target).to_contain_text(str(step["value"]), timeout=TIMEOUT)
    elif action == "expect_visible":
        expect(target).to_be_visible(timeout=TIMEOUT)
    else:
        expect(target).to_be_hidden(timeout=TIMEOUT)


def result_for(scenario, index):
    return {"id": scenario.get("id", f"invalid-{index}"),
            "us": scenario.get("us", ""), "status": "fail",
            "reason": "Not started", "screenshot": None}


def skip_reason(scenario):
    if scenario.get("automation", "auto") != "auto":
        return "automation is not auto; screenshot unavailable: not executed"
    if not scenario.get("steps"):
        return "Empty steps; screenshot unavailable: not executed"
    return None


def run_one(browser, scenario, index, html, shots):
    result = result_for(scenario, index)
    context = page = None
    blocked = []
    try:
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        def offline(route):
            if route.request.url.startswith(("http://", "https://")):
                blocked.append(route.request.url)
                route.abort()
            else:
                route.continue_()
        context.route("**/*", offline)
        page = context.new_page()
        page.set_default_timeout(TIMEOUT)
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.goto('file://' + os.path.abspath(html), timeout=10000)
        result.update(status="pass", reason="All assertions observed; mock UI only")
        for number, step in enumerate(scenario["steps"], 1):
            try:
                perform(page, step)
            except Exception as exc:
                result.update(status="fail", reason=f"Step {number}: {type(exc).__name__}: {exc}"[:2400])
                # Dependent steps stop; the next independent scenario still runs.
                break
    except Exception as exc:
        result.update(status="fail", reason=f"Setup/runtime: {type(exc).__name__}: {exc}"[:2400])
    finally:
        if page is not None:
            safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", str(result["id"]))[:100]
            shot = shots / f"{index:03d}-{safe_id}.png"
            try:
                page.screenshot(path=str(shot), full_page=True, timeout=5000)
                result["screenshot"] = str(shot)
            except Exception as exc:
                result["status"] = "fail"
                result["reason"] += f"; screenshot unavailable: {exc}"[:600]
        else:
            result["reason"] += "; screenshot unavailable: no page"
        if blocked:
            result["status"] = "fail"
            result["reason"] += "; offline violation: network request attempted"
        if context is not None:
            try:
                context.close()
            except Exception as exc:
                result["status"] = "fail"
                result["reason"] += f"; context cleanup: {exc}"[:600]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, help="Local UI v2 HTML")
    parser.add_argument("--scenarios", default="input/ui-scenarios.json")
    parser.add_argument("--out", default="work/ui-results-round-0.json")
    parser.add_argument("--shots", default="work/shots/round-0")
    parser.add_argument("--allow-fail", action="store_true", help="Exit 0 even with failed scenarios")
    args = parser.parse_args(argv)
    out, shots = Path(args.out), Path(args.shots)
    try:
        data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
        scenarios = data.get("scenarios") if isinstance(data, dict) else data
        if not isinstance(scenarios, list) or any(not isinstance(s, dict) for s in scenarios):
            raise ValueError("Expected an array of scenario objects")
        if out.exists() or (shots.exists() and (not shots.is_dir() or any(shots.iterdir()))):
            raise ValueError("Use a new report path and a new/empty screenshot directory")
        if out.resolve() in {Path(args.html).resolve(), Path(args.scenarios).resolve()}:
            raise ValueError("Output must differ from inputs")
        out.parent.mkdir(parents=True, exist_ok=True)
        shots.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        parser.error(str(exc))
    results = [None] * len(scenarios)
    for index, scenario in enumerate(scenarios):
        reason = skip_reason(scenario)
        if reason:
            results[index] = dict(result_for(scenario, index), status="skip", reason=reason)
    engine, fallback = "not-needed", None
    if any(r is None for r in results):
        try:
            with sync_playwright() as playwright:
                browser = None
                try:
                    try:
                        browser = playwright.chromium.launch()
                        engine = "launch"
                    except Exception as exc:
                        fallback = str(exc)[:1200]
                        browser = playwright.chromium.connect_over_cdp('http://127.0.0.1:9222')
                        engine = "cdp"
                    for index, scenario in enumerate(scenarios):
                        if results[index] is None:
                            results[index] = run_one(browser, scenario, index, args.html, shots)
                finally:
                    # Do not close the shared CDP browser or any existing user tabs.
                    if browser is not None and engine == "launch":
                        browser.close()
        except Exception as exc:
            for index, scenario in enumerate(scenarios):
                if results[index] is None:
                    results[index] = dict(result_for(scenario, index),
                        reason=f"Infrastructure: {exc}; screenshot unavailable: no page"[:2400])
            if results and all(r["status"] != "fail" for r in results):
                for result in results:
                    if result["status"] == "pass":
                        result.update(status="fail", reason=f"Browser cleanup: {exc}"[:2400])
                        break
    report = {"results": results,
              "passed": sum(r["status"] == "pass" for r in results),
              "failed": sum(r["status"] == "fail" for r in results),
              "skipped": sum(r["status"] == "skip" for r in results),
              "browser": engine, "launch_fallback_reason": fallback,
              "html": os.path.abspath(args.html), "scope": "offline mock UI"}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("passed", "failed", "skipped")}, ensure_ascii=False))
    return 0 if report["failed"] == 0 or args.allow_fail else 1


if __name__ == "__main__":
    sys.exit(main())
