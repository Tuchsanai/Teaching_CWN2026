import unittest
from solve import cafe_bill as f

def it(p, q=1): return {"price": p, "qty": q}

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([it(10000, 2)], False), 21400)
        self.assertEqual(f([it(60000)], False), 60000*95*107//10000)  # 60990 exact
        self.assertEqual(f([it(60000)], True), 54891)
        self.assertEqual(f([], False), 0)
    def test_boundary(self):
        self.assertEqual(f([it(49999)], False), 53499)   # 53498.93
        self.assertEqual(f([it(50000)], False), 50825)   # 50825.0
    def test_halfup(self):
        # 5 * 1.07 = 5.35 -> 5 ; 50 *1.07=53.5 -> 54
        self.assertEqual(f([it(50)], False), 54)
    def test_reject(self):
        for bad in [[it(-1)], [it(100, 0)], [it(100.0)], [it("1")], [it(True)],
                    [{"price": 1}], ["x"], None, [it(1, 1.0)]]:
            with self.assertRaises(ValueError): f(bad, False)
        for m in [1, None, "True"]:
            with self.assertRaises(ValueError): f([it(100)], m)
unittest.main() if __name__ == "__main__" else None
