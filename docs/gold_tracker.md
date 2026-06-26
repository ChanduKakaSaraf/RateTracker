Overview
This system is designed to:

- Track gold and metal rates from multiple jeweller websites
- Detect changes in rates based on website update timestamp
- Store data in MySQL database
- Avoid duplicate entries using update-time comparison
- Support multiple website structures using template-based scraping


🧱 Architecture
/var/www/rate-tracker/
│
├── tracker.py          # Main execution script
├── config.py           # DB and table configuration
├── templates/
│     ├── template1.py  # Scraper for specific site structure
│
├── utils/
│     └── db.py         # DB connection
│
└── docs/
      └── gold_tracker.md


🗄️ Database Structure
✅ 1. jeweller_master
CREATE TABLE jeweller_master (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jeweller_name VARCHAR(100),
    url VARCHAR(500),
    template_type INT,
    rate_updated VARCHAR(500),
    is_active CHAR DEFAULT 'Y'
);


✅ 2. metal_rate
CREATE TABLE metal_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jeweller_id INT,
    purity_text VARCHAR(50),
    purity VARCHAR(15),
    rate DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



🔄 Workflow
✅ Step-by-step flow

Fetch active jewellers:

SELECT * FROM jeweller_master WHERE is_active='Y'

1. For each jeweller:
    - Identify template_type
    - Load corresponding template


2. Scrape:
    - Extract update-time
    - Extract all rates (multiple metals)


3. Compare:
    - If scraped update_time matches the stored rate_updated value, the scraper returns no new rates and the tracker skips insertion.
    - Otherwise, the tracker inserts the new rows into metal_rate.

4. Store data:
    - Insert into metal_rate
    - Commit the batch to the database

🧠 Template System
Each template handles a different website structure.
✅ template1.py responsibilities:

Fetch HTML
Parse using XPath
Extract:

purity_text
rate
update_time


Normalize data
Return structured response


📥 Template Return Format
The scraper returns a dictionary containing the extracted rates and update time:

{
    "rates": [
        {
            "purity": 24,
            "purity_text": "24K Gold",
            "rate": 13986
        },
        ...
    ],
    "update_time": "25 Jun 2026 10:30 AM"
}

The tracker normalizes this structure by reading the rates list from the response and inserting only those row objects.

🔍 Data Extraction Logic
✅ XPath used
nodes = tree.xpath("/html/body/div[1]/div[1]/div/div[3]/div/a[3]/div/div[2]/ul/li")


✅ Extract purity_text
purity_text = re.sub(r"₹.*", "", full_text).strip()


✅ Extract rate
clean_rate = re.sub(r"[^\d.]", "", raw_rate)
rate = float(clean_rate)



🧪 Purity Normalization
if "24K GOLD" → 24
if "22K GOLD" → 22
if "18K GOLD" → 18
if "14K GOLD" → 14
if "PLATINUM" → "Platinum"
if "SILVER" → "Silver"
else → original text

🕒 Update-Time Logic (Important)
The scraper reads the webpage timestamp from:
//*[@id="update-time"]

If the passed-in rate_updated value already matches the latest update time, the scraper returns an empty rates list so the tracker skips a duplicate insert.

🧾 Insert Logic
The tracker accepts either a raw list of rate items or a scraper response dictionary and extracts the rates before inserting them into metal_rate.

INSERT INTO metal_rate
(jeweller_id, purity_text, purity, rate)


🔄 Update Logic
UPDATE jeweller_master
SET rate_updated = ?
WHERE id = ?


✅ Benefits of This Design
✅ Avoids duplicate entries
✅ Reduces DB load
✅ Faster execution
✅ Easily scalable to multiple websites
✅ Template-based handling
✅ Clean separation of logic

⚠️ Important Considerations
1. XPath Fragility
Absolute XPath may break if website layout changes.
👉 Future improvement:

Use relative XPath
Use class selectors


2. Update-Time Dependency
If website fails to update timestamp:

System may miss actual changes

👉 Future fallback:

Compare rate snapshot


3. Error Handling
Currently uses:
print()

👉 Should be replaced with logging system later

🧱 Future Enhancements
✅ High Priority

Cron job (automate script execution)
Logging system
Duplicate protection fallback


✅ Medium Priority

Laravel dashboard for visualization
API integration
Alert system (Telegram/Email)


✅ Advanced

Multi-thread scraping
Queue system (Redis)
Microservice deployment


🚀 Execution
Run manually:
python tracker.py


✅ Status Summary
✅ Multi-jeweller support
✅ Multi-template scraping
✅ Multiple rates extraction
✅ Data normalization
✅ MySQL storage
✅ Update-time based change detection
✅ Duplicate-safe insert flow
✅ Clean modular structure

📌 Conclusion
This system is a scalable and production-ready scraper engine that:

Minimizes redundant DB writes
Supports multiple website formats
Ensures data integrity
Is ready for automation and scaling


✅ You can save this as:
/var/www/gold-tracker/docs/gold_tracker.md

