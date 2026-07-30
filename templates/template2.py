from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lxml import html
from utils.helper import extract_purity
import re
from datetime import datetime


def scrape(url, rate_updated):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        # ✅ WAIT until jQuery loads content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "last-updated-time-page"))
        )

        # ✅ Get rendered page
        page = driver.page_source
        tree = html.fromstring(page)

        # ✅ Get update_time (NOW WORKS ✅)
        update_time = None

        nodes = tree.xpath('//div[@class="last-updated-time-page"]/text()')

        if nodes:
            raw_text = nodes[0].strip()

            # match = re.search(
            #     r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2} ?[ap]m)",
            #     raw_text,
            #     re.IGNORECASE
            # )

            # if match:
            #     dt = datetime.strptime(match.group(1), "%d/%m/%Y %I:%M %p")
            #     update_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        print("UPDATE TIME:", raw_text)

        # ✅ Skip if no change
        if update_time and update_time == rate_updated:
            driver.quit()
            return {
                "rates": [],
                "update_time": update_time
            }

        # ✅ Extract table data
        rows = tree.xpath('(//tbody[@id="Metal-Rates"])[1]/tr')

        results = []
        seen = set()

        for row in rows:
            cols = row.xpath('./td')

            if len(cols) < 2:
                continue

            purity_text = cols[0].text_content().strip()
            rate_text = cols[1].text_content().strip()

            # ✅ SKIP unwanted entries
            if "24 CT" in purity_text.upper() and ("995" in purity_text or "999" in purity_text or "GW" in purity_text):
                continue

            # ✅ remove duplicates
            key = (purity_text, rate_text)
            if key in seen:
                continue
            seen.add(key)

            # ✅ clean rate
            clean_rate = re.sub(
                r"[^\d.]",
                "",
                rate_text.replace("Rs.", "").replace("₹", "")
            )

            if not clean_rate:
                continue

            rate = float(clean_rate)

            purity = extract_purity(purity_text)

            print(f"{purity_text} → {rate}")

            results.append({
                "purity": purity,
                "purity_text": purity_text,
                "rate": rate
            })

        driver.quit()

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:
        print(f"Template Error: {e}")
        return {
            "rates": [],
            "update_time": None
        }