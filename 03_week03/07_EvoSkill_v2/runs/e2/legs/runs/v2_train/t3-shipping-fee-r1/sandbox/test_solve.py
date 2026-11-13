import unittest, subprocess, json
from solve import shipping_fee as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500,10,False),4000)
        self.assertEqual(f(3000,10,False),8000)
        self.assertEqual(f(10000,10,False),15500)
        self.assertEqual(f(10000,101,True),27900)
    def test_boundary(self):
        self.assertEqual(f(1000,100,False),4000)
        self.assertEqual(f(1001,100,False),8000)
        self.assertEqual(f(5000,100,False),8000)
        self.assertEqual(f(5001,100,False),8002)  # 8001.5 half-up
        self.assertEqual(f(1000,101,False),4800)
        self.assertEqual(f(30000,0,False),45500)
    def test_round(self):
        self.assertEqual(f(5001,0,False),8002)
        self.assertEqual(f(5003,0,False),8005)  # 8004.5
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(-1,1,False),(1.0,1,False),("3",1,False),(True,1,False),(None,1,False),
                  (1,-1,False),(1,1.0,False),(1,True,False),(1,float('nan'),False),(1,1,1),(1,1,None),(1,10**12,False) ][:-1]:
            with self.assertRaises(ValueError): f(*a)
        self.assertEqual(f(1,10**12,True),7200)
    def test_cli(self):
        r=subprocess.run(["python3","solve.py"],input='{"weight_g":500,"distance_km":0,"express":false}',capture_output=True,text=True)
        self.assertEqual(json.loads(r.stdout),{"ok":True,"result":4000})
        r=subprocess.run(["python3","solve.py"],input='{"weight_g":0,"distance_km":0,"express":false}',capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
unittest.main() if __name__=="__main__" else None
