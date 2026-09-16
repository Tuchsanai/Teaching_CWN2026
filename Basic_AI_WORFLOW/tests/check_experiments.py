#!/usr/bin/env python3
"""Check §5 against immutable experiment evidence; write only JSON and README.

No arguments. Missing evidence/tooling => None, observed mismatch => False.
UI and textual heuristics are deliberately not a semantic correctness proof.
No experiment files, browser profiles, screenshots or rendered HTML are written.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
TZ = timezone(timedelta(hours=7))
FEATURES = {"ห้อง": r"ห้อง|room", "เวลาว่าง": r"ว่าง|availab", "จอง": r"จอง|book",
            "ยกเลิก": r"ยกเลิก|cancel", "สถานะ": r"สถานะ|status"}
DESC = {
    "F1_features_present": "พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก",
    "F2_opens_no_console_error": "เปิด file:// โดยไม่มี console error/pageerror",
    "F3_two_clicks": "เข้าถึง keyword ของทุก feature ภายใน 2 คลิก",
    "F4_no_cdn": "ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก",
    "E1_trace_all_sentences": "Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม",
    "E2_conflict_open_issue": "Open Issues มีเกณฑ์ 5,000 และ 10,000",
    "E3_no_invented_amounts": "ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR",
    "E4_entity_consistency": "ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD",
    "E5_state_holder": "ชื่อ state หรือ note ระบุผู้ถือเรื่อง",
    "E6_mermaid_renders": "Mermaid ทุกบล็อก render ได้",
    "M1_five_problem_types": "ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา",
    "M2_ambiguous_date_flagged": "แถววันที่เป้าหมายมีข้อความ flag ความกำกวม",
    "M3_identity_strategy": "หัวข้อ mapping/migration/identity มี normalization และการยืนยัน",
    "M4_plan_version_log": "บันทึกเวอร์ชันแผนมี v1 และ v2",
    "M5_impact_analysis": "เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม",
    "M6_mermaid_renders": "Mermaid ทุกบล็อก render ได้",
}


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""


def clean(value):
    """Do not export machine paths from renderer/browser exceptions."""
    return re.sub(r"/(?:root|home|tmp)/[^\s<>\"']+", "[local path]", str(value)).strip()


def criterion(key, passed, method, evidence):
    return {"id": key, "desc_th": DESC[key], "pass": passed, "method": method,
            "evidence": clean(evidence)}


def lines(text):
    return list(enumerate(text.splitlines(), 1))


def sections(text, pattern):
    """Return source lines under matching headings, including child sections."""
    source = text.splitlines()
    headings, fence = [], None
    for i, line in enumerate(source):
        f = re.match(r"^\s*(`{3,}|~{3,})", line)
        if f:
            if fence is None:
                fence = f[1][0]
            elif f[1][0] == fence:
                fence = None
            continue
        if fence:
            continue
        h = re.match(r"^(#{1,6})\s+(.+)", line)
        if h:
            headings.append((i, len(h[1]), h[2]))
    found = {}
    for k, (start, level, title) in enumerate(headings):
        if not re.search(pattern, title, re.I):
            continue
        end = next((j for j, depth, _ in headings[k + 1:] if depth <= level), len(source))
        found.update((i + 1, source[i]) for i in range(start, end))
    return sorted(found.items())


def refs(rows, name="output.md"):
    return name + ":" + (",".join(str(n) for n, _ in rows) if rows else "ไม่พบ")


def blocks(text):
    # Use the same Markdown parser as render_md, including tilde/indented fences.
    try:
        from markdown_it import MarkdownIt
        return [(t.map[0] + 1, t.content) for t in MarkdownIt().parse(text)
                if t.type == "fence" and t.info.strip().split()[:1] == ["mermaid"]]
    except ImportError:
        return [(text[:m.start()].count("\n") + 1, m[1])
                for m in re.finditer(r"```mermaid\s*\n(.*?)```", text, re.S)]


def log_records(path):
    records, invalid = [], 0
    for line in read(path).splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
            else:
                invalid += 1
        except ValueError:
            invalid += 1
    return records, invalid


def stamp(path):
    try:
        dt = datetime.fromisoformat(read(path).strip().replace("Z", "+00:00"))
        return dt.astimezone(TZ) if dt.tzinfo else None
    except ValueError:
        return None


def phase(directory, engine, second=False):
    suffix = "2" if second else ""
    records, invalid = log_records(directory / ("log-phase2.jsonl" if second else "log.jsonl"))
    start, end = stamp(directory / (".start" + suffix)), stamp(directory / (".end" + suffix))
    usages = [r["usage"] for r in records if r.get("type") ==
              ("result" if engine == "claude" else "turn.completed") and isinstance(r.get("usage"), dict)]
    totals = {k: None for k in ("input", "cached", "output", "total")}
    if usages:
        # Codex input already includes cached input; Claude cache reads/writes are separate.
        def aggregate(key):
            values = [u.get(key) for u in usages]
            return sum(values) if all(isinstance(v, (int, float)) for v in values) else None
        raw_input = aggregate("input_tokens")
        output = aggregate("output_tokens")
        cached = aggregate("cache_read_input_tokens" if engine == "claude" else "cached_input_tokens")
        writes = aggregate("cache_creation_input_tokens") if engine == "claude" else 0
        inp = raw_input + writes if raw_input is not None and writes is not None else None
        total = (inp + output + (cached if engine == "claude" else 0)
                 if inp is not None and output is not None and (engine != "claude" or cached is not None)
                 else None)
        totals = {"input": inp, "cached": cached, "output": output, "total": total}
    duration = round((end - start).total_seconds(), 3) if start and end and end >= start else None
    return {"start": start.isoformat() if start else None, "end": end.isoformat() if end else None,
            "duration_s": duration, "tokens": totals}, invalid


def metadata(directory):
    records, _ = log_records(directory / "log.jsonl")
    marker = read(directory / ".engine").split()
    engine = marker[0] if marker and marker[0] in ("codex", "claude") else next(
        ("codex" if r.get("type") == "thread.started" else "claude" for r in records
         if r.get("type") == "thread.started" or (r.get("type"), r.get("subtype")) == ("system", "init")), "unknown")
    model = next((r.get("model") or (r.get("thread") or {}).get("model") for r in records
                  if r.get("type") in ("thread.started", "system") and
                  (r.get("model") or (r.get("thread") or {}).get("model"))), None)
    if not model:
        model = next((x for x in marker[1:] if not re.fullmatch(r"(?:c?yolo)\d+", x)), None)
    first, invalid1 = phase(directory, engine)
    has_phase2 = (directory / "log-phase2.jsonl").is_file()
    second, invalid2 = phase(directory, engine, True) if has_phase2 else (None, 0)
    trace = read(directory / "trace.md")
    workflow = directory.name
    if workflow.startswith("loop"):
        kind = "iterations"
        found = re.findall(r"^#{1,6}\s+Iteration\s+(\d+)\b", trace, re.M | re.I)
    elif workflow == "graph":
        kind = "nodes"
        found = re.findall(r'"node"\s*:\s*"(N\d+[a-z]?)"', trace)
        if not found:
            found = re.findall(r"^\|\s*(N\d+[a-z]?)\s*\|\s*(?:DONE|FAILED)\b", trace, re.M)
    else:
        kind = "plan_versions"
        found = re.findall(r"^#{1,6}\s+Plan\s+(v\d+(?:\.\d+)*)\b", trace, re.M | re.I)
    ids = list(dict.fromkeys(found))
    detail = ("trace.md: นับรหัสไม่ซ้ำ " + ", ".join(ids) +
              ("; รวมสองเฟส; จำนวน node ไม่ใช่จำนวนการเรียกซ้ำ" if kind == "nodes" and has_phase2 else "")) if ids else "trace.md: ไม่มีรูปแบบบันทึกรอบที่ตรวจนับได้"
    def file(name):
        path = directory / name
        return str(path.relative_to(ROOT)) if path.is_file() else None
    files = {k: file(n) for k, n in [("prompt", "prompt.md"), ("trace", "trace.md"),
             ("response", "response.md"), ("output", "output.html" if (directory / "output.html").is_file() else "output.md"),
             ("events", "events.md")]}
    files["screens"] = [str(p.relative_to(ROOT)) for p in sorted(directory.rglob("*.png"))]
    for name in ("log.jsonl", "log-phase2.jsonl", "prompt-phase2.md", "response-phase2.md", "shoot.json"):
        files[name] = file(name)
    notes = []
    if not model:
        notes.append("ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน")
    if invalid1 + invalid2:
        notes.append(f"log มี JSON ที่อ่านไม่ได้ {invalid1 + invalid2} บรรทัด; usage อาจไม่ครบ")
    if any(re.search(r"append|ต่อท้าย", line, re.I) for line in trace.splitlines()):
        notes.append("trace.md กล่าวถึงการ append/ต่อท้าย; ไม่ใช่หลักฐานยืนยันประวัติไฟล์ทุกช่วง")
    else:
        notes.append("ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only")
    if has_phase2:
        notes.append("output คือฉบับหลังเฟส 2; เกณฑ์ตรวจฉบับปัจจุบัน; เวลา/โทเคนแยกตาม log ของแต่ละเฟส")
    return {"engine": engine, "model": model, "phase1": first, "phase2": second,
            "rounds": {"kind": kind, "count": len(ids) if ids else None, "detail": detail}, "files": files}, notes


NAV = "nav a, nav button, header a, header button, [role=tab], .tab, .nav a, .nav button, button, a[href]"


def check_ui(directory):
    path = directory / "output.html"
    if not path.is_file():
        return [criterion(k, None, "script" if k in ("F2_opens_no_console_error", "F4_no_cdn") else "heuristic",
                          "ไม่มี output.html") for k in DESC if k.startswith("F")]
    source = read(path)
    # External attributes, CSS resources, JS imports/fetch and protocol-relative CDN URLs.
    external = []
    resource = re.compile(r'''(?:\b(?:src|href)\s*=\s*["']|url\(\s*["']?|@import\s*["']|(?:fetch|import|importScripts)\s*\(\s*["']|\bfrom\s*["'])(?:https?:)?//[^\s"'<>)]*''', re.I)
    for n, line in lines(source):
        for match in resource.finditer(line):
            external.append((n, match.group()[:160]))
    cdn = criterion("F4_no_cdn", not external, "script", (refs(external, "output.html") if external else "output.html: สแกน source ทั้งไฟล์") +
                    ("; " + "; ".join(x for _, x in external) if external else "; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source"))
    errors, blocked = [], []
    landing_error = None
    paths, first_level = {}, set()
    issues, truncated = [], False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                def visit(path_steps):
                    nonlocal truncated
                    context = browser.new_context(viewport={"width": 1280, "height": 800})
                    page = context.new_page()
                    page.set_default_timeout(2000)
                    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("dialog", lambda dialog: dialog.dismiss())
                    def block(route):
                        blocked.append(route.request.url)
                        route.abort()
                    page.route(re.compile(r"^https?://"), block)
                    try:
                        page.goto(path.resolve().as_uri(), wait_until="load", timeout=10000)
                        for css, label in path_steps:
                            page.locator(css).click()
                        page.evaluate("document.fonts.ready")
                        visible = page.locator("body").inner_text()
                        candidates = []
                        for locator in page.locator(NAV).all():
                            if not locator.is_visible() or not locator.is_enabled():
                                continue
                            label = " ".join((locator.inner_text() or locator.get_attribute("aria-label") or "").split())
                            if not label:
                                continue
                            # All navigation plus feature-oriented buttons, not arbitrary submit actions.
                            is_nav = locator.evaluate("el => !!el.closest('nav, header, [role=tablist], .nav') || el.matches('[role=tab], .tab, a[href]')")
                            if not is_nav and not any(re.search(pat, label, re.I) for pat in FEATURES.values()):
                                continue
                            css = locator.evaluate("""el => {
                                const parts = [];
                                while (el && el.nodeType === 1) {
                                    const same = el.parentElement ? [...el.parentElement.children].filter(x => x.localName === el.localName) : [el];
                                    parts.unshift(el.localName + ':nth-of-type(' + (same.indexOf(el) + 1) + ')');
                                    el = el.parentElement;
                                }
                                return parts.join(' > ');
                            }""")
                            candidates.append((css, label))
                        if len(candidates) > 48:
                            truncated = True
                        return visible, candidates[:48]
                    finally:
                        context.close()
                def remember(text, route):
                    for feature, pat in FEATURES.items():
                        if re.search(pat, text, re.I):
                            if feature not in paths:
                                paths[feature] = f"{len(route)} คลิก: หน้าแรก" + "".join(" → " + label for _, label in route)
                            if len(route) <= 1:
                                first_level.add(feature)
                try:
                    visible, top = visit([])
                except Exception as exc:
                    landing_error = clean(exc)
                    raise
                remember(visible, [])
                landing_errors = list(errors)
                second_routes = []
                for candidate in top:
                    try:
                        visible, next_candidates = visit([candidate])
                        remember(visible, [candidate])
                        second_routes.extend([candidate, c] for c in next_candidates)
                    except Exception as exc:
                        issues.append(clean(str(exc).splitlines()[0]))
                if len(paths) < len(FEATURES):
                    for route in second_routes:
                        try:
                            visible, _ = visit(route)
                            remember(visible, route)
                        except Exception as exc:
                            issues.append(clean(str(exc).splitlines()[0]))
                        if len(paths) == len(FEATURES):
                            break
                path_text = "; ".join(f"{k}: {paths.get(k, 'ไม่พบในเส้นทางที่ตรวจ')}" for k in FEATURES)
                incomplete = bool(issues or truncated)
                f1 = True if len(first_level) == 5 else None if incomplete else False
                f3 = True if len(paths) == 5 else None if incomplete else False
                details = f"output.html: DOM file://, 1280×800, nav ชั้นแรก {len(top)} ตัว; {path_text}"
                if incomplete:
                    details += f"; เส้นทางที่ตรวจไม่สำเร็จ {len(issues)}, จำกัด candidate={truncated}"
                if blocked:
                    cdn = criterion("F4_no_cdn", False, "script", "output.html: พบ source/คำขอเครือข่ายภายนอก: " + "; ".join(sorted(set(blocked)))[:500])
                return [criterion("F1_features_present", f1, "heuristic", details),
                        criterion("F2_opens_no_console_error", not landing_errors, "script",
                                  "output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=" +
                                  str(len(landing_errors)) + ("; " + "; ".join(landing_errors)[:500] if landing_errors else "") +
                                  f"; error รวมระหว่างสำรวจ={len(errors)}; ปิด network"),
                        criterion("F3_two_clicks", f3, "heuristic", details), cdn]
            finally:
                browser.close()
    except Exception as exc:
        reason = "output.html: ตรวจ DOM ไม่สำเร็จ: " + clean(str(exc).splitlines()[0])
        # Existing shoot.json is an explicit fallback, not a fabricated success.
        try:
            shot = json.loads(read(directory / "shoot.json"))
        except ValueError:
            shot = {}
        usable = shot.get("kind") == "html" and shot.get("screens") and all(isinstance(shot.get(k), list) for k in ("console_errors", "page_errors"))
        error_criterion = criterion("F2_opens_no_console_error", None, "script", reason)
        if usable:
            old_errors = shot["console_errors"] + shot["page_errors"]
            error_criterion = criterion("F2_opens_no_console_error", not old_errors, "script",
                f"shoot.json: ใช้ capture เดิม {shot.get('shot_at', 'ไม่ระบุเวลา')}; errors={len(old_errors)}; " + reason)
        if landing_error:
            error_criterion = criterion("F2_opens_no_console_error", None, "script", reason)
        return [criterion("F1_features_present", None, "heuristic", reason), error_criterion,
                criterion("F3_two_clicks", None, "heuristic", reason), cdn]


def render_check(text, key):
    diagrams = blocks(text)
    if not diagrams:
        return criterion(key, False, "render", "output.md: ไม่พบบล็อก Mermaid")
    locations = ",".join(str(n) for n, _ in diagrams)
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from render_md import render_markdown, MERMAID_JS
        if not Path(MERMAID_JS).is_file():
            return criterion(key, None, "render", "output.md: ไม่มี Mermaid JS ในเครื่องสำหรับ render_markdown")
        html, errors = render_markdown(text)
        if errors:
            unavailable = any(re.search(r"Executable doesn't exist|BrowserType.launch|No module named|Target.*closed|ENOENT", err, re.I) for err in errors)
            return criterion(key, None if unavailable else False, "render",
                f"output.md:{locations}; render_markdown {len(diagrams)} บล็อก; errors={len(errors)}; " + clean(errors[0].splitlines()[0])[:280])
        count = html.count('<figure class="mermaid-svg">')
        return criterion(key, count == len(diagrams), "render",
                         f"output.md:{locations}; render_markdown ได้ SVG {count}/{len(diagrams)} บล็อก; ไม่เขียนไฟล์ render")
    except Exception as exc:
        return criterion(key, None, "render", "output.md: render_markdown ใช้ไม่ได้: " + clean(str(exc).splitlines()[0]))


def expense(text):
    result = []
    trace = sections(text, r"Traceability")
    patterns = [r"ถ่ายรูปใบเสร็จ|รูปใบเสร็จ", r"ค่าน้ำมัน|ที่พัก|รับรอง", r"5,?000", r"10,?000",
                r"สองรอบ|ซ้ำ", r"30 วัน|วันที่ 25", r"ชื่อลูกค้า|ชื่อบริษัท", r"ค่าที่พักต่อคืน|ระดับ", r"ค้างอยู่|ค้าง"]
    hits = [[(n, l) for n, l in trace if re.search(p, l, re.I)] for p in patterns]
    result.append(criterion("E1_trace_all_sentences", all(hits), "heuristic", "output.md: Traceability; " +
                            "; ".join(f"กลุ่ม {i + 1}: " + (",".join(str(n) for n, _ in rows) if rows else "ไม่พบ") for i, rows in enumerate(hits))))
    oi = sections(text, r"Open\s+Issues?")
    found = [[(n, l) for n, l in oi if re.search(p, l)] for p in (r"5,?000", r"10,?000")]
    result.append(criterion("E2_conflict_open_issue", all(found), "script",
                            refs([row for rows in found for row in rows]) + "; Open Issues: " + ("พบทั้งสองค่า" if all(found) else "ไม่ครบทั้งสองค่า")))
    frbr = sections(text, r"(?<!Non-)Functional Requirements|Business Rules|(?<![A-Za-z])(?:FR|BR)(?![A-Za-z])")
    frbr = [(n, l) for n, l in frbr if not re.match(r"^#+.*Non.functional", l, re.I)]
    violations = []
    for n, line in frbr:
        for m in re.finditer(r"(?<![\d,])\d[\d,]*(?:\.\d+)?\s*บาท", line):
            amount = float(re.sub(r"[\s,]|บาท", "", m.group()))
            near = line[max(0, m.start()-100):m.end()+100]
            if amount not in (5000, 10000) and re.search(r"ที่พัก|คืน|วงเงิน", near):
                violations.append((n, m.group()))
    result.append(criterion("E3_no_invented_amounts", not violations if frbr else None, "heuristic",
                            (refs(violations) + "; พบ " + ", ".join(v for _, v in violations)) if violations else
                            (refs(frbr[:1]) + "; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000" if frbr else "output.md: ไม่พบหัวข้อ FR/BR")))
    diagrams = blocks(text)
    er = [(n, b) for n, b in diagrams if b.lstrip().startswith("erDiagram")]
    seqstate = [(n, b) for n, b in diagrams if b.lstrip().startswith(("sequenceDiagram", "stateDiagram"))]
    entities = set()
    for _, block in er:
        entities.update(re.findall(r"^\s*([A-Za-z_]\w*)\s*\{\s*$", block, re.M))
        for line in block.splitlines():
            m = re.match(r"\s*(\w+)\s+[|o}{.\-]+\s+(\w+)\s*:", line)
            if m:
                entities.update(m.groups())
    normalize = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    canon = {normalize(e) for e in entities}
    referenced, missing = set(), set()
    for _, block in seqstate:
        # Literal participants: deliberately report infrastructure/role aliases too.
        for identifier, label in re.findall(r"^\s*participant\s+(\w+)(?:\s+as\s+([^\n]+))?", block, re.M):
            referenced.add(identifier)
            if not any(normalize(x) in canon for x in (identifier, label) if x):
                missing.add(identifier + (" (" + label.strip() + ")" if label else ""))
        for identifier in re.findall(r"\b([A-Z][A-Za-z0-9_]*)\.[a-zA-Z_]\w*", block):
            referenced.add(identifier)
            if normalize(identifier) not in canon:
                missing.add(identifier)
        # Entity-like standalone CamelCase words; state aliases and actor IDs are not entities.
        aliases = set(re.findall(r"^\s*(?:actor\s+(\w+)|state\s+\"[^\"]+\"\s+as\s+(\w+))", block, re.M))
        aliases = {x for pair in aliases for x in pair if x}
        for identifier in re.findall(r"\b[A-Z][a-z]+(?:[A-Z][A-Za-z0-9]*)+\b", block):
            if identifier in aliases:
                continue
            referenced.add(identifier)
            if normalize(identifier) not in canon:
                missing.add(identifier)
    verdict = not missing if entities and len(seqstate) >= 2 and referenced else None
    result.append(criterion("E4_entity_consistency", verdict, "heuristic",
        "output.md:" + ",".join(str(n) for n, _ in er + seqstate) +
        f"; ERD {len(entities)} entity; ชื่อไม่พบ: " + (", ".join(sorted(missing)) or "ไม่มี" ) +
        "; เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย"))
    state_lines = []
    for start, block in seqstate:
        if not block.lstrip().startswith("stateDiagram"):
            continue
        in_note = False
        for offset, line in enumerate(block.splitlines(), 1):
            if re.match(r"\s*note\b", line, re.I):
                in_note = True
            if (in_note or re.match(r"\s*state\b", line)) and re.search(r"หัวหน้า|ผู้จัดการ|บัญชี|TeamLead|Manager|Accounting|Approver", line, re.I):
                state_lines.append((start + offset, line))
            if re.match(r"\s*end note\b", line, re.I):
                in_note = False
    result.append(criterion("E5_state_holder", bool(state_lines), "heuristic", refs(state_lines) + "; ตรวจเฉพาะชื่อ state และ note"))
    result.append(render_check(text, "E6_mermaid_renders"))
    return result


def first_table(rows):
    """Only the first findings table; do not inflate count with per-row/CR tables."""
    table, started = [], False
    for row in rows:
        if row[1].lstrip().startswith("|"):
            table.append(row)
            started = True
        elif started:
            break
    if len(table) < 2 or not re.fullmatch(r"[\s|:\-]+", table[1][1]):
        return []
    return table[2:]


def clinic(text, directory):
    result = []
    findings = first_table(sections(text, r"Data Quality Findings"))
    result.append(criterion("M1_five_problem_types", len(findings) >= 5, "heuristic",
                            refs(findings) + f"; ตาราง Findings แรกมี {len(findings)} แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท)"))
    date_rows = [(n, l) for n, l in lines(text) if "09/03/2026" in l]
    flagged = [(n, l) for n, l in date_rows if re.search(r"กำกวม|ambiguous|วันพุธ|Wednesday", l, re.I)]
    result.append(criterion("M2_ambiguous_date_flagged", bool(flagged), "script",
                            refs(flagged or date_rows) + "; " + ("พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่" if flagged else "ไม่พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย")))
    identity = sections(text, r"mapping|migration|identity|matching|จับคู่|ตัวตน")
    normalized = [(n, l) for n, l in identity if re.search(r"normaliz|ทำให้เป็นมาตรฐาน|ตัดขีด", l, re.I)]
    confirm = [(n, l) for n, l in identity if re.search(r"ยืนยัน|confirm", l, re.I)]
    result.append(criterion("M3_identity_strategy", bool(normalized and confirm), "heuristic",
                            refs(normalized[:3]) + "; normalization marker; " + refs(confirm[:3]) + "; confirmation marker ในหัวข้อที่กำหนด"))
    version = sections(text, r"Plan Version|บันทึกเวอร์ชันแผน|Plan\s+v\d+")
    v1 = [(n, l) for n, l in version if re.search(r"\bv1\b", l, re.I)]
    v2 = [(n, l) for n, l in version if re.search(r"\bv2\b", l, re.I)]
    result.append(criterion("M4_plan_version_log", bool(v1 and v2), "script",
                            refs(v1[:2] + v2[:2]) + f"; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1={bool(v1)}, v2={bool(v2)}; v1.1 ไม่นับเป็น v2"))
    if not (directory / "log-phase2.jsonl").is_file():
        impact = criterion("M5_impact_analysis", None, "script", "ไม่มี log-phase2.jsonl; ไม่มีหลักฐานเฟส 2")
    else:
        files = [("output.md", text), ("response-phase2.md", read(directory / "response-phase2.md"))]
        found = []
        for pattern in (r"Impact", r"Reuse|คงเดิม"):
            found.append([(name, n) for name, content in files for n, l in lines(content) if re.search(pattern, l, re.I)])
        impact = criterion("M5_impact_analysis", all(found), "script",
                           "; ".join(label + ": " + (", ".join(f"{name}:{n}" for name, n in rows[:3]) if rows else "ไม่พบใน output.md + response-phase2.md")
                                     for label, rows in zip(("Impact", "Reuse/คงเดิม"), found)) + "; ตรวจคำเท่านั้น")
    result.append(impact)
    result.append(render_check(text, "M6_mermaid_renders"))
    return result


def display(value):
    return "ไม่มีข้อมูล" if value is None else f"{value:,}" if isinstance(value, (int, float)) else str(value)


def mdcell(text):
    return clean(text).replace("|", "&#124;").replace("\n", " ").replace("<", "&lt;")


def write_readme(report):
    results = report["results"]
    content = ["# ผลการทดลอง Workflow", "",
        "ผลจากไฟล์จริง ณ " + report["generated_at"] + " ตรวจใหม่ด้วย [สคริปต์ตรวจ](../tests/check_experiments.py) และเก็บรายละเอียดใน [JSON](../tests/experiments-results.json)", "",
        "```bash", "# รันจากรากโปรเจกต์ ไม่ต้องส่ง argument", "python3 tests/check_experiments.py", "```", "",
        "สคริปต์อ่านทุกชุดที่มี log.jsonl ตรวจผลฉบับปัจจุบัน แล้วเขียน JSON และหน้านี้ใหม่ ใช้ Python, markdown-it-py, Playwright/Chromium และ Mermaid JS ในเครื่องตาม tools/render_md.py; ไม่เรียก AI และไม่เขียนทับหลักฐานดิบ หากเครื่องมือหรือหลักฐานขาดให้ผล ‘ไม่มีข้อมูล’ ส่วน FAIL คือพบว่าไม่ตรงกฎตรวจ", "",
        "## วิธีทดลองซ้ำ", "",
        "ใช้สำเนาโฟลเดอร์ทดลองใหม่และคง prompt ภาษาไทยเดิม เลือกคำสั่งตาม engine จากรูปแบบใน run_experiment.sh; ตัวอย่างต่อไปนี้รันจากโฟลเดอร์สำเนานั้น ใช้เฉพาะ cyolo1 หรือ yolo1 และเลือกเพียงคำสั่งเดียวต่อการรัน", "",
        "```bash", "# Codex: เฟสแรก", 'date -u +%FT%TZ > .start',
        'printf "%s\\n" "codex cyolo1" > .engine',
        'cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response.md "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt',
        'printf "exit=%s\\n" "$?" > .exit', 'date -u +%FT%TZ > .end', "```", "",
        "```bash", "# Claude: เฟสแรก; รันบัญชีนี้ทีละ process", 'date -u +%FT%TZ > .start',
        'printf "%s\\n" "claude yolo1" > .engine',
        'yolo1 -p --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt',
        'printf "exit=%s\\n" "$?" > .exit', 'date -u +%FT%TZ > .end',
        "python3 - <<'PY'", "import json", "from pathlib import Path",
        'rows = [json.loads(line) for line in Path("log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]',
        'result = next((r for r in reversed(rows) if r.get("type") == "result"), {})',
        'Path("response.md").write_text(result.get("result", ""), encoding="utf-8")', "PY", "```", "",
        "ชื่อโมเดลในตัวอย่างเป็นค่าคำสั่งของ harness ไม่ใช้แทนชื่อโมเดลที่ขาดใน log ผลทดลองจริง สำหรับเฟส 2 ให้อ่าน thread_id/session_id ของเฟสแรกเป็น SESSION แล้ว resume session เดิมหลังได้รับผลเฟสแรก เก็บ .start2/.end2/.exit2 และ .stderr2.txt แยกจากเฟสแรก", "",
        "```bash", "# เลือกตาม engine; SESSION คือรหัสจาก log ของการรันซ้ำของตนเอง",
        'cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response-phase2.md resume "$SESSION" "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt',
        'yolo1 -p --resume "$SESSION" --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt', "```", "",
        "สำหรับ Claude ให้แยก result เป็น response-phase2.md ด้วยวิธีเดียวกับเฟสแรก จำกัด yolo1 ทีละ 1 process และ cyolo1 ไม่เกิน 2 jobs พร้อมกัน เมื่อโควตาหมดหยุดรอ ไม่สลับบัญชี หลังทดลองใช้ tools/events_from_log.py และ tools/shoot.py ตาม --help กับสำเนาชุดใหม่เพื่อเก็บ events และภาพ", "",
        "## โครงไฟล์ต่อชุด", "",
        "แต่ละชุดอยู่ที่ `<โจทย์>/<workflow>/`: prompt.md คือคำสั่งที่คงเดิม; log.jsonl คือ event ดิบ; response.md คือคำตอบ; trace.md คือบันทึกกระบวนการ; events.md คือสรุป event; output.html หรือ output.md คือผลงาน; shoot.json และภาพ PNG คือหลักฐาน capture ส่วน .engine, .start/.end บอก engine และเวลารัน เฟส 2 ใช้ prompt-phase2.md, log-phase2.jsonl, response-phase2.md และ .start2/.end2", "",
        "## ตารางเปรียบเทียบ 3 × 3", "",
        "โทเคนและเวลาคือผลรวมของเฟสที่มีข้อมูล (เวลารันแต่ละเฟส ไม่รวมเวลาพักระหว่างเฟส) Codex total = input + output โดย cached เป็นส่วนหนึ่งของ input; Claude input = input_tokens + cache_creation_input_tokens และ total = input + cached + output จาก result.usage; ไม่บวก modelUsage ซ้ำ จึงไม่ใช่ยอดบิลทั้งบัญชี ค่า reasoning เป็นส่วนของ output และไม่บวกซ้ำ", "",
        "รอบนับจาก trace: Loop นับเลข Iteration ไม่ซ้ำ, Graph นับ node ID ไม่ซ้ำ (การรัน node เดิมซ้ำไม่เพิ่มจำนวน), Dynamic นับ Plan version ไม่ซ้ำ จำนวนผ่าน/ทั้งหมดรวมเกณฑ์ไม่มีข้อมูลไว้ในตัวหาร จึงไม่ใช่คะแนนรับรองคุณภาพ", "",
        "| Workflow | โจทย์ 1: จองห้องประชุม | โจทย์ 2: เบิกค่าใช้จ่าย | โจทย์ 3: ย้ายระบบนัดหมาย |", "|---|---|---|---|"]
    tasks = ("1_meeting_room", "2_expense_claim", "3_clinic_migration")
    def summary(task, workflow):
        item = results.get(task, {}).get(workflow)
        if not item:
            return "ไม่มีข้อมูล"
        meta = item["meta"]
        links = []
        for key in ("prompt", "trace", "events", "output", "response"):
            path = meta["files"][key]
            if path:
                relative = str(Path(path).relative_to("experiments"))
                links.append(f"[{Path(path).name}]({relative})")
        phases = [meta[p] for p in ("phase1", "phase2") if meta[p] is not None]
        totals = [p["tokens"]["total"] for p in phases]
        durations = [p["duration_s"] for p in phases]
        total = sum(totals) if all(v is not None for v in totals) else None
        duration = sum(durations) if all(v is not None for v in durations) else None
        rounds = meta["rounds"]
        return (" · ".join(links) + "<br>" + meta["engine"] + " / " + display(meta["model"]) +
                f"<br>{rounds['kind']}: {display(rounds['count'])}; token total: {display(total)}; เวลา: {display(duration)} s" +
                f"<br>ผ่าน {sum(c['pass'] is True for c in item['criteria'])}/{len(item['criteria'])}; ไม่มีข้อมูล {sum(c['pass'] is None for c in item['criteria'])}")
    for label, workflow in (("Loop", "loop"), ("Graph", "graph"), ("Dynamic", "dynamic")):
        content.append("| " + label + " | " + " | ".join(summary(t, workflow) for t in tasks) + " |")
    extras = sorted({w for rows in results.values() for w in rows if w not in ("loop", "graph", "dynamic")})
    for workflow in extras:
        content.append("| " + workflow + " (ชุดเสริม) | " + " | ".join(summary(t, workflow) for t in tasks) + " |")
    content += ["", "## เวลาและโทเคนรายเฟส", "",
                "| ชุด / เฟส | เริ่ม (+07:00) | จบ (+07:00) | วินาที | input | cached | output | total |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for task, workflows in results.items():
        for workflow, item in workflows.items():
            for key in ("phase1", "phase2"):
                p = item["meta"][key]
                if p is not None:
                    content.append("| " + task + "/" + workflow + " / " + key + " | " + " | ".join(display(v) for v in
                        [p["start"], p["end"], p["duration_s"], *[p["tokens"][k] for k in ("input", "cached", "output", "total")]]) + " |")
    content += ["", "## เกณฑ์และข้อจำกัด", "",
        "PASS/FAIL ใน heuristic คือผลกฎข้อความที่ระบุ ไม่ยืนยันความหมายทั้งหมด F1/F3 ตรวจ keyword ที่มองเห็น (รวมป้าย nav) และสำรวจ candidate ที่ระบุในสคริปต์ จึงไม่พิสูจน์ว่าจองหรือยกเลิกสำเร็จจริง แต่ละเส้นทางเริ่มด้วย browser context ใหม่; F2 ตรวจ error ขณะเปิดหน้าและรายงาน error ระหว่างสำรวจแยกต่างหาก; F4 ตรวจแหล่งอ้างอิงภายนอกและคำขอที่ browser พบโดยปิด network", "",
        "E1 ตรวจ keyword ใน Traceability โดยไม่ได้พิสูจน์ mapping ทุก FR/BR; E3 ตรวจบริบท 100 ตัวอักษรรอบจำนวนเงิน; E4 เทียบชื่อ literal ของ participant/entity กับ ERD จึงอาจ FAIL กับชื่อระบบหรือบทบาทที่ไม่ใช่ Entity ต้องอ่าน diagram ประกอบ ส่วนเกณฑ์ M ตรวจรูปแบบเอกสาร/marker ตามกติกาเท่านั้น; M4 รองรับหัวข้อภาษาไทยและ Plan vN ด้วย ไม่เปลี่ยน v1.1 ให้เป็น v2. Mermaid ตรวจด้วย render_markdown จาก tools/render_md.py จริงโดยไม่เขียน output.render.html", ""]
    for task, workflows in results.items():
        content += ["### " + task, "", "| Workflow | เกณฑ์ | วิธี | ผล | Evidence |", "|---|---|---|---|---|"]
        for workflow, item in workflows.items():
            for c in item["criteria"]:
                status = "ไม่มีข้อมูล" if c["pass"] is None else "PASS" if c["pass"] else "FAIL"
                content.append(f"| {workflow} | {c['id']} — {c['desc_th']} | {c['method']} | {status} | {mdcell(c['evidence'])} |")
        content.append("")
    content += ["## หมายเหตุจากหลักฐาน", ""]
    for task, workflows in results.items():
        for workflow, item in workflows.items():
            content.append(f"- `{task}/{workflow}`: {mdcell(item['notes'])}; {mdcell(item['meta']['rounds']['detail'])}")
    content.append("")
    (EXPERIMENTS / "README.md").write_text("\n".join(content), encoding="utf-8")


def main():
    results = {}
    for log in sorted(EXPERIMENTS.glob("*/*/log.jsonl")):
        directory = log.parent
        task = directory.parent.name
        meta, notes = metadata(directory)
        print(f"ตรวจ {task}/{directory.name}", flush=True)
        if task.startswith("1_"):
            criteria = check_ui(directory)
            cdn = next(c for c in criteria if c["id"] == "F4_no_cdn")
            notes.append("CDN/external resources: " + ("ไม่พบ" if cdn["pass"] is True else "พบ" if cdn["pass"] is False else "ไม่มีข้อมูล"))
        else:
            text = read(directory / "output.md")
            if not text:
                prefix = "E" if task.startswith("2_") else "M"
                criteria = [criterion(k, None, "render" if k.endswith("mermaid_renders") else "heuristic", "ไม่มี output.md ให้ตรวจ")
                            for k in DESC if k.startswith(prefix)]
            elif task.startswith("2_"):
                criteria = expense(text)
            elif task.startswith("3_"):
                criteria = clinic(text, directory)
            else:
                criteria = []
                notes.append("ไม่มีเกณฑ์ §5 สำหรับชื่อโจทย์นี้")
        results.setdefault(task, {})[directory.name] = {"meta": meta, "criteria": criteria, "notes": "; ".join(notes)}
    report = {"generated_at": datetime.now(TZ).isoformat(timespec="seconds"), "results": results}
    (ROOT / "tests" / "experiments-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(report)
    print("เขียน tests/experiments-results.json และ experiments/README.md แล้ว; exit 0 หมายถึงตรวจเสร็จ ไม่ได้หมายถึงทุกเกณฑ์ PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
