"""ทดสอบ Kokoro แบบไลบรารีล้วน ๆ (ยังไม่เกี่ยวกับ MCP)"""
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code="a", device="cpu")   # 'a' = American English
for i, (graphemes, phonemes, audio) in enumerate(pipeline("Kokoro library test, no MCP yet.", voice="af_heart")):
    sf.write(f"/tmp/kokoro-lib-{i}.wav", audio, 24000)
    print("wrote", f"/tmp/kokoro-lib-{i}.wav", "frames:", len(audio))
