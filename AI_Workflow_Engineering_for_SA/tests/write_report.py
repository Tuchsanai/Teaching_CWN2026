#!/usr/bin/env python3
"""Render the dated QA snapshot from the saved JSON reports; does not run tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'


def read(name):
    return json.loads((TESTS / name).read_text())


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ').replace(str(ROOT.parent), '<PROJECT_ROOT>')


def main():
    results, links = read('results.json'), read('link-report.json')
    fixes, protected = read('link-fixes.json'), read('protected-evidence.json')
    evidence = links['evidence']
    evidence_broken_files = len({item['file'] for item in evidence['broken']})
    slides, ui, context = results['slides'], results['ui'], results['context']
    audit = read('source-audit.json')
    original = context['lab006_reference']
    lines = [
        '# รายงานสถานะทดสอบบทเรียน', '',
        f"วันที่เริ่มตรวจสไลด์: **{slides['timestamp_thai']}** (เวลาไทย UTC+7); เวลา UI แต่ละรุ่นอยู่ใน JSON", '',
        'ผลนี้มาจากการเปิดเบราว์เซอร์และรันสคริปต์จริง ไม่ได้เรียกโมเดลสร้างผลรันล่วงหน้าเพิ่ม เวลา/รอบ/โทเคนของการเรียกโมเดลใหม่: **ไม่มีข้อมูล — ไม่ได้เรียก**', '',
        f"เครื่องมือ QA ที่ตรวจรุ่นจริง: **Playwright {slides['playwright']} / Chromium {slides['chromium']}** ผ่าน {slides['browser']}; Codex CLI {context['codex_cli']} ตรวจด้วยคำสั่งแสดงเวอร์ชัน", '',
        f"รุ่นที่โจทย์ระบุคือ Playwright {context['requested_playwright']} Chromium แต่ package index ของเครื่องนี้มีถึงรุ่นที่ใช้จริงข้างต้น จึงไม่ได้รับรองผลบนรุ่นที่ร้องขอ ส่วน Excalidraw MCP {context['excalidraw_mcp']} เป็นเครื่องมือของภาพเดิมตาม [ทะเบียนภาพ](../img/README.md) ไม่ได้เรียกวาดภาพใหม่ในรอบ QA", '',
        'ค่าผลทดสอบทั้งหมดด้านล่างอ่านจาก [results.json](../tests/results.json) และ [link-report.json](../tests/link-report.json); ค่าเสริมใน context คัดจากหลักฐานเดิมพร้อมระบุขอบเขต', '',
        '## ทดสอบแล้ว', '',
        '| รายการ | ผลจริง | หลักฐาน / ขอบเขต |', '|---|---|---|',
        f"| สไลด์ | {slides['total']} หน้า / {len(slides['screenshots'])} ภาพ / console error และ pageerror {len(slides['console_errors'])} / ล้น {len(slides['overflow'])}; {slides['status']} | [ภาพทุกหน้า](../tests/screenshots/slides/); file://, viewport {slides['viewport']['width']}×{slides['viewport']['height']} |",
        f"| overview | {slides['overview']} | เปิดภาพรวม ตรวจทุกหน้าแสดง คลิกเลือกหน้า และออกด้วย Esc |",
        f"| iframe | {'; '.join(cell(f['title']) + ': ' + f['status'] for f in slides['iframes'])} | สลับลูกค้า → ครัว → หน้าร้าน → ผู้จัดการ แล้วรีเซ็ต |",
        f"| UI v1 | ผ่าน {ui['v1']['passed']} / ตก {ui['v1']['failed']} / ข้าม {ui['v1']['skipped']} | [ภาพ UI v1](../tests/screenshots/ui-v1/) |",
        f"| UI v2 | ผ่าน {ui['v2']['passed']} / ตก {ui['v2']['failed']} / ข้าม {ui['v2']['skipped']} | [ภาพ UI v2](../tests/screenshots/ui-v2/) |",
        f"| ลิงก์ในไฟล์ที่นักศึกษาใช้ | ตรวจ {links['checked']} / เสีย {len(links['broken'])} / แก้ {context['fixed_link_occurrences']} occurrence ({context['fixed_link_files']} ไฟล์) | {'ผ่าน' if not links['broken'] else 'ยังไม่ผ่าน'}; ขอบเขตเริ่มต้นของ check_links.py |",
        f"| ลิงก์ในหลักฐานดิบผูก SHA-256 | ตรวจ {evidence['checked']} / เสีย {len(evidence['broken'])} = known issue | ตรวจ Markdown/HTML {evidence['files']} ไฟล์ตามรายชื่อ manifest; รายการเสียครบใน evidence.broken |", '',
        '### ผลต่อ scenario', '',
        'ใช้ fixture เดิมของ LAB ทั้งสองรุ่น ครบทุกเคสและแยก context ต่อเคส ไม่ปรับ selector หรือความคาดหวังเพื่อให้ผ่าน สถานะ pass หมายถึง assertions ของ mock ผ่านเท่านั้น', '',
        '| Scenario / US | v1 | v2 | สาเหตุกรณีตก |', '|---|---|---|---|',
    ]
    for left, right in zip(ui['v1']['results'], ui['v2']['results']):
        reasons = []
        for version, item in [('v1', left), ('v2', right)]:
            if item['status'] != 'pass':
                reasons.append(f"{version}: {cell(item.get('diagnosis', item['reason']))}")
        lines.append(f"| {left['id']} / {left['us']} | {left['status']} | {right['status']} | {'; '.join(reasons) or '—'} |")
    lines += ['',
        f"หลักฐานเดิม LAB 006 ผ่าน {original['passed']} / ตก {original['failed']} / ข้าม {original['skipped']} ตรงกับผล v2 รอบนี้; อ่านคำวิเคราะห์ [F01/F02](../006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md) โดยไม่แก้หลักฐานเดิม", '',
        'เคสคืนรายการของ v2 แสดงยอดจำลองที่ปรับแล้วในภาพ แต่ fixture ค้นหา payment-summary-total ซึ่งไม่มีใน DOM; เคสกำลังการผลิตใช้ rush-start ที่ไม่มีและไม่ได้เปิด nav-capacity ก่อน จึงยังไม่ใช่หลักฐานว่ากฎธุรกิจสองข้อนี้ผ่านครบ', '',
        'เปิดดูภาพตัวอย่างด้วยสายตาที่หน้าฝัง v2 และเคสคืนรายการประกอบ DOM; ภาพหน้าที่เหลือเก็บด้วย automation ไม่ได้อ้างว่าตรวจทุก pixel ด้วยสายตา', '',
        '### การแก้ลิงก์', '',
        'ตารางนี้แจกแจงทุกการแก้ลิงก์เสียใน Markdown; occurrence คือจำนวนที่พบในเนื้อหา ไม่ใช่จำนวนไฟล์ ส่วนลิงก์ต้นฉบับที่เพิ่มแทน path ภายในและข้อแก้ถ้อยคำตามรายการสะสมอยู่ในตารางถัดไป', '',
        '| ไฟล์ | เดิม | ปลายทางที่มีจริง | occurrence |', '|---|---|---|---|',
    ]
    for fix in fixes:
        lines.append(f"| `{cell(fix['file'])}` | `{cell(fix['old'])}` | `{cell(fix['new'])}` | {fix['occurrences']} |")
    lines += ['', '### ข้อแก้เอกสารและขอบเขตที่รักษา', '',
              '| ไฟล์ | การแก้ที่ได้รับอนุญาต |', '|---|---|']
    for change in read('editorial-changes.json'):
        lines.append(f"| `{cell(change['file'])}` | {cell(change['reason'])} |")
    lines += ['',
        'ทะเบียนปัญหาข้อมูลกล่าวถึงรหัสอ้างในเซลล์ US-20 อยู่แล้ว; input ของ LAB 005 อธิบายฐาน path และชี้ UI ที่มีจริงแล้ว; รายงานเปรียบเทียบและ impact ของ LAB สุดท้ายระบุ docs/ui-contract.md ว่าไม่มีไฟล์เป็นข้อความธรรมดาอยู่แล้ว จึงรักษาข้อความและหลักฐานเดิม', '',
        'ลบ cache/checkpoint และ symlink absolute ใน session ตามคำขอ โดยไม่ลบเป้าหมายของ symlink; รายการอยู่ใน [cleanup.json](../tests/cleanup.json) โค้ด metrics ที่อยู่นอก tests กลางและภาพแผนภาพไม่ได้แก้', '',
        'ไฟล์บทเรียนยังไม่ได้อยู่ใน Git index จึงใช้ git diff เพียงอย่างเดียวสรุปการแก้ไม่ได้ เก็บรายการไฟล์ที่เปลี่ยนเทียบ snapshot ก่อนงานและตรวจ hash ไฟล์ที่ห้ามแก้ใน [scope-audit.json](../tests/scope-audit.json) โดยไม่มีการ add/commit/push', '',
        f"### known issue ในหลักฐานดิบ (ลิงก์ {len(evidence['broken'])} จุดใน {evidence_broken_files} ไฟล์ที่ผูก SHA-256 — ไม่แก้)", '',
        'แยกเฉพาะไฟล์ที่ path อยู่ใน keys ของ protected-evidence.json เป็นหลักฐานดิบผูก SHA-256; ไฟล์อื่นทั้งหมดอยู่ในขอบเขตนักศึกษาที่ต้องไม่มีลิงก์เสีย โดยไม่คัดออกด้วยชื่อ README หรือ summary ลิงก์ในหลักฐานเสียเพราะ AI เขียน path สัมพัทธ์กับ work/ หรือ cwd ขณะรัน เมื่อนำผลมาเก็บใน reference/ ตำแหน่งจึงต่างออกไป', '',
        'ผลขอบเขตนักศึกษาผ่านเมื่อ broken ว่าง ส่วนรายการต่อไปนี้คงครบใน evidence.broken และเป็น known issue เพื่อรักษา hash ต้นฉบับ ใช้ check_links.py --all เพื่อตรวจรวมทุกขอบเขต ซึ่งคืน exit 1 เมื่อพบลิงก์เสียในหลักฐานด้วย', '',
        'ดูทะเบียน hash ต้นทางรายไฟล์ใน [protected-evidence.json](../tests/protected-evidence.json); ตารางด้านล่างไม่สร้างลิงก์ใหม่ไปยัง path ที่เสีย', '',
        '| ไฟล์หลักฐาน | path ที่เสีย | เหตุผลที่ยังคงไว้ |', '|---|---|---|',
    ]
    for item in evidence['broken']:
        reason = 'ผูก SHA-256' if item['file'] in protected else 'ต้องตรวจข้อจำกัดเพิ่มเติม'
        lines.append(f"| `{cell(item['file'])}` | `{cell(item['link'])}` | {reason} |")
    lines += ['', '## ยังไม่ทดสอบ', '',
        '| รายการ | สถานะ / สิ่งที่ต้องทำต่อ |', '|---|---|',
        '| เปิดบนมือถือจริง / สแกน QR จริง | ยังไม่ทดสอบ; viewport ของ desktop ไม่ใช่ผลอุปกรณ์จริง |',
        '| เบราว์เซอร์อื่นและระบบปฏิบัติการอื่น | ยังไม่ทดสอบ |',
        '| เว็บไซต์ภายนอกและ anchor ID | ตรวจเฉพาะปลายทางไฟล์ relative; ไม่ได้ตรวจ HTTP หรือ anchor ภายใน |',
        '| NFR บนระบบจริง | ยังไม่ทดสอบเวลา LAN/Wi-Fi, offline ระหว่างอุปกรณ์, ETA จาก log เซิร์ฟเวอร์, สิทธิ์ฝั่งเซิร์ฟเวอร์ และการติดตั้ง |',
        '| แก้ fixture แล้วตรวจ US ที่ตกซ้ำ | ยังไม่ทำ; คง fixture และ HTML เดิมตามขอบเขต |',
        f"| readiness ผล LAB 003 | {context['lab003_readiness']}; ผล merge ไม่รับรองความพร้อมพัฒนา |", '',
        'แผนและเกณฑ์ระบบจริงอยู่ใน [nfr-split.md](../006_LAB_Test_Scenarios_Traceability/reference/step-04-nfr-split/nfr-split.md); ผล readiness อยู่ใน [merge-validation.json](../003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-validation.json)', '',
        '## ข้อจำกัด', '',
        '- UI เป็น mock-up ข้อมูลในหน่วยความจำ บทบาทและนาฬิกาจำลอง ไม่ได้ต่อระบบหลังบ้านหรือฐานข้อมูลจริง',
        '- PromptPay และการคืนรายการเป็นการจำลอง ไม่มีการรับเงิน โอนเงิน หรือคืนเงินจริง',
        '- ผล pre-run ของบทเรียนเป็นการรันครั้งเดียวต่อเงื่อนไข ไม่ใช่ค่าเฉลี่ย; จำนวนรอบสูงสุดของกิจกรรมไม่ใช่จำนวนรอบที่รันแล้ว',
        '- ค่าที่ไม่มีข้อมูล เช่นต้นทุนเงินหรือยอดจาก log ที่ไม่มี terminal event คง “ไม่มีข้อมูล” ไม่แทนด้วยศูนย์; ยอดรายแถวที่มีหลักฐานยังอ่านจาก CSV ได้',
        '- เก็บ log.jsonl และผลที่ผูก SHA-256 ตามเดิม ไม่ redact path เครื่องหรือข้อความในหลักฐาน เพราะต้องตรวจย้อนกลับและเทียบ hash ได้',
        '- เกณฑ์ล้นตรวจ scrollHeight ตามที่กำหนด ไม่ครอบคลุมการตัดข้อความทุกลักษณะ; รูปและ iframe ภายในมีพื้นที่เลื่อนของตนเอง',
        '- สคริปต์ UI ใช้ --allow-fail ตาม runner เดิม จึงต้องอ่าน failed ใน JSON; exit code สำเร็จไม่ได้แปลว่าทุก scenario ผ่าน',
        '- README เป็นเอกสารแนะนำที่แก้ได้ ส่วน manifest ประวัติที่เคย hash README/ข้อมูลนำเข้าเป็น snapshot ของรอบเดิม ไม่ปรับ hash ย้อนหลัง', '',
        '### ผลสแกนข้อความที่เหลือ', '',
        f"พบไฟล์ที่ยังมีชื่อขั้นตอนภายใน/alias บัญชี/path เครื่องหรือแหล่งข้อมูลภายใน {context['source_audit_files']} ไฟล์ในต้นฉบับทั้งหมด; รายไฟล์ หมวด และเลขบรรทัดอยู่ใน [source-audit.json](../tests/source-audit.json) ไม่คัดข้อความเหล่านั้นมาซ้ำในคู่มือ", '',
        'รายการที่เหลือเป็น log/หลักฐานที่ผูก SHA หรือโค้ด HTML/JSON/ภาพที่อยู่นอกสิทธิ์แก้เนื้อหา จึงยังไม่ผ่านข้อกำหนดล้างข้อความทั้งโฟลเดอร์; README หลัก คู่มือทดสอบ และรายงานนี้ใช้ placeholder และลิงก์สำหรับผู้เรียน', '',
        'สมมติฐาน QA: ใช้ผลอ้างอิงปัจจุบันเป็นไฟล์ทดสอบ ใช้เกณฑ์จาก fixture เดิมทุกเคส ลิงก์ในไฟล์นักศึกษาต้องเสียศูนย์ ส่วนไฟล์ใน protected-evidence.json รักษาต้นฉบับและรายงาน known issue แยกต่างหาก', '',
    ]
    lines += [f"การสแกนข้อความทั้งโฟลเดอร์รวมไฟล์ QA พบ {context.get('full_tree_text_scan_files', 'ไม่มีข้อมูล')} ไฟล์; รายงานลิงก์ต้องเก็บ path เสียตามจริงด้วย ส่วน grep ที่ไม่ข้าม binary พบ {context.get('full_tree_raw_grep_files', 'ไม่มีข้อมูล')} ไฟล์ เพราะไบต์บีบอัดของ PNG บางไฟล์ตรง pattern สั้นโดยบังเอิญ ดู [text-scan.json](../tests/text-scan.json)", '',
              '### ผลตรวจตามคำสั่งที่กำหนด', '',
              '| ชุดตรวจ | exit code | สถานะ |', '|---|---|---|']
    for validation in read('validation-results.json'):
        code = validation['exit_code']
        status = ('ผ่านตามคาด: รายงานลิงก์เสียในหลักฐาน' if validation.get('expected_exit_code') == code and code != 0
                  else 'ผ่าน' if code == 0 else 'ไม่ผ่าน')
        lines.append(f"| {validation['check']} | {code} | {status} |")
    lines += ['', 'ผล stdout/stderr ของแต่ละชุดอยู่ใน [validation-results.json](../tests/validation-results.json); ชุด Git diff ผ่านเงื่อนไขคำสั่ง แต่ไม่มี diff ของไฟล์ untracked จึงใช้ integrity report ประกอบด้วย', '']
    (ROOT / 'docs/test-report.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
