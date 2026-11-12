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
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestSplitBill(unittest.TestCase):
    # ค่าปกติ
    def test_even_split_no_tip(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_with_tip(self):
        # 1000 + 5% = 1050 -> 525 + 525
        self.assertEqual(split_bill(1000, 2, 5), [525, 525])

    def test_single_person(self):
        self.assertEqual(split_bill(12345, 1, 0), [12345])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])

    # แจกเศษ: คนลำดับแรกจ่ายเพิ่มคนละ 1 สตางค์
    def test_remainder_goes_to_first_people(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_remainder_larger(self):
        # 10 สตางค์หาร 4 คน -> เศษ 2
        self.assertEqual(split_bill(10, 4, 0), [3, 3, 2, 2])

    def test_sum_equals_grand_total(self):
        result = split_bill(9999, 7, 13)
        grand = (9999 * 113 * 2 + 100) // 200
        self.assertEqual(sum(result), grand)
        self.assertEqual(len(result), 7)
        self.assertLessEqual(max(result) - min(result), 1)

    # ขอบของช่วง tip
    def test_tip_boundary_zero(self):
        self.assertEqual(split_bill(100, 1, 0), [100])

    def test_tip_boundary_hundred(self):
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_tip_boundary_hundred_split(self):
        self.assertEqual(split_bill(100, 2, 100), [100, 100])

    # ปัดครึ่งขึ้น (half-up) ไม่ใช่ปัดเข้าจำนวนคู่
    def test_half_up_exact_point_five(self):
        # 3 * 1.5 = 4.5 -> 5 (banker's rounding would give 4)
        self.assertEqual(split_bill(3, 1, 50), [5])

    def test_half_up_point_five_small(self):
        # 5 * 1.1 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_round_down_point_four(self):
        # 1 * 1.4 = 1.4 -> 1
        self.assertEqual(split_bill(1, 1, 40), [1])

    def test_round_up_point_six(self):
        # 3 * 1.2 = 3.6 -> 4
        self.assertEqual(split_bill(3, 1, 20), [4])

    def test_rounding_single_step_not_per_stage(self):
        # ปัดครั้งเดียวตอนท้าย: 1 * 1.5 = 1.5 -> 2 และไม่ปัดกลางทาง
        self.assertEqual(split_bill(1, 1, 50), [2])

    # ValueError: นอกช่วง / ชนิดผิด
    def test_total_negative_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 1, 0)

    def test_people_zero_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 0, 0)

    def test_people_negative_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, -2, 0)

    def test_tip_below_range_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 1, -1)

    def test_tip_above_range_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 1, 101)

    def test_float_total_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 1, 0)

    def test_float_people_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 0)

    def test_float_tip_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(100, 1, 5.0)

    def test_bool_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(True, 1, 0)
        with self.assertRaises(ValueError):
            split_bill(100, True, 0)
        with self.assertRaises(ValueError):
            split_bill(100, 1, False)

    def test_str_rejected(self):
        with self.assertRaises(ValueError):
            split_bill('100', 1, 0)

    def test_none_rejected(self):
        with self.assertRaises(ValueError):
            split_bill(None, 1, 0)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli({'total': 1000, 'people': 2, 'tip_percent': 5})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': [525, 525]})

    def test_cli_ok_remainder(self):
        proc = run_cli({'total': 10000, 'people': 3, 'tip_percent': 0})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': [3334, 3333, 3333]})

    def test_cli_error_out_of_range(self):
        proc = run_cli({'total': 100, 'people': 0, 'tip_percent': 0})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_error_float(self):
        proc = run_cli({'total': 100.0, 'people': 1, 'tip_percent': 0})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_error_missing_key(self):
        proc = run_cli({'total': 100, 'people': 1})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_error_bad_json(self):
        proc = run_cli('{not json')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
