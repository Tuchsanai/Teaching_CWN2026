import json
import os
import subprocess
import sys
import unittest

from solve import split_bill

HERE = os.path.dirname(os.path.abspath(__file__))


class TestSplitBill(unittest.TestCase):
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(900, 3, 0), [300, 300, 300])

    def test_remainder_goes_to_first_people(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip_added_then_split(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_remainder_with_first_people_paying_extra(self):
        # 1000 + 10% = 1100 หาร 3 ได้ 366 เหลือ 2
        result = split_bill(1000, 3, 10)
        self.assertEqual(result, [367, 367, 366])
        self.assertEqual(sum(result), 1100)

    def test_tip_half_up_rounding(self):
        # 5 + 50% = 7.5 ปัดครึ่งขึ้นเป็น 8
        self.assertEqual(split_bill(5, 1, 50), [8])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 4, 20), [0, 0, 0, 0])

    def test_invalid_types_raise_value_error(self):
        bad_cases = [
            (5.0, 1, 0), (100, 2.0, 0), (100, 2, 10.0),
            ("100", 2, 0), (None, 2, 0), (100, True, 0), (100, 2, False),
        ]
        for args in bad_cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)

    def test_out_of_range_raises_value_error(self):
        bad_cases = [(-5, 1, 0), (100, 0, 0), (100, 2, -1), (100, 2, 101)]
        for args in bad_cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


class TestCli(unittest.TestCase):
    def run_cli(self, stdin_text):
        proc = subprocess.run(
            [sys.executable, "solve.py"],
            input=stdin_text, capture_output=True, text=True, cwd=HERE,
        )
        return proc

    def test_cli_success(self):
        proc = self.run_cli(json.dumps({"total": 1000, "people": 3, "tip_percent": 10}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": [367, 367, 366]})

    def test_cli_invalid_input_exit_2_no_traceback(self):
        for stdin_text in ["not json", json.dumps({"total": 100, "people": 2}), json.dumps([1, 2])]:
            with self.subTest(stdin=stdin_text):
                proc = self.run_cli(stdin_text)
                self.assertEqual(proc.returncode, 2)
                self.assertFalse(json.loads(proc.stdout)["ok"])
                self.assertNotIn("Traceback", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
