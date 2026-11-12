import json
import subprocess
import sys
import unittest

from solve import shipping_fee


class ShippingFeeTests(unittest.TestCase):
    # ค่าคาดคำนวณด้วยมือ (หน่วยสตางค์)

    def test_light_tier(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)  # 40 บาท

    def test_tier_boundary_1000_is_40(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_just_over_1000_is_80(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_tier_boundary_5000_is_80(self):
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_heavy_proportional_half_up(self):
        # 80 + 1/1000*15 = 80.015 บาท = 8001.5 สตางค์ -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_max_weight(self):
        # 80 + 25000/1000*15 = 455 บาท
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_exactly_100_no_surcharge(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)

    def test_distance_over_100_plus_20_percent(self):
        self.assertEqual(shipping_fee(500, 100.5, False), 4800)  # 48 บาท

    def test_distance_float_exact_not_affected_by_binary_error(self):
        self.assertEqual(shipping_fee(500, 100.0000001, False), 4800)

    def test_express_plus_50_percent(self):
        self.assertEqual(shipping_fee(500, 0, True), 6000)  # 60 บาท

    def test_express_and_distance_multiply(self):
        # 40 * 1.2 * 1.5 = 72 บาท
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_single_final_rounding_heavy_express_distance(self):
        # 80.015 * 1.2 * 1.5 = 144.027 บาท = 14402.7 สตางค์ -> 14403
        self.assertEqual(shipping_fee(5001, 101, True), 14403)

    def test_single_final_rounding_heavy_express(self):
        # 80.015 * 1.5 = 120.0225 บาท = 12002.25 สตางค์ -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    def test_zero_distance_ok(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)

    def test_rejects_bad_weight(self):
        for bad in (0, 30001, -5, 1.5, 4500.0, True, "500", None):
            with self.subTest(weight_g=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(bad, 10, False)

    def test_rejects_bad_distance(self):
        for bad in (-0.1, -1, True, "10", None, float("nan"), float("inf")):
            with self.subTest(distance_km=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(500, bad, False)

    def test_rejects_bad_express(self):
        for bad in (1, 0, None, "true", 1.0):
            with self.subTest(express=bad):
                with self.assertRaises(ValueError):
                    shipping_fee(500, 10, bad)


class CliTests(unittest.TestCase):
    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        p = self._run({"weight_g": 500, "distance_km": 101, "express": True})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 7200})

    def test_cli_error(self):
        p = self._run({"weight_g": 0, "distance_km": 10, "express": False})
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
