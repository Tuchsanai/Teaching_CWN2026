#!/usr/bin/env python3
"""Recompute the report from actual model usage and explicitly manual judgments."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'
cases = json.loads((TESTS / 'cases.json').read_text())
judgments = json.loads((TESTS / 'judgements.json').read_text())
inventory = json.loads((TESTS / 'original_manifest.json').read_text())


def score(phase, filename=None):
    ids = {c['id'] for c in cases if filename is None or c['file'] == filename}
    entries = [j for j in judgments if j['phase'] == phase and j['id'] in ids]
    return f"{sum(j['passed'] for j in entries)}/{len(entries)}"


latest_new = {j['id']: j for j in judgments if j['phase'] in ('new', 'new-r2')}
latest = [j for j in judgments if j['phase'] == 'after'] + list(latest_new.values())
changed_since_tests = set()
for j in latest:
    case = next(c for c in cases if c['id'] == j['id'])
    meta = json.loads((ROOT / j['source']).with_name('metadata.json').read_text())
    request = (ROOT / j['source']).with_name('request.txt').read_text()
    tested_prompt = request.split('<PROMPT>\n', 1)[1].split('\n</PROMPT>', 1)[0]
    assert hashlib.sha256(tested_prompt.encode()).hexdigest() == meta['prompt_sha256'], j['source']
    if hashlib.sha256((ROOT / case['file']).read_bytes()).hexdigest() != meta['prompt_sha256']:
        changed_since_tests.add(case['file'])

for item in inventory:
    if not item['path'].startswith('backup/') or '/.ipynb_checkpoints/' in item['path']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']

metadata = [json.loads(p.read_text()) for p in (TESTS / 'results').glob('*/*/metadata.json')]
usage = {}
for meta in metadata:
    for k, v in (meta.get('usage') or {}).items():
        if isinstance(v, (int, float)):
            usage[k] = usage.get(k, 0) + v
old_chars = sum(len(p.read_text()) for p in (TESTS / 'originals').glob('*.txt'))
new_chars = sum(len(p.read_text()) for p in (ROOT / 'backup').glob('*.md'))
old_lines = sum(len(p.read_text().splitlines()) for p in (TESTS / 'originals').glob('*.txt'))
new_lines = sum(len(p.read_text().splitlines()) for p in (ROOT / 'backup').glob('*.md'))
summary = {'before': score('before'), 'after': score('after'), 'new_initial': score('new'),
           'new_retest': score('new-r2'), 'new_final': f"{sum(j['passed'] for j in latest_new.values())}/{len(latest_new)}",
           'model_calls': len(metadata), 'usage': usage, 'cost': None,
           'original_characters': old_chars, 'revised_characters': new_chars,
           'original_lines': old_lines, 'revised_lines': new_lines,
           'changed_since_model_tests': sorted(changed_since_tests),
           'live': {p.parent.name: json.loads(p.read_text())['status'] for p in (TESTS / 'results/live').glob('*/metadata.json')}}
(TESTS / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')

findings = {
    'base_wave_verify_graph': 'ทางลัดงานเล็ก; คงการตรวจหลักฐาน',
    'blackboard_pull_graph': 'ติดตาม process ที่ยังรัน ไม่ย้ายกลับ TODO และเริ่มซ้ำ',
    'conditional_branch_graph': 'เพิ่ม answer/calculate; ถามเฉพาะข้อมูลจำเป็น',
    'dag_dependency_graph': 'ใช้เวลาสะสมแทนจำนวนลูกเมื่อประเมิน critical path',
    'fork_join_graph': 'ใช้ JOIN เดิมเมื่อ input/output/เกณฑ์ไม่เปลี่ยน',
    'hierarchical_tree_graph': 'ระบุผู้แก้ integration และงบให้ชัด',
    'iterative_refinement_loop_graph': 'เช็กผ่านทุกข้อก่อนเทียบคะแนนรวม',
    'multi_verifier_consensus_graph': 'กำหนดผล FAIL ที่ตรวจซ้ำได้เป็น veto ชัดเจน',
    'parallel_wave_graph': 'ระบุ read/write dependency ชัดเจน',
    'pipeline_graph': 'ย้อนถึงต้นเหตุได้; invalidate ปลายน้ำ; งบรวม',
    'saga_rollback_graph': 'ตรวจรุ่นไฟล์ก่อน undo เพื่อรักษางานผู้ใช้',
}
rows = []
for name, finding in findings.items():
    filename = 'backup/' + name + '.md'
    rows.append(f"{name}: {score('before', filename)} → {score('after', filename)} | {finding}")

report = f'''ผลตรวจ AI Router Prompt — 2026-09-15

หมายเหตุรุ่นไฟล์: ปัจจุบันมี {len(changed_since_tests)} ไฟล์เปลี่ยนหลังการทดสอบโมเดล
เพิ่ม diagram และจัดย่อหน้าให้อ่านง่าย โดยคงข้อความกติกาเดิม; คะแนนด้านล่างเป็นของรุ่นที่เก็บใน results/ ไม่ใช่ผลทดสอบโมเดลซ้ำของรุ่น diagram

สรุป: ควรปรับ ไม่จำเป็นต้องทิ้งแนวคิด graph ทั้งชุด
อ่าน .md เดิมครบ {len(inventory)} ไฟล์รวม checkpoint (19 เนื้อหาไม่ซ้ำ); สอง backup มี prompt หลักเหมือนกัน 11 แบบ
ปรับ backup/*.md ครบ 11 แบบ; เก็บ backup-Copy1/ และ checkpoint เป็นประวัติเดิม
เพิ่ม prompt ใหม่ 5 ไฟล์ที่ root ใช้เดี่ยวได้ เริ่มที่ 01_adaptive_router.md
ขนาดชุดเดิม {old_lines} บรรทัด / {old_chars} ตัวอักษร; ปัจจุบันรวม diagram {new_lines} บรรทัด / {new_chars} ตัวอักษร

ผลทดสอบด้วย cyolo1 / gpt-6-astra / high
- โจทย์เดิม: {score('before')} → {score('after')}
- prompt ใหม่ครั้งแรก: {score('new')}; แก้ชื่อสถานะ dependency ของ Contract First แล้วตรวจซ้ำ {score('new-r2')}
- prompt ใหม่รุ่นสุดท้าย: {summary['new_final']} กรณี (ใช้ผลล่าสุดต่อกรณี ไม่บวกรอบซ้ำ)
- ลอง workflow กับไฟล์จริง 2 กรณี: ENVIRONMENT_BLOCKED ทั้งคู่ ไม่รวมเป็น PASS
  bwrap: No permissions to create a new namespace
  โมเดลยังแก้/อ่านไฟล์ด้วย shell ไม่ได้ ไม่มีผลยืนยันการแก้ add หรือการตรวจ hash จริง
  ไฟล์ผู้ใช้ยังอยู่ แต่การไม่เปลี่ยนไฟล์อย่างเดียวไม่ใช่หลักฐานว่า rollback workflow ผ่าน

ผลรายแบบ (ทุกแบบมีคำถามเล็ก 7+5 และ 2 กรณีเฉพาะ)
''' + '\n'.join(rows) + f'''

บทเรียนที่พบจากคำตอบจริง
- 10/11 แบบหยุดเมื่อไม่มี agent แม้เป็นคำถามบวกเลข; Saga ตอบได้ในรอบนี้
- Blackboard เริ่มใหม่ขณะ process เดิมยังรัน, Fork-Join ทำ JOIN ซ้ำโดย hash ไม่เปลี่ยน
- DAG เลือกจากจำนวนลูก; Pipeline ห้ามย้อนถึง spec ต้นเหตุ; Refinement หยุดแม้ผ่านทุกข้อแล้ว
- Conditional ยังส่งโจทย์ค่าเฉลี่ยเข้า CLASSIFY แทนตอบเลย
- สถานะ blocked กับ blocked_by_dependency ต้องเขียนให้แยกชัด
การเพิ่ม veto, read/write conflict และการรักษาไฟล์ผู้ใช้เป็นการทำกฎให้ชัดขึ้น:
กรณีเหล่านี้ต้นฉบับก็ตอบผ่านอยู่แล้ว จึงไม่อ้างว่าคะแนนดีขึ้นในกรณีนั้น

เลือก prompt ใหม่
01_adaptive_router.md — งานทั่วไป เลือกวิธีให้พอดีกับขนาดงาน
02_evidence_gate.md — ตรวจคำอ้างและหลักฐานของ output รุ่นปัจจุบัน
03_safe_resume.md — กลับมาทำต่อ ไม่ทำซ้ำ ไม่เขียนทับงานผู้ใช้
04_budgeted_repair.md — แก้ต้นเหตุ คุมงบ และตรวจเกณฑ์ก่อนคะแนนรวม
05_contract_first.md — ส่งต่อ input/output และ dependency โดยรักษาโจทย์เดิม

ขอบเขตข้อสรุป
เป็น smoke test ของการตัดสินใจ: session ใหม่ต่อ prompt แต่ 3–5 กรณีอยู่ใน batch เดียวกัน
ใช้โมเดลเดียวและเรียกหนึ่งครั้งต่อชุด; ไม่ใช่ benchmark หลายโมเดลหรือหลักฐานว่า multi-agent ทำงานครบจริง
โจทย์และเกณฑ์คาดหวังบันทึกไว้ก่อนแต่ละชุด; expected ไม่ส่งให้โมเดล ผู้ช่วยหลักอ่านและให้คะแนนตามความหมาย
ใช้ข้อผิดพลาดชุดแรกเพื่อปรับและทดสอบซ้ำ จึงเป็น regression test ไม่ใช่ชุดทดสอบอิสระที่ไม่เคยเห็น
live test ถูก environment ขวาง; ยังไม่ยืนยันการเรียก yolo/cyolo จริง, atomic claim, ภาพ, rollback และประสิทธิภาพการทำงานขนาน
แบบทดสอบรันผ่าน Codex CLI ซึ่งมีคำสั่งระบบ/ค่าบัญชีร่วมอยู่ด้วย; ไม่ใช่การแยก prompt อย่างสมบูรณ์

หลักฐานและการทำซ้ำ
cases.json = คำถาม + expected; judgements.json = คะแนนที่ตรวจด้วยมือ + คำตอบจริง
results/ = request, answer, JSONL events และ metadata ต่อ call; originals/ = prompt ก่อนแก้
python tests/run_probes.py before|after|new --label ชื่อรอบใหม่
python tests/run_probes.py new --only 05_contract_first.md --label ชื่อรอบใหม่
python tests/run_live.py ใช้ sandbox ที่เครื่องนี้ยังรัน shell ไม่ได้ และจะไม่เขียนทับผลรอบเดิม
การเรียก model ใช้บัญชีที่ล็อกอินและใช้โทเคน; ไม่มี automatic retry หลัง call error
python tests/summarize.py สรุปหลักฐานเดิมโดยไม่เรียก model

รวม {len(metadata)} model calls; input_tokens={usage.get('input_tokens', 0):,}; output_tokens={usage.get('output_tokens', 0):,}
cached_input_tokens={usage.get('cached_input_tokens', 0):,}; reasoning_output_tokens={usage.get('reasoning_output_tokens', 0):,}
รายงาน field ตาม CLI แยกกัน ไม่บวก cached/reasoning ซ้ำ; input รวม overhead ของ CLI ไม่ใช่เฉพาะไฟล์ prompt
ค่าใช้จ่าย: ไม่มีข้อมูลราคา จึงไม่ประมาณเป็นเงิน
'''
(TESTS / 'report.txt').write_text(report)
print(json.dumps(summary, ensure_ascii=False, indent=2))
