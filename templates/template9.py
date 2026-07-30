import requests


SECRET_KEY = "MoxW4bgfLJbhYzQjXT8VKkdl0l3TI/NAVTkS0AGm+0E="

HEADERS = {
    "Origin": "https://csjewels.com",
    "Referer": "https://csjewels.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def scrape(url, rate_updated):

    try:

        session = requests.Session()

        # -------------------------------------
        # Get Guest Session ID
        # -------------------------------------

        response = session.post(
            f"{url}/indexAction",
            json={
                "secret_key": SECRET_KEY
            },
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        guest_data = response.json()

        guest_id = guest_data.get(
            "guest_id"
        )

        if not guest_id:
            raise Exception(
                "Guest Session ID not found"
            )

        # -------------------------------------
        # Get Rate Data
        # -------------------------------------

        response = session.get(
            f"{url}/getUpdatedRate",
            headers={
                **HEADERS,
                "Guest-Session-ID": guest_id
            },
            timeout=20
        )

        response.raise_for_status()

        payload = response.json()

        # -------------------------------------
        # Extract Update Time
        # -------------------------------------

        update_time = payload.get(
            "updated_on"
        )

        # -------------------------------------
        # Already Processed?
        # -------------------------------------

        if (
            update_time
            and update_time == rate_updated
        ):

            return {
                "rates": [],
                "update_time": update_time
            }

        # -------------------------------------
        # Extract Rates
        # -------------------------------------

        results = []

        for item in payload.get(
            "data",
            []
        ):

            purity_text = item.get(
                "material_name",
                ""
            ).strip()

            rate = item.get(
                "rate"
            )

            if rate in (
                None,
                ""
            ):
                continue

            purity = purity_text

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

        print(f"CS Jewels Error: {e}")

        return {
            "rates": [],
            "update_time": None
        }