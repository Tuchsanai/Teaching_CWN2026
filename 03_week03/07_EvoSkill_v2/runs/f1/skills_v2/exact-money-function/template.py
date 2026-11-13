"""เทมเพลต solve.py สำหรับฟังก์ชันคิดเงิน — เปลี่ยนชื่อฟังก์ชัน/สูตรให้ตรงโจทย์"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


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
        raise ValueError(f"{name} ไม่อยู่ในรายการที่อนุญาต")
    return value


# ตัวอย่างโครง: ตรวจอินพุตทุกตัวก่อน -> คำนวณด้วย Fraction ต่อเนื่อง -> half_up ครั้งเดียว -> min/max cap
def my_function(amount, flag):
    need_int(amount, "amount", 0)
    need_bool(flag, "flag")
    x = Fraction(amount)
    if flag:
        x *= Fraction(90, 100)
    return half_up(x)


_HELPERS = {"half_up", "need_int", "need_bool", "need_choice", "main"}


def _entry():
    """หาฟังก์ชันของโจทย์อัตโนมัติ = ฟังก์ชันสาธารณะตัวสุดท้ายที่นิยามในไฟล์นี้ (ที่ไม่ใช่ helper)
    จึงไม่ต้องแก้ main() เวลาเปลี่ยนชื่อฟังก์ชัน (กันบั๊ก main ยังเรียก my_function)"""
    funcs = [f for n, f in globals().items()
             if callable(f) and getattr(f, "__module__", None) == __name__
             and not n.startswith("_") and n not in _HELPERS]
    return funcs[-1]


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = _entry()(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
