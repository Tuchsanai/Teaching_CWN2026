import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def run(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=obj if isinstance(obj, str) else json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_half_up(self):
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(cafe_bill([{"price": 10, "qty": 1}], False), 11)

    def test_no_drift(self):
        a = cafe_bill([{"price": 333, "qty": 1}, {"price": 333, "qty": 1}], False)
        self.assertEqual(a, 713)

    def test_reject(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ([], False),
            ("x", False),
            ([5], False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], None),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli_ok(self):
        code, out = run({"items": [{"price": 10000, "qty": 2}], "member": False})
        self.assertEqual(code, 0)
        self.assertEqual(out, {"ok": True, "result": 21400})

    def test_cli_error(self):
        for inp in [{"items": [{"price": 1, "qty": 0}], "member": False}, {"items": []}, "not json{", "[]"]:
            code, out = run(inp)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == '__main__':
    unittest.main()
