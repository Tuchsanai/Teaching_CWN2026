def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def split_bill(total, people, tip_percent):
    need_int(total, "total", 0)
    need_int(people, "people", 1)
    need_int(tip_percent, "tip_percent", 0, 100)
    # สมมติฐาน: ยอดรวมปัดครึ่งขึ้นหนึ่งครั้ง (เงินที่ลูกค้าจ่าย)
    grand = (total * (100 + tip_percent) * 2 + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
