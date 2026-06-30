import requests
from lxml import html
from utils.helper import extract_purity
import re



def scrape(url, rate_updated):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    tree = html.fromstring(response.content)

    try:
        update_time = None

        update_time_node = tree.xpath('//*[@class="sc-dtBdUo jhbdXm"]/text()')

        if update_time_node:
            update_time = update_time_node[0].strip()
        
            if rate_updated == update_time:
                return {
                    "rates": [],
                    "update_time": update_time
                }
            

        nodes = tree.xpath("/html/body/div[1]/div[1]/div/div[3]/div/a[3]/div/div[2]/ul/li")

        results = []

        for node in nodes:
            full_text = node.text_content().strip()

            purity_text = re.sub(r"₹.*", "", full_text).strip()

            rate_text = node.xpath(".//span/text()")
            if not rate_text:
                continue

            raw_rate = rate_text[0]
            clean_rate = re.sub(r"[^\d.]", "", raw_rate)

            if not clean_rate:
                continue

            rate = float(clean_rate)

            purity = extract_purity(purity_text)

            results.append({
                "purity": purity,
                "purity_text": purity_text,
                "rate": rate
            })

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


    except Exception as e:
        print(f"Template1 Error: {e}")
        return {
            "rates": [],
            "update_time": None
        }