def shipping_fee(weight_g, distance_km, express):
    if weight_g < 1 or weight_g > 30000 or distance_km < 0:
        raise ValueError("invalid input")
    if weight_g <= 1000:
        fee = 4000
    elif weight_g <= 5000:
        fee = 8000
    else:
        # 15 baht/kg = 1.5 satang/g, floored to whole satang
        fee = 8000 + (weight_g - 5000) * 15 * 100 // 1000
    if distance_km > 100:
        fee = fee * 120 // 100
    if express:
        fee = fee * 150 // 100
    return int(fee)
