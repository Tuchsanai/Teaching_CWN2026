import unittest, subprocess, json
from solve import shipping_fee as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(1000,0,False),4000)
        self.assertEqual(f(1001,0,False),8000)
        self.assertEqual(f(5000,100,False),8000)
        self.assertEqual(f(5000,101,False),9600)
        self.assertEqual(f(10000,0,False),15500)
        self.assertEqual(f(10000,101,True),27900)
        self.assertEqual(f(500,0,True),6000)
    def test_round(self):
        self.assertEqual(f(5001,0,False),8002)  # 8001.5 -> 8002
        self.assertEqual(f(30000,0,False),45500)
    def test_reject(self):
        for a in [(0,0,False),(30001,0,False),(1,-1,False),(1.0,0,False),("3",0,False),(True,0,False),(1,0.0,False),(1,True,False),(1,0,1),(None,0,False),(float('nan'),0,False),(1,0,None)]:
            with self.assertRaises(ValueError): f(*a)
    def test_big(self):
        self.assertEqual(f(1,10**12,False),4800)
    def test_cli(self):
        r=subprocess.run(["python3","solve.py"],input='{"weight_g":500,"distance_km":0,"express":false}',capture_output=True,text=True)
        self.assertEqual(json.loads(r.stdout),{"ok":True,"result":4000})
        r=subprocess.run(["python3","solve.py"],input='{"weight_g":0,"distance_km":0,"express":false}',capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
