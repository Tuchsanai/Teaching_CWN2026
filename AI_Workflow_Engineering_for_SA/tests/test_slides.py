#!/usr/bin/env python3
"""Walk every slide using the keyboard and exercise overview and both UI frames."""
import argparse
from datetime import datetime, timezone, timedelta
import importlib.metadata
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def save_section(out, key, value):
    path = out / 'results.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    data[key] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def exercise_frame(frame):
    expect(frame.get_by_test_id('btn-reset')).to_be_visible()
    frame.get_by_test_id('btn-reset').click()
    frame.get_by_test_id('role-customer').click()
    expect(frame.get_by_test_id('table-select')).to_be_visible()
    for role, user, nav, screen in (
        ('role-staff', 'demokitchen', 'nav-kitchen', 'kitchen-queue'),
        ('role-staff', 'demofront', 'nav-front', 'front-orders'),
        ('role-manager', 'demomanager', 'nav-menu', 'screen-manager'),
    ):
        frame.get_by_test_id(role).click()
        frame.get_by_test_id('staff-user').select_option(user)
        frame.get_by_test_id('staff-pin').fill('0000')
        frame.get_by_test_id('btn-login').click()
        if nav != 'nav-menu':
            frame.get_by_test_id(nav).click()
        expect(frame.get_by_test_id(screen)).to_be_visible()
    frame.get_by_test_id('btn-reset').click()
    expect(frame.get_by_test_id('table-select')).to_be_visible()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=ROOT / 'AI_Workflow_Engineering_SA.html')
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'tests')
    args = parser.parse_args()
    out = args.out_dir.resolve()
    shots = out / 'screenshots/slides'
    if shots.exists() and any(shots.iterdir()):
        history = out / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        history.mkdir(parents=True)
        shots.rename(history / 'previous-slides')
        old_result = out / 'results.json'
        if old_result.exists():
            (history / 'previous-results.json').write_text(old_result.read_text())
    shots.mkdir(parents=True, exist_ok=True)
    report = {'total': 0, 'screenshots': [], 'console_errors': [], 'overflow': [],
              'status': 'fail', 'overview': 'not-run', 'iframes': [],
              'timestamp_thai': datetime.now(timezone(timedelta(hours=7))).isoformat(),
              'playwright': importlib.metadata.version('playwright'),
              'viewport': {'width': 1600, 'height': 900}, 'errors': []}
    with sync_playwright() as pw:
        browser = context = None
        engine = 'launch'
        try:
            try:
                browser = pw.chromium.launch()
            except Exception as exc:
                report['launch_fallback_reason'] = str(exc).replace(str(ROOT.parent), '<PROJECT_ROOT>')
                engine = 'cdp'
                browser = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')
            report.update(browser=engine, chromium=browser.version)
            context = browser.new_context(viewport=report['viewport'])
            page = context.new_page()
            page.set_default_timeout(5000)
            page.on('console', lambda msg: report['console_errors'].append({'type': 'console', 'message': msg.text}) if msg.type == 'error' else None)
            page.on('pageerror', lambda exc: report['console_errors'].append({'type': 'pageerror', 'message': str(exc)}))
            page.goto(args.html.resolve().as_uri())
            expect(page.locator('#total')).not_to_have_text('0')
            report['total'] = int(page.locator('#total').inner_text())
            page.keyboard.press('Home')
            for number in range(1, report['total'] + 1):
                expect(page.locator('#cur')).to_have_text(str(number))
                page.evaluate('document.fonts.ready')
                page.locator('.slot.active img').evaluate_all('(imgs) => Promise.all(imgs.map(i => i.decode().catch(() => {})))')
                page.wait_for_timeout(60)  # Required presentation settle interval.
                height = page.locator('.slot.active .slide').evaluate('el => el.scrollHeight')
                if height > 730:
                    report['overflow'].append({'slide': number, 'scrollHeight': height})
                shot = shots / f'slide-{number:03d}.png'
                page.screenshot(path=str(shot))
                report['screenshots'].append(str(shot.relative_to(out)))
                for iframe in page.locator('.slot.active iframe').all():
                    record = {'slide': number, 'title': iframe.get_attribute('title'), 'status': 'fail'}
                    try:
                        frame = iframe.element_handle().content_frame()
                        exercise_frame(frame)
                        record['status'] = 'pass'
                    except Exception as exc:
                        record['reason'] = str(exc)
                    report['iframes'].append(record)
                # Frame clicks move keyboard focus; restore focus to the deck.
                page.locator('.slot.active .slide').click(position={'x': 10, 'y': 10})
                if number < report['total']:
                    page.keyboard.press('ArrowRight')
            page.keyboard.press('o')
            expect(page.locator('body')).to_have_class('overview')
            assert page.locator('.slot:visible').count() == report['total']
            page.screenshot(path=str(shots / 'overview.png'), full_page=True)
            page.locator('.slot').nth(0).click()
            expect(page.locator('#cur')).to_have_text('1')
            expect(page.locator('body')).not_to_have_class('overview')
            page.keyboard.press('o')
            page.keyboard.press('Escape')
            expect(page.locator('body')).not_to_have_class('overview')
            report['overview'] = 'pass'
            report['status'] = 'pass' if (report['total'] >= 90 and not report['overflow']
                and not report['console_errors'] and len(report['iframes']) == 2
                and all(f['status'] == 'pass' for f in report['iframes'])) else 'fail'
        except Exception as exc:
            report['errors'].append(str(exc))
        finally:
            if context is not None:
                context.close()
            if browser is not None and engine == 'launch':
                browser.close()
            save_section(out, 'slides', report)
    print(f"Slides: {report['total']}, screenshots: {len(report['screenshots'])}, {report['status']}")
    return int(report['status'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
