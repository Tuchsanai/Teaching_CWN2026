#!/usr/bin/env python3
"""Inspect every slide with Chromium and write screenshots plus a JSON report."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright, expect


def relative(path):
    return os.path.relpath(path, Path.cwd())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=Path('AI_Workflow_Engineering.html'))
    parser.add_argument('--out', type=Path, default=Path('tests/results.json'))
    parser.add_argument('--shots', type=Path, default=Path('tests/screenshots'))
    args = parser.parse_args()
    args.shots.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = {'html': relative(args.html), 'checked_at': datetime.now(timezone.utc).isoformat(),
              'slides': 0, 'ok': False, 'overflow': [], 'console_errors': [], 'copy_ok': False,
              'iframes': {'count': 0, 'loaded': 0}, 'mermaid_svg': 0, 'tabs_ok': None, 'pages': []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                context = browser.new_context(viewport={'width': 1600, 'height': 900},
                                              permissions=['clipboard-read', 'clipboard-write'])
                page = context.new_page()
                page.on('console', lambda msg: result['console_errors'].append(msg.text) if msg.type == 'error' else None)
                page.on('pageerror', lambda error: result['console_errors'].append(str(error)))
                page.goto(args.html.resolve().as_uri(), wait_until='load')
                page.wait_for_function("document.documentElement.dataset.deckReady === 'true'")
                page.evaluate('document.fonts.ready')
                result['slides'] = page.locator('#stage > .slot').count()
                copy_checked = False
                tab_checks = []
                page.keyboard.press('Home')
                for index in range(1, result['slides'] + 1):
                    active = page.locator('#stage > .slot.active > .slide')
                    expect(page).to_have_url(re.compile(rf'#p{index}$'))
                    info = active.evaluate('''slide => {
                        const body = slide.querySelector('.body');
                        return {title: slide.dataset.title || '', chapter: slide.dataset.chapter || '',
                            scrollHeight: slide.scrollHeight,
                            overflow: slide.scrollHeight > 720 || !!(body && body.scrollHeight > body.clientHeight + 2)};
                    }''')
                    if info['overflow']:
                        result['overflow'].append({'index': index, 'title': info['title'], 'scrollHeight': info['scrollHeight']})
                    shot = args.shots / f'slide-{index:03d}.png'
                    active.screenshot(path=str(shot), animations='disabled')
                    result['pages'].append({'index': index, 'title': info['title'], 'chapter': info['chapter'], 'screenshot': relative(shot)})
                    copies = active.locator('.copybox > button.copy')
                    if not copy_checked and copies.count():
                        copy_checked = True
                        button = copies.nth(0)
                        # Reveal a first copy box inside a non-default workflow pane.
                        button.evaluate('''button => {
                            const panes = []; for(let p=button.parentElement;p;p=p.parentElement) if(p.matches('.tabpane')) panes.unshift(p);
                            panes.forEach(p => [...p.parentElement.querySelectorAll(':scope > .tabbar > button')].find(b => b.dataset.tab === p.dataset.tab)?.click());
                        }''')
                        expected = button.locator('..').locator('pre').text_content().strip()
                        button.click()
                        expect(button).to_have_text('Copied')
                        result['copy_ok'] = page.evaluate('navigator.clipboard.readText()').strip() == expected
                    for tabs in active.locator('.tabs').all():
                        buttons = tabs.locator(':scope > .tabbar > button[data-tab]')
                        if buttons.count() < 2:
                            continue
                        buttons.nth(0).click()
                        before = tabs.locator(':scope > .tabpane:visible').get_attribute('data-tab')
                        buttons.nth(1).click()
                        pane = tabs.locator(':scope > .tabpane:visible')
                        expect(pane).to_have_attribute('data-tab', buttons.nth(1).get_attribute('data-tab'))
                        tab_checks.append(pane.get_attribute('data-tab') != before)
                        buttons.nth(0).click()
                    # Navigation keys belong to the deck only when no control has focus.
                    page.evaluate('document.activeElement.blur()')
                    if index < result['slides']:
                        page.keyboard.press('ArrowRight')
                result['tabs_ok'] = all(tab_checks) if tab_checks else None
                result['iframes'] = page.locator('#stage iframe').evaluate_all('''frames => ({count: frames.length,
                    loaded: frames.filter(f => {try {return f.contentDocument?.readyState === 'complete' && f.contentDocument.body?.children.length > 0;} catch (_) {return false;}}).length})''')
                result['mermaid_svg'] = page.locator('#stage .mermaid-svg svg').count()
                page.keyboard.press('o')
                expect(page.locator('body')).to_have_class(re.compile(r'\boverview\b'))
                page.screenshot(path=str(args.shots / 'overview.png'), full_page=True, animations='disabled')
            finally:
                browser.close()
    except Exception as exc:
        result['console_errors'].append(f'Test runner: {type(exc).__name__}: {exc}')
    result['ok'] = not result['overflow'] and not result['console_errors'] and result['copy_ok']
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{result['slides']} slides; ok={result['ok']}; report={args.out}")
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
