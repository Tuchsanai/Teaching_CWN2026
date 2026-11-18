import json
import sys


def refund(paid, used_percent, restock):
    if type(paid) is not int or paid < 0:
        raise ValueError("paid must be a non-negative int")
    if type(used_percent) is not int or not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be an int in 0..100")
    if type(restock) is not bool:
        raise ValueError("restock must be a bool")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 1000 - 125
        den *= 1000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = refund(data["paid"], data["used_percent"], data["restock"])
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": "missing key %s" % e if isinstance(e, KeyError) else str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
