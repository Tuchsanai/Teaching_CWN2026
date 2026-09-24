"""Turn an OpenAI-style message list into one prompt for a stateless CLI call.

The CLIs remember nothing between calls, so every request carries the full history.
The history is embedded as JSON so message boundaries cannot be forged by content.
"""

from __future__ import annotations

import json

SYSTEM_PROMPT = (
    "You are a helpful assistant in a plain text chat. You have no tools: you cannot run "
    "commands, read or write files, or browse. Answer the user's latest message directly, "
    "using the earlier conversation as context. Reply with the answer text only."
)


def build_prompt(messages: list[dict[str, str]]) -> str:
    history = json.dumps(messages, ensure_ascii=False, indent=1)
    return (
        "Below is the full conversation so far as a JSON array of messages in order. "
        "Messages with role \"system\" or \"developer\" are instructions from the application; "
        "\"user\" messages are from the user; \"assistant\" messages are your earlier replies.\n\n"
        f"<conversation>\n{history}\n</conversation>\n\n"
        "Write the assistant's reply to the last user message. Output only the reply itself, "
        "without a role label, JSON, or any preamble."
    )
