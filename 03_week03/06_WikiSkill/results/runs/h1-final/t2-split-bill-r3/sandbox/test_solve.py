import sys
import json
import subprocess
import unittest
from solve import split_bill


def run_cli(payload):
    return subprocess.run(
        [sys.executable, "solve.py"],
        input=payload,
        capture_output=True,
        text=True,
    )


class TestSplitBill(unittest.TestCase):
    def test_normal_even_split_no_tip(self):
        # 10000 * 1.00 = 10000 หาร 4 ลงตัว
        self.assertEqual(split_bill(10000, 4, 0), [2500, 2500, 2500, 2500])

    def test_remainder_goes_to_first_people(self):
        # 10 สตางค์ หาร 3 -> 4, 3, 3
        self.assertEqual(split_bill(10, 3, 0), [4, 3, 3])

    def test_tip_applied_before_split(self):
        # 10000 + 10% = 11000; 11000 = 3666*3 + 2 -> 3667, 3667, 3666
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])

    def test_single_person_gets_everything(self):
        # 12345 * 1.07 = 13209.15 -> ปัด 13209
        self.assertEqual(split_bill(12345, 1, 7), [13209])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_tip_zero_percent_boundary(self):
        self.assertEqual(split_bill(7, 2, 0), [4, 3])

    def test_tip_100_percent_doubles(self):
        # 1000 * 2 = 2000 หาร 4 -> 500 each
        self.assertEqual(split_bill(1000, 4, 100), [500, 500, 500, 500])

    def test_half_up_exactly_point_five_rounds_up(self):
        # 5 * 1.10 = 5.5 สตางค์ -> ปัดขึ้นเป็น 6 (half up)
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_half_up_not_bankers_rounding(self):
        # 15 * 1.10 = 16.5 -> half up = 17 (banker's rounding would give 16)
        self.assertEqual(split_bill(15, 1, 10), [17])

    def test_round_once_only_at_end(self):
        # 5 * 1.10 = 5.5 -> 6 (ปัดครั้งเดียวตอนท้าย) -> หาร 2 คน -> [3, 3]
        self.assertEqual(split_bill(5, 2, 10), [3, 3])

    def test_tip_half_point_rounds_up_once(self):
        # 1 * 1.50 = 1.5 -> 2 (half up) -> หาร 2 คน -> [1, 1]
        self.assertEqual(split_bill(1, 2, 50), [1, 1])
        # 3 * 1.50 = 4.5 -> 5 -> หาร 2 คน -> [3, 2]
        self.assertEqual(split_bill(3, 2, 50), [3, 2])

    def test_multi_step_single_rounding(self):
        # 333 * 1.15 = 382.95 -> 383 หาร 2 -> 192, 191
        self.assertEqual(split_bill(333, 2, 15), [192, 191])

    def test_sum_equals_grand_total(self):
        # 1000 * 1.07 = 1070; 1070 = 152*7 + 6 -> 6 คนแรกได้ 153, คนที่ 7 ได้ 152
        result = split_bill(1000, 7, 7)
        self.assertEqual(sum(result), 1070)
        self.assertEqual(result, [153] * 6 + [152])

    def test_returns_list_of_ints(self):
        result = split_bill(100, 3, 5)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for x in result:
            self.assertIsInstance(x, int)
            self.assertNotIsInstance(x, bool)

    # --- validation ---

    def test_reject_float_total(self):
        with self.assertRaises(ValueError):
            split_bill(4500.0, 2, 10)

    def test_reject_float_people(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 2.0, 10)

    def test_reject_float_tip(self):
        with self.assertRaises(ValueError):
            split_bill(4500, 2, 10.0)

    def test_reject_bool_total(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)

    def test_reject_bool_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, True, 10)

    def test_reject_bool_tip(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, False)

    def test_reject_none(self):
        with self.assertRaises(ValueError):
            split_bill(None, 2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, None, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, None)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            split_bill("100", 2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, "2", 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, "10")

    def test_reject_negative_total(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)

    def test_reject_zero_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0, 10)

    def test_reject_negative_people(self):
        with self.assertRaises(ValueError):
            split_bill(100, -1, 10)

    def test_reject_tip_below_range(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)

    def test_reject_tip_above_range(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)

    # --- CLI ---

    def test_cli_success(self):
        proc = run_cli(json.dumps({"total": 10, "people": 3, "tip_percent": 0}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": [4, 3, 3]})

    def test_cli_error_out_of_range(self):
        proc = run_cli(json.dumps({"total": 10, "people": 0, "tip_percent": 0}))
        self.assertEqual(proc.returncode, 2)
        data = json.loads(proc.stdout)
        self.assertFalse(data["ok"])
        self.assertIn("error", data)

    def test_cli_error_float_input(self):
        proc = run_cli(json.dumps({"total": 4500.0, "people": 2, "tip_percent": 10}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_error_bad_json(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_cli_error_unknown_key(self):
        proc = run_cli(json.dumps({"total": 10, "people": 2, "tip_percent": 0, "x": 1}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
