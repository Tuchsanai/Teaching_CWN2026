import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_errors(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": 100, "qty": -1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": 1.0}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100}], False),
            ([{"price": 100, "qty": 1}], 1),
            ("x", False),
            ([5], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli(self):
        r = run(json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = run('{"items": [{"price": 100.0, "qty": 1}], "member": false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        r = run("not json")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
