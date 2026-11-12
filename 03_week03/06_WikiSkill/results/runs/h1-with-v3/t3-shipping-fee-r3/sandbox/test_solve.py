import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

SOLVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py")


def run_cli(text):
    return subprocess.run(
        [sys.executable, SOLVE_PATH],
        input=text,
        capture_output=True,
        text=True,
    )


class ShippingFeeTests(unittest.TestCase):
    def test_light_band_and_boundary(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_mid_band(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_heavy_band_is_proportional(self):
        self.assertEqual(shipping_fee(7000, 0, False), 11000)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_half_up_rounding_at_final_step(self):
        # 8000 + 3 * 1 / 2 = 8001.5 ปัดครึ่งขึ้นเป็น 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_distance_surcharge_strictly_above_100(self):
        self.assertEqual(shipping_fee(500, 0, False), 4000)
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express_and_combined_surcharges(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid_inputs_raise_value_error(self):
        bad_cases = [
            (0, 0, False),
            (30001, 0, False),
            (float(500), 0, False),
            (True, 0, False),
            (500, -1, False),
            (500, float(10), False),
            (500, 0, "yes"),
            (500, 0, 1),
        ]
        for weight, distance, express in bad_cases:
            with self.subTest(args=(weight, distance, express)):
                with self.assertRaises(ValueError):
                    shipping_fee(weight, distance, express)

    def test_cli_success(self):
        proc = run_cli(json.dumps({"weight_g": 500, "distance_km": 101, "express": True}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 7200})

    def test_cli_errors_exit_2_without_traceback(self):
        inputs = [
            "not json",
            json.dumps([1, 2, 3]),
            json.dumps({"weight_g": 500, "distance_km": 10}),
            json.dumps({"weight_g": 500, "distance_km": 10, "express": False, "extra": 1}),
            json.dumps({"weight_g": float(500), "distance_km": 10, "express": False}),
            json.dumps({"weight_g": 0, "distance_km": 10, "express": False}),
        ]
        for text in inputs:
            with self.subTest(text=text):
                proc = run_cli(text)
                self.assertEqual(proc.returncode, 2)
                self.assertFalse(json.loads(proc.stdout)["ok"])
                self.assertNotIn("Traceback", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
