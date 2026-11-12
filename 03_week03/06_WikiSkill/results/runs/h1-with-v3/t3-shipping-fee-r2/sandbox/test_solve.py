import json
import os
import subprocess
import sys
import unittest

from solve import shipping_fee

HERE = os.path.dirname(os.path.abspath(__file__))


class TestShippingFee(unittest.TestCase):
    def test_base_bands(self):
        self.assertEqual(shipping_fee(1, 50, False), 4000)
        self.assertEqual(shipping_fee(1000, 50, False), 4000)
        self.assertEqual(shipping_fee(1001, 50, False), 8000)
        self.assertEqual(shipping_fee(5000, 50, False), 8000)

    def test_extra_weight_and_max(self):
        self.assertEqual(shipping_fee(6000, 50, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_half_up_rounding(self):
        # 8001.5 บาทสตางค์ -> ปัดขึ้นเป็น 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_distance_surcharge(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)

    def test_express_and_combined(self):
        self.assertEqual(shipping_fee(1000, 50, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_invalid_inputs(self):
        bad_weights = [0, 30001, True, float("1000.0"), "1000", None]
        for w in bad_weights:
            with self.subTest(weight_g=w), self.assertRaises(ValueError):
                shipping_fee(w, 10, False)
        bad_distances = [-1, True, float("5.0"), "10"]
        for d in bad_distances:
            with self.subTest(distance_km=d), self.assertRaises(ValueError):
                shipping_fee(1000, d, False)
        bad_express = [1, 0, "yes", None]
        for e in bad_express:
            with self.subTest(express=e), self.assertRaises(ValueError):
                shipping_fee(1000, 10, e)

    def _run_cli(self, stdin_text):
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "solve.py")],
            input=stdin_text, capture_output=True, text=True,
        )
        return proc.returncode, json.loads(proc.stdout), proc.stderr

    def test_cli_success(self):
        code, out, err = self._run_cli(
            '{"weight_g": 6000, "distance_km": 50, "express": false}')
        self.assertEqual(code, 0)
        self.assertEqual(out, {"ok": True, "result": 9500})
        self.assertEqual(err, "")

    def test_cli_errors(self):
        cases = [
            "not json",
            "[1, 2]",
            '{"weight_g": 1000, "distance_km": 5}',
            '{"weight_g": 0, "distance_km": 5, "express": false}',
        ]
        for text in cases:
            with self.subTest(stdin=text):
                code, out, err = self._run_cli(text)
                self.assertEqual(code, 2)
                self.assertFalse(out["ok"])
                self.assertIn("error", out)
                self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
