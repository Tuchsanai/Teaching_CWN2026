import json
import os
import subprocess
import sys
import unittest

from solve import split_bill

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload_text):
    return subprocess.run(
        [sys.executable, 'solve.py'],
        input=payload_text,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


class TestSplitBill(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])
        self.assertEqual(split_bill(1000, 1, 0), [1000])
        self.assertEqual(split_bill(1005, 2, 0), [503, 502])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_exact_division_no_remainder(self):
        self.assertEqual(split_bill(900, 3, 0), [300, 300, 300])

    def test_tip_100_percent_doubles(self):
        self.assertEqual(split_bill(500, 2, 100), [500, 500])

    def test_half_up_exact_point_five(self):
        # 15 * 1.10 = 16.5 -> 17 (ปัดขึ้น ไม่ปัดลง)
        self.assertEqual(split_bill(15, 1, 10), [17])

    def test_half_up_point_six(self):
        # 26 * 1.10 = 28.6 -> 29
        self.assertEqual(split_bill(26, 1, 10), [29])

    def test_round_down_below_half(self):
        # 24 * 1.10 = 26.4 -> 26
        self.assertEqual(split_bill(24, 1, 10), [26])

    def test_no_drift_remainder_to_first_people(self):
        # 1000 * 1.15 = 1150 หาร 7 = 164 เศษ 2 -> สองคนแรกได้ 165
        result = split_bill(1000, 7, 15)
        self.assertEqual(result, [165, 165, 164, 164, 164, 164, 164])
        self.assertEqual(sum(result), 1150)

    def test_boundaries(self):
        self.assertEqual(split_bill(0, 1, 0), [0])        # ต่ำสุดทุกค่า
        self.assertEqual(split_bill(0, 1, 100), [0])
        self.assertEqual(split_bill(1, 1, 100), [2])      # 1 * 2 = 2
        self.assertEqual(len(split_bill(10, 30000, 0)), 30000)  # ไม่ใช่ขอบจริง แค่ยืนยันว่าทำงาน

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            split_bill(-1, 2, 10)      # total ติดลบ
        with self.assertRaises(ValueError):
            split_bill(100, 0, 10)     # people ต่ำกว่า 1
        with self.assertRaises(ValueError):
            split_bill(100, -2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, -1)     # tip ต่ำกว่า 0
        with self.assertRaises(ValueError):
            split_bill(100, 2, 101)    # tip เกิน 100

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            split_bill(100.0, 2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2.0, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, 10.0)

    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            split_bill(True, 2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, True, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, False)

    def test_reject_wrong_type(self):
        with self.assertRaises(ValueError):
            split_bill('100', 2, 10)
        with self.assertRaises(ValueError):
            split_bill(100, None, 10)
        with self.assertRaises(ValueError):
            split_bill(100, 2, None)


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = run_cli(json.dumps({'total': 1000, 'people': 3, 'tip_percent': 10}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout),
                         {'ok': True, 'result': [367, 367, 366]})

    def test_cli_error_out_of_range(self):
        proc = run_cli(json.dumps({'total': 1000, 'people': 0, 'tip_percent': 10}))
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_error_missing_key(self):
        proc = run_cli(json.dumps({'total': 1000, 'people': 3}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_error_bad_json(self):
        proc = run_cli('not json')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
