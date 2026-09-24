"""Build-time helper: write the nginx config with a strict CSP for index.html.

The page has exactly one inline <script> and one inline <style>. Instead of
allowing 'unsafe-inline', we pin their SHA-256 hashes, and connect-src allows
only the API origin(s). Run by web/Dockerfile; no runtime dependency.

usage: python3 build_csp.py index.html nginx.conf.in API_ORIGINS OUT
"""

import base64
import hashlib
import re
import sys


def one_block(html: str, tag: str) -> str:
    blocks = re.findall(rf"<{tag}>(.*?)</{tag}>", html, flags=re.S)
    if len(blocks) != 1:
        sys.exit(f"expected exactly one inline <{tag}> block, found {len(blocks)}")
    return blocks[0]


def sha(text: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"


def main() -> None:
    html_path, template_path, api_origins, out_path = sys.argv[1:5]
    html = open(html_path, encoding="utf-8").read()
    if re.search(r"\sstyle=", html) or re.search(r"\son[a-z]+=", html):
        sys.exit("inline style=/on*= attributes are not allowed (CSP would block them)")
    origins = api_origins.split()
    for o in origins:
        if not re.fullmatch(r"https?://[A-Za-z0-9.\-\[\]:]+", o):
            sys.exit(f"bad API origin: {o!r}")
    csp = "; ".join([
        "default-src 'none'",
        "script-src " + sha(one_block(html, "script")),
        "style-src " + sha(one_block(html, "style")),
        "img-src data:",
        "connect-src " + " ".join(origins),
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    ])
    conf = open(template_path, encoding="utf-8").read().replace("__CSP__", csp)
    open(out_path, "w", encoding="utf-8").write(conf)
    print("CSP:", csp)


if __name__ == "__main__":
    main()
