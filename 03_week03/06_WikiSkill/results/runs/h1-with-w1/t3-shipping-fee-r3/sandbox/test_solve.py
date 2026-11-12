import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

HERE = os.path.dirname(os.path.abspath(__file__))


class TestShippingFee(unittest.TestCase):
    # ค่าปกติ
    def test_basic_light(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_basic_mid(self):
        self.assertEqual(shipping_fee(3000, 50, False), 8000)

    def test_basic_heavy(self):
        # 80 บาท + (10000-5000)*15/1000 = 80 + 75 = 155 บาท
        self.assertEqual(shipping_fee(10000, 10, False), 15500)

    # ขอบน้ำหนัก
    def test_weight_boundary_1000(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_weight_boundary_1001(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_weight_boundary_5000(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_weight_max_30000(self):
        # 80 + 25000*15/1000 = 80 + 375 = 455 บาท
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_weight_min_1(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    # ขอบระยะทาง
    def test_distance_exactly_100_no_surcharge(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_distance_101_surcharge(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_distance_zero(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    # ส่งด่วน
    def test_express(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)

    def test_express_and_distance_compound(self):
        # 4000 * 1.2 * 1.5 = 7200
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    # half-up: 5003 g -> 8000 + 4.5 = 8004.5 -> 8005 (ไม่ใช่ banker's 8004)
    def test_half_up_point_five(self):
        self.assertEqual(shipping_fee(5003, 0, False), 8005)

    # 5001 g -> 8001.5 -> 8002 (half-up)
    def test_half_up_on_weight_step(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    # 5002 g -> 8003.0 ; express -> 12004.5 -> 12005 (half-up)
    def test_express_half_up(self):
        self.assertEqual(shipping_fee(5002, 0, True), 12005)

    def test_round_once_at_end(self):
        # 5001 g, dist 101, express: 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    # ValueError
    def test_weight_below_range(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)

    def test_weight_above_range(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_negative(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -1, False)

    def test_weight_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(100.0, 10, False)

    def test_distance_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10.0, False)

    def test_weight_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee('1000', 10, False)

    def test_weight_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(None, 10, False)

    def test_weight_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 10, False)

    def test_express_not_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, 1)

    def test_express_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 10, 'yes')


class TestCli(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, 'solve.py')],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        p = self._run(json.dumps({'weight_g': 1000, 'distance_km': 101, 'express': True}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {'ok': True, 'result': 7200})

    def test_cli_error(self):
        p = self._run(json.dumps({'weight_g': 0, 'distance_km': 10, 'express': False}))
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', p.stderr)

    def test_cli_missing_key(self):
        p = self._run(json.dumps({'weight_g': 1000, 'distance_km': 10}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
