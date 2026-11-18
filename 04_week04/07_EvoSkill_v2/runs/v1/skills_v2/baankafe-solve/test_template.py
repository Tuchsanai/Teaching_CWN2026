"""แม่แบบเทสต์: python3 -m unittest -q test_solve  (เปลี่ยนชื่อไฟล์เป็น test_solve.py และแก้ให้ตรงโจทย์)"""
import json
import subprocess
import sys
import unittest

from solve import example as fn  # เปลี่ยน example เป็นชื่อฟังก์ชันของโจทย์


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn([{'price': 4500, 'qty': 2}], False), 9630)


class Boundary(unittest.TestCase):
    def test_threshold_exact(self):
        self.assertEqual(fn([{'price': 50000, 'qty': 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(fn([{'price': 49999, 'qty': 1}], False), 53499)


class NoDrift(unittest.TestCase):
    def test_fraction(self):
        self.assertEqual(fn([{'price': 4505, 'qty': 1}], True), 4338)


class Reject(unittest.TestCase):
    def test_reject(self):
        for bad in ([{'price': 4500, 'qty': 0}], [{'price': 4500.0, 'qty': 1}],
                    [{'price': 4500, 'qty': '2'}], [{'price': True, 'qty': 1}], [{'qty': 1}]):
            with self.assertRaises(ValueError):
                fn(bad, False)
        with self.assertRaises(ValueError):
            fn([], 1)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                              capture_output=True, text=True)

    def test_ok(self):
        r = self.run_cli({"items": [{"price": 4500, "qty": 2}], "member": False})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 9630})

    def test_error(self):
        r = self.run_cli({"items": [{"price": 4500, "qty": 0}], "member": False})
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
