import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def clean_rate(value):

    if not value:
        return ""

    match = re.search(
        r"([\d,]+(?:\.\d+)?)",
        value
    )

    if match:
        return (
            match.group(1)
            .replace(",", "")
            .split(".")[0]
        )

    return ""


def scrape(url, rate_updated):

    driver = None

    try:

        options = Options()

        options.page_load_strategy = "eager"
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(60)

        try:
            driver.get(url)

        except TimeoutException:
            print("Kalyan page loading timeout. Continuing...")

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

        time.sleep(3)

        # -----------------------------------------
        # Select INDIA → MAHARASHTRA → PUNE
        # -----------------------------------------

        selects = driver.find_elements(
            By.TAG_NAME,
            "select"
        )

        country_selected = False
        state_selected = False
        store_selected = False

        for select_element in selects:

            try:

                select = Select(select_element)

                options_text = [
                    option.text.strip().upper()
                    for option in select.options
                ]

                if (
                    "INDIA" in options_text
                    and not country_selected
                ):
                    select.select_by_visible_text("INDIA")
                    country_selected = True
                    time.sleep(2)

                elif (
                    "MAHARASHTRA" in options_text
                    and not state_selected
                ):
                    select.select_by_visible_text("MAHARASHTRA")
                    state_selected = True
                    time.sleep(2)

                elif (
                    "PUNE" in options_text
                    and not store_selected
                ):
                    select.select_by_visible_text("PUNE")
                    store_selected = True
                    time.sleep(2)

            except Exception:
                continue

        # -----------------------------------------
        # Click Submit
        # -----------------------------------------

        submit_buttons = driver.find_elements(
            By.XPATH,
            "//button | //input[@type='submit']"
        )

        for button in submit_buttons:

            try:

                button_text = (
                    button.text.strip().upper()
                )

                value_text = (
                    button.get_attribute("value")
                    or ""
                ).strip().upper()

                if (
                    "SUBMIT" in button_text
                    or "SUBMIT" in value_text
                ):
                    driver.execute_script(
                        "arguments[0].click();",
                        button
                    )
                    break

            except Exception:
                continue

        time.sleep(8)

        # -----------------------------------------
        # Extract Update Time
        # -----------------------------------------

        body_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        update_match = re.search(
            r"Board Rate Last Refreshed on\s*"
            r"(\d{2}-\d{2}-\d{4}\s+"
            r"\d{2}:\d{2}:\d{2}\s+IST)",
            body_text,
            re.IGNORECASE
        )

        update_time = (
            update_match.group(1)
            if update_match
            else None
        )

        # -----------------------------------------
        # Already Processed?
        # -----------------------------------------

        if update_time and update_time == rate_updated:

            return {
                "rates": [],
                "update_time": update_time
            }

        # -----------------------------------------
        # Extract 22KT Rate
        # -----------------------------------------

        rate_22k = ""

        all_elements = driver.find_elements(
            By.XPATH,
            "//*"
        )

        for element in all_elements:

            try:

                text = (
                    element.text or ""
                ).strip()

                if (
                    "22 kt" in text.lower()
                    and (
                        "INR" in text.upper()
                        or "₹" in text
                    )
                ):

                    rate_match = re.search(
                        r"22\s*kt"
                        r".{0,100}?"
                        r"(?:INR|₹|Rs\.?)"
                        r"\s*"
                        r"([\d,]+(?:\.\d+)?)",
                        text,
                        re.IGNORECASE | re.DOTALL
                    )

                    if rate_match:

                        rate_22k = clean_rate(
                            rate_match.group(1)
                        )

                        break

            except Exception:
                continue

        if not rate_22k:

            rate_match = re.search(
                r"22\s*kt"
                r".{0,100}?"
                r"(?:INR|₹|Rs\.?)"
                r"\s*"
                r"([\d,]+(?:\.\d+)?)",
                body_text,
                re.IGNORECASE | re.DOTALL
            )

            if rate_match:

                rate_22k = clean_rate(
                    rate_match.group(1)
                )

        if not rate_22k:

            html_source = driver.page_source

            rate_match = re.search(
                r"22\s*kt"
                r".{0,2000}?"
                r"(?:INR|₹|Rs\.?)"
                r"\s*"
                r"([\d,]+(?:\.\d+)?)",
                html_source,
                re.IGNORECASE | re.DOTALL
            )

            if rate_match:

                rate_22k = clean_rate(
                    rate_match.group(1)
                )

        # -----------------------------------------
        # Build Response
        # -----------------------------------------

        results = []

        if rate_22k:

            results.append({
                "purity": "22K",
                "purity_text": "22 KT",
                "rate": float(rate_22k)
            })

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:

        print(f"Kalyan Error: {e}")

        return {
            "rates": [],
            "update_time": None
        }

    finally:

        if driver:
            driver.quit()