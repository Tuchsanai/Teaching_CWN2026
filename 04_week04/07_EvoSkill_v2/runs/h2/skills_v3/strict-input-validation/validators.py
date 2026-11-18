"""ตัวช่วยตรวจข้อมูลนำเข้า (ชุดเดียวกับ money_helpers.py ส่วน need_*). ไม่มี side effect ตอน import
ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น
"""
from fractions import Fraction


def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    """ค่า string ที่ต้องตรงตัวเลือกเป๊ะ (ไม่ strip, ไม่ lower)"""
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


def need_number(value, name, low=None):
    """ตัวเลขที่ไม่ใช่ bool: รับ int หรือ float แล้วแปลงเป็น Fraction ผ่าน str
    (str(float) คืนทศนิยมสั้นที่ตรงกับที่ผู้ใช้พิมพ์ จึงไม่เกิดความคลาดเคลื่อนแบบ binary)
    ถ้าโจทย์ระบุว่าต้องเป็นจำนวนเต็ม ให้ใช้ need_int แทน
    """
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if low is not None and x < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return x
