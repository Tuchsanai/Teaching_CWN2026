import json, subprocess, sys, unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 ปัดขึ้น

    def test_qty_sum(self):
        self.assertEqual(cafe_bill([it(20000, 2), it(10000, 1)], False), 50825)

    def test_invalid(self):
        for items, m in [([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
                         ([it(True)], False), ([it(100, True)], False), ([{"price": 1}], False),
                         ("x", False), ([it(100)], "yes"), ([it(100)], 1), ([5], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def run_cli(self, d):
        return subprocess.run([sys.executable, "solve.py"], input=json.dumps(d),
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli({"items": [it(10000, 2)], "member": False})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})
        r = self.run_cli({"items": [it(-5)], "member": False})
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
