"""One real, short, tool-less answer per provider, run inside the app container:
    python3 -m app.smoke
Uses the same launcher, flags and limits as the API. Prints only a short excerpt of each answer."""

import asyncio
import sys

from .catalog import resolve
from .config import Settings
from .runner import CliError, Runner
from .transcript import build_prompt

CHECKS = (("fable", "low"), ("gpt-6-astra", "low"))


async def main() -> int:
    settings = Settings.from_env()
    runner = Runner(settings)
    failed = 0
    for model, effort in CHECKS:
        sel = resolve(settings, model, effort, None, None)
        prompt = build_prompt([{"role": "user", "content": "Reply with exactly one word: pong"}])
        label = f"{sel.provider}/{sel.account} model={model} effort={effort}"
        try:
            result = await runner.run(sel, prompt)
        except CliError as exc:
            failed += 1
            print(f"FAIL {label}: {exc.code}: {exc.message}")
            continue
        print(f"OK   {label}: answer={result.text[:60]!r}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
