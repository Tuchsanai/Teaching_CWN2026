import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", True), 8000)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(10**7, "platinum", True), 20000)

    def test_half_up(self):
        # 10010*0.015=150.15 -> 150 ; 10050*.015=150.75 -> 151 ; 10100*.025=252.5 -> 253
        self.assertEqual(cashback(10100, "gold", False), 253)
        self.assertEqual(cashback(10050, "silver", False), 151)

    def test_reject(self):
        for a, t, b in [(-1, "gold", False), (1.0, "gold", False), ("1", "gold", False),
                        (True, "gold", False), (None, "gold", False), (100, "bronze", False),
                        (100, None, False), (100, [], False), (100, "gold", 1), (100, "gold", None),
                        (50, "bad", False)]:
            with self.assertRaises(ValueError):
                cashback(a, t, b)


if __name__ == "__main__":
    unittest.main()
