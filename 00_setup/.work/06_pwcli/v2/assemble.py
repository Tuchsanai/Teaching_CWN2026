#!/usr/bin/env python3
import re, subprocess
from pathlib import Path
H = Path(__file__).parent
txt = (H/"readme_A.md").read_text() + "\n" + (H/"readme_B1.md").read_text() + "\n" + (H/"readme_B2.md").read_text()
txt = re.sub(r"\{\{PROMPT:(\w+)\}\}", lambda m: (H/"prompts"/f"{m.group(1)}.txt").read_text().rstrip("\n"), txt)
walk = subprocess.run(["python3", str(H/"gen_lab6.py")], capture_output=True, text=True, check=True).stdout.rstrip()
txt = txt.replace("{{LAB6_WALK}}", walk)
assert "{{" not in txt
(H/"README.md").write_text(txt)
print(len(txt.splitlines()), "lines")
