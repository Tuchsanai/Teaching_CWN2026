#!/usr/bin/env python3
"""ดึงกรอบ 💬 ของ LAB N จาก README ทุกตัวอักษร: python3 extract_prompt.py N > labN.prompt.txt"""
import re, sys
n = int(sys.argv[1])
md = open('/root/workspace/CWN/Teaching/00_setup/06_Playwright/01_playwright-mcp/README.md', encoding='utf-8').read()
sec = re.search(rf'^### LAB {n} ·.*?(?=^### LAB {n+1} ·|^## ส่วน C)', md, re.S | re.M).group(0)
i = sec.index('💬 **พรอมต์**')
m = re.search(r'^```text\n(.*?)\n```$', sec[i:], re.S | re.M)
sys.stdout.write(m.group(1))
