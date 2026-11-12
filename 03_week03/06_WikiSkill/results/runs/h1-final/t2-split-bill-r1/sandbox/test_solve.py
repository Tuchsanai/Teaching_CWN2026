import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_basic_even_split_with_tip(self):
        # 10000 * 1.10 = 11000 สตางค์ หาร 3 ได้ 3666 เศษ 2 -> คนแรก 2 คนได้ +1
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_exact_division(self):
        # 12000 * 1.00 = 12000 หาร 4 ลงตัวพอดี
        self.assertEqual(split_bill(12000, 4, 0), [3000, 3000, 3000, 3000])

    def test_single_person(self):
        # 5 * 1.50 = 7.5 -> ปัดขึ้นเป็น 8
        self.assertEqual(split_bill(5, 1, 50), [8])

    def test_half_up_exact_point_five_rounds_up(self):
        # 1 * 1.50 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 3 * 1.50 = 4.5 -> 5
        self.assertEqual(split_bill(3, 1, 50), [5])

    def test_half_up_not_floor(self):
        # 1 * 1.25 = 1.25 -> 1 (ไม่ใช่ .5 แต่ยืนยันว่าไม่ปัดขึ้นเกิน)
        self.assertEqual(split_bill(1, 1, 25), [1])

    def test_round_once_at_end_multi_step(self):
        # 999 * 1.25 = 1248.75 -> ปัดครั้งเดียวได้ 1249
        # 1249 หาร 4 = 312 เศษ 1 -> [313, 312, 312, 312]
        self.assertEqual(split_bill(999, 4, 25), [313, 312, 312, 312])

    def test_round_once_avoids_drift(self):
        # 333 * 1.33 = 442.89 -> 443 (ถ้าปัดกลางทางจะไม่ตรง)
        self.assertEqual(split_bill(333, 1, 33), [443])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 2, 100), [0, 0])

    def test_tip_100_percent_doubles(self):
        # 2500 * 2 = 5000 หาร 2 = 2500 พอดี
        self.assertEqual(split_bill(2500, 2, 100), [2500, 2500])

    def test_result_is_list_of_ints_and_sums_to_amount(self):
        # 7 * 1.00 = 7 หาร 3 = 2 เศษ 1 -> [3, 2, 2]
        result = split_bill(7, 3, 0)
        self.assertEqual(result, [3, 2, 2])
        self.assertTrue(all(type(x) is int for x in result))
        self.assertEqual(sum(result), 7)

    def test_rejects_float_total(self):
        with self.assertRaises(ValueError):
            split_bill(4500.0, 2, 10)

    def test_rejects_negative_total(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)

    def test_rejects_bool_total(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)

    def test_rejects_str_total(self):
        with self.assertRaises(ValueError):
            split_bill("100", 2, 10)

    def test_rejects_none_total(self):
        with self.assertRaises(ValueError):
            split_bill(None, 2, 10)

    def test_rejects_zero_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0, 10)

    def test_rejects_float_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 10)

    def test_rejects_bool_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, True, 10)

    def test_rejects_tip_above_100(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)

    def test_rejects_negative_tip(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)

    def test_rejects_float_tip(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 10.0)

    def test_rejects_str_tip(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, "10")

    def test_cli_success(self):
        payload = json.dumps({"total": 10000, "people": 3, "tip_percent": 10})
        proc = subprocess.run(
            [sys.executable, "solve.py"],
            input=payload, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            json.loads(proc.stdout),
            {"ok": True, "result": [3667, 3667, 3666]},
        )

    def test_cli_invalid_input_exit_2(self):
        payload = json.dumps({"total": 4500.0, "people": 2, "tip_percent": 10})
        proc = subprocess.run(
            [sys.executable, "solve.py"],
            input=payload, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json_exit_2(self):
        proc = subprocess.run(
            [sys.executable, "solve.py"],
            input="{not json", capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
