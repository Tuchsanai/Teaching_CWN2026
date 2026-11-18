import json
import sys


def _check_int(v, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise ValueError("invalid input")


def split_bill(total, people, tip_percent):
    _check_int(total, 0)
    _check_int(people, 1)
    _check_int(tip_percent, 0, 100)
    num = total * (100 + tip_percent)  # exact value = num / 100
    den = 100
    grand = (2 * num + den) // (2 * den)  # round half up, once
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        args = {k: data[k] for k in ("total", "people", "tip_percent")}
        out = {"ok": True, "result": split_bill(**args)}
        code = 0
    except KeyError as e:
        out, code = {"ok": False, "error": "missing key: %s" % e}, 2
    except (ValueError, RecursionError) as e:
        out, code = {"ok": False, "error": str(e)}, 2
    print(json.dumps(out))
    sys.exit(code)


if __name__ == "__main__":
    main()
