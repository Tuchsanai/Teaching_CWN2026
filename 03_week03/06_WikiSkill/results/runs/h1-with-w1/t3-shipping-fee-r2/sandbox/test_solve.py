import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

HERE = os.path.dirname(os.path.abspath(__file__))


class TestShippingFeeBasic(unittest.TestCase):
    def test_light_tier(self):
        self.assertEqual(shipping_fee(500, 0, False), 4000)

    def test_middle_tier(self):
        self.assertEqual(shipping_fee(3000, 0, False), 8000)

    def test_heavy_tier_proportional(self):
        # 6,000 g = 80 + 15 = 95 บาท
        self.assertEqual(shipping_fee(6000, 0, False), 9500)

    def test_heavy_tier_max_weight(self):
        # 30,000 g = 80 + 375 = 455 บาท
        self.assertEqual(shipping_fee(30000, 0, False), 45500)


class TestBoundaries(unittest.TestCase):
    def test_weight_1000_stays_light(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_weight_1001_is_middle(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_weight_5000_is_middle(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_weight_5001_is_heavy(self):
        # 8000 + 1.5 = 8001.5 -> half-up -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_weight_min_and_max(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_100_no_surcharge(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)

    def test_distance_101_surcharge(self):
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_distance_0(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)


class TestRounding(unittest.TestCase):
    def test_half_rounds_up_not_to_even(self):
        # 8000 + 4.5 = 8004.5 -> half-up = 8005 (banker's rounding would give 8004)
        self.assertEqual(shipping_fee(5003, 0, False), 8005)

    def test_point_five_express(self):
        # 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_point_six_rounds_up(self):
        # 8001.5 * 1.2 = 9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)

    def test_no_intermediate_rounding_drift(self):
        # ปัดครั้งเดียวตอนท้าย: 8001.5 * 1.2 * 1.5 = 14402.7 -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)


class TestExpressAndDistance(unittest.TestCase):
    def test_express_multiplier(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)

    def test_express_and_distance_compound(self):
        # 4000 * 1.2 * 1.5 = 7200
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_max_weight_far_express(self):
        # 45500 * 1.2 * 1.5 = 81900
        self.assertEqual(shipping_fee(30000, 101, True), 81900)


class TestValidation(unittest.TestCase):
    def test_weight_zero_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 0, False)

    def test_weight_too_large_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 0, False)

    def test_negative_distance_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -1, False)

    def test_float_weight_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000.0, 0, False)

    def test_float_distance_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 100.0, False)

    def test_string_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee('1000', 0, False)

    def test_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(None, 0, False)

    def test_bool_weight_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 0, False)

    def test_non_bool_express_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, 0, 'yes')
        with self.assertRaises(ValueError):
            shipping_fee(1000, 0, 1)


def _run_cli(payload):
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


class TestCli(unittest.TestCase):
    def test_cli_ok(self):
        proc = _run_cli({'weight_g': 1000, 'distance_km': 0, 'express': False})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {'ok': True, 'result': 4000})

    def test_cli_error(self):
        proc = _run_cli({'weight_g': 0, 'distance_km': 0, 'express': False})
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertFalse(out['ok'])
        self.assertIn('error', out)
        self.assertNotIn('Traceback', proc.stderr)

    def test_cli_missing_key(self):
        proc = _run_cli({'weight_g': 1000, 'distance_km': 0})
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])

    def test_cli_invalid_json(self):
        proc = _run_cli('not json')
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
