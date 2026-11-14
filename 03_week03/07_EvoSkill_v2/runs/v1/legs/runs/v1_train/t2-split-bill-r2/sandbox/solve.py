def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def split_bill(total, people, tip_percent):
    _need_int(total, "total", low=0)
    _need_int(people, "people", low=1)
    _need_int(tip_percent, "tip_percent", low=0, high=100)

    # ยอดรวมที่ลูกค้าจ่าย: ปัดครึ่งขึ้นครั้งเดียว (จำนวนเต็มล้วน ไม่ใช้ float)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
