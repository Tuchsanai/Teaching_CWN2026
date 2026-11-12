import json
import subprocess
import sys
import unittest

from solve import late_fee


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_no_fee(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_after_threshold(self):
        self.assertEqual(late_fee(100000, 4), 3000)   # 4*0.75% = 3%
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_half_up(self):
        # 200*0.0075*4 = 6.0 ; 50*0.0075*5 = 1.875 -> 2 ; 10*0.0075*10=0.75 ->1
        self.assertEqual(late_fee(50, 5), 2)
        self.assertEqual(late_fee(10, 10), 1)
        # 2*0.0075*4=0.06 ->0 ; 100*0.0075*... exact .5: 200*.0075*... 
        # amount=2000,days=... 15*d=... use 1 *0.0075*... : 200*0.0075*... skip
        # 20000*0.0075*... n/a; exact .5: amount=100,days=... 0.75*d=x.5 -> d=10 gives 7.5 -> 8
        self.assertEqual(late_fee(100, 10), 8)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(0, 100), 0)

    def test_invalid(self):
        for a, d in [(1.0, 5), (True, 5), ("1", 5), (None, 5), (-1, 5),
                     (100, 5.0), (100, True), (100, "5"), (100, None),
                     (100, -1), (100, 366)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        r = run(json.dumps({"amount": 100000, "days_late": 4}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})
        r = run(json.dumps({"amount": 1.5, "days_late": 4}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
