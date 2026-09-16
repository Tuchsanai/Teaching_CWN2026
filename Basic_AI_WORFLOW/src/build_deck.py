#!/usr/bin/env python3
"""Build sorted HTML fragments into one offline, interactive slide deck."""
import argparse
import base64
from html import escape
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from bs4 import BeautifulSoup
from xml.dom import minidom, Node

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / 'tools'))
from render_md import render_markdown

SANDBOX = 'allow-scripts allow-same-origin allow-forms allow-modals'


def soup(text):
    return BeautifulSoup(text, 'html.parser')


def add_class(tag, name):
    tag['class'] = list(dict.fromkeys([*tag.get('class', []), name]))


def append_html(tag, html):
    for child in list(soup(html).contents):
        tag.append(child)


def copybox(pre, document):
    add_class(pre, 'code')
    if pre.parent and 'copybox' in pre.parent.get('class', []):
        box = pre.parent
    else:
        box = document.new_tag('div', attrs={'class': 'copybox'})
        # Allow a directive to set its scrolling container height.
        if pre.has_attr('style'):
            box['style'] = pre.attrs.pop('style')
        pre.wrap(box)
    if not box.select_one('button.copy'):
        button = document.new_tag('button', attrs={'class': 'copy', 'type': 'button'})
        button.string = 'Copy'
        box.append(button)


def inline_svg(path, original):
    source = path.read_text(encoding='utf-8')
    source = re.sub(r'<\?.*?\?>|<!--.*?-->|<!DOCTYPE(?:[^>\[]|\[[\s\S]*?\])*>', '', source, flags=re.S | re.I)
    xml = minidom.parseString(source)
    document = soup('')
    def convert(node):
        if node.nodeType == Node.ELEMENT_NODE:
            tag = document.new_tag(node.tagName, attrs=dict(node.attributes.items()))
            for child in node.childNodes:
                converted = convert(child)
                if converted is not None:
                    tag.append(converted)
            return tag
        if node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
            return node.data
        return None
    svg = convert(xml.documentElement)
    if svg is None or svg.name != 'svg':
        raise ValueError('SVG ไม่มี <svg>')
    if not svg.get('viewBox'):
        def dimension(name):
            value = str(svg.get(name, ''))
            match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)(?:px)?\s*', value)
            if not match or float(match[1]) <= 0:
                raise ValueError(f'SVG ไม่มี viewBox และ {name} ไม่ใช่ขนาด px ที่ใช้ได้')
            return match[1]
        svg['viewBox'] = f'0 0 {dimension("width")} {dimension("height")}'
    for attr in ('width', 'height'):
        svg.attrs.pop(attr, None)
    for attr in ('class', 'style', 'id', 'role', 'aria-label'):
        if original.has_attr(attr):
            svg[attr] = original[attr]
    if original.get('alt') and not svg.get('aria-label'):
        svg['aria-label'] = original['alt']
        svg['role'] = 'img'
    return svg.extract()


def remote_references(slides):
    problems = []
    remote = re.compile(r'^\s*https?://', re.I)
    css_url = re.compile(r'url\(\s*[\'\"]?\s*https?://[^)]+\)', re.I)
    css_import = re.compile(r'@import\s+[\'\"]https?://[^\'\"]+', re.I)
    for index, slide in enumerate(slides, 1):
        for tag in [slide, *slide.find_all(True)]:
            # srcdoc and escaped pre text are not parsed as outer DOM.
            for attr, value in tag.attrs.items():
                if attr.lower() in ('src', 'href', 'xlink:href') and remote.search(str(value)):
                    problems.append(f'หน้า {index} <{tag.name}> {attr}={value}')
                if attr.lower() == 'srcset' and re.search(r'https?://', str(value), re.I):
                    problems.append(f'หน้า {index} <{tag.name}> srcset={value}')
            css = ' '.join(str(value) for attr, value in tag.attrs.items() if attr != 'srcdoc') + ('\n' + tag.get_text() if tag.name == 'style' else '')
            for match in [*css_url.findall(css), *css_import.findall(css)]:
                problems.append(f'หน้า {index} <{tag.name}> {match}')
    return problems


def build(args):
    files = sorted(p for p in args.slides.iterdir() if p.is_file() and p.suffix.lower() in ('.html', '.htm'))
    document = soup('')
    slides, errors = [], []
    for file in files:
        fragment = soup(file.read_text(encoding='utf-8'))
        sections = fragment.select('section.slide, section[data-auto="toc"]')
        sections = [s for s in sections if not s.find_parent('section', class_='slide')]
        if not sections:
            errors.append(f'{file}: ไม่มี section.slide')
        for block, section in enumerate(sections, 1):
            add_class(section, 'slide')
            section.extract()
            for node in list(section.select('[data-svg],[data-png],[data-inline-src],[data-md],[data-file]')):
                directive = next(k for k in ('data-svg', 'data-png', 'data-inline-src', 'data-md', 'data-file') if node.has_attr(k))
                relative = node[directive]
                path = args.root / relative
                try:
                    if directive == 'data-svg':
                        node.replace_with(inline_svg(path, node))
                    elif directive == 'data-png':
                        node['src'] = 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
                        del node[directive]
                    elif directive == 'data-inline-src':
                        node['srcdoc'] = path.read_text(encoding='utf-8')
                        node['sandbox'] = SANDBOX
                        node.attrs.pop('src', None)
                        del node[directive]
                    elif directive == 'data-md':
                        html, failures = render_markdown(path.read_text(encoding='utf-8'))
                        if failures:
                            errors.extend(f'{file} section {block}: {relative} Mermaid block {i}: {error}' for i, error in enumerate(failures, 1))
                        node.clear()
                        append_html(node, html)
                        add_class(node, 'mdbox')
                        del node[directive]
                        # Code/template fences in markdown also get copy controls.
                        for pre in node.select('pre'):
                            copybox(pre, document)
                    else:
                        node.clear()
                        node.string = path.read_text(encoding='utf-8')
                        del node[directive]
                        copybox(node, document)
                except Exception as exc:
                    errors.append(f'{file} section {block}: {directive}="{relative}": {exc}')
            for pre in section.select('.copybox > pre'):
                copybox(pre, document)
            slides.append(section)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 2
    if not slides:
        print('ไม่มี fragment สไลด์', file=sys.stderr)
        return 2
    placeholders = [s for s in slides if s.get('data-auto') == 'toc']
    if not placeholders:
        toc = document.new_tag('section', attrs={'class': ['slide'], 'data-auto': 'toc'})
        slides.insert(1, toc)
        placeholders = [toc]
    chapters = {}
    for index, slide in enumerate(slides, 1):
        chapter = slide.get('data-chapter', '').strip()
        if chapter and slide not in placeholders:
            chapters.setdefault(chapter, index)
    for toc in placeholders:
        toc.clear()
        toc['data-title'] = 'สารบัญ'
        toc['data-chapter'] = toc.get('data-chapter', 'สารบัญ')
        append_html(toc, '<header class="head"><h2>สารบัญ</h2></header><div class="body"><div class="toc"></div></div>')
        grid = toc.select_one('.toc')
        for chapter, page in chapters.items():
            append_html(grid, f'<button type="button" data-goto="{page}"><b>{escape(chapter)}</b><span>หน้า {page}</span></button>')
    for index, slide in enumerate(slides, 1):
        if not slide.get('data-title'):
            heading = slide.find(['h1', 'h2'])
            slide['data-title'] = heading.get_text(' ', strip=True) if heading else f'หน้า {index}'
        foot = slide.select_one('.foot')
        if foot is None:
            foot = document.new_tag('footer', attrs={'class': 'foot'})
            append_html(foot, f'<span>{escape(slide.get("data-chapter", ""))}</span>')
            slide.append(foot)
        pg = foot.select_one('.pg')
        if pg is None:
            pg = document.new_tag('span', attrs={'class': 'pg'})
            foot.append(pg)
        pg.string = f'{index} / {len(slides)}'
    title_pages = {}
    for index, slide in enumerate(slides, 1):
        title_pages.setdefault(slide['data-title'], []).append(index)
    goto_errors, resolved = [], 0
    for index, slide in enumerate(slides, 1):
        for node in [slide, *slide.find_all(True)]:
            if not node.has_attr('data-goto-title'):
                continue
            title = node['data-goto-title']
            targets = title_pages.get(title, [])
            if not targets:
                goto_errors.append(f'หน้า {index}: data-goto-title="{title}" ไม่พบชื่อหน้า')
            elif len(targets) > 1:
                goto_errors.append(f'หน้า {index}: data-goto-title="{title}" ซ้ำในหน้า {", ".join(map(str, targets))}')
            else:
                node['data-goto'] = str(targets[0])
                resolved += 1
    if goto_errors:
        print('\n'.join(goto_errors), file=sys.stderr)
        return 4
    print(f'resolve data-goto-title: {resolved} รายการ')
    problems = remote_references(slides)
    if problems:
        print('พบ URL ภายนอกใน DOM สไลด์:\n' + '\n'.join(problems), file=sys.stderr)
        return 3
    engine = Path(__file__).parent / 'engine'
    css = (engine / 'deck.css').read_text(encoding='utf-8')
    js = (engine / 'deck.js').read_text(encoding='utf-8')
    # Always double quote attributes, including escaped srcdoc HTML.
    from bs4.formatter import HTMLFormatter
    class QuotedFormatter(HTMLFormatter):
        def quoted_attribute_value(self, value):
            return '"' + value.replace('"', '&quot;') + '"'
    formatter = QuotedFormatter(entity_substitution=lambda value: escape(value, quote=False))
    body = '\n'.join('<div class="slot">' + s.decode(formatter=formatter) + '</div>' for s in slides)
    html = f'''<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Workflow Engineering</title><style>{css}</style></head><body>
<main id="stage">{body}</main>
<div id="ui"><div id="counter" aria-live="polite"></div><nav id="controls" aria-label="ควบคุมสไลด์">
<button id="prev" aria-label="หน้าก่อนหน้า">←</button><button id="overview" aria-label="Overview" aria-pressed="false">▦</button><button id="next" aria-label="หน้าถัดไป">→</button>
</nav><div id="progress"><i></i></div></div>
<script>{js}</script></body></html>
'''
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding='utf-8')
    print(f'สร้าง {args.out}: {len(slides)} หน้า')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slides', type=Path, default=Path('src/slides'))
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, default=Path('AI_Workflow_Engineering.html'))
    args = parser.parse_args()
    try:
        return build(args)
    except (OSError, ValueError) as exc:
        print(f'build_deck: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
