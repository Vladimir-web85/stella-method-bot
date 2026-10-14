import unittest
from app.numerology import life_path_number, interpretation

class NumerologyTests(unittest.TestCase):
    def test_valid_date_returns_number(self):
        result = life_path_number("24.08.1995")
        self.assertIn(result, set(range(1, 10)) | {11, 22, 33})

    def test_invalid_date_raises(self):
        with self.assertRaises(ValueError):
            life_path_number("31.02.2000")

    def test_future_date_raises(self):
        with self.assertRaises(ValueError):
            life_path_number("01.01.2999")

    def test_master_number_has_interpretation(self):
        self.assertTrue(interpretation(11))

if __name__ == "__main__":
    unittest.main()
