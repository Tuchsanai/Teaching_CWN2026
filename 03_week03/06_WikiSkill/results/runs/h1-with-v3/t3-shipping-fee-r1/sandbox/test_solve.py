import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVE = os.path.join(HERE, "solve.py")


def run_cli(text):
    return subprocess.run(
        [sys.executable, SOLVE],
        input=text,
        capture_output=True,
        text=True,
    )


class TestShippingFee(unittest.TestCase):
    def test_small_weight_boundary(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_mid_weight(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_heavy_excess_rounds_half_up(self):
        # 5001 g -> 8001.5 สตางค์ -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)
        # 5003 g -> 8004.5 สตางค์ -> 8005
        self.assertEqual(shipping_fee(5003, 0, False), 8005)

    def test_max_weight(self):
        self.assertEqual(shipping_fee(30000, 0, False), 45500)
        self.assertEqual(shipping_fee(30000, 0, True), 68250)

    def test_distance_surcharge_boundary(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    def test_express_surcharge(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 0, True), 6000)

    def test_express_and_distance_compound(self):
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_out_of_range_weight(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 0, False)
        with self.assertRaises(ValueError):
            shipping_fee(30001, 0, False)

    def test_invalid_types_and_values(self):
        cases = [
            (500.0, 0, False),
            ("500", 0, False),
            (True, 0, False),
            (None, 0, False),
            (500, -1, False),
            (500, 1.0, False),
            (500, 0, 1),
            (500, 0, "yes"),
        ]
        for weight, distance, express in cases:
            with self.subTest(weight=weight, distance=distance, express=express):
                with self.assertRaises(ValueError):
                    shipping_fee(weight, distance, express)


class TestCli(unittest.TestCase):
    def test_success(self):
        proc = run_cli(json.dumps({"weight_g": 500, "distance_km": 0, "express": False}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 4000})

    def test_invalid_json(self):
        proc = run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_missing_key(self):
        proc = run_cli(json.dumps({"weight_g": 500, "distance_km": 0}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)

    def test_bad_value_from_cli(self):
        proc = run_cli(json.dumps({"weight_g": 500.0, "distance_km": 0, "express": False}))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
