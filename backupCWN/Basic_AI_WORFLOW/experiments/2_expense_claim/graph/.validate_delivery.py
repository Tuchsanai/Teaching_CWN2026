import json, re
from pathlib import Path
import sys

contracts = []
preflight = "--preflight" in sys.argv
names = ("N1", "N1b", "N2", "N3", "N4") if preflight else ("N1", "N1b", "N2", "N3", "N4", "N5")
for name in names:
    data = json.loads(Path("." + name + ".json").read_text())
    assert set(data) == {"node", "status", "output", "assumptions"}, name
    assert data["node"] == name and data["status"] == "DONE", name
    assert isinstance(data["output"], str) and isinstance(data["assumptions"], list), name
    contracts.append(data)
trace = Path("trace.md").read_text()
entries = [json.loads(m) for m in re.findall(r"```json\n(.*?)\n```", trace, re.S)]
node_entries = [x for x in entries if "node" in x]
order = [x["node"] for x in node_entries]
assert order.index("N1") < min(order.index(n) for n in ("N2", "N3", "N4", "N1b"))
if not preflight:
    assert max(order.index(n) for n in ("N2", "N3", "N4", "N1b")) < order.index("N5")
for contract in contracts:
    assert contract in node_entries, contract["node"]
if not preflight:
    assert entries[-1].get("event") == "MERGE_REVIEW"
output = Path("output.md").read_text()
response = Path("response.md").read_text()
for heading in ("## 1. Execution trace", "## 2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว", "## 3. ข้อขัดแย้งที่พบและวิธีหาข้อสรุป"):
    assert heading in output and heading in response
assert "[output.md](" in response and "[trace.md](" in response
assert output.count("```") % 2 == 0
blocks = re.findall(r"```mermaid\n(.*?)\n```", output, re.S)
assert len(blocks) == 4, len(blocks)
assert {x.splitlines()[0].strip() for x in blocks} == {"flowchart LR", "erDiagram", "sequenceDiagram", "stateDiagram-v2"}
for marker in ("Actor", "NFR-01", "FR-10", "BR-07", "Traceability Matrix", "Open Issues", "Execution trace"):
    assert marker in output, marker
for i in range(1, 12):
    assert "S%02d" % i in output
uc, erd, seq, state = blocks
assert set(re.findall(r'UC(\d\d)\(\[', uc)) == {f'{n:02}' for n in range(1,11)}
entities = set(re.findall(r'^    ([A-Z_]+) \{', erd, re.M))
relations = re.findall(r'^    ([A-Z_]+) [|o{}\-]+ ([A-Z_]+) :', erd, re.M)
assert len(entities) == 10
assert len(relations) == 13
assert all(a in entities and b in entities for a,b in relations)
sequence_depth = 0
for line in seq.splitlines():
    line = line.strip()
    if line.startswith('alt '):
        sequence_depth += 1
    elif line == 'end':
        sequence_depth -= 1
        assert sequence_depth >= 0
assert sequence_depth == 0
state_labels = dict(re.findall(r'^    state "([^"]+)" as (\w+)$', state, re.M))
state_ids = set(state_labels.values())
assert state_ids and all('ผู้ถือเรื่อง:' in x for x in state_labels)
edges = re.findall(r'^    (\w+|\[\*\]) --> (\w+):?', state, re.M)
assert all((a == '[*]' or a in state_ids) and b in state_ids for a,b in edges)
assert not any(a in ('PolicyHold','CheckHold','DecisionHold','ScheduleHold','PaymentHold') for a,b in edges)
matrix = output.split('### Traceability Matrix',1)[1].split('### ความสอดคล้องข้ามแผนภาพ',1)[0]
for i in range(1,12):
    assert f'| S{i:02} ' in matrix
for i in range(1,11):
    assert f'FR-{i:02}' in matrix and f'UC-{i:02}' in matrix
for br in ('BR-01','BR-02A','BR-02B','BR-03','BR-04','BR-05','BR-06','BR-07'):
    assert br in matrix
if not preflight:
    assert contracts[-1]['output'] == output
print('PASS: DONE contracts; dependency completion order; append-log records; four Mermaid blocks; ERD references; sequence branches; state owners and hold paths; complete traceability; required response format')
print("LIMIT: structural checks only; Mermaid parser/render not available")
