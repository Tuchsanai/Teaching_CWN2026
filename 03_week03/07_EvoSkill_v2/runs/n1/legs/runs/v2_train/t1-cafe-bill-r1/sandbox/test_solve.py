import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_boundary(self):
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50000*.95*1.07
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50001*.95*1.07=50826.0..

    def test_half_up(self):
        # 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [None, {}, [1], [{"price": 1}], [it(1, 0)], [it(-1)], [it(1.0)],
               [it(1, 1.0)], [it("1")], [it(True)], [it(1, True)], [it(None)]]
        for b in bad:
            with self.assertRaises(ValueError):
                cafe_bill(b, False)
        for m in (1, 0, None, "yes"):
            with self.assertRaises(ValueError):
                cafe_bill([it(1)], m)


if __name__ == "__main__":
    unittest.main()
