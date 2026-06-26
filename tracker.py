from utils.db import get_connection
from config import TABLES
import importlib


def get_active_jewellers(cursor):
    query = f"""
        SELECT id, jeweller_name, url, template_type
        FROM {TABLES['jeweller_master']}
        WHERE is_active = 'Y'
    """
    cursor.execute(query)
    return cursor.fetchall()



def insert_rates(cursor, db, jeweller_id, items):
    query = f"""
        INSERT INTO {TABLES['metal_rate']}
        (jeweller_id, purity_text, purity, rate)
        VALUES (%s, %s, %s, %s)
    """

    values = [
        (jeweller_id, i["purity_text"], i["purity"], i["rate"])
        for i in items
    ]

    cursor.executemany(query, values)
    db.commit()



def process_jeweller(cursor, db, jeweller):
    jeweller_id, name, url, template_type = jeweller

    print(f"Processing: {name}")

    try:
        module_name = f"templates.template{template_type}"
        scraper = importlib.import_module(module_name)

        results = scraper.scrape(url)

        if not results:
            print(f"No data for {name}")
            return

        insert_rates(cursor, db, jeweller_id, results)

    except Exception as e:
        print(f"Error for {name}: {e}")


def main():
    db = get_connection()
    cursor = db.cursor()

    jewellers = get_active_jewellers(cursor)

    for jeweller in jewellers:
        process_jeweller(cursor, db, jeweller)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()