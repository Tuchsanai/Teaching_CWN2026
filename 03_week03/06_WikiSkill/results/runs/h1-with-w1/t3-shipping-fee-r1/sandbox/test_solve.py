import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

HERE = os.path.dirname(os.path.abspath(__file__))


def run_cli(payload):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, 'solve.py')],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


class TestShippingFee(unittest.TestCase):
    # ---- ค่าปกติ ----
    def test_basic_light(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)  # 40 บาท

    def test_basic_medium(self):
        self.assertEqual(shipping_fee(3000, 10, False), 8000)  # 80 บาท

    def test_over_5000_proportional(self):
        # 80 + 15 บาท/กก. ของส่วนเกิน 1 กก. = 95 บาท
        self.assertEqual(shipping_fee(6000, 10, False), 9500)

    def test_far_distance(self):
        self.assertEqual(shipping_fee(500, 150, False), 4800)  # 40 * 1.2

    def test_express(self):
        self.assertEqual(shipping_fee(500, 10, True), 6000)  # 40 * 1.5

    def test_far_and_express_compound(self):
        # 95 บาท * 1.2 * 1.5 = 171 บาท
        self.assertEqual(shipping_fee(6000, 150, True), 17100)

    # ---- ขอบเขตของแต่ละเงื่อนไข ----
    def test_weight_boundary_1000(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_weight_boundary_5000(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 สตางค์ ปัดขึ้น

    def test_weight_min_and_max(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        # 80 + 25 กก. * 15 = 455 บาท
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_boundary_100(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)  # ไม่เกิน 100 ไม่คิดเพิ่ม
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_distance_zero(self):
        self.assertEqual(shipping_fee(500, 0, False), 4000)

    # ---- ปัดครึ่งขึ้น (half-up) ----
    def test_half_up_exact_point_five(self):
        # 5001 g: 80 บาท + 1 g * 15/1000 บาท = 8000 + 1.5 สตางค์ -> 8002 (ปัดขึ้น)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_half_up_point_six(self):
        # 5001 g express: (8000 + 1.5) * 1.5 = 12002.25 -> 12002
        # 5003 g express: (8000 + 4.5) * 1.5 = 12006.75 -> 12007
        self.assertEqual(shipping_fee(5003, 0, True), 12007)

    def test_half_up_not_truncate(self):
        # (8000 + 1.5) * 1.2 = 9601.8 -> 9602 (ถ้าตัดทิ้งจะได้ 9601)
        self.assertEqual(shipping_fee(5001, 150, False), 9602)

    def test_no_float_drift(self):
        # ตรวจว่าคำนวณซ้ำแล้วได้ค่าเดิมเสมอ และเป็น int
        results = {shipping_fee(7777, 123, True) for _ in range(100)}
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results.pop(), int)

    # ---- validation ----
    def test_reject_weight_out_of_range(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(-5, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_reject_negative_distance(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, -1, False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            shipping_fee(500.0, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(500, 10.5, False)

    def test_reject_str_none(self):
        with self.assertRaises(ValueError):
            shipping_fee('500', 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(None, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(500, None, False)

    def test_reject_bool_as_number(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 10, False)
        with self.assertRaises(ValueError):
            shipping_fee(500, False, False)

    def test_reject_non_bool_express(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, 1)
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, 'yes')
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, None)

    # ---- CLI ----
    def test_cli_ok(self):
        proc = run_cli({'weight_g': 6000, 'distance_km': 150, 'express': True})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out, {'ok': True, 'result': 17100})

    def test_cli_error(self):
        proc = run_cli({'weight_g': 0, 'distance_km': 10, 'express': False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = run_cli({'weight_g': 500, 'distance_km': 10})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
