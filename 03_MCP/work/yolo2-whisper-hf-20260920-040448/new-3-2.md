### 3.2 ตัวอย่างที่สอง: Whisper แปลงเสียงเป็นข้อความ (STT) ด้วย `MCPServer`

Whisper คือโมเดล Speech-to-Text (STT) แบบ open-source ของ OpenAI ทำงาน **กลับทิศกับ Kokoro**: Kokoro รับข้อความแล้วให้ไฟล์เสียง ส่วน Whisper รับไฟล์เสียงแล้วให้ข้อความ

ในบทนี้เราโหลด Whisper **จาก Hugging Face Hub ด้วยไลบรารี Transformers** เพื่อให้เห็นวิธีดึงโมเดลจาก Hub ซึ่งเป็นแพตเทิร์นเดียวกับที่ Kokoro ใช้ (`hexgrad/Kokoro-82M`) แยกให้ชัด 2 ชั้น:

- **โมเดล** ยังคือ Whisper ของ OpenAI อยู่ที่ repo id [`openai/whisper-base`](https://huggingface.co/openai/whisper-base)
- **ไลบรารี** ที่ใช้ดาวน์โหลดและรันคือ [`transformers`](https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.AutomaticSpeechRecognitionPipeline) ของ Hugging Face (ไม่ใช่แพ็กเกจ `openai-whisper`)

`MODEL_ID = "openai/whisper-base"` คือ **repo id** บน Hub (รูปแบบ `องค์กร/ชื่อโมเดล` — เปิดดูไฟล์ทั้งหมดได้ที่หน้าโมเดล) เมื่อเรียก `from_pretrained(MODEL_ID)` ไลบรารีจะดาวน์โหลดไฟล์น้ำหนักและไฟล์ตั้งค่าของ repo นั้นมาเก็บใน cache เครื่อง (ค่าเริ่มต้น `~/.cache/huggingface/hub`, เปลี่ยนได้ด้วย `HF_HOME`) **ครั้งแรกครั้งเดียว** ครั้งถัดไปโหลดจาก cache จึงเร็วขึ้นและใช้ออฟไลน์ได้ โมเดลนี้เป็น public **ไม่ต้องใช้ API key หรือ token** และการถอดเสียงทั้งหมดรันบนเครื่องตัวเอง (ต้องต่อเน็ตเฉพาะตอนดาวน์โหลดครั้งแรก) รุ่น `base` เป็นแบบหลายภาษา (ต่างจาก `base.en` ที่รับเฉพาะอังกฤษ) จึงระบุ `language="th"` ได้ แต่บทเรียนยังไม่ได้วัดคุณภาพภาษาไทยของรุ่นนี้

**ติดตั้งเพิ่ม** ใน `work/.venv` เดิมที่มี torch รุ่น CPU และ `mcp` อยู่แล้ว (รันจาก `03_MCP`) — `transformers` จะดึง `tokenizers`/`safetensors`/`huggingface_hub` ให้เอง ส่วน `ffmpeg` จำเป็นเพราะ pipeline อ่านไฟล์เสียงจาก path ผ่าน ffmpeg:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
work/.venv/bin/pip install -U "transformers>=5,<6"
```

**สร้าง MCP server** — บันทึกเป็น `work/whisper_mcp_demo.py` (ยังไม่มีในแล็บ ให้พิมพ์เอง):

```python
"""whisper_mcp_demo.py — MCP server ที่โหลด Whisper จาก Hugging Face แล้วถอดเสียง"""
import contextlib
import pathlib
import sys

from mcp.server import MCPServer

MODEL_ID = "openai/whisper-base"   # repo id บน Hugging Face Hub
_asr = None


def get_asr():
    """โหลดโมเดล+processor จาก Hub ครั้งแรกที่ถูกเรียก แล้วใช้ pipeline เดิมซ้ำ"""
    global _asr
    if _asr is None:
        # import/ดาวน์โหลด/โหลดโมเดลอาจ print ลง stdout จึงเบี่ยงไป stderr ไม่ให้ปนกับ JSON-RPC
        with contextlib.redirect_stdout(sys.stderr):
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

            processor = AutoProcessor.from_pretrained(MODEL_ID)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_ID, dtype=torch.float32)
            _asr = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                device=-1,               # -1 = CPU
            )
    return _asr


mcp = MCPServer("whisper-demo", instructions="ถอดเสียงพูดจากไฟล์เสียงเป็นข้อความด้วย Whisper")


@mcp.tool()
def transcribe(audio_path: str, language: str = "en") -> dict:
    """ถอดเสียงจากไฟล์เสียง (path สัมบูรณ์บนเครื่องที่รัน server) แล้วคืนข้อความ"""
    path = pathlib.Path(audio_path)
    if not path.is_absolute():
        raise ValueError("audio_path must be an absolute path")
    if not path.is_file():
        raise ValueError(f"audio file not found: {path}")

    asr = get_asr()
    with contextlib.redirect_stdout(sys.stderr):
        result = asr(
            str(path),
            # ส่งต่อให้ model.generate() — บังคับ "ถอดเสียงภาษาเดิม" ไม่ใช่แปลเป็นอังกฤษ
            generate_kwargs={"language": language, "task": "transcribe"},
        )
    return {"text": result["text"].strip(), "language": language}


if __name__ == "__main__":
    mcp.run()   # stdio — ห้ามครอบด้วย redirect_stdout เช่นเดียวกับตัวอย่าง Kokoro
```

- โครงเหมือน `kokoro_mcp_demo.py` ทุกจุด: `MCPServer` + `@mcp.tool()` + โหลดโมเดลแบบ lazy (ครั้งแรกที่มีคนเรียก `transcribe` แล้วเก็บ pipeline ไว้ใช้ซ้ำ) + `mcp.run()` ผ่าน stdio ต่างกันแค่ tool ชื่อ `transcribe` รับ path เสียงแทนข้อความ
- `AutoProcessor.from_pretrained(MODEL_ID)` ดึง **ตัวเตรียมข้อมูล** ของ repo นี้มา ซึ่งรวม 2 ส่วน: `feature_extractor` (แปลงคลื่นเสียง 16 kHz เป็น log-Mel ที่โมเดลรับ) และ `tokenizer` (แปลง token กลับเป็นข้อความ) ส่วน `AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_ID, dtype=torch.float32)` ดึง **ตัวโมเดล** แบบ float32 ซึ่งเป็นรุ่นที่ CPU รันได้ (ตรงกับ `torch_dtype: float32` ใน `config.json` ของ repo) — ไม่มี `fp16` ในตัวอย่างนี้
- `pipeline("automatic-speech-recognition", ...)` ประกอบ 3 ชิ้นข้างบนเป็นขั้นตอนเดียว: อ่านไฟล์ → feature extractor → `model.generate()` → tokenizer decode คืน dict ที่มีคีย์ `text` ส่วน `device=-1` คือ CPU (ถ้าอยากชัดกว่านี้ใช้ `device="cpu"` ได้)
- `generate_kwargs={"language": ..., "task": "transcribe"}` ถูกส่งต่อไปยัง `model.generate()` ของ Whisper — `task="transcribe"` กันไม่ให้โมเดลเผลอ **แปล** เป็นภาษาอังกฤษ (นั่นคือ `task="translate"`) และ `language` รับค่าอย่าง `"en"`/`"th"` ค่า `language` ที่ tool คืนกลับคือ **ค่าที่ผู้เรียกระบุมา** ไม่ใช่ภาษาที่โมเดลตรวจจับได้เอง (pipeline ไม่ได้คืนภาษาที่ detect มาให้ในโหมดนี้)
- **ไฟล์เสียงต้องอยู่บนเครื่องที่ server รัน** เพราะ tool รับ path ไม่ได้รับตัวไฟล์ ถ้า Host อยู่คนละเครื่องกับ server ต้องส่งไฟล์ไปไว้ที่ฝั่ง server ก่อน ตัวอย่างนี้ตรวจแค่ว่าเป็น path สัมบูรณ์และเป็นไฟล์จริง (path แบบ relative หรือโฟลเดอร์จะได้ `isError: true`) ยังไม่จำกัดโฟลเดอร์ที่อ่านได้ ซึ่งพอสำหรับ demo บนเครื่องตัวเอง แต่ควรเพิ่มถ้าจะเปิดให้คนอื่นใช้

**ลงทะเบียนและทดลอง** ในชื่อ `whisper-demo` รันจาก `03_MCP` (Codex CLI ใช้ `codex mcp add` ตามข้อ 4.6 ด้วยชื่อและ path เดียวกัน):

```bash
claude mcp add --scope user whisper-demo -- "$(pwd)/work/.venv/bin/python" "$(pwd)/work/whisper_mcp_demo.py"
```

เปิด Host session ใหม่แล้วต่อจากผลของข้อ 3.1 — ให้ TTS สร้าง WAV แล้วส่ง path นั้นให้ STT อ่านกลับ:

```text
ใช้ tool transcribe ของ whisper-demo อ่านไฟล์เสียงที่ kokoro-demo เพิ่งสร้าง
(ใช้ path จากผลของ speak) ด้วย language "en" แล้วบอกข้อความที่ถอดได้
```

**ลำดับการทำงาน:** ข้อความ → `speak` (Kokoro) → ไฟล์ `.wav` ใน `work/audio_out/` → `transcribe` (Whisper) → ข้อความ ผลที่ควรได้คือข้อความใกล้เคียงประโยคต้นฉบับ แต่ไม่จำเป็นต้องตรงทุกตัวอักษร (ตัวพิมพ์ เครื่องหมายวรรคตอน หรือคำบางคำอาจต่างไป) ถ้าได้ข้อความว่างหรือ `isError: true` ให้ตรวจ path และ `ffmpeg` ก่อน

หมายเหตุหลักฐาน: ตัวอย่าง Whisper ในข้อนี้ **ยังไม่ได้ทดสอบรันจริง** ทั้งการติดตั้ง การดาวน์โหลดโมเดล และการถอดเสียง ตรวจเฉพาะชื่อ API กับเอกสารและซอร์สโค้ดเมื่อ 20 กันยายน 2026: หน้าโมเดล [`openai/whisper-base`](https://huggingface.co/openai/whisper-base) (มีตัวอย่าง `AutoProcessor` + `AutoModelForSpeechSeq2Seq` และ `torch_dtype: float32` ใน `config.json`), [เอกสาร ASR pipeline](https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.AutomaticSpeechRecognitionPipeline) (อินพุตเป็น path ต้องมี ffmpeg, ผลลัพธ์มีคีย์ `text`, ส่ง `generate_kwargs` ได้) และซอร์สของ `transformers` **5.14.1** ที่ติดตั้งบน Remote (พารามิเตอร์ `tokenizer`/`feature_extractor`/`device` ของ `pipeline()`, พารามิเตอร์ `language`/`task` ของ `WhisperGenerationMixin.generate`, `dtype` ของ `from_pretrained`) — ยังไม่มีตัวเลขเวลาหรือข้อความผลลัพธ์ให้อ้าง
