"""Turn a chat `messages` array into ONE prompt for a one-shot CLI call.

Why this exists: `claude -p` and `codex exec` answer a single prompt and exit.
They have no server-side memory between our HTTP requests (we also run them
with --no-session-persistence / --ephemeral). So follow-up context only exists
because the browser re-sends the whole text history every turn, and this module
serialises that history into the prompt.

The history is embedded as a JSON array. JSON escaping means a user cannot fake
a role boundary by typing something like "ASSISTANT:" inside a message.
This is still NOT a native chat API: a "system" message here is just text the
model is asked to respect, not a privileged system prompt.
"""

from __future__ import annotations

import json

PREAMBLE = """You are the assistant in a simple web chat application.
The conversation so far is given below as a JSON array of {"role", "content"} objects, oldest first.
Roles: "system" = instructions from the chat operator, "user" = the human, "assistant" = your own earlier replies.
Write ONLY your next reply to the last "user" message, as plain text (Markdown is fine).
Reply in the language the user is using. Use earlier turns as context for follow-up questions.
Do not use tools, do not run commands, and do not read or write files. Do not repeat the JSON.

CONVERSATION_JSON:
"""


def build_prompt(messages: list[dict[str, str]]) -> str:
    payload = [{"role": m["role"], "content": m["content"]} for m in messages]
    return PREAMBLE + json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
