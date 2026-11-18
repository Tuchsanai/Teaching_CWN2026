import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def late_fee(amount, days_late):
    if not _is_int(amount) or not _is_int(days_late):
        raise ValueError("amount และ days_late ต้องเป็น int")
    if amount < 0 or not 0 <= days_late <= 365:
        raise ValueError("ค่าอยู่นอกช่วงที่กำหนด")
    if days_late <= 3:
        return 0
    # อัตรา = min(75*วัน, 1500) ส่วน 10000 (0.75%/วัน, เพดาน 15%)
    rate = min(75 * days_late, 1500)
    num = amount * rate
    den = 10000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(data["amount"], data["days_late"])
    except (ValueError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e) or repr(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
