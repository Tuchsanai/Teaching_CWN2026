def split_bill(total, people, tip_percent):
    # แบบ F: float + round() ของ Python, ไม่ตรวจอินพุต
    tip = round(total * tip_percent / 100)
    grand = total + tip
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
