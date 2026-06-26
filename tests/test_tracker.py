import unittest
from unittest.mock import MagicMock

from tracker import insert_rates


class InsertRatesTests(unittest.TestCase):
    def test_insert_rates_accepts_scraper_dict_output(self):
        cursor = MagicMock()
        db = MagicMock()

        insert_rates(cursor, db, 7, {
            "rates": [
                {"purity_text": "24K GOLD", "purity": 24, "rate": 123.45}
            ],
            "update_time": "10:00 AM"
        })

        cursor.executemany.assert_called_once()
        db.commit.assert_called_once()

        args, kwargs = cursor.executemany.call_args
        self.assertEqual(args[0], "\n        INSERT INTO metal_rate\n        (jeweller_id, purity_text, purity, rate)\n        VALUES (%s, %s, %s, %s)\n    ")
        self.assertEqual(args[1][0], (7, "24K GOLD", 24, 123.45))


if __name__ == "__main__":
    unittest.main()
