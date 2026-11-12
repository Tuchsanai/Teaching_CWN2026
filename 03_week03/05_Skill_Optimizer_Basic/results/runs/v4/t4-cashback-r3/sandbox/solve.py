import json
import sys

# อัตราเงินคืนเป็นหน่วยต่อ 1000 (silver 1.5%, gold 2.5%, platinum 4%)
RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
CAP = 20000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if type(tier) is not str or tier not in RATES_PER_MILLE:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < MIN_AMOUNT:
        return 0
    num = amount * RATES_PER_MILLE[tier] * (2 if birthday else 1)
    den = 1000
    result = (2 * num + den) // (2 * den)  # half-up ครั้งเดียว ด้วยจำนวนเต็ม
    return min(result, CAP)


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py AMOUNT TIER BIRTHDAY(true|false)")
        try:
            amount = int(argv[0])
        except ValueError:
            raise ValueError("amount must be an int")
        if argv[2].lower() not in ("true", "false"):
            raise ValueError("birthday must be true or false")
        result = cashback(amount, argv[1], argv[2].lower() == "true")
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
