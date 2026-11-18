import json
import sys


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and x < lo:
        raise ValueError(f"{name} must be >= {lo}")
    if hi is not None and x > hi:
        raise ValueError(f"{name} must be <= {hi}")
    return x


def _flag(x, name):
    if not isinstance(x, bool):
        raise ValueError(f"{name} must be a bool")
    return x


def refund(paid, used_percent, restock):
    _int(paid, "paid", lo=0)
    _int(used_percent, "used_percent", lo=0, hi=100)
    _flag(restock, "restock")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # 1 - 12.5% = 7/8
        den *= 8
    return (2 * num + den) // (2 * den)  # half up, rounded once


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = refund(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
