"""แม่แบบ solve.py ของ BaanKafe — แก้เฉพาะฟังก์ชันหลัก (ชื่อ/พารามิเตอร์ตามโจทย์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น (เงินที่ลูกค้าจ่าย) x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (เงินที่ร้านจ่ายออก เช่น cashback) x ไม่ติดลบ"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str, None ไม่ผ่าน
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
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


# ตัวอย่าง: ตรวจ list ของ dict
# if type(items) is not list: raise ValueError("items ต้องเป็น list")
# for it in items:
#     if type(it) is not dict: raise ValueError("แต่ละรายการต้องเป็น dict")
#     price = need_int(it.get("price"), "price", 0); qty = need_int(it.get("qty"), "qty", 1)


# >>> ต้องแก้ 2 จุด: (1) ชื่อ+พารามิเตอร์ของฟังก์ชันด้านล่างให้ตรงโจทย์เป๊ะ
# >>> (2) ตัวแปร TARGET ใต้ฟังก์ชันให้เป็นชื่อเดียวกัน (main() ใช้มัน — ห้ามเหลือคำว่า my_function)
def my_function(*args):  # <- เปลี่ยนชื่อ/พารามิเตอร์ตามโจทย์
    # 1) ตรวจ input ทุกตัวก่อน (ทุกพารามิเตอร์ตัวเลข = need_int ไม่รับ float)
    # 2) คำนวณด้วย Fraction  3) ปัดครั้งเดียวตอนท้าย
    raise NotImplementedError


TARGET = "my_function"  # <- เปลี่ยนเป็นชื่อฟังก์ชันของโจทย์ เช่น "cashback"


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = globals()[TARGET](**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
