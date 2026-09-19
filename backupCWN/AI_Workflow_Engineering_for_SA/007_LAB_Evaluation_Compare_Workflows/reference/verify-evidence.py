#!/usr/bin/env python3
"""Verify each rubric evidence path; existence is not a human score review."""
import re
from pathlib import Path

ref = Path(__file__).resolve().parent
root = ref.parent.parent
rubric = ref / "step-02-rubric/rubric-filled.md"
text = rubric.read_text(encoding="utf-8")
pattern = r"(00[1-7]_LAB_[A-Za-z_]+/reference/[\w./-]+)"
paths = sorted(set(re.findall(pattern, text)))
rows = [line for line in text.splitlines() if re.match(r"\|\s*(?:LAB\s*)?00[1-7]_LAB", line) and re.search(r"\|\s*M[1-5]\s*\|", line)]
lines = ["# ตรวจ path หลักฐาน Rubric", "", "ตรวจด้วย Python re.findall และ Path.exists (เทียบเท่า os.path.exists) จากราก AI_Workflow_Engineering_for_SA/", "ตรวจเฉพาะการมีไฟล์ ไม่ยืนยันความถูกต้องของคะแนนหรือ locator และยังไม่ใช่การตรวจซ้ำโดยคน", "ไม่แก้คะแนนที่ AI ให้; path ที่ไม่มีให้ทำเครื่องหมาย หลักฐานไม่พบ", "", "| Path | ผลตรวจ |", "|---|---|"]
missing = []
for path in paths:
    found = (root / path).is_file()
    lines.append(f"| `{path}` | {'พบไฟล์' if found else 'หลักฐานไม่พบ'} |")
    if not found:
        missing.append(path)
lines += ["", f"ตรวจ {len(paths)} path; พบ {len(paths)-len(missing)}; หลักฐานไม่พบ {len(missing)}", "", "## การตรวจทุกช่องคะแนน", ""]
score_rows = [line for line in text.splitlines() if line.startswith("|") and re.search(r"\|\s*M[1-5]\s*\|", line)]
for n, row in enumerate(score_rows, 1):
    row_paths = re.findall(pattern, row)
    ok = bool(row_paths) and all((root / p).is_file() for p in row_paths)
    lines.append(f"- แถว {n}: {'พบไฟล์หลักฐานครบ' if ok else 'หลักฐานไม่พบ'} ({len(set(row_paths))} path)")
lines.append(f"\nแถวคะแนนที่ตรวจ: {len(score_rows)}; ต้องมี 35 แถว")
(ref / "step-02-rubric/verification.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
print({"paths": len(paths), "missing": missing, "score_rows": len(score_rows)})
