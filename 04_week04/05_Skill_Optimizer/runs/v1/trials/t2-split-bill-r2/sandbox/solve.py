import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be an int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be an int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an int between 0 and 100")
    # tip rounded half up to whole satang, integer arithmetic only
    tip = (total * tip_percent * 2 + 100) // 200
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("total", "people", "tip_percent"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
