import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_below_min(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)

    def test_at_min(self):
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_rates(self):
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)

    def test_birthday_double(self):
        self.assertEqual(cashback(100000, "silver", True), 3000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)

    def test_half_up_once(self):
        # 10033*150/10000 = 150.495 -> 150 ; 10034 -> 150.51 -> 151
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        # birthday: 10017*300/10000=300.51 -> 301 (ไม่ปัดก่อนคูณ)
        self.assertEqual(cashback(10017, "silver", True), 301)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), (True, "gold", False),
                     ("100", "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
