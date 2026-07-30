import requests
from bs4 import BeautifulSoup
import re


def scrape(url, rate_updated):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        block = soup.select_one(
            "div.gold_rates"
        )

        if not block:
            return {
                "rates": [],
                "update_time": None
            }

        # -------------------------------------
        # Extract Update Time
        # -------------------------------------

        update_time = None

        updated = block.select_one(
            "div.updated"
        )

        if updated:

            text = updated.get_text(
                " ",
                strip=True
            )

            match = re.search(
                r"\d{2}/\d{2}/\d{2,4}\s+[\d:]+\s*[AP]M",
                text,
                re.I
            )

            update_time = (
                match.group()
                if match
                else text.replace(
                    "Updated On:",
                    ""
                ).strip()
            )

        # -------------------------------------
        # Already Processed?
        # -------------------------------------

        if update_time and update_time == rate_updated:

            return {
                "rates": [],
                "update_time": update_time
            }

        # -------------------------------------
        # Extract Rates
        # -------------------------------------

        results = []

        for row in block.select("table tr"):

            cells = row.find_all("td")

            if len(cells) < 2:
                continue

            label = cells[0].get_text(
                strip=True
            )

            match = re.search(
                r"[\d,]+\.?\d*",
                cells[1].get_text(strip=True)
            )

            if not label or not match:
                continue

            rate = float(
                match.group().replace(",", "")
            )

            purity = label

            # Optional normalization
            if "24" in label:
                purity = "24K"
            elif "23" in label:
                purity = "23K"
            elif "22" in label:
                purity = "22K"
            elif "18" in label:
                purity = "18K"
            elif "silver" in label.lower():
                purity = "Silver"
            elif "platinum" in label.lower():
                purity = "Platinum"

            results.append({
                "purity": purity,
                "purity_text": label,
                "rate": rate
            })

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:

        print(f"KRA Jewellers Error: {e}")

        return {
            "rates": [],
            "update_time": None
        }