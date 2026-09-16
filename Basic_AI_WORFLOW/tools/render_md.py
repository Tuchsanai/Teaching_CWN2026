#!/usr/bin/env python3
"""Render Markdown and local Mermaid to offline HTML; no browser needed for plain MD."""
import argparse
from html import escape
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

from markdown_it import MarkdownIt

MERMAID_JS = os.environ.get("MERMAID_JS") or "/usr/local/lib/node_modules/mcp-excalidraw-server/node_modules/mermaid/dist/mermaid.min.js"


def responsive_svg(svg):
    def replace(match):
        opening = re.sub(r'\s(?:width|height)\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27)', "", match.group(0))
        style = re.search(r'\sstyle\s*=\s*(["\x27])(.*?)\1', opening)
        if style:
            opening = opening[:style.start()] + opening[style.end():]
        css = (style.group(2).rstrip(";") + ";" if style else "") + "max-width:100%;height:auto;"
        return opening[:-1] + f' style="{css}">'
    return re.sub(r"<svg\b[^>]*>", replace, svg, count=1)


def render_markdown(md_text):
    """Return (HTML fragment, list of Mermaid error strings); preserve failed sources."""
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    tokens = md.parse(md_text)
    diagrams = [t for t in tokens if t.type == "fence" and t.info.strip().split()[:1] == ["mermaid"]]
    rendered, errors = {}, []

    def failure(token, error):
        message = str(error)
        errors.append(message)
        rendered[id(token)] = ('<div class="mermaid-error"><b>Mermaid render error</b>'
                               f'<pre>{escape(message)}</pre><pre class="src">{escape(token.content)}</pre></div>\n')

    if diagrams:
        # Fragments may be combined into a deck: keep SVG IDs unique across calls.
        diagram_prefix = "diagram_" + uuid4().hex
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.route("http://**/*", lambda route: route.abort())
                    page.route("https://**/*", lambda route: route.abort())
                    page.set_content("<html><body></body></html>")
                    page.add_script_tag(path=MERMAID_JS)
                    page.evaluate("mermaid.initialize({startOnLoad:false, securityLevel:'strict'})")
                    for index, token in enumerate(diagrams):
                        try:
                            svg = page.evaluate("""async ({source, id}) => {
                                const result = await mermaid.render(id, source);
                                return result.svg;
                            }""", {"source": token.content, "id": f"{diagram_prefix}_{index}"})
                            rendered[id(token)] = f'<figure class="mermaid-svg">{responsive_svg(svg)}</figure>\n'
                        except Exception as exc:
                            failure(token, exc)
                        finally:
                            page.evaluate("document.body.replaceChildren()")
                finally:
                    browser.close()
        except Exception as exc:
            for token in diagrams:
                if id(token) not in rendered:
                    failure(token, exc)

    original_fence = md.renderer.rules["fence"]

    def fence(tokens, index, options, env):
        token = tokens[index]
        return rendered[id(token)] if id(token) in rendered else original_fence(tokens, index, options, env)

    md.renderer.rules["fence"] = fence
    return md.renderer.render(tokens, md.options, {}), errors


def standalone(html, title="Markdown"):
    return f'''<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><style>
* {{box-sizing:border-box}} body {{font-family:"Leelawadee UI","Noto Sans Thai",Tahoma,sans-serif;
max-width:1100px;margin:0 auto;padding:24px;line-height:1.6;color:#172033;background:#fff}}
table {{border-collapse:collapse;width:100%;margin:16px 0}} th,td {{border:1px solid #aab3c0;padding:8px;text-align:left}}
th {{background:#edf2f7}} pre {{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;padding:16px}}
img,svg {{max-width:100%}} figure {{margin:24px 0}} code {{font-family:monospace}}
</style></head><body>{html}</body></html>\n'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--standalone", action="store_true")
    args = parser.parse_args()
    try:
        html, errors = render_markdown(args.input.read_text(encoding="utf-8", errors="replace"))
        args.output.write_text(standalone(html, args.input.stem) if args.standalone else html, encoding="utf-8")
    except OSError as exc:
        print(f"render_md: {exc}", file=sys.stderr)
        return 1
    if errors:
        print(f"MERMAID_FAIL {len(errors)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
