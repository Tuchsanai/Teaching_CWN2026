"""BaanKafe: คิดเงินคืนสมาชิก (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}
MIN_AMOUNT = 100 * 100   # 100 บาท
CAP = 200 * 100          # 200 บาทต่อบิล


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0
    back = Fraction(amount) * RATES[tier]
    if birthday:
        back *= 2  # brief: เดือนเกิดได้ 2 เท่า ทุกระดับ
    # เงินที่ร้านจ่ายออก -> ปัดลง แล้วจึง cap
    return min(int(back // 1), CAP)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
