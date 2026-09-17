from pathlib import Path
from datetime import datetime,timezone
import json
root=Path.cwd();run=root/'lab-results/graph'/('run-'+datetime.now().strftime('%Y-%m-%d-%H%M%S'));run.mkdir(parents=True)
(root/'work/graph-current-run.txt').write_text(str(run))
for key in ['1_meeting_room','2_expense_claim','3_clinic_migration']:
 p=run/key;(p/'nodes').mkdir(parents=True)
 for name,src in [('prompt-used.md',f'{key}-prompt.md'),('input-used.md',f'{key}-input.md')]:
  (p/name).write_text((root/'labs/prompts/graph'/src).read_text())
 (p/'events.jsonl').write_text('')
 (p/'trace.md').write_text('# Execution Trace — Graph\n\nวิธีรัน: Codex ในบทสนทนาเดียวจำลองบทบาทตามลำดับ Node และสร้างไฟล์แยก ใช้ dependency gate ก่อนบันทึกผล ไม่ได้แยกบริบทหรือรันขนานจริง จึงยังไม่พิสูจน์ความเป็นอิสระของ N2–N4 เก็บผลทดสอบเครื่องมือใหม่ทั้งหมด\n\n')
(run/'run-info.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'mode':'single-conversation role simulation; sequential nodes; no context isolation or concurrency','source':'Current Graph prompts from section 2.3','reused_loop_outputs':False,'verification':'New Chromium/Playwright and Mermaid renders on remote'},ensure_ascii=False,indent=2))
print(run)
