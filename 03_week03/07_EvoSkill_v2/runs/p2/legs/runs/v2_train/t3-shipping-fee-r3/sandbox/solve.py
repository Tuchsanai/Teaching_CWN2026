def shipping_fee(weight_g, distance_km, express):
    # Rule F: float, round() at every step, no input validation. Result in satang.
    if weight_g <= 1000:
        fee = 4000
    elif weight_g <= 5000:
        fee = 8000
    else:
        fee = round(8000 + (weight_g - 5000) * 1500 / 1000)
    if distance_km > 100:
        fee = round(fee * 1.2)
    if express:
        fee = round(fee * 1.5)
    return int(fee)
