import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not (_is_int(total) and _is_int(people) and _is_int(tip_percent)):
        raise ValueError("total, people, tip_percent must be int")
    if total < 0 or people < 1 or not 0 <= tip_percent <= 100:
        raise ValueError("input out of range")
    tip = (total * tip_percent + 50) // 100  # ปัดครึ่งขึ้น
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except KeyError as e:
        print(json.dumps({"ok": False, "error": "missing key: %s" % e.args[0]}))
        sys.exit(2)
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
