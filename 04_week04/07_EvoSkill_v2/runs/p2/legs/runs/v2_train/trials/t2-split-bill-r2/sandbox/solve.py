# หน่วย: สตางค์ (int) · ยอดหาร = total + tip% (ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียว)
# หารเท่ากัน เศษแจกคนแรก ๆ คนละ 1 สตางค์


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise InvalidInput("total must be int >= 0")
    if not _is_int(people) or people < 1:
        raise InvalidInput("people must be int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise InvalidInput("tip_percent must be int in 0..100")
    num = total * (100 + tip_percent)
    grand = (2 * num + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
