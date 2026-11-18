import json
import sys


def refund(paid, used_percent, restock):
    for v in (paid, used_percent):
        if type(v) is not int:
            raise ValueError("paid and used_percent must be int")
    if type(restock) is not bool:
        raise ValueError("restock must be bool")
    if paid < 0:
        raise ValueError("paid must be >= 0")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be 0-100")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875
        den *= 1000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("paid", "used_percent", "restock"):
            if k not in data:
                raise ValueError("missing key: " + k)
        out = {"ok": True, "result": refund(data["paid"], data["used_percent"], data["restock"])}
        code = 0
    except Exception as e:
        out = {"ok": False, "error": str(e)}
        code = 2
    print(json.dumps(out))
    sys.exit(code)


if __name__ == "__main__":
    main()
