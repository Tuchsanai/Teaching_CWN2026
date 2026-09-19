# วิธีรันแล็บ MCP server ของตัวเอง (labs/my-mcp-server)

ทุกคำสั่งรันจากโฟลเดอร์นี้ ใช้ Python ของเครื่องเรียน `/opt/venv/bin/python` (มี `mcp` 2.0.0 และ `kokoro` 0.9.4 ติดตั้งแล้ว)

| ขั้น | คำสั่ง | สิ่งที่ได้ |
| --- | --- | --- |
| 1. ทดสอบ server ด้วย Python client (stdio) | `/opt/venv/bin/python client_test.py --server hello` | เห็น protocol_version, tools/list, ผล tools/call |
| 2. ดูข้อความจริงบนสาย | `/opt/venv/bin/python client_test.py --server hello --wire wire-hello.jsonl` แล้วเปิด `wire-hello.jsonl` | JSON-RPC ทุกข้อความทั้งสองทิศทาง |
| 3. server เสียง Kokoro | `/opt/venv/bin/python client_test.py --server tts --wire wire-tts.jsonl` | ไฟล์ .wav ใน `../kokoro-web/audio_out/` |
| 4. Streamable HTTP | เทอร์มินัล 1: `/opt/venv/bin/python hello_server.py --http` · เทอร์มินัล 2: `/opt/venv/bin/python client_test.py --server http` | server เดียวกันให้บริการผ่าน `http://127.0.0.1:8766/mcp` |
| 5. ต่อกับ Claude Code (ครั้งเดียว) | `claude -p --strict-mcp-config --mcp-config mcp.json "<prompt>"` | Claude ค้นพบและเรียก tool ของเรา |
| 5b. ต่อกับ Claude Code แบบถาวร | `claude mcp add hello-lab -- /opt/venv/bin/python $(pwd)/hello_server.py` แล้ว `claude mcp list` | ใช้ได้ทุก session ในโปรเจกต์ |
| 6. เก็บหลักฐานอัตโนมัติ | `./claude_lab.sh <ชื่อ> <โฟลเดอร์ผล> "<prompt>"` แล้ว `python summarize_stream.py <โฟลเดอร์ผล>/claude-<ชื่อ>-stream.jsonl` | stream-json + wire log + สรุป Markdown |
| 7. Codex CLI | คัดลอก `codex-config-snippet.toml` ต่อท้าย `~/.codex/config.toml` แล้ว `codex mcp list` | (ยังไม่ได้รันในรอบทดลองนี้) |

ข้อควรระวัง
- server แบบ stdio ห้าม `print()` ลง stdout เพราะ stdout คือช่องทางส่ง JSON-RPC ให้ log ไป stderr แทน
- `mcp.json` ใช้ path แบบเต็ม (absolute) เพราะ host เป็นคนเปิด process ของ server ไม่ใช่เรา
- `wire_capture.py` เป็นเพียงตัวส่งผ่าน ถอดออกได้ทุกเมื่อโดยเปลี่ยน `command`/`args` ให้ชี้ไปที่ server ตรง ๆ
