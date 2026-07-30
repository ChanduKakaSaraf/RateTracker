from playwright.sync_api import sync_playwright


def scrape(url, rate_updated):
    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                channel="chrome",
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )

            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                locale="en-IN",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()

            page.goto(
                url,
                wait_until="load",
                timeout=120000
            )

            page.wait_for_selector(
                "table.goldrate-history-table tbody tr",
                timeout=6000
            )

            row = page.locator(
                "table.goldrate-history-table tbody tr"
            ).first

            update_time = row.locator("td").nth(0).inner_text().strip()

            if update_time and rate_updated == update_time:
                browser.close()
                return {
                    "rates": [],
                    "update_time": update_time
                }

            span = row.locator("span.goldpurity-rate")

            rates = []

            rate_18k = span.get_attribute("data-goldrate18kt")
            rate_22k = span.get_attribute("data-goldrate22kt")
            rate_24k = span.get_attribute("data-goldrate24kt")

            if rate_18k:
                rates.append({
                    "purity": "18K",
                    "purity_text": "18K",
                    "rate": float(rate_18k.replace(",", ""))
                })

            if rate_22k:
                rates.append({
                    "purity": "22K",
                    "purity_text": "22K",
                    "rate": float(rate_22k.replace(",", ""))
                })

            if rate_24k:
                rates.append({
                    "purity": "24K",
                    "purity_text": "24K",
                    "rate": float(rate_24k.replace(",", ""))
                })

            browser.close()

            return {
                "rates": rates,
                "update_time": update_time
            }

    except Exception as e:
        print(f"Tanishq Error: {e}")
        return {
            "rates": [],
            "update_time": None
        }
