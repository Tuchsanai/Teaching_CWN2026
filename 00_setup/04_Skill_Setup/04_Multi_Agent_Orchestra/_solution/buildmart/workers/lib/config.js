// workers/lib/config.js — เลือกโหมด LLM ของ chat-worker
// ค่า LLM_* / MODE มาจาก .env.vast (env_file ใน compose · ไม่บังคับ)
//   - มี LLM_BASE_URL → MODE ตามที่ตั้ง (ค่าเริ่มต้น ai)
//   - ไม่มี LLM_BASE_URL หรือ MODE=mock → ใช้ mock-llm (MOCK_LLM_URL, ค่าเริ่มต้น http://mock-llm:8000)
export function getLlmConfig(env = process.env) {
  const base = (env.LLM_BASE_URL || '').trim();
  let mode = (env.MODE || '').trim().toLowerCase() || (base ? 'ai' : 'mock');
  if (!base) mode = 'mock';
  const mockUrl = (env.MOCK_LLM_URL || 'http://mock-llm:8000').trim();
  return {
    mode,
    baseUrl: mode === 'mock' ? mockUrl : base,
    model: mode === 'mock' ? env.LLM_MODEL || 'mock-buildmart' : env.LLM_MODEL || '',
    apiKey: mode === 'mock' ? '' : env.LLM_API_KEY || '',
    timeoutMs: Number(env.LLM_TIMEOUT_MS || 90000),
  };
}
