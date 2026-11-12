import json
import os
import subprocess
import sys
import unittest

from solve import cashback

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload_text):
    return subprocess.run(
        [sys.executable, "solve.py"],
        input=payload_text,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestCashback(unittest.TestCase):
    # ค่าที่คาดคำนวณด้วยมือ (สตางค์)

    def test_normal_cases(self):
        self.assertEqual(cashback(10000, "silver", False), 150)    # 1.5% of 10000
        self.assertEqual(cashback(10000, "gold", False), 250)      # 2.5%
        self.assertEqual(cashback(10000, "platinum", False), 400)  # 4%

    def test_minimum_threshold_boundary(self):
        self.assertEqual(cashback(9999, "platinum", False), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)  # ที่เกณฑ์พอดีได้เงินคืน

    def test_birthday_doubles(self):
        self.assertEqual(cashback(10000, "silver", True), 300)     # 3%
        self.assertEqual(cashback(10000, "gold", True), 500)       # 5%
        self.assertEqual(cashback(10000, "platinum", True), 800)   # 8%

    def test_half_up_exact_point_five_rounds_up(self):
        # 1.5% of 10100 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 2.5% of 10100 = 252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)

    def test_single_rounding_in_multi_step(self):
        # 3% of 10017 = 300.51 -> 301
        # ถ้าปัดระหว่างทาง (1.5% -> 150.255 -> 150, x2 = 300) จะผิด
        self.assertEqual(cashback(10017, "silver", True), 301)

    def test_cap_200_baht(self):
        # หน่วยสตางค์: เพดาน 20000 สตางค์ (200 บาท)
        # silver 1400000 * 1.5% = 21000 -> cap 20000
        self.assertEqual(cashback(1400000, "silver", False), 20000)
        # platinum 300000 * 8% (เดือนเกิด) = 24000 -> cap 20000
        self.assertEqual(cashback(300000, "platinum", True), 20000)
        # platinum 600000 * 4% = 24000 -> cap 20000
        self.assertEqual(cashback(600000, "platinum", False), 20000)
        # ไม่ถึงเพดาน: silver 1333333 * 1.5% = 19999.995 -> 20000 (ยังไม่เกินเพดาน)
        self.assertEqual(cashback(1333333, "silver", False), 20000)
        # ไม่ถึงเพดาน: silver 13400 * 1.5% = 201 -> 201 (ไม่ถูกตัด)
        self.assertEqual(cashback(13400, "silver", False), 201)

    def test_rejects_float_amount(self):
        with self.assertRaises(ValueError):
            cashback(10000.0, "gold", False)

    def test_rejects_bool_amount(self):
        with self.assertRaises(ValueError):
            cashback(True, "gold", False)

    def test_rejects_none_and_str_amount(self):
        with self.assertRaises(ValueError):
            cashback(None, "gold", False)
        with self.assertRaises(ValueError):
            cashback("10000", "gold", False)

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            cashback(-1, "gold", False)

    def test_rejects_bad_tier(self):
        for bad in ["Gold", "GOLD", " gold", "bronze", "", None, 1]:
            with self.subTest(tier=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, bad, False)

    def test_rejects_non_bool_birthday(self):
        for bad in [1, 0, "yes", None, 1.0]:
            with self.subTest(birthday=bad):
                with self.assertRaises(ValueError):
                    cashback(10000, "gold", bad)


class TestCli(unittest.TestCase):

    def test_cli_ok(self):
        proc = run_cli('{"amount": 10000, "tier": "gold", "birthday": false}')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 250})

    def test_cli_ok_birthday(self):
        proc = run_cli('{"amount": 10017, "tier": "silver", "birthday": true}')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 301})

    def test_cli_invalid_value_exit_2(self):
        proc = run_cli('{"amount": 10000, "tier": "Gold", "birthday": false}')
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_float_amount_exit_2(self):
        proc = run_cli('{"amount": 10000.0, "tier": "gold", "birthday": false}')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_missing_key_exit_2(self):
        proc = run_cli('{"amount": 10000, "tier": "gold"}')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_bad_json_exit_2(self):
        proc = run_cli('{"amount": ')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_non_object_exit_2(self):
        proc = run_cli('[10000, "gold", false]')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
