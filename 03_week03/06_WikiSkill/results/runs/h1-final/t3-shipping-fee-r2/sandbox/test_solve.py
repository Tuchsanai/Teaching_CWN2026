import json
import subprocess
import sys
import unittest

from solve import shipping_fee

# Expected values are worked out by hand (satang = baht * 100).


class TestShippingFee(unittest.TestCase):
    # --- weight tiers -------------------------------------------------
    def test_light_tier(self):
        self.assertEqual(shipping_fee(500, 50, False), 4000)  # 40 baht

    def test_light_tier_upper_boundary(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)  # 1000 g is still 40 baht

    def test_middle_tier_lower_boundary(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)  # 80 baht

    def test_middle_tier_upper_boundary(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)  # 5000 g is still 80 baht

    def test_heavy_tier_prorated_half_up(self):
        # 5001 g: 80 + 1 g * 1.5 satang = 8001.5 -> half up -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_heavy_tier_max_weight(self):
        # 30000 g: 80 baht + 25000 g * 1.5 satang = 8000 + 37500 = 45500
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    # --- distance surcharge -------------------------------------------
    def test_distance_exactly_100_no_surcharge(self):
        self.assertEqual(shipping_fee(5000, 100, False), 8000)

    def test_distance_over_100_adds_20_percent(self):
        self.assertEqual(shipping_fee(1000, 100.5, False), 4800)  # 4000 * 1.2

    def test_distance_zero_allowed(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    # --- express surcharge --------------------------------------------
    def test_express_adds_50_percent(self):
        self.assertEqual(shipping_fee(1000, 0, True), 6000)  # 4000 * 1.5

    def test_combined_example(self):
        # 6000 g: 8000 + 1000 * 1.5 = 9500; *1.2 = 11400; *1.5 = 17100
        self.assertEqual(shipping_fee(6000, 150, True), 17100)

    def test_surcharges_compound_with_single_final_rounding(self):
        # 5003 g: 8000 + 3 * 1.5 = 8004.5; *1.2 = 9605.4; *1.5 = 14408.1 -> 14408
        # Rounding after each step would give 8005 -> 9606 -> 14409, so this checks one final rounding.
        self.assertEqual(shipping_fee(5003, 101, True), 14408)

    def test_max_weight_with_long_distance_and_express(self):
        # 45500 * 1.2 = 54600; * 1.5 = 81900
        self.assertEqual(shipping_fee(30000, 100.01, True), 81900)

    # --- validation ---------------------------------------------------
    def test_weight_must_be_int(self):
        for bad in (1000.0, "1000", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(bad, 10, False)

    def test_weight_out_of_range(self):
        for bad in (0, -1, 30001):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(bad, 10, False)

    def test_distance_must_be_number(self):
        for bad in ("10", None, True, [10]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(1000, bad, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(1000, -0.5, False)

    def test_distance_non_finite_rejected(self):
        for bad in (float("nan"), float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(1000, bad, False)

    def test_express_must_be_bool(self):
        for bad in (1, 0, "yes", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(1000, 10, bad)

    # --- CLI ----------------------------------------------------------
    def _run_cli(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_success(self):
        proc = self._run_cli(json.dumps({"weight_g": 1000, "distance_km": 0, "express": False}))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"ok": True, "result": 4000})

    def test_cli_invalid_input(self):
        proc = self._run_cli(json.dumps({"weight_g": 0, "distance_km": 0, "express": False}))
        self.assertEqual(proc.returncode, 2)
        data = json.loads(proc.stdout)
        self.assertFalse(data["ok"])
        self.assertIn("error", data)
        self.assertNotIn("Traceback", proc.stderr)

    def test_cli_bad_json(self):
        proc = self._run_cli("{not json")
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
