import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


def scrape(url, rate_updated):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # -------------------------------------
        # Extract Update Time
        # -------------------------------------
        update_time = None

        date_div = soup.select_one("div.metal-ticker-date")

        if date_div:
            text = date_div.get_text(" ", strip=True)

            text = re.sub(
                r"Rates\s+as\s+on\s*",
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

            try:
                update_time = datetime.strptime(
                    text,
                    "%d %b %Y"
                ).strftime("%d/%m/%Y")
            except ValueError:
                update_time = text

        # If rates already processed
        if update_time and rate_updated == update_time:
            return {
                "rates": [],
                "update_time": update_time
            }

        # -------------------------------------
        # Extract Rates
        # -------------------------------------
        results = []

        ticker = soup.select("div.metal-ticker-track span")

        for item in ticker:

            text = item.get_text(" ", strip=True)

            if ":" not in text:
                continue

            metal, price = text.split(":", 1)

            metal = metal.strip()

            price = re.sub(r"[₹,]", "", price).strip()
            price = price.split(".")[0]

            purity = None

            if "23.50K" in metal:
                purity = "24K"
            elif re.search(r"\b23K\b", metal):
                purity = "23K"
            elif "22K HM" in metal:
                purity = "22K"
            elif re.search(r"\b18K\b", metal):
                purity = "18K"
            elif "Silver" in metal:
                purity = "Silver"
            elif "Platinum" in metal:
                purity = "Platinum"

            if not purity:
                continue

            results.append({
                "purity": purity,
                "purity_text": metal,
                "rate": float(price)
            })

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:
        print(f"JBJewellers Error: {e}")
        return {
            "rates": [],
            "update_time": None
        }