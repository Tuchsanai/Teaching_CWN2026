from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[2]
readme = (root / "006_LAB_Prototype_and_UAT/README.md").read_text()
blocks = re.findall(r"### 📋 พรอมท์สำหรับคัดลอก[^\n]*\n+```text\n(.*?)```", readme, re.S)
lines = [f"README prompt blocks: {len(blocks)}"]
ok = len(blocks) == 4
for n in range(1, 5):
    path = root / f"006_LAB_Prototype_and_UAT/prompts/step-{n:02}.md"
    file_text = path.read_text()
    frame_text = blocks[n - 1] if n <= len(blocks) else ""
    match = file_text == frame_text
    ok = ok and match
    digest = hashlib.sha256(file_text.encode()).hexdigest()
    lines.append(f"step-{n:02}: {'MATCH' if match else 'DIFF'} sha256={digest}")
lines.append(f"RESULT: {'PASS' if ok else 'FAIL'}")
output = "\n".join(lines) + "\n"
(root / "evidence/lab006/prompt-diff.txt").write_text(output)
print(output, end="")
raise SystemExit(0 if ok else 1)
