import requests
from lxml import html
import re


def extract_purity(purity_text):
    text = purity_text.upper()

    if "24K GOLD" in text:
        return 24
    elif "22K GOLD" in text:
        return 22
    elif "18K GOLD" in text:
        return 18
    elif "14K GOLD" in text:
        return 14
    elif "PLATINUM" in text:
        return "Platinum"
    elif "SILVER" in text:
        return "Silver"
    else:
        return purity_text  # fallback


def scrape(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    tree = html.fromstring(response.content)

    try:
        # ✅ Extract update time (new logic)
        update_time_node = tree.xpath('//*[@id="update-time"]/text()')
        update_time = None

        if update_time_node:
            update_time = update_time_node[0].strip()

        # ✅ Extract all metal rows
        nodes = tree.xpath("/html/body/div[1]/div[1]/div/div[3]/div/a[3]/div/div[2]/ul/li")

        results = []

        for node in nodes:
            full_text = node.text_content().strip()

            # ✅ Clean purity_text (remove ₹ and after)
            purity_text = re.sub(r"₹.*", "", full_text).strip()

            # ✅ Extract rate
            rate_text = node.xpath(".//span/text()")
            if not rate_text:
                continue

            raw_rate = rate_text[0]

            # ✅ Clean numeric value (remove ₹, commas, text)
            clean_rate = re.sub(r"[^\d.]", "", raw_rate)

            if not clean_rate:
                continue

            rate = float(clean_rate)

            # ✅ Normalize purity
            purity = extract_purity(purity_text)

            results.append({
                "purity": purity,
                "purity_text": purity_text,
                "rate": rate
            })

        # ✅ Final return structure
        return {
            "rates": results,
            "update_time": update_time
        }

    except Exception as e:
        print(f"Template1 Error: {e}")
        return {
            "rates": [],
            "update_time": None
        }