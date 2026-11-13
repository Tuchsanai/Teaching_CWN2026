import unittest, subprocess, sys
from solve import cashback as c

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(100000, "silver", False), 1500)
        self.assertEqual(c(100000, "gold", True), 5000)
        self.assertEqual(c(50000, "platinum", False), 2000)
    def test_boundary(self):
        self.assertEqual(c(9999, "gold", True), 0)
        self.assertEqual(c(10000, "gold", False), 250)
        self.assertEqual(c(500000, "platinum", False), 20000)
        self.assertEqual(c(1000000, "platinum", True), 20000)
    def test_round(self):
        self.assertEqual(c(10010, "silver", False), 150)   # 150.15
        self.assertEqual(c(10100, "silver", False), 152)   # 151.5 -> 152
    def test_reject(self):
        for a in [(-1,"gold",False),(1000.0,"gold",False),("3","gold",False),(True,"gold",False),
                  (None,"gold",False),(float("nan"),"gold",False),(5,"gold",False)[:0] or (10000,"x",False),
                  (10000,["a"],False),(10000,"gold",1),(10000,"gold",None),(-5,"gold",True)]:
            with self.assertRaises(ValueError): c(*a)
        self.assertEqual(c(10**12, "gold", True), 20000)
    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":100000,"tier":"silver","birthday":false}', capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), '{"ok": true, "result": 1500}')
        r = subprocess.run([sys.executable, "solve.py"], input='{"amount":-1,"tier":"silver","birthday":false}', capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
if __name__ == "__main__": unittest.main()
