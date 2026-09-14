#!/usr/bin/env python3
"""Check local Markdown destinations and HTML href/src, excluding srcdoc."""
import argparse
from html.parser import HTMLParser
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MD_LINK = re.compile(r'\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.script = False

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ('href', 'src') and value)
        if tag == 'script':
            # Executable JS templates are not HTML URL attributes.
            self.script = dict(attrs).get('type') in ('text/plain', 'text/html')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script = False

    def handle_data(self, data):
        # The deck stores slide markup inside text/plain script elements.
        # Parsing it as HTML leaves encoded srcdoc attributes opaque.
        if self.script and ('href=' in data or 'src=' in data):
            nested = Links()
            nested.feed(data)
            self.links.extend(nested.links)


def extract(path):
    content = path.read_text(encoding='utf-8', errors='replace')
    if path.suffix.lower() == '.md':
        links = [m.group(1).strip('<>') for m in MD_LINK.finditer(content)]
        parser = Links()
        parser.feed(content)
        return links + parser.links
    parser = Links()
    parser.feed(content)
    return parser.links


def protected_paths(root):
    """Use explicit manifest keys, never filename or directory patterns."""
    manifest = json.loads((root / 'tests/protected-evidence.json').read_text())
    paths = set()
    for name in manifest:
        path = Path(name)
        if not path.is_absolute():
            path = root.parent / path if path.parts[0] == root.name else root / path
        paths.add(Path(os.path.abspath(path)))
    return paths


def check(root, include_all=False):
    protected = protected_paths(root)
    checked, broken = 0, []
    evidence = {'files': 0, 'checked': 0, 'broken': []}
    for directory, folders, files in os.walk(root, followlinks=False):
        # Do not follow directory symlinks: a linked tree is checked at its source.
        folders.sort()
        for name in sorted(files):
            path = Path(directory, name)
            if path.suffix.lower() not in ('.md', '.html'):
                continue
            is_evidence = path in protected
            if is_evidence:
                evidence['files'] += 1
            for link in extract(path):
                if link.startswith(('#', '//')) or urlsplit(link).scheme:
                    continue
                target = unquote(html.unescape(link).split('#', 1)[0].split('?', 1)[0])
                if not target:
                    continue
                if is_evidence:
                    evidence['checked'] += 1
                if not is_evidence or include_all:
                    checked += 1
                destination = os.path.normpath(os.path.join(path.parent, target))
                if not os.path.exists(destination):
                    item = {'file': str(path.relative_to(root)), 'link': link}
                    if is_evidence:
                        evidence['broken'].append(item)
                    if not is_evidence or include_all:
                        broken.append(item)
    return {'checked': checked, 'broken': broken, 'evidence': evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, default=ROOT / 'tests/link-report.json')
    parser.add_argument('--all', action='store_true', help='Include SHA-256 evidence in the failing scope')
    args = parser.parse_args()
    report = check(args.root.resolve(), include_all=args.all)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"Links: {report['checked']} checked, {len(report['broken'])} broken")
    print(f"Evidence: {report['evidence']['files']} files, "
          f"{report['evidence']['checked']} checked, {len(report['evidence']['broken'])} broken (known issues)")
    return int(bool(report['broken']))


if __name__ == '__main__':
    raise SystemExit(main())
