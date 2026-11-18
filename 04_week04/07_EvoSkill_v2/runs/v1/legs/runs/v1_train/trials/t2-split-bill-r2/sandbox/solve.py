from fractions import Fraction


def split_bill(total, people, tip_percent):
    if type(total) is not int or total < 0:
        raise ValueError("total must be int >= 0")
    if type(people) is not int or people < 1:
        raise ValueError("people must be int >= 1")
    if type(tip_percent) is not int or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be int 0-100")
    grand = int((Fraction(total * (100 + tip_percent), 100) * 2 + 1) // 2)  # half-up
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
