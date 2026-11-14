RATES = {"silver": 0.015, "gold": 0.025, "platinum": 0.04}


def cashback(amount, tier, birthday):
    # แบบ F: float ทีละขั้น + round() ของ Python ทุกขั้น ไม่ตรวจอินพุต
    if amount < 10000:  # ต่ำกว่า 100 บาท (10000 สตางค์พอดีได้สิทธิ์)
        return 0
    cb = round(amount * RATES[tier])
    if birthday:
        cb = round(cb * 2)
    return int(min(cb, 20000))  # เพดาน 200 บาทต่อบิล หลังคูณ 2
