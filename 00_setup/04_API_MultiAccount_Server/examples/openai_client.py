"""LAB 004 · call the lab API with the OpenAI Python SDK.

The API speaks a small OpenAI-like dialect, so the official `openai` client works
as long as you only send what the API supports:
  * model, messages (system/user/assistant), reasoning_effort
  * account (and optionally provider) go in `extra_body`, they are not OpenAI fields
  * NOT max_completion_tokens / max_tokens / temperature / tools / stream=True:
    the API rejects those with HTTP 400 instead of silently ignoring them.

The key you type is the LAB API token (deploy/.secrets/api_token on the control host),
NOT an OpenAI or Anthropic credential. It is read with getpass and never printed.

Default base URL is for running INSIDE devtools. From a Windows host terminal use
    LAB04_BASE_URL=http://localhost:8004/v1

    python examples/openai_client.py
    python examples/openai_client.py --model gpt-6-astra --effort low --account cyolo1
"""

from __future__ import annotations

import argparse
import getpass
import os

from openai import OpenAI


def main() -> None:
    ap = argparse.ArgumentParser(description="LAB 004 OpenAI-SDK client")
    ap.add_argument("--base-url", default=os.environ.get("LAB04_BASE_URL", "http://host.docker.internal:8004/v1"))
    ap.add_argument("--model", default="fable", help="fable | opus | gpt-6-astra | gpt-6-sol | gpt-6-luna")
    ap.add_argument("--effort", default="low", help="low medium high xhigh max (sol/luna also: none)")
    ap.add_argument("--account", default=None, help="yolo1 for Claude models, cyolo1 for Codex models (default: API default)")
    args = ap.parse_args()

    token = getpass.getpass("LAB 004 API token (input hidden): ").strip()
    client = OpenAI(base_url=args.base_url, api_key=token, max_retries=0, timeout=330)

    # Follow-up context works the same way as in the web page: send the whole history every time.
    messages = [
        {"role": "system", "content": "ตอบเป็นภาษาไทย สั้น ๆ ไม่เกินสองประโยค"},
        {"role": "user", "content": "ฉันชื่อเมย์ เปิดร้านกาแฟชื่อ Cloud Cup ลาเต้ราคา 80 บาท"},
        {"role": "assistant", "content": "รับทราบค่ะคุณเมย์ ร้าน Cloud Cup ลาเต้ 80 บาท"},
        {"role": "user", "content": "ลาเต้สามแก้วราคาเท่าไร และร้านชื่ออะไร"},
    ]

    extra = {"account": args.account} if args.account else {}
    resp = client.chat.completions.create(
        model=args.model,
        messages=messages,
        reasoning_effort=args.effort,
        extra_body=extra,
    )
    print("model:", resp.model)
    print("reply:", resp.choices[0].message.content)


if __name__ == "__main__":
    main()
