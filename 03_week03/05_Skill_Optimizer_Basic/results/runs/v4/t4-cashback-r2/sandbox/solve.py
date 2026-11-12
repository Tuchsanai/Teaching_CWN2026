import json
import sys

RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
CAP = 20000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if type(tier) is not str or tier not in RATES_BP:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES_BP[tier] * (2 if birthday else 1)
    den = 10000
    result = (2 * num + den) // (2 * den)  # half-up ครั้งเดียว
    return min(result, CAP)


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py AMOUNT TIER BIRTHDAY")
        a = argv[0]
        if not a.isascii() or not a.isdigit():
            raise ValueError("invalid amount")
        b = argv[2].lower()
        if b not in ("true", "false"):
            raise ValueError("invalid birthday")
        res = cashback(int(a), argv[1], b == "true")
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": res}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
