import json
import subprocess
import sys
import unittest
from fractions import Fraction

from solve import shipping_fee


# ค่าที่คาดไว้คำนวณด้วยมือ (สตางค์) ไม่ได้คัดลอกมาจากฟังก์ชัน
class TestShippingFee(unittest.TestCase):

    # --- เคสปกติ ---
    def test_light_short_standard(self):
        # 500 g, 10 km, ธรรมดา -> 40 บาท
        self.assertEqual(shipping_fee(500, 10, False), 4000)

    def test_mid_weight_standard(self):
        # 3,000 g -> 80 บาท
        self.assertEqual(shipping_fee(3000, 10, False), 8000)

    def test_express_only(self):
        # 500 g, 10 km, ด่วน -> 40 * 1.5 = 60 บาท
        self.assertEqual(shipping_fee(500, 10, True), 6000)

    # --- ขอบเขตน้ำหนัก ---
    def test_weight_boundary_1000(self):
        # 1000 g ยังอยู่ในขั้น 40 บาท
        self.assertEqual(shipping_fee(1000, 0, False), 4000)

    def test_weight_boundary_1001(self):
        # 1001 g เข้าขั้น 80 บาท
        self.assertEqual(shipping_fee(1001, 0, False), 8000)

    def test_weight_boundary_5000(self):
        # 5000 g ยัง 80 บาท (ไม่มีส่วนเกิน)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)

    def test_weight_boundary_5001_half_satang_rounds_up(self):
        # ส่วนเกิน 1 g = 1.5 สตางค์ -> 8001.5 -> ปัดขึ้น 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)

    def test_weight_max_30000(self):
        # ส่วนเกิน 25,000 g * 1.5 = 37,500 สตางค์ + 8,000 = 45,500 สตางค์
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_weight_6000_proportional(self):
        # 6000 g -> 8000 + 1.5*1000 = 9500 สตางค์
        self.assertEqual(shipping_fee(6000, 0, False), 9500)

    # --- ขอบเขตระยะทาง ---
    def test_distance_exactly_100_no_surcharge(self):
        # 100 กม. ไม่เกิน 100 จึงไม่คิดเพิ่ม
        self.assertEqual(shipping_fee(500, 100, False), 4000)

    def test_distance_101_surcharge(self):
        # 101 กม. -> 40 * 1.2 = 48 บาท
        self.assertEqual(shipping_fee(500, 101, False), 4800)

    # --- ปัดครั้งเดียว และคูณหลายขั้น ---
    def test_multi_step_single_rounding(self):
        # 5001 g: 8001.5; *1.2 = 9601.8; *1.5 = 14402.7 -> ปัดครั้งเดียว 14403
        # (ถ้าปัดระหว่างทางจะได้ค่าต่างกัน)
        self.assertEqual(shipping_fee(5001, 150, True), 14403)

    def test_half_up_exact_point_five(self):
        # 5001 g ธรรมดา ระยะ 0: 8001.5 -> 8002 (ปัดขึ้นเมื่อพอดี .5)
        self.assertEqual(shipping_fee(5001, 100, False), 8002)

    def test_express_and_long_distance(self):
        # 6000 g, 150 กม., ด่วน: 9500 * 1.2 * 1.5 = 17100
        self.assertEqual(shipping_fee(6000, 150, True), 17100)

    def test_fraction_kept_until_end(self):
        # 5001 g, 0 กม., ด่วน: 8001.5 * 1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)

    # --- Validation: ValueError เท่านั้น ---
    def test_weight_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500.0, 10, False)

    def test_weight_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(True, 10, False)

    def test_weight_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(None, 10, False)

    def test_weight_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee("500", 10, False)

    def test_weight_zero_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(0, 10, False)

    def test_weight_too_large_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(30001, 10, False)

    def test_distance_float_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10.0, False)

    def test_distance_bool_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, False, False)

    def test_distance_negative_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, -1, False)

    def test_distance_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, None, False)

    def test_express_int_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, 1)

    def test_express_str_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, "true")

    def test_express_none_rejected(self):
        with self.assertRaises(ValueError):
            shipping_fee(500, 10, None)


class TestCli(unittest.TestCase):

    def _run(self, payload):
        return subprocess.run(
            [sys.executable, "solve.py"],
            input=payload,
            capture_output=True,
            text=True,
        )

    def test_cli_ok(self):
        p = self._run(json.dumps({"weight_g": 500, "distance_km": 10, "express": False}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": 4000})

    def test_cli_invalid_input_exit_2(self):
        p = self._run(json.dumps({"weight_g": 500.0, "distance_km": 10, "express": False}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)

    def test_cli_bad_json_exit_2(self):
        p = self._run("{not json")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])

    def test_cli_missing_key_exit_2(self):
        p = self._run(json.dumps({"weight_g": 500, "distance_km": 10}))
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
