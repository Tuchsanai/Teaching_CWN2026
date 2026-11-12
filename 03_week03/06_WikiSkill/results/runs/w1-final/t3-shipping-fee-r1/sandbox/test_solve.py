import json
import subprocess
import sys
import unittest

from solve import shipping_fee


def cli(obj):
    return subprocess.run([sys.executable, 'solve.py'], input=json.dumps(obj),
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_distance_express(self):
        self.assertEqual(shipping_fee(1000, 100, False), 4000)
        self.assertEqual(shipping_fee(1000, 101, False), 4800)
        self.assertEqual(shipping_fee(1000, 0, True), 6000)
        self.assertEqual(shipping_fee(1000, 101, True), 7200)

    def test_half_up(self):
        # 5001g: 8001.5 -> 8002 ; 5003g: 8004.5*... check .5 and .6
        self.assertEqual(shipping_fee(5001, 0, False), 8002)   # 8001.5
        self.assertEqual(shipping_fee(5002, 0, False), 8003)   # 8003.0
        self.assertEqual(shipping_fee(5001, 101, False), 9602) # 9601.8
        self.assertEqual(shipping_fee(5001, 0, True), 12002)   # 12002.25

    def test_invalid(self):
        for args in [(0, 0, False), (30001, 0, False), (10, -1, False),
                     (10.0, 0, False), (10, 1.5, False), (True, 0, False),
                     ('10', 0, False), (None, 0, False), (10, 0, 1), (10, 0, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)

    def test_cli(self):
        r = cli({'weight_g': 1000, 'distance_km': 101, 'express': True})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {'ok': True, 'result': 7200})
        for bad in [{'weight_g': 0, 'distance_km': 1, 'express': False},
                    {'weight_g': 5}]:
            r = cli(bad)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)['ok'])
        r = subprocess.run([sys.executable, 'solve.py'], input='nope',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == '__main__':
    unittest.main()
