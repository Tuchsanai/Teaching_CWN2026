# เรียก dag-planner จาก host (Claude Code app นอก container)

Claude Code app บน host ใช้ผ่าน `docker exec` เท่านั้น (ชื่อ container ค่าเริ่มต้น `multi-account` เปลี่ยนตามเครื่อง) ทุกคำสั่งรันใน container:

```bash
docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/dag-planner/SKILL.md          # อ่านสกิลก่อน
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/dag-planner/scripts/dagplan.py doctor
docker exec -i multi-account python3 /root/ai-accounts/.Claude/shared/skills/dag-planner/scripts/dagplan.py dag cafe --blocks - < blocks.json
docker cp blocks.json multi-account:/workspace/plans/cafe/blocks.json                              # หรือส่งไฟล์ด้วย docker cp
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/dag-planner/scripts/dagplan.py plan cafe
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/dag-planner/scripts/dagplan.py run cafe --detach
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/dag-planner/scripts/dagplan.py report cafe
```

Git Bash บน Windows แปลง `/root/...` เป็น path ของ Windows → เขียนเป็น `//root/...` หรือใช้ PowerShell · `/workspace/plans/` = โฟลเดอร์ `workspace/plans/` บน host เปิด PNG/MD ได้ตรง ๆ
