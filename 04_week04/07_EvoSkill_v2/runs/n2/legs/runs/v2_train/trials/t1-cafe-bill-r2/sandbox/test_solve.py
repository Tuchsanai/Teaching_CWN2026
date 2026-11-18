"""แม่แบบ test_solve.py — แทนชื่อฟังก์ชัน/ค่าตามโจทย์ ค่าคาดหวังต้องคำนวณมือด้วย Fraction แล้วใส่เป็นเลขตายตัว
รัน: python3 -m unittest -q test_solve"""
import json
import subprocess
import sys
import unittest

from solve import cafe_bill  # <- เปลี่ยนชื่อ


class Normal(unittest.TestCase):          # >= 3 เคสทั่วไป ทุกสาขาของสูตร
    def test_normal_1(self):
        self.assertEqual(cafe_bill([{'price': 4500, 'qty': 2}], False), 9630)

    def test_normal_2(self):
        self.assertEqual(cafe_bill([{'price': 4500, 'qty': 2}], True), 8667)

    def test_normal_3(self):
        self.assertEqual(cafe_bill([{'price': 12000, 'qty': 1}, {'price': 6500, 'qty': 2}], False), 26750)


class Boundary(unittest.TestCase):        # >= 3 เคส: ทุกเกณฑ์ ด้านเท่ากับและด้านต่ำกว่า 1 หน่วย, ค่า 0, ค่าต่ำสุด
    def test_boundary_1(self):
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_boundary_2(self):
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)

    def test_boundary_3(self):
        self.assertEqual(cafe_bill([{'price': 0, 'qty': 1}, {'price': 4500, 'qty': 1}], False), 4815)


class NoDrift(unittest.TestCase):         # >= 2 เคสที่ผลต่างระหว่างปัดครึ่งขึ้น/ปัดทิ้ง/float/ปัดกลางทาง
    def test_no_drift_1(self):
        self.assertEqual(cafe_bill([{'price': 4505, 'qty': 1}], True), 4338)

    def test_no_drift_2(self):
        self.assertEqual(cafe_bill([{'price': 25075, 'qty': 2}], True), 45880)


class Reject(unittest.TestCase):          # >= 4 เคส: ลบ/0 นอกช่วง, float, str, bool, enum ผิด, โครงสร้างผิด
    def test_reject_qty_zero(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': 0}], False)

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': -1}], False)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500.0, 'qty': 1}], False)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': '2'}], False)

    def test_reject_bool_as_int(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': True}], False)

    def test_reject_flag_not_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': 1}], 1)


class Cli(unittest.TestCase):             # ทดสอบ main() ผ่าน stdin
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        code, out = self.run_cli({"items": [{"price": 4500, "qty": 2}], "member": False})
        self.assertEqual((code, out), (0, {"ok": True, "result": 9630}))

    def test_cli_error(self):
        code, out = self.run_cli({"items": [{"price": 4500, "qty": 0}], "member": False})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
