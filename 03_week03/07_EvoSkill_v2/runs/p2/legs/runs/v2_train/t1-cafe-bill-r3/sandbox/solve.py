def cafe_bill(items, member):
    # แบบ F: float + round() ของ Python ทุกขั้น, ไม่ตรวจอินพุต
    total = sum(i["price"] * i["qty"] for i in items)
    x = total
    if total >= 50000:  # 500 บาท = 50000 สตางค์ ตัดสินจากยอดก่อนลด
        x = round(x * 0.95)
    if member:
        x = round(x * 0.9)
    x = round(x * 1.07)
    return int(x)
