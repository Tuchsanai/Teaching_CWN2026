#!/usr/bin/env python3
"""Capture an experiment's landing page and up to eight visible navigation actions."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from render_md import render_markdown, standalone

SELECTOR = "nav a, nav button, header a, header button, [role=tab], .tab, .nav a, .nav button, button"


def shoot(directory):
    result = {"dir": str(directory), "kind": "none", "title": "", "screens": [],
              "console_errors": [], "page_errors": [], "shot_at": datetime.now(timezone.utc).isoformat()}
    status = 0
    source = directory / "output.html"
    if source.is_file():
        result["kind"] = "html"
    elif (directory / "output.md").is_file():
        result["kind"] = "md"
        source = directory / "output.render.html"
    try:
        if result["kind"] == "md":
            html, errors = render_markdown((directory / "output.md").read_text(encoding="utf-8", errors="replace"))
            source.write_text(standalone(html, "output"), encoding="utf-8")
            if errors:
                print(f"MERMAID_FAIL {len(errors)}", file=sys.stderr)
                result["page_errors"].extend(errors)
                status = 2
        if result["kind"] != "none":
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 800})
                    page.set_default_timeout(10000)
                    page.on("console", lambda msg: result["console_errors"].append(msg.text) if msg.type == "error" else None)
                    page.on("pageerror", lambda error: result["page_errors"].append(str(error)))
                    page.on("dialog", lambda dialog: dialog.dismiss())
                    url = source.resolve().as_uri()
                    page.goto(url, wait_until="load")
                    page.evaluate("document.fonts.ready")
                    result["title"] = page.title()
                    page.screenshot(path=str(directory / "output.png"), full_page=result["kind"] == "md")
                    result["screens"].append({"file": "output.png", "action": "landing", "selector": "", "text": ""})
                    candidates, seen = [], set()
                    if result["kind"] == "html":
                        for locator in page.locator(SELECTOR).all():
                            if not locator.is_visible() or not locator.is_enabled():
                                continue
                            box = locator.bounding_box()
                            if not box or box["x"] >= 1280 or box["y"] >= 800 or box["x"] + box["width"] <= 0 or box["y"] + box["height"] <= 0:
                                continue
                            text = " ".join((locator.inner_text() or locator.get_attribute("aria-label") or "").split())
                            if text in seen:
                                continue
                            seen.add(text)
                            selector = locator.evaluate("""el => {
                                const parts = [];
                                while (el && el.nodeType === 1) {
                                    const tag = el.localName;
                                    const siblings = el.parentElement ? [...el.parentElement.children].filter(n => n.localName === tag) : [el];
                                    parts.unshift(tag + ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')');
                                    el = el.parentElement;
                                }
                                return parts.join(' > ');
                            }""")
                            candidates.append((selector, text))
                            if len(candidates) >= 8:
                                break
                    for index, (selector, text) in enumerate(candidates, 1):
                        try:
                            page.goto(url, wait_until="load")
                            page.locator(selector).click(timeout=3000)
                            page.wait_for_timeout(500)
                            filename = f"output-{index}.png"
                            page.screenshot(path=str(directory / filename))
                            result["screens"].append({"file": filename, "action": "click", "selector": selector, "text": text})
                        except Exception as exc:
                            result["page_errors"].append(f"click {text}: {exc}")
                finally:
                    browser.close()
    except Exception as exc:
        result["page_errors"].append(str(exc))
        status = status or 1
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "shoot.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    return shoot(parser.parse_args().directory)


if __name__ == "__main__":
    sys.exit(main())
