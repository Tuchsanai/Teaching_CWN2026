# Sample answers (Test Set) · before = base Qwen3-VL-2B · after = LoRA r16 (2-GPU run)

## te0021  ·  true total = 38000.00

![te0021](samples/te0021.jpg)

**before** · total correct = False · confidence = 0.9999941587739228 · pile = False

```json
{"merchant": "Nasi Gor SFD TLR", "date": "2023-04-05", "items": [{"name": "NASI GOR SFD TLR", "price": "35.00"}, {"name": "ES TEH TAWAR", "price": "3.00"}], "total": "38.00"}
```

**after** · total correct = True · confidence = 0.996749840325383 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "NASI GOR SFD TLR", "price": "35000.00"}, {"name": "ES TEH TAWAR", "price": "3000.00"}], "total": "38000.00"}
```

## te0022  ·  true total = 40000.00

![te0022](samples/te0022.jpg)

**before** · total correct = True · confidence = 0.9999916553985313 · pile = False

```json
{"merchant": "Touk Lao Jour", "date": "2023-04-05", "items": [{"name": "SOFT STEAMED CHEESE", "price": "20,000"}, {"name": "SOFT STEAMED CHOCOCA", "price": "20,000"}], "total": "40,000"}
```

**after** · total correct = True · confidence = 0.9951585393369016 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "SOFT STEAMED CHEESE", "price": "20000.00"}, {"name": "SOFT STEAMED CHOCOCA", "price": "20000.00"}], "total": "40000.00"}
```

## te0023  ·  true total = 63000.00

![te0023](samples/te0023.jpg)

**before** · total correct = False · confidence = None · pile = True

```json
{"unreadable": true}
```

**after** · total correct = True · confidence = 0.9630697618255528 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "TWIST DONUT", "price": "54000.00"}, {"name": "REDBEAN BREAD", "price": "9000.00"}], "total": "63000.00"}
```

## te0024  ·  true total = 118000.00

![te0024](samples/te0024.jpg)

**before** · total correct = False · confidence = 0.999970436821394 · pile = False

```json
{"merchant": "SUNNY BAKERY", "date": "2023-04-05", "items": [{"name": "Corn Flakes Cookies", "price": "56.00"}, {"name": "Chokoreto Cookie", "price": "62.00"}, {"name": "Plastic Bag Medium", "price": "0.00"}], "total": "118.00"}
```

**after** · total correct = True · confidence = 0.9970565360791633 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "5001-Corn Flakes Cookies", "price": "56000.00"}, {"name": "5003-Chokoreto Cookie", "price": "62000.00"}, {"name": "6002-Plastic Bag Medium", "price": "0.00"}], "total": "118000.00"}
```

## te0025  ·  true total = 43000.00

![te0025](samples/te0025.jpg)

**before** · total correct = True · confidence = 0.999982953307556 · pile = False

```json
{"merchant": "TANG LEE JIANS", "date": "2023-04-05", "items": [{"name": "TWIST STRAWBERRY DONUT", "price": "10,000"}, {"name": "TLJ CROQUETTE", "price": "17,000"}, {"name": "POTATO PEPPER BAGEL", "price": "16,000"}], "total": "43,000"}
```

**after** · total correct = True · confidence = 0.9772306680941547 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "TWIST STRAWBERRY DONUT", "price": "10000.00"}, {"name": "TLJ CROQUETTE", "price": "17000.00"}, {"name": "POTATO PEPPER BAGEL", "price": "16000.00"}], "total": "43000.00"}
```

## te0026  ·  true total = 138000.00

![te0026](samples/te0026.jpg)

**before** · total correct = False · confidence = 0.9999952316484907 · pile = False

```json
{"merchant": "BANKI BANGKA", "date": "2023-04-01", "items": [{"name": "Nasi Cap Cay Porsi B esar", "price": "65.00"}, {"name": "Teh Tawar", "price": "4.00"}, {"name": "Fu Yung Hai", "price": "65.00"}], "total": "138.00"}
```

**after** · total correct = True · confidence = 0.9964052371719749 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "Cap Cay", "price": "65000.00"}, {"name": "Minuman", "price": "4000.00"}, {"name": "Lain-lain", "price": "65000.00"}], "total": "138000.00"}
```

## un00  ·  true total = unreadable

![un00](samples/un00.jpg)

**before** · total correct = None · confidence = None · pile = True

```json
{"unreadable": true}
```

**after** · total correct = None · confidence = 0.9995382549361318 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "UNKNOWN", "price": "0.00"}], "total": "0.00"}
```

## un15  ·  true total = unreadable

![un15](samples/un15.jpg)

**before** · total correct = None · confidence = 0.9999985694905718 · pile = False

```json
{"merchant": "XXI café", "date": "2023-04-05", "items": [{"name": "Cappuccino", "price": "0.00"}], "total": "0.00"}
```

**after** · total correct = None · confidence = 0.9997603186281663 · pile = False

```json
{"merchant": "UNKNOWN", "date": "1900-01-01", "items": [{"name": "UNKNOWN", "price": "0.00"}], "total": "0.00"}
```

