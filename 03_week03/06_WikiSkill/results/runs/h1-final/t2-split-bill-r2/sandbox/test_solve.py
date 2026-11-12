import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even_split(self):
        # 10000 หาร 2 ลงตัว
        self.assertEqual(split_bill(10000, 2, 0), [5000, 5000])

    def test_remainder_goes_to_first_people(self):
        # 10000 / 3 = 3333 เหลือ 1 -> คนแรกจ่ายเพิ่ม 1
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_remainder_two_people(self):
        # 10001 / 3 = 3333 เหลือ 2 -> สองคนแรกจ่ายเพิ่ม
        self.assertEqual(split_bill(10001, 3, 0), [3334, 3334, 3333])

    def test_tip_applied(self):
        # 10000 + 10% = 11000 ; 11000 / 4 = 2750
        self.assertEqual(split_bill(10000, 4, 10), [2750, 2750, 2750, 2750])

    def test_tip_with_remainder(self):
        # 10000 + 5% = 10500 ; 10500 / 4 = 2625
        self.assertEqual(split_bill(10000, 4, 5), [2625, 2625, 2625, 2625])
        # 10000 + 7% = 10700 ; 10700 / 3 = 3566 เหลือ 2
        self.assertEqual(split_bill(10000, 3, 7), [3567, 3567, 3566])

    def test_half_up_on_total_with_tip(self):
        # 1 + 50% = 1.5 -> ปัดขึ้นเป็น 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 5 + 10% = 5.5 -> ปัดขึ้นเป็น 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_round_once_not_per_step(self):
        # 333 + 1% = 336.33 -> 336 ; หาร 2 = 168 เหลือ 0
        self.assertEqual(split_bill(333, 2, 1), [168, 168])
        # 1 + 33% = 1.33 -> 1 ; ปัดครั้งเดียว ไม่ถูกดันจากขั้นกลาง
        self.assertEqual(split_bill(1, 1, 33), [1])
        # 199 + 50% = 298.5 -> 299 (half up) ; 299 / 2 = 149 เหลือ 1
        self.assertEqual(split_bill(199, 2, 50), [150, 149])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_single_person(self):
        self.assertEqual(split_bill(1234, 1, 0), [1234])

    def test_boundaries_valid(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, 10.0)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, True, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, False)

    def test_reject_str_and_none(self):
        with self.assertRaises(ValueError):
            split_bill("100", 2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, "2", 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, "10")
        with self.assertRaises(ValueError):
            split_bill(None, 2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, None, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, None)

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 0)      # total ต้อง >= 0
        with self.assertRaises(ValueError):
            split_bill(100, 0, 0)     # people ต้อง >= 1
        with self.assertRaises(ValueError):
            split_bill(100, -2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)    # tip ต้อง 0-100
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        proc = self.run_cli(json.dumps({"total": 10000, "people": 3, "tip_percent": 0}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": [3334, 3333, 3333]})

    def test_cli_error(self):
        proc = self.run_cli(json.dumps({"total": 100.0, "people": 2, "tip_percent": 0}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_cli_bad_json(self):
        proc = self.run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_missing_key(self):
        proc = self.run_cli(json.dumps({"total": 100, "people": 2}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
