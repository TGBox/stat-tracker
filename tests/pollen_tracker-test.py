import unittest

from modules.pollen_tracker import (
    get_pollen_count,
    is_pollen_high,
    get_pollen_forecast,
    PollenLevel,
)

class TestPollenTracker(unittest.TestCase):
    def test_get_pollen_count_valid_location(self):
        count = get_pollen_count("New York")
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_get_pollen_count_invalid_location(self):
        with self.assertRaises(ValueError):
            get_pollen_count("Atlantis")

    def test_is_pollen_high_true(self):
        self.assertTrue(is_pollen_high(150))

    def test_is_pollen_high_false(self):
        self.assertFalse(is_pollen_high(20))

    def test_get_pollen_forecast(self):
        forecast = get_pollen_forecast("Los Angeles")
        self.assertIsInstance(forecast, list)
        self.assertTrue(all(isinstance(day, dict) for day in forecast))
        self.assertTrue(all("date" in day and "level" in day for day in forecast))
        self.assertTrue(all(isinstance(day["level"], PollenLevel) for day in forecast))

    def test_get_pollen_forecast_invalid_location(self):
        with self.assertRaises(ValueError):
            get_pollen_forecast("Unknown City")

if __name__ == "__main__":
    unittest.main()