#!/usr/bin/env python3
"""ตรวจไฟล์ส่งมอบแบบ offline: python3 tests/check_links.py (ไม่มี argument).

ใช้เฉพาะ stdlib และ beautifulsoup4; เขียนเฉพาะ tests/link-report.json.
A = readme.md, experiments/README.md, docs/*.md, src/README.md และ events.md
ใน experiments/*/*; B = src/slides/*.html; C = deck และ tests/results.json.
ไม่อ่านเนื้อหาหลักฐานดิบ prompt/trace/response/output/log เพื่อตรวจกฎของ worker.
links_total นับการอ้าง path ภายใน (รวมซ้ำและ directory) ไม่นับ URL/anchor;
รองรับ Markdown inline/image/reference links และ HTML img/src, a/href.
ตัวอย่างลิงก์ใน fenced/inline code ไม่ใช่ลิงก์ที่ render จึงไม่นับ.
ข้อความ f-string ที่ destination มีช่องว่าง เช่น [{name}]({root / name})
ไม่ใช่ Markdown link ที่สมบูรณ์ จึงไม่ตีความส่วนก่อนช่องว่างเป็นไฟล์เสีย.
no_placeholder ยกเว้น fenced/inline code ใน A และ pre.code/data-file ใน B.
การ mask คงตำแหน่งและ newline เดิม เพื่อรายงานเลขบรรทัดต้นฉบับ.

รหัส T1–T11 เป็นชื่องานในแผนของ AI รวมทั้ง T2a จึงไม่เหมารวมเป็นรหัส
ของ ROUTER: ใช้ regex ตามสัญญา ไม่ตรวจ T10/T11 เปล่า แต่ตรวจ T10b/T11a.
ข้อยกเว้นโค้ดข้างต้นใช้กับ placeholder/ลิงก์เท่านั้น กฎข้อความอื่นตรวจทั้งไฟล์.
deck ไม่ตรวจข้อความหลักฐานดิบที่ฝังอยู่; ตรวจ asset นอก iframe srcdoc,
ชื่อและเลขหน้าปลายทาง และผลทดสอบหน้าจาก results.json เท่านั้น.
warnings ไม่เปลี่ยน ok; สคริปต์ไม่ลบ cache หรือแก้ต้นทางอัตโนมัติ.
"""

from datetime import datetime, timedelta, timezone
from html import unescape
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
RULES = [
    "links_exist", "no_abs_path", "no_placeholder", "no_task_code",
    "no_checkpoints", "no_email", "hidden_answers", "no_external_asset",
    "goto_resolves", "deck_pages",
]
TASK_CODE = re.compile(r"\bT(0[0-9][a-z]?|10b|11[a-z]|1[2-9][a-z]?|2[0-3][a-z]?)\b")
EMAIL = re.compile(r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
                   r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
                   r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}\b")
HTTP = re.compile(r"^https?://", re.I)
PRE_CODE = re.compile(
    r'''<pre\b(?=[^>]*\sclass\s*=\s*(?:"(?:[^"]*\s)?code(?:\s[^"]*)?"|'(?:[^']*\s)?code(?:\s[^']*)?'|code(?=\s|>)))[^>]*>.*?</pre\s*>''',
    re.I | re.S,
)
DATA_FILE = re.compile(r'''\bdata-file\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)''', re.I)


def blank(text):
    return re.sub(r"[^\n]", " ", text)


def mask_markdown(text):
    """Mask fenced code, then matching backtick runs (including multi-line spans)."""
    rows = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            rows.append(blank(line))
            if (marker and marker[1][0] == fence[0] and
                    len(marker[1]) >= fence[1] and not marker[2].strip()):
                fence = None
        elif marker and not (marker[1][0] == "`" and "`" in marker[2]):
            fence = (marker[1][0], len(marker[1]))
            rows.append(blank(line))
        else:
            rows.append(line)
    masked = "".join(rows)
    return re.sub(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)",
                  lambda m: blank(m[0]), masked, flags=re.S)


def line_number(text, offset):
    return text.count("\n", 0, offset) + 1


def markdown_links(text):
    """Yield (destination, source offset); retain balanced URL parentheses."""
    references = {}
    definition = re.compile(r"^ {0,3}\[([^]\n]+)\]:\s*(<[^>\n]*>|\S+)", re.M)
    normalize = lambda label: " ".join(label.split()).casefold()
    suffix = re.compile(r'''\s*(?:"[^"\n]*"|'[^'\n]*'|\([^()\n]*\))?\s*\)''')
    for match in definition.finditer(text):
        references.setdefault(normalize(match[1]), match[2].strip("<>"))
    visible = definition.sub(lambda m: blank(m[0]), text)
    # Nested brackets allow linked images and labels containing bracketed text.
    label = re.compile(r"(?<!\\)!?\[((?:\\.|[^\[\]\\]|\[[^\[\]]*\])*)\]", re.S)
    consumed = 0
    for match in label.finditer(visible):
        if match.start() < consumed:
            continue
        if "[" in match[1]:
            for link, offset in markdown_links(match[1]):
                yield link, match.start(1) + offset
        end = match.end()
        if end < len(visible) and visible[end] == "(":
            pos = end + 1
            while pos < len(visible) and visible[pos].isspace():
                pos += 1
            start = pos
            if pos < len(visible) and visible[pos] == "<":
                close = visible.find(">", pos + 1)
                if close >= 0 and suffix.match(visible, close + 1):
                    yield visible[pos + 1:close], match.start()
                continue
            depth = 0
            while pos < len(visible):
                char = visible[pos]
                if char == "\\" and pos + 1 < len(visible):
                    pos += 2
                    continue
                if char == "(":
                    depth += 1
                elif char == ")":
                    if not depth:
                        break
                    depth -= 1
                elif char.isspace() and not depth:
                    break
                pos += 1
            if pos < len(visible) and not depth and suffix.match(visible, pos):
                yield re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1",
                             visible[start:pos]), match.start()
        else:
            reference = re.match(r"\[([^]\n]*)\]", visible[end:])
            key = normalize((reference[1] if reference else "") or match[1])
            if key in references:
                yield references[key], match.start()
                if reference:
                    consumed = end + reference.end()


class Checker:
    def __init__(self, root):
        self.root = root
        self.report = {"ok": False,
                       "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
                       "files_checked": 0, "links_total": 0, "rules": RULES,
                       "files": [], "broken": [], "violations": [], "warnings": []}
        self.rows = {}

    def violation(self, name, rule, text, offset=0, detail=None, line=None):
        snippet = detail if detail is not None else text[offset:offset + 180].split("\n")[0]
        self.report["violations"].append({
            "file": name, "rule": rule,
            "line": line if line is not None else line_number(text, offset),
            "snippet": snippet[:220],
        })
        self.rows[name]["violations"] += 1

    def read(self, path, missing_rule):
        name = path.relative_to(self.root).as_posix()
        self.rows[name] = {"file": name, "links": 0, "broken": 0, "violations": 0}
        self.report["files"].append(self.rows[name])
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            self.violation(name, missing_rule, "", detail=f"อ่านไฟล์ไม่ได้: {type(exc).__name__}")
            return name, None
        self.report["files_checked"] += 1
        return name, text

    def link(self, name, text, link, line):
        link = unescape(link).strip()
        if not link or link.startswith(("#", "//")):
            return
        try:
            url = urlsplit(link)
        except ValueError:
            self.violation(name, "links_exist", text, detail=f"URL ไม่ถูกต้อง: {link}", line=line)
            return
        if url.scheme or not url.path:
            return
        self.rows[name]["links"] += 1
        self.report["links_total"] += 1
        path = Path(unquote(url.path))
        target = (self.root / name).parent / path
        resolved = target.resolve()
        display = os.path.relpath(resolved, self.root)
        if any(part in (".work", ".ipynb_checkpoints") for part in (*path.parts, *resolved.parts)):
            self.violation(name, "links_exist", text, detail=f"ลิงก์ไปไฟล์ภายใน: {link}", line=line)
        if not resolved.exists():
            self.report["broken"].append({"file": name, "line": line, "link": link, "resolved": display})
            self.rows[name]["broken"] += 1

    def worker_file(self, path, markdown):
        name, text = self.read(path, "links_exist")
        if text is None:
            return
        patterns = [("no_abs_path", re.compile(re.escape("/root" + "/workspace"))),
                    ("no_task_code", TASK_CODE), ("no_checkpoints", re.compile(r"\.ipynb_checkpoints")),
                    ("no_email", EMAIL)]
        if name != "docs/teacher-notes.md":
            patterns.append(("hidden_answers", re.compile("ปัญหาที่ซ่อนไว้")))
        for rule, pattern in patterns:
            for match in pattern.finditer(text):
                self.violation(name, rule, text, match.start())
        if markdown:
            masked = mask_markdown(text)
        else:
            masked = PRE_CODE.sub(lambda m: blank(m[0]), text)
            masked = DATA_FILE.sub(lambda m: blank(m[0]), masked)
        for match in re.finditer(r"\{\{", masked):
            self.violation(name, "no_placeholder", text, match.start())
        if markdown:
            for link, offset in markdown_links(masked):
                self.link(name, text, link, line_number(text, offset))
            soup = BeautifulSoup(masked, "html.parser")
            for tag in soup.find_all(["img", "a"]):
                attr = "src" if tag.name == "img" else "href"
                if tag.has_attr(attr):
                    self.link(name, text, str(tag[attr]), tag.sourceline or 1)
        else:
            soup = BeautifulSoup(text, "html.parser")
            for tag in soup.find_all(["script", "link"]):
                attr = "src" if tag.name == "script" else "href"
                if HTTP.match(str(tag.get(attr, "")).lstrip()):
                    self.violation(name, "no_external_asset", text,
                                   detail=f"<{tag.name} {attr}={tag[attr]}", line=tag.sourceline or 1)
            for match in re.finditer(r'''(?:url\(\s*["']?\s*|@import\s+["']?\s*)https?://''', text, re.I):
                self.violation(name, "no_external_asset", text, match.start())

    def deck(self):
        result_name, result_text = self.read(self.root / "tests/results.json", "deck_pages")
        results = {}
        if result_text is not None:
            try:
                results = json.loads(result_text)
                if not isinstance(results, dict):
                    raise ValueError("results ต้องเป็น object")
            except ValueError:
                results = {}
                self.violation(result_name, "deck_pages", result_text, detail="results.json ไม่ใช่ JSON object ที่ถูกต้อง")
            for key, expected in (("ok", True), ("overflow", []), ("console_errors", [])):
                valid = results.get(key) is True if key == "ok" else results.get(key) == expected
                if not valid:
                    match = re.search('"' + key + '"', result_text)
                    self.violation(result_name, "deck_pages", result_text, match.start() if match else 0,
                                   detail=f"ต้องมี {key}={json.dumps(expected)}")
        name, text = self.read(self.root / "AI_Workflow_Engineering.html", "deck_pages")
        if text is None:
            return
        soup = BeautifulSoup(text, "html.parser")
        for iframe in soup.find_all("iframe"):
            iframe.attrs.pop("srcdoc", None)
        for tag in soup.find_all(True):
            for attr in ("src", "href", "xlink:href", "srcset"):
                value = str(tag.get(attr, "")).strip()
                external = (re.search(r"(?:^|[\s,])https?://", value, re.I)
                            if attr == "srcset" else HTTP.match(value))
                if external:
                    self.violation(name, "no_external_asset", text,
                                   detail=f"<{tag.name} {attr}={value}", line=tag.sourceline or 1)
        sections = soup.select("section.slide")
        pages = results.get("pages")
        if pages is None:
            pages = [{"title": tag.get("data-title"), "index": index}
                     for index, tag in enumerate(sections, 1)]
        if not isinstance(pages, list):
            self.violation(result_name, "deck_pages", result_text or "", detail="pages ต้องเป็น list")
            pages = []
        titles = {}
        for page in pages:
            if not isinstance(page, dict) or not isinstance(page.get("title"), str) or type(page.get("index")) is not int:
                self.violation(result_name, "deck_pages", result_text or "", detail="pages ต้องมี title และ index จำนวนเต็ม")
                continue
            titles.setdefault(page["title"], []).append(page["index"])
        for tag in soup.select("[data-goto-title]"):
            title = tag["data-goto-title"]
            indices = titles.get(title, [])
            valid = (len(indices) == 1 and str(indices[0]) == tag.get("data-goto") and
                     1 <= indices[0] <= len(sections) and
                     sections[indices[0] - 1].get("data-title") == title)
            if not valid:
                self.violation(name, "goto_resolves", text, line=tag.sourceline or 1,
                               detail=f"data-goto-title={title!r}; data-goto={tag.get('data-goto')!r}; expected={indices}")

    def run(self):
        markdown = {self.root / name for name in
                    ("readme.md", "experiments/README.md", "src/README.md", "docs/test-report.md")}
        markdown.update(self.root.glob("docs/*.md"))
        markdown.update(self.root.glob("experiments/*/*/events.md"))
        for path in sorted(markdown):
            self.worker_file(path, markdown=True)
        for path in sorted(self.root.glob("src/slides/*.html")):
            self.worker_file(path, markdown=False)
        self.deck()
        for parent, directories, files in os.walk(self.root / "experiments", followlinks=False):
            for directory in sorted(directories):
                if directory in (".ipynb_checkpoints", "__pycache__"):
                    self.report["warnings"].append({"rule": "cache_directory",
                        "detail": (Path(parent) / directory).relative_to(self.root).as_posix()})
            if "output.png" in files:
                path = Path(parent) / "output.png"
                size = path.stat().st_size
                if size > 1_000_000:
                    self.report["warnings"].append({"rule": "large_output_png",
                        "detail": f"{path.relative_to(self.root).as_posix()}: {size} bytes (> 1 MB)"})
        self.report["warnings"].append({"rule": "raw_evidence_excluded",
            "detail": "ไม่ตรวจลิงก์ภายในหลักฐานดิบ prompt*.md, trace.md, response*.md, output.*, log*.jsonl และ critic*; ตรวจเพียงว่าปลายทางลิงก์จากไฟล์ส่งมอบมีอยู่"})
        self.report["ok"] = not self.report["broken"] and not self.report["violations"]
        return self.report


def main():
    report = Checker(ROOT).run()
    (ROOT / "tests/link-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in report["files"]:
        print(f"{row['file']}: links={row['links']} broken={row['broken']} violations={row['violations']}")
    for broken in report["broken"]:
        print(f"BROKEN {broken['file']}:{broken['line']}: {broken['link']} -> {broken['resolved']}")
    for violation in report["violations"]:
        print(f"VIOLATION {violation['file']}:{violation['line']} [{violation['rule']}] {violation['snippet']}")
    for warning in report["warnings"]:
        print(f"WARNING [{warning['rule']}] {warning['detail']}")
    print(f"ok={report['ok']} files_checked={report['files_checked']} links_total={report['links_total']} "
          f"broken={len(report['broken'])} violations={len(report['violations'])} warnings={len(report['warnings'])}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
