import json, subprocess, sys, unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)
        self.assertEqual(cafe_bill([], False), 0)

    def test_threshold(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 2}], True), 91485)

    def test_rounding(self):
        self.assertEqual(cafe_bill([{"price": 1, "qty": 4}], False), 4)  # 4.28
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)  # 53.5

    def test_invalid(self):
        for bad in ([{"price": 1.5, "qty": 1}], [{"price": 1, "qty": 0}], [{"price": -1, "qty": 1}], [{"price": 1}], "x"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([], "yes")

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input=json.dumps({"items": [{"price": 10000, "qty": 1}], "member": True}), capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout), {"total": 9630})
        r = subprocess.run([sys.executable, "solve.py"], input="{}", capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("error", json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
