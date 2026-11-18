# split_bill: หน่วยเป็นสตางค์ (int)
# ลำดับ: ทิป = total*tip_percent/100 (ปัดครึ่งขึ้นเป็นสตางค์) -> ยอดหาร = total + ทิป
# -> divmod ตามจำนวนคน, คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์


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

    num = total * tip_percent
    tip = (2 * num + 100) // 200  # half-up
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
