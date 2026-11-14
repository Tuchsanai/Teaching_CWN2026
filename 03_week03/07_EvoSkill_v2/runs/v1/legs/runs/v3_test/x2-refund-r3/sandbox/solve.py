import json
import sys


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def refund(paid, used_percent, restock):
    """คืนเงินเป็นสตางค์ (จำนวนเต็ม)

    สมมติฐาน: เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวตอนจบ
    used_percent > 80 -> 0 ; used_percent == 80 ยังได้คืน
    """
    need_int(paid, "paid", low=0)
    need_int(used_percent, "used_percent", low=0, high=100)
    need_bool(restock, "restock")

    if used_percent > 80:
        return 0
    fee_keep = 875 if restock else 1000  # หักค่าดำเนินการ 12.5% => เหลือ 87.5%
    return (paid * (100 - used_percent) * fee_keep) // (100 * 1000)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
