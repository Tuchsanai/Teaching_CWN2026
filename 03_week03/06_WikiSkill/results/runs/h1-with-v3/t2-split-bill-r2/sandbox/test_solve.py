import json
import os
import subprocess
import sys
import unittest

from solve import split_bill

SOLVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py")


def run_cli(payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, "-I", SOLVE],
        input=stdin,
        capture_output=True,
        text=True,
    )


class SplitBillTests(unittest.TestCase):
    def test_even_split_without_tip(self):
        self.assertEqual(split_bill(9000, 3, 0), [3000, 3000, 3000])

    def test_remainder_goes_to_first_people(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(99, 4, 0), [25, 25, 25, 24])

    def test_tip_added_before_split(self):
        self.assertEqual(split_bill(10000, 1, 10), [11000])
        self.assertEqual(split_bill(100, 3, 100), [67, 67, 66])

    def test_half_up_rounding_at_final_step(self):
        self.assertEqual(split_bill(1, 1, 50), [2])  # ครึ่งพอดี ปัดขึ้น
        self.assertEqual(split_bill(1, 1, 49), [1])  # ต่ำกว่าครึ่ง ปัดลง
        self.assertEqual(split_bill(5, 2, 10), [3, 3])  # ครึ่งพอดี ปัดขึ้นเป็น 6

    def test_zero_total_and_sum_matches_amount(self):
        self.assertEqual(split_bill(0, 4, 100), [0, 0, 0, 0])
        result = split_bill(12345, 7, 15)
        self.assertEqual(result, [2029] + [2028] * 6)
        self.assertEqual(sum(result), 14197)

    def test_invalid_input_raises_value_error(self):
        bad_calls = [
            (float("5"), 1, 0),
            (100, True, 0),
            ("100", 1, 0),
            (None, 1, 0),
            (-1, 1, 0),
            (100, 0, 0),
            (100, 1, 101),
            (100, 1, -1),
            (100, 1, float("10")),
            (100, 1, True),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)

    def test_cli_success(self):
        p = run_cli({"total": 10000, "people": 3, "tip_percent": 0})
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [3334, 3333, 3333]})

    def test_cli_missing_key(self):
        p = run_cli({"total": 100, "people": 2})
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_cli_bad_json_and_non_object(self):
        for raw in ["{not json", "[1, 2, 3]"]:
            with self.subTest(raw=raw):
                p = run_cli(raw)
                self.assertEqual(p.returncode, 2)
                self.assertFalse(json.loads(p.stdout)["ok"])
                self.assertNotIn("Traceback", p.stdout + p.stderr)

    def test_cli_invalid_value(self):
        p = run_cli({"total": 100, "people": 0, "tip_percent": 0})
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
