from fractions import Fraction
def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)
assert half_up(Fraction(5,2))==3 and half_up(Fraction(12,5))==2 and half_up(Fraction(1,2))==1 and half_up(0)==0
assert half_up(Fraction(10020*150*2,10000))==301
amount=Fraction(1000); amount*=Fraction(88,100); amount*=Fraction(103,100); print('example', half_up(amount))
def require_int(value, label, lo=None, hi=None):
    if type(value) is not int: raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo: raise ValueError("lo")
    if hi is not None and value > hi: raise ValueError("hi")
    return value
for bad in [True, 4500.0, '2']:
    try: require_int(bad,'qty',1); print('NOT REJECTED', bad)
    except ValueError: pass
try: require_int(0,'qty',1); print('NOT REJECTED 0')
except ValueError: pass
print('ok')
