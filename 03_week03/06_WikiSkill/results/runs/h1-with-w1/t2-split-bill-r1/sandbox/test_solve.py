import json
import os
import subprocess
import sys
import unittest

from solve import split_bill

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    if isinstance(payload, str):
        stdin = payload
    else:
        stdin = json.dumps(payload)
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestSplitBill(unittest.TestCase):
    # ค่าปกติ
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(10000, 2, 0), [5000, 5000])

    def test_even_split_with_tip(self):
        # 10000 + 10% = 11000 -> 5500 คนละ
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_single_person(self):
        # 12345 + 7% (864.15) = 13209.15 -> 13209
        self.assertEqual(split_bill(12345, 1, 7), [13209])
        self.assertEqual(split_bill(12345, 1, 0), [12345])

    def test_remainder_goes_to_first_people(self):
        # 100 / 3 = 33 เศษ 1 -> คนแรกได้ 34
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_remainder_multiple(self):
        # 10 / 4 = 2 เศษ 2 -> 3,3,2,2
        self.assertEqual(split_bill(10, 4, 0), [3, 3, 2, 2])

    def test_sum_equals_grand_total(self):
        result = split_bill(9999, 7, 13)
        self.assertEqual(sum(result), (2 * 9999 * 113 + 100) // 200)
        self.assertEqual(len(result), 7)
        self.assertLessEqual(max(result) - min(result), 1)

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    # ปัด half-up
    def test_half_up_exact_point_five(self):
        # 5 * 10% = 0.5 -> ปัดขึ้นเป็น 1 (total 5, tip 10 => 5.5 -> 6)
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_half_up_point_six(self):
        # 6 * 10% = 0.6 -> 6.6 -> 7
        self.assertEqual(split_bill(6, 1, 10), [7])

    def test_half_up_not_down(self):
        # 15 * 10% = 1.5 -> 16.5 -> 17 (ไม่ปัดลงเป็น 16)
        self.assertEqual(split_bill(15, 1, 10), [17])

    def test_no_float_drift(self):
        # 0.1 + 0.2 แบบ float จะพลาด; ต้องได้ผลจำนวนเต็มที่แน่นอน
        self.assertEqual(split_bill(1, 1, 100), [2])
        self.assertEqual(split_bill(999999999, 1, 0), [999999999])

    # boundary
    def test_tip_boundaries(self):
        self.assertEqual(split_bill(1000, 1, 0), [1000])
        self.assertEqual(split_bill(1000, 1, 100), [2000])

    def test_people_boundary(self):
        self.assertEqual(split_bill(500, 1, 0), [500])
        with self.assertRaises(ValueError):
            split_bill(500, 0, 0)

    def test_total_boundary(self):
        self.assertEqual(split_bill(0, 1, 0), [0])
        with self.assertRaises(ValueError):
            split_bill(-1, 1, 0)

    def test_tip_out_of_range(self):
        with self.assertRaises(ValueError):
            split_bill(100, 1, -1)
        with self.assertRaises(ValueError):
            split_bill(100, 1, 101)

    # validation
    def test_float_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 2, 10.5)

    def test_bool_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(True, 1, 0)
        with self.assertRaises(ValueError):
            split_bill(100, True, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 1, False)

    def test_str_and_none_rejected(self):
        with self.assertRaises(ValueError):
            split_bill('100', 1, 0)
        with self.assertRaises(ValueError):
            split_bill(100, None, 0)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'total': 10000, 'people': 3, 'tip_percent': 10})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out, {'ok': True, 'result': [3667, 3667, 3666]})

    def test_cli_error(self):
        proc = run_cli({'total': 100, 'people': 0, 'tip_percent': 0})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('people', out['error'])
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli({'total': 100, 'people': 2})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_float_rejected(self):
        proc = run_cli({'total': 100.0, 'people': 2, 'tip_percent': 0})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
