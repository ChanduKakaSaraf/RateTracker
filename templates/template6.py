import re
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def scrape(url, rate_updated, driver):

    try:

        print("Loading Ranka Jewellers...")

        try:
            driver.get(url)

        except TimeoutException:

            print("Ranka page loading timeout.")
            print("Continuing with loaded page...")

        WebDriverWait(
            driver,
            30
        ).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "body"
                )
            )
        )

        page_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        # -----------------------------------------
        # Update Time
        # -----------------------------------------

        update_time = get_current_datetime()

        if rate_updated == update_time:

            return {
                "rates": [],
                "update_time": update_time
            }

        # -----------------------------------------
        # Extract Rates
        # -----------------------------------------

        patterns = {
            "24K": r"Gold\s*24\s*KT\s*[-|:]*\s*([\d,]+)",
            "23K": r"Gold\s*23\s*KT\s*[-|:]*\s*([\d,]+)",
            "22K": r"Gold\s*22\s*KT\s*[-|:]*\s*([\d,]+)",
            "18K": r"Gold\s*18\s*KT\s*[-|:]*\s*([\d,]+)",
            "Silver": r"Silver\s*[-|:]*\s*([\d,]+)",
            "Platinum": r"Platinum\s*[-|:]*\s*([\d,]+)"
        }

        results = []

        for purity, pattern in patterns.items():

            match = re.search(
                pattern,
                page_text,
                re.IGNORECASE
            )

            if not match:
                continue

            rate = float(
                match.group(1).replace(",", "")
            )

            results.append({
                "purity": purity,
                "purity_text": purity,
                "rate": rate
            })

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:

        print(f"Ranka Error: {e}")

        return {
            "rates": [],
            "update_time": None
        }