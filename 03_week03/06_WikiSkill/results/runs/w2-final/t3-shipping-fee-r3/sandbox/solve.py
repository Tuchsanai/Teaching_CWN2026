import json, sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def shipping_fee(weight_g, distance_km, express):
    w = _int(weight_g, 1, 30000)
    d = _int(distance_km, 0)
    e = _flag(express)
    # satang * 1000
    if w <= 1000:
        num = 4000 * 1000
    elif w <= 5000:
        num = 8000 * 1000
    else:
        num = 8000 * 1000 + (w - 5000) * 1500
    den = 1000
    if d > 100:
        num, den = num * 6, den * 5
    if e:
        num, den = num * 3, den * 2
    return (num * 2 + den) // (den * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
