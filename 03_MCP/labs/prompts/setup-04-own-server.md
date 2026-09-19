# Setup Prompt S4 — ลงทะเบียน MCP server ของนักศึกษา (hello-lab, kokoro-tts)

```text
ลงทะเบียน MCP server ของบทเรียนกับ Claude Code (โฟลเดอร์ปัจจุบันคือ 03_MCP) โดยไม่ต้องถามกลับ
1. ใช้ python ของ labs/.venv (ถ้ายังไม่มี venv หรือยังไม่มีแพ็กเกจ mcp ให้สร้างและ pip install "mcp[cli]" ก่อน)
2. ทดสอบ server โดยไม่ใช้ LLM: <python ของ venv> labs/my-mcp-server/client_test.py --server hello ต้องได้ add(17, 25) = 42
3. claude mcp add --scope user hello-lab -- <python ของ venv> <path เต็มของ labs/my-mcp-server/hello_server.py>
4. claude mcp add --scope user kokoro-tts -e KOKORO_DEVICE=cpu -- <python ของ venv> <path เต็มของ labs/my-mcp-server/tts_server.py>
5. claude mcp list ต้องเห็นทั้งสองตัว Connected ถ้าไม่ให้แก้จนผ่าน แล้วบอกผู้ใช้ให้พิมพ์ /exit และเปิด claude ใหม่
```
