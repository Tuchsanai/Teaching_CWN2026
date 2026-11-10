#!/usr/bin/env python3
"""grade.py <sandbox> <task.json> : เรียก harness.cjs (Playwright) ตรวจเว็บที่เอเจนต์สร้าง · ไม่ใช้โทเคน"""
import os, subprocess, sys
r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "harness.cjs"), sys.argv[1], sys.argv[2]],
                   capture_output=True, text=True, timeout=300)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '{"score":0,"checks":[{"id":"harness","pass":false,"note":"%s"}]}' % r.stderr[-150:].replace('"', "'").replace("\n", " "))
