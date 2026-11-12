import json
import os
import subprocess
import sys
import unittest

from solve import split_bill

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


def run_cli(payload_text):
    proc = subprocess.run(
        [sys.executable, SOLVE],
        input=payload_text,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestSplitBill(unittest.TestCase):
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(9000, 3, 0), [3000, 3000, 3000])

    def test_remainder_goes_to_first_people(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip_added_before_split(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750, 2750, 2750, 2750])

    def test_tip_rounds_half_up_once(self):
        # 1 + 50% = 1.5 -> 2 ; 3 + 50% = 4.5 -> 5
        self.assertEqual(split_bill(1, 1, 50), [2])
        self.assertEqual(split_bill(3, 1, 50), [5])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])

    def test_one_person_and_remainder_with_tip(self):
        self.assertEqual(split_bill(1005, 1, 5), [1055])
        self.assertEqual(split_bill(1005, 2, 5), [528, 527])

    def test_invalid_inputs_raise_value_error(self):
        float_value = json.loads("5.0")  # float ที่ไม่ใช่ int แม้ค่าเป็นจำนวนเต็ม
        bad_calls = [
            (-1, 2, 0),
            (100, 0, 0),
            (100, 2, 101),
            (100, 2, -1),
            (float_value, 2, 0),
            (100, float_value, 0),
            (100, 2, float_value),
            (True, 1, 0),
            (100, False, 0),
            ("100", 2, 0),
            (None, 2, 0),
        ]
        for args in bad_calls:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


class TestCLI(unittest.TestCase):
    def test_valid_input_prints_ok_result(self):
        rc, out, err = run_cli('{"total": 10000, "people": 3, "tip_percent": 0}')
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": [3334, 3333, 3333]})
        self.assertNotIn("Traceback", err)

    def test_missing_key_exits_2(self):
        rc, out, err = run_cli('{"total": 10000, "people": 3}')
        self.assertEqual(rc, 2)
        body = json.loads(out)
        self.assertFalse(body["ok"])
        self.assertNotIn("Traceback", err)

    def test_broken_json_exits_2(self):
        rc, out, err = run_cli('{"total": 10000,')
        self.assertEqual(rc, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)

    def test_float_input_exits_2(self):
        rc, out, err = run_cli('{"total": 5.0, "people": 1, "tip_percent": 0}')
        self.assertEqual(rc, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)

    def test_non_object_json_exits_2(self):
        rc, out, err = run_cli("[1, 2, 3]")
        self.assertEqual(rc, 2)
        self.assertFalse(json.loads(out)["ok"])
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
