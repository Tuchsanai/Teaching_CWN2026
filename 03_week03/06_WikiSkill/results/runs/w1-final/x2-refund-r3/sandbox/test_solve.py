import json
import subprocess
import sys
import unittest

from solve import refund


def cli(obj):
    p = subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_boundary(self):
        self.assertEqual(refund(1000, 80, False), 200)
        self.assertEqual(refund(1000, 81, False), 0)
        self.assertEqual(refund(1000, 100, True), 0)

    def test_half_up(self):
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 1*50/100*0.875 = 0.4375 -> 0
        self.assertEqual(refund(1, 50, True), 0)
        # 10*50*7/800 = 4.375 -> 4 ; 12*50*7/800=5.25 ; 18*50*7/800=7.875 -> 8
        self.assertEqual(refund(18, 50, True), 8)
        # exactly .5: 4*50*... paid=40,used=60,restock: 40*40*7/800=14.0; paid=20,used=60: 20*40*7/800=7.0
        # paid=1,used=0,restock: 7/8=.875->1 ; paid=4,used=50? 4*50*7/800=1.75->2
        self.assertEqual(refund(4, 50, True), 2)
        # exact .5 with restock: paid*(100-u)*7 = 400 mod 800 -> paid=8,u=... 8*50*7=2800/800=3.5
        self.assertEqual(refund(8, 50, True), 4)

    def test_invalid(self):
        for args in [(-1, 10, False), (10, -1, False), (10, 101, False),
                     (10.0, 10, False), (10, 10.0, False), ('10', 10, False),
                     (None, 10, False), (True, 10, False), (10, True, False),
                     (10, 10, 1), (10, 10, None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)

    def test_cli(self):
        code, out = cli({'paid': 10000, 'used_percent': 50, 'restock': True})
        self.assertEqual((code, out), (0, {'ok': True, 'result': 4375}))
        code, out = cli({'paid': -5, 'used_percent': 50, 'restock': True})
        self.assertEqual(code, 2)
        self.assertFalse(out['ok'])
        code, out = cli({'paid': 5})
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
