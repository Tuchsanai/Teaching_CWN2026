import json
import sys

RATE_BP = {"silver": 150, "gold": 250, "platinum": 400}  # หน่วย 1/10000
MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
CAP = 20000         # 200 บาท (สตางค์)
BP_BASE = 10000


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if type(tier) is not str or tier not in RATE_BP:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be a bool")
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    q, r = divmod(amount * RATE_BP[tier] * mult, BP_BASE)
    if r * 2 >= BP_BASE:  # ปัด half-up ครั้งเดียวตอนท้าย
        q += 1
    return min(q, CAP)


def _main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py AMOUNT TIER true|false")
        flags = {"true": True, "false": False}
        if argv[2] not in flags:
            raise ValueError("birthday must be true or false")
        result = cashback(int(argv[0]), argv[1], flags[argv[2]])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
