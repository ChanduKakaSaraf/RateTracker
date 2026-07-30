import json
import requests


def scrape(url, rate_updated):

    query = (
        "query getMetalRate($filter: MetalRateFilterInput) { "
        "getMetalRate(filter: $filter) { "
        "items { entry_date entry_time purity unit rate country state } } }"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.malabargoldanddiamonds.com/in/pan-india/en/live-gold-rate.html"
    }

    try:

        response = requests.get(
            url,
            params={
                "query": query,
                "variables": json.dumps({
                    "filter": {
                        "metal_type": "gold",
                        "country": "India"
                    }
                })
            },
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        payload = response.json()

        if "errors" in payload:
            raise Exception(str(payload["errors"]))

        items = payload["data"]["getMetalRate"]["items"]

        # -------------------------------------
        # Extract Update Time
        # -------------------------------------

        if items:

            latest_date = max(
                item["entry_date"]
                for item in items
            )

            times = [
                item["entry_time"]
                for item in items
                if item["entry_date"] == latest_date
            ]

            update_time = (
                f"{latest_date},{min(times)}"
                if times
                else latest_date
            )

        else:

            update_time = None

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

        purity_map = {
            "24k": "24K",
            "22k": "22K",
            "23k": "23K",
            "18k": "18K"
        }

        for item in items:

            purity_text = item.get(
                "purity",
                ""
            ).strip()

            purity = purity_map.get(
                purity_text.lower(),
                purity_text
            )

            rate = item.get("rate")

            if not rate:
                continue

            results.append({
                "purity": purity,
                "purity_text": purity_text,
                "rate": float(str(rate).replace(",", ""))
            })

        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:

        print(f"Malabar Error: {e}")

        return {
            "rates": [],
            "update_time": None
        }