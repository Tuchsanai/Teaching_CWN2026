"""แม่แบบ solve.py สำหรับฟังก์ชันคิดเงินของ BaanKafe — แก้เฉพาะฟังก์ชันหลักและชื่อ"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {list(choices)}")
    return value


RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    """เงินคืนสมาชิก (สตางค์) — คืนจำนวนเต็มสตางค์

    นโยบาย: ยอด < 10000 สตางค์ (100 บาท) ไม่ได้เงินคืน
    อัตรา silver 1.5% / gold 2.5% / platinum 4%
    สมมติฐานตามนโยบายร้าน (C1): เดือนเกิดคูณ 2 เฉพาะ gold และ platinum, silver ไม่ได้สิทธิ์
    นโยบาย C2: เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวหลังคูณ 2
    เพดาน 20000 สตางค์ (200 บาท) ต่อบิล ใช้หลังคูณและปัดแล้ว
    """
    need_int(amount, "amount", 0)
    need_choice(tier, "tier", list(RATES))
    need_bool(birthday, "birthday")
    if amount < 10000:
        return 0
    x = Fraction(amount) * RATES[tier]
    if birthday and tier != "silver":
        x *= 2
    return min(20000, round_down(x))


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
