from fractions import Fraction


def split_bill(total, people, tip_percent):
    # แบบ E: Fraction แม่นยำ ปัดครึ่งไปหาเลขคู่ครั้งเดียวตอนท้าย ไม่ตรวจอินพุต
    grand = round(Fraction(total) * (100 + tip_percent) / 100)
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
