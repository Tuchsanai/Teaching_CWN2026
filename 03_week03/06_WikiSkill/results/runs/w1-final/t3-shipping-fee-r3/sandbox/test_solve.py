import json
import subprocess
import sys
import unittest

from solve import shipping_fee


def run(payload):
    p = subprocess.run([sys.executable, 'solve.py'], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_distance_express(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_half_up(self):
        # 5001 g: 8000+1.5=8001.5 -> 8002
        self.assertEqual(shipping_fee(5001, 0, False), 8002)
        # 5001, express: 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        # 5003 g: 8004.5 -> 8005 ; far: 9605.4 -> 9605
        self.assertEqual(shipping_fee(5003, 0, False), 8005)
        self.assertEqual(shipping_fee(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(shipping_fee(5002, 0, False), 8003)

    def test_errors(self):
        for a in [(0, 0, False), (30001, 0, False), (100, -1, False),
                  (100.0, 0, False), (100, 1.0, False), (True, 0, False),
                  (100, 0, 1), ('100', 0, False), (None, 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_cli(self):
        code, out = run(json.dumps({'weight_g': 500, 'distance_km': 0, 'express': False}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'ok': True, 'result': 4000})
        code, out = run(json.dumps({'weight_g': 0, 'distance_km': 0, 'express': False}))
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)['ok'])
        code, out = run('{}')
        self.assertEqual(code, 2)
        code, out = run('not json')
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
