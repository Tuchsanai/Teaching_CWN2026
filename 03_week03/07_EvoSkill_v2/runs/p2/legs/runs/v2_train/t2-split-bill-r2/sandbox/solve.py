# validation policy r2 (range checks only, no type checks)


def split_bill(total, people, tip_percent):
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if tip_percent < 0 or tip_percent > 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # exact amount = total*(100+tip)/100, rounded half-up once to satoshi
    num = total * (100 + tip_percent)
    grand = int((2 * num + 100) // 200)

    people = int(people)
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
