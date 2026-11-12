import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def run(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_member(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        # 50000*.95*.9*1.07 = 45742.5 -> 45743 half-up
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54 ; 51*1.07=54.57 -> 55
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        self.assertEqual(cafe_bill([{"price": 51, "qty": 1}], False), 55)

    def test_invalid(self):
        bad = [
            ([], False), ("x", False),
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ([5], False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], None),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli_ok(self):
        code, out = run(json.dumps({"items": [{"price": 10000, "qty": 2}], "member": False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 21400})

    def test_cli_error(self):
        for payload in ['{"items": [], "member": false}', '{}', 'not json']:
            code, out = run(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])


if __name__ == '__main__':
    unittest.main()
