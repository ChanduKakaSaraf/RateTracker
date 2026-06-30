import re

def extract_purity(purity_text):
    text = purity_text.upper()

    # ✅ Match 24K, 24 K, 22K, etc.
    match = re.search(r"(24|22|18|14)\s*K", text)

    if match:
        return int(match.group(1))

    elif "PLATINUM" in text:
        return "Platinum"
    elif "SILVER" in text:
        return "Silver"

    return purity_text  # fallback