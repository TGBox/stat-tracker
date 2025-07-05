import unittest

from modules.shopping_list_tracker import ShoppingListTracker

class TestShoppingListTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = ShoppingListTracker()

    def test_add_item(self):
        self.tracker.add_item("apples", 3)
        self.assertIn("apples", self.tracker.items)
        self.assertEqual(self.tracker.items["apples"], 3)

    def test_add_item_existing(self):
        self.tracker.add_item("bananas", 2)
        self.tracker.add_item("bananas", 4)
        self.assertEqual(self.tracker.items["bananas"], 6)

    def test_remove_item(self):
        self.tracker.add_item("milk", 1)
        self.tracker.remove_item("milk")
        self.assertNotIn("milk", self.tracker.items)

    def test_remove_item_not_exists(self):
        with self.assertRaises(KeyError):
            self.tracker.remove_item("bread")

    def test_update_quantity(self):
        self.tracker.add_item("eggs", 5)
        self.tracker.update_quantity("eggs", 10)
        self.assertEqual(self.tracker.items["eggs"], 10)

    def test_update_quantity_not_exists(self):
        with self.assertRaises(KeyError):
            self.tracker.update_quantity("cheese", 2)

    def test_get_items(self):
        self.tracker.add_item("rice", 1)
        self.tracker.add_item("beans", 2)
        items = self.tracker.get_items()
        self.assertEqual(items, {"rice": 1, "beans": 2})

    def test_clear_list(self):
        self.tracker.add_item("juice", 2)
        self.tracker.clear_list()
        self.assertEqual(self.tracker.items, {})

if __name__ == '__main__':
    unittest.main()