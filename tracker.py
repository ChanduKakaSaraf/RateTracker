from utils.db import get_connection
from config import TABLES
import importlib


def get_active_jewellers(cursor):
    query = f"""
        SELECT id, jeweller_name, url, template_type, rate_updated
        FROM {TABLES['jeweller_master']}
        WHERE is_active = 'Y'
    """
    cursor.execute(query)
    return cursor.fetchall()



def insert_rates(cursor, db, jeweller_id, items, update_time):
    query = f"""
        INSERT INTO {TABLES['metal_rate']}
        (jeweller_id, purity_text, purity, rate)
        VALUES (%s, %s, %s, %s)
    """

    if isinstance(items, dict):
        items = items.get("rates", [])

    values = [
        (jeweller_id, i["purity_text"], i["purity"], i["rate"])
        for i in items or []
    ]

    

    # if values: then execute the insert query and update the rate_updated field in jeweller_master table for the jeweller. This ensures that the database is updated with the latest rates for the jeweller
    if values:
        cursor.executemany(query, values)
        update_query = f"""
            UPDATE {TABLES['jeweller_master']}
            SET rate_updated = %s
            WHERE id = %s
        """
        #print(update_query, (update_time, jeweller_id))
        cursor.execute(update_query, (update_time, jeweller_id))
        

    db.commit()



def process_jeweller(cursor, db, jeweller):
    jeweller_id, name, url, template_type, rate_updated = jeweller

    print(f"Processing: {name}")

    try:
        module_name = f"templates.template{template_type}"
        scraper = importlib.import_module(module_name)

        results = scraper.scrape(url, rate_updated)

        if isinstance(results, dict):
            items = results.get("rates", [])
        else:
            items = results

        # Save update_time from result into update_time variable restult = return {
        #    "rates": results,
        #    "update_time": update_time_node
        #}
        update_time = results.get("update_time")
        
        if not items:
            print(f"No data for {name}")
            return

        insert_rates(cursor, db, jeweller_id, items, update_time)

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